#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
from httplib import HTTPConnection

HOST = "127.0.0.1"
PORT = "8080"

##################
# request_info
##################

def request_info(operator, url_path, method, request=None):
    session = HTTPConnection("%s:%s" % (HOST, PORT))

    header = {
        "Content-Type": "application/json"
        }
    if method == "GET":
        if request:
            session.request("GET", url_path, request, header)
        else:
            session.request("GET", url_path, "", header)
    elif method == "POST":
        session.request("POST", url_path, request, header)
    elif method == "PUT":
        session.request("PUT", url_path, request, header)
    elif method == "DELETE":
        session.request("DELETE", url_path, request, header)

    return json.load(session.getresponse())

