#!/usr/bin/env python3

from datetime import datetime
import json
import requests
from requests.exceptions import Timeout
import sys
import time

def http_get(session, uri, timeout=5, retries=1):
    """
    This function attempts to retrieve the specified URI using an HTTP GET request.
    If a timeout is specified, the function will wait at most that number of seconds.
    """

    attempt = 0
    while attempt <= retries:
        start = time.time()

        response = None
        try:
            response = session.get(uri, timeout=timeout)

        except Timeout:
            print(f"HTTP GET timed out (timeout was set to {timeout} sec)")
            attempt += 1

        except Exception as e:
            print("HTTP GET failed for {} with exception: {}".format(uri, e))
            sys.exit(1)

        else:
            end = time.time()
            elapsed = end - start
            #print("Request took {0:.3f} seconds".format(elapsed))
            break

    if attempt == retries:
        print(f"Too many timeouts ({attempt}) for HTTP GET")
        sys.exit(1)

    return response

def http_post(session, uri, post_data, timeout=5):
    """
    This function attempts to make an HTTP POST to the specified URI
    """
    #print(f"Making POST request to {uri}")

    start = time.time()

    if post_data == None:
        post_data = ""

    #print(post_data)
    response = None
    try:
        response = session.post(uri, data=post_data, timeout=timeout)

    except Exception as e:
        print("HTTP POST failed for {} with exception: {}".format(uri, e))
        sys.exit(1)

    end = time.time()
    elapsed = end - start
    #print("Request took {0:.3f} seconds".format(elapsed))

    return response

def get_bool(session, uri):
    """
    This function performs an HTTP GET for the specified URI, and returns True
    or False depending on the response code.
    """
    response = http_get(session, uri)

    if response.status_code == 200:
        return True
    else:
        return False

def get_json(session, uri):
    """
    This function GETs the specified URI, expecting a JSON response.
    The JSON response is formatted into a python dictionary and returned.
    """
    response = http_get(session, uri)

    if response.status_code != 200:
        print(f"HTTP GET failed for {uri}")
        sys.exit(1)

    json_result = response.content.decode('utf-8')
    dict_result = json.loads(json_result)
    return dict_result

def post_cmd(session, uri, obj):
    post_data = json.dumps(obj)
    post_data = {
            "json": post_data
        }

    response = http_post(session, uri, post_data)

    if response.status_code != 200:
        print(f"Kismet command failed for {uri} with status {response.status_code}")
        sys.exit(1)

def post_cmd_json(session, uri, obj):
    post_data = json.dumps(obj)
    post_data = {
            "json": post_data
        }

    response = http_post(session, uri, post_data)

    if response.status_code != 200:
        print(f"Kismet command failed for {uri} with status {response.status_code}")
        sys.exit(1)

    json_result = response.content.decode('utf-8')
    dict_result = json.loads(json_result)
    return dict_result

def check_session(session, base_uri):
    return get_bool(session, f"{base_uri}/session/check_session")

def get_sources(session, base_uri):
    """
    Return a dictionary of all available datasources on the kismet server
    """
    uri = f"{base_uri}/datasource/all_sources.json"
    return get_json(session, uri)

def get_interfaces(session, base_uri):
    """
    Return a dictionary of all available interfaces on the kismet server
    """
    uri = f"{base_uri}/datasource/list_interfaces.json"
    return get_json(session, uri)

def have_source(session, base_uri, source_name):
    """
    This function determines whether the specified datasource is known to
    the Kismet server

    Arguments:
    source_name -- The name of a datasource to look for
    """
    sources = get_sources(session, base_uri)
    for source in sources:
        if source['kismet.datasource.name'] == source_name:
            return True
    
    return False

def add_source(session, base_uri, interface_name):
    """
    This function adds the specified interface as a datasource

    Arguments:
    interface_name -- The name of an interface to look for
    """
    print(f"Adding datasource {interface_name}")

    cmd = {
        "definition": interface_name
    }

    post_cmd(session, f"{base_uri}/datasource/add_source.cmd", cmd)

def have_interface(session, base_uri, interface_name):
    """
    This function determines whether the specified interface is known to
    the Kismet server

    Arguments:
    interface_name -- The name of an interface to look for
    """
    interfaces = get_interfaces(session, base_uri)
    for interface in interfaces:
        if interface['kismet.datasource.probed.interface'] == interface_name:
            return True

    return False

def set_channel(session, base_uri, uuid, channel):
    print(f"Setting channel for datasource {uuid} to {channel}")

    cmd = {
        "channel": channel
    }

    post_cmd(session, f"{base_uri}/datasource/by-uuid/{uuid}/set_channel.cmd", cmd)
