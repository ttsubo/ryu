#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import time
from oslo_config import cfg
from common_func import request_info

port1_opts = []
port2_opts = []
port3_opts = []

port1_opts.append(cfg.StrOpt('port', default=[], help='OpenFlow Port'))
port1_opts.append(cfg.StrOpt('macaddress', default=[], help='MacAddress'))
port1_opts.append(cfg.StrOpt('ipaddress', default=[], help='IpAddress'))
port1_opts.append(cfg.StrOpt('netmask', default=[], help='netmask'))
port1_opts.append(cfg.StrOpt('opposite_ipaddress', default=[],
                   help='opposite_IpAddress'))
port1_opts.append(cfg.StrOpt('opposite_asnumber', default=[],
                   help='opposite_asnumber'))
port1_opts.append(cfg.StrOpt('port_offload_bgp', default=[], help='port_offload_bgp'))
port1_opts.append(cfg.StrOpt('bgp_med', default=[], help='bgp_med'))
port1_opts.append(cfg.StrOpt('bgp_local_pref', default=[], help='bgp_local_pref'))
port1_opts.append(cfg.StrOpt('bgp_filter_asnumber', default=[], help='bgp_filter_asnumber'))
port1_opts.append(cfg.StrOpt('vrf_routeDist', default=[], help='vrf_routeDist'))


CONF = cfg.CONF
CONF.register_cli_opts(port1_opts, 'Port1')


##################
# create_interface
##################

def start_create_interface(dpid, port, macaddress, ipaddress, netmask, opposite_ipaddress, opposite_asnumber, port_offload_bgp, bgp_med, bgp_local_pref, bgp_filter_asnumber, vrf_routeDist):
    operation = "create_interface"
    url_path = "/openflow/" + dpid + "/interface"
    method = "POST"
    request = '''
{
"interface": {
"port": "%s",
"macaddress": "%s",
"ipaddress": "%s",
"netmask": "%s",
"opposite_ipaddress": "%s",
"opposite_asnumber": "%s",
"port_offload_bgp": "%s",
"bgp_med": "%s",
"bgp_local_pref": "%s",
"bgp_filter_asnumber": "%s",
"vrf_routeDist": "%s"
}
}'''% (port, macaddress, ipaddress, netmask, opposite_ipaddress, opposite_asnumber, port_offload_bgp, bgp_med, bgp_local_pref, bgp_filter_asnumber, vrf_routeDist)

    interface_result = request_info(operation, url_path, method, request)
    print "----------"
    print json.dumps(interface_result, sort_keys=False, indent=4)
    print ""


##############
# main
##############

def main():
    dpid = "0000000000000001"
    try:
        CONF(default_config_files=['BGP.ini'])
        port1 = CONF.Port1.port
        macaddress1 = CONF.Port1.macaddress
        ipaddress1 = CONF.Port1.ipaddress
        netmask1 = CONF.Port1.netmask
        opposite_ipaddress1 = CONF.Port1.opposite_ipaddress
        opposite_asnumber1 = CONF.Port1.opposite_asnumber
        port_offload_bgp1 = CONF.Port1.port_offload_bgp
        bgp_med1 = CONF.Port1.bgp_med
        bgp_local_pref1 = CONF.Port1.bgp_local_pref
        bgp_filter_asnumber1 = CONF.Port1.bgp_filter_asnumber
        vrf_routeDist1 = CONF.Port1.vrf_routeDist
    except cfg.ConfigFilesNotFoundError:
        print "Error: Not Found <BGP.ini> "

    start_create_interface(dpid, port1, macaddress1, ipaddress1, netmask1,
                           opposite_ipaddress1, opposite_asnumber1,
                           port_offload_bgp1, bgp_med1, bgp_local_pref1,
                           bgp_filter_asnumber1, vrf_routeDist1)

if __name__ == "__main__":
    main()
