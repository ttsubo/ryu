#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
from common_func import request_info

###############
# get_rib
###############

def start_get_rib(dpid):
    operation = "get_rib"
    url_path = "/openflow/" + dpid + "/rib" 
    method = "GET"

    rib_result = request_info(operation, url_path, method, "")
    print ""
    result = rib_result['rib']
    print "%s" % result
    print ""
        

##############
# main
##############

def main():
    dpid = "0000000000000001"
    start_get_rib(dpid)


if __name__ == "__main__":
    main()
