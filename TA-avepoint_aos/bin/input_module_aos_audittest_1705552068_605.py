# encoding = utf-8
import os
import sys
import time
import datetime
import urllib.parse
import json
from datetime import datetime, timedelta
from dateutil.parser import parse as dp
from dateutil.tz import UTC
'''
IMPORTANT
Edit only the validate_input and collect_events functions.
Do not edit any other part in this file.
This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
return True
'''
def validate_input(helper, definition):
    #"""Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # client_id = definition.parameters.get('client_id', None)
    # client_secret = definition.parameters.get('client_secret', None)
    pass
def collect_events(helper, ew):
    # """Implement your data collection logic here
    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_client_id = helper.get_arg('client_id')
    opt_client_secret = helper.get_arg('client_secret')
    opt_identity_services_url = helper.get_arg('identity_services_url')
    opt_web_api_url = helper.get_arg('web_api_url')
# In single instance mode, to get arguments of a particular input, use
# opt_client_id = helper.get_arg('client_id', stanza_name)
# opt_client_secret = helper.get_arg('client_secret', stanza_name)
# opt_identity_services_url = helper.get_arg('identity_services_url', stanza_name)
# opt_web_api_url = helper.get_arg('web_api_url', stanza_name)
    
# get input type
    helper.get_input_type()

# The following examples get input stanzas.
# get all detailed input stanzas
# helper.get_input_stanza()
# get specific input stanza with stanza name
# helper.get_input_stanza(stanza_name)
# get all stanza names
# helper.get_input_stanza_names()
# The following examples get options from setup page configuration.
# get the loglevel from the setup page
# loglevel = helper.get_log_level()
# get proxy setting configuration
# proxy_settings = helper.get_proxy()
# get account credentials as dictionary
# account = helper.get_user_credential_by_username("username")
# account = helper.get_user_credential_by_id("account id")
# get global variable configuration
# global_userdefined_global_var = helper.get_global_setting("userdefined_global_var")
# The following examples show usage of logging related helper functions.
# write to the log for this modular input using configured global log level or INFO as default
# helper.log("log message")
# write to the log using specified log level
# helper.log_debug("log message")
# helper.log_info("log message")
# helper.log_warning("log message")
# helper.log_error("log message")
# helper.log_critical("log message")
# set the log level for this modular input
# (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
# helper.set_log_level("debug")
# The following examples send rest requests to some endpoint.
    verifyHTTPS = False
    url = f"{opt_identity_services_url}/connect/token"
    method = 'Post'
    payload = {
        "client_id": opt_client_id,
        "client_secret": opt_client_secret,
        "scope": "audit.read.all",
        "grant_type" : "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = helper.send_http_request(
        url,
        method,
        parameters=None,
        payload=urllib.parse.urlencode(payload),
        headers=headers,
        cookies=None,
        verify=verifyHTTPS,
        cert=None,
        timeout=60,
        use_proxy=True)
    
# helper.log_debug(response.text)

# check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()
    access_token = response.json()["access_token"]

# helper.delete_check_point('lastEventTimeInSeconds')
    lastEventTimeInSecondsFromCache = helper.get_check_point('lastEventTimeInSeconds')
    helper.log_info(f"The last event: {str(lastEventTimeInSecondsFromCache)}")

# Please note: The audit logs of some products are written with delay, so a buffer of at least 5 minutes needs to be reserved here.
    end_time = datetime.utcnow() - timedelta(minutes=5)
    end_time = end_time.replace(tzinfo=UTC)

    if lastEventTimeInSecondsFromCache is None:
        start_time = end_time - timedelta(days=7)
    else:
        start_time = dp(lastEventTimeInSecondsFromCache)
    if (end_time - timedelta(days=7)) > start_time:
        start_time = end_time - timedelta(days=7)
    helper.log_info(f"Start time: {start_time.isoformat()}, End time: {end_time.isoformat()}")

# get response body as json. If the body text is not a json string, raise a ValueError
    url = f'{opt_web_api_url}/audit'
    method = 'Get'
    parameters = {
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat()
    }
    headers = {"Authorization": "Bearer " + access_token }

    while True:
        response = helper.send_http_request(
            url,
            method,
            parameters=parameters,
            payload=None,
            headers=headers,
            cookies=None,
            verify=verifyHTTPS,
            cert=None,
            timeout=300,
            use_proxy=True)
        helper.log_debug(response.text)
        response.raise_for_status()

# get the response headers
# r_headers = response.headers
# get the response body as text
# r_text = response.text
# get response body as json. If the body text is not a json string, raise a ValueError

    r_json = response.json()
    helper.log_debug(r_json['data'])


    for d in r_json['data']:
        realData = json.dumps(d)
        event = helper.new_event(
            time=dp(d["actionTime"]).timestamp(),
            source=helper.get_input_type(),
            index=helper.get_output_index(),
            sourcetype=helper.get_sourcetype(),
            data=realData,
            done=True,
            unbroken=True)
        helper.log_debug(realData)
        ew.write_event(event)

        if r_json['nextLink'] is None:
            helper.log_debug("No next link")
        break
    else:
        url = r_json['nextLink']
        parameters = None
        helper.log_debug(f"Next link is {url}")
        helper.save_check_point('lastEventTimeInSeconds', end_time.isoformat())
        helper.log_debug(f"Update lastEventTimeInSeconds to {end_time.isoformat()}")