# Copyright (c) 2015 ttsubo
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import json
import logging
import datetime
import time

from webob import Response
from ryu.base import app_manager
from simpleBGPSpeaker import SimpleBGPSpeaker
from ryu.lib import dpid
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route

LOG = logging.getLogger('bgpSimulator')
LOG.setLevel(logging.INFO)

class BgpSimulator(app_manager.RyuApp):
    _CONTEXTS = {
        'bgps' : SimpleBGPSpeaker,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(BgpSimulator, self).__init__(*args, **kwargs)
        self.bgps = kwargs['bgps']
        self.ports = {}
        wsgi = kwargs['wsgi']
        wsgi.register(RouterController, {'BgpSimulator' : self})


    def get_bgp_rib(self):
        return self.bgps.show_rib()


    def get_bgp_vrfs(self):
        return self.bgps.show_vrfs()


    def get_bgp_neighbor(self, routetype, address):
        return self.bgps.show_neighbor(routetype, address)


    def start_bgpspeaker(self, dpid, as_number, router_id, label_range_start, label_range_end):
        if as_number:
            asNum = int(as_number)
            label_start = int(label_range_start)
            label_end = int(label_range_end)
        LOG.debug("start BGPSpeaker [%s, %s]"%(as_number, router_id))
        self.bgps.start_bgpspeaker(asNum, router_id, label_start, label_end)


    def register_vrf(self, dpid, vrf_routeDist, importRt, exportRt):
        importList = []
        exportList = []
        importList.append(importRt)
        exportList.append(exportRt)
        LOG.debug("Register vrf(RD:%s)"%vrf_routeDist)
        self.bgps.add_vrf(vrf_routeDist, importList, exportList)


    def delete_vrf(self, dpid, vrf_routeDist):
        LOG.debug("Delete vrf(RD:%s)"%vrf_routeDist)
        self.bgps.del_vrf(vrf_routeDist)


    def register_inf(self, dpid, routerIp, netMask, routerMac, hostIp, asNumber, Port, bgpPort, med, localPref, filterAsNumber, vrf_routeDist):
        LOG.debug("Register Interface(port%s)"% Port)
        outPort = int(Port)

        if asNumber:
            asNum = int(asNumber)

        if med:
            medValue = int(med)
        else:
            medValue = None

        if localPref:
            localPrefValue = int(localPref)
        else:
            localPrefValue = None

        if filterAsNumber:
            filterAsNum = int(filterAsNumber)
        else:
            filterAsNum = None

        LOG.debug("start BGP peering with [%s]"% hostIp)
        self.bgps.add_neighbor(hostIp, asNum, medValue, localPrefValue,
                               filterAsNum)


    def update_neighborMed(self, dpid, peerIp, med): 
        LOG.debug("change MED [%s]"% med)
        med_value = int(med)
        self.bgps.update_neighbor_med(peerIp, med_value)


class RouterController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(RouterController, self).__init__(req, link, data, **config)
        self.router_spp = data['BgpSimulator']


    @route('router', '/openflow/{dpid}/neighbor', methods=['GET'], requirements={'dpid': dpid.DPID_PATTERN})
    def get_bgpneighbor(self, req, dpid, **kwargs):
        show_param = eval(req.body)
        result = self.getBgpNeighbor(int(dpid, 16), show_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/vrf', methods=['GET'], requirements={'dpid': dpid.DPID_PATTERN})
    def get_bgpvrfs(self, req, dpid, **kwargs):
        result = self.getBgpVrfs(int(dpid, 16))
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/rib', methods=['GET'], requirements={'dpid': dpid.DPID_PATTERN})
    def get_bgprib(self, req, dpid, **kwargs):
        result = self.getBgpRib(int(dpid, 16))
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)



    @route('router', '/openflow/{dpid}/bgp', methods=['POST'], requirements={'dpid': dpid.DPID_PATTERN})
    def start_bgp(self, req, dpid, **kwargs):
        bgp_param = eval(req.body)
        result = self.startBgp(int(dpid, 16), bgp_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/bmp', methods=['POST'], requirements={'dpid': dpid.DPID_PATTERN})
    def start_bmp(self, req, dpid, **kwargs):
        bmp_param = eval(req.body)
        result = self.startBmp(int(dpid, 16), bmp_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/bmp', methods=['DELETE'], requirements={'dpid': dpid.DPID_PATTERN})
    def stop_bmp(self, req, dpid, **kwargs):
        bmp_param = eval(req.body)
        result = self.stopBmp(int(dpid, 16), bmp_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/vrf', methods=['POST'], requirements={'dpid': dpid.DPID_PATTERN})
    def create_vrf(self, req, dpid, **kwargs):
        vrf_param = eval(req.body)
        result = self.createVrf(int(dpid, 16), vrf_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/vrf', methods=['DELETE'], requirements={'dpid': dpid.DPID_PATTERN})
    def delete_vrf(self, req, dpid, **kwargs):
        vrf_param = eval(req.body)
        result = self.deleteVrf(int(dpid, 16), vrf_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/interface', methods=['POST'], requirements={'dpid': dpid.DPID_PATTERN})
    def set_interface(self, req, dpid, **kwargs):
        interface_param = eval(req.body)
        result = self.setInterface(int(dpid, 16), interface_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    @route('router', '/openflow/{dpid}/neighbor', methods=['PUT'], requirements={'dpid': dpid.DPID_PATTERN})
    def update_med(self, req, dpid, **kwargs):
        neighbor_param = eval(req.body)
        result = self.updateNeighborMed(int(dpid, 16), neighbor_param)
        message = json.dumps(result)
        return Response(status=200,
                        content_type = 'application/json',
                        body = message)


    def startBgp(self, dpid, bgp_param):
        simpleRouter = self.router_spp
        as_number = bgp_param['bgp']['as_number']
        router_id = bgp_param['bgp']['router_id']
        label_range_start = bgp_param['bgp']['label_range_start']
        label_range_end = bgp_param['bgp']['label_range_end']
        simpleRouter.start_bgpspeaker(dpid, as_number, router_id, label_range_start, label_range_end)
        return {
            'id': '%016d' % dpid,
            'bgp': {
                'as_number': '%s' % as_number,
                'router_id': '%s' % router_id,
                'label_range_start': '%s' % label_range_start,
                'label_range_end': '%s' % label_range_end,
            }
        }


    def startBmp(self, dpid, bmp_param):
        simpleRouter = self.router_spp
        address = bmp_param['bmp']['address']
        port = bmp_param['bmp']['port']
        simpleRouter.start_bmpclient(dpid, address, port)
        return {
            'id': '%016d' % dpid,
            'bmp': {
                'address': '%s' % address,
                'port': '%s' % port,
            }
        }


    def stopBmp(self, dpid, bmp_param):
        simpleRouter = self.router_spp
        address = bmp_param['bmp']['address']
        port = bmp_param['bmp']['port']
        simpleRouter.stop_bmpclient(dpid, address, port)
        return {
            'id': '%016d' % dpid,
            'bmp': {
                'address': '%s' % address,
                'port': '%s' % port,
            }
        }


    def createVrf(self, dpid, vrf_param):
        simpleRouter = self.router_spp
        routeDist = vrf_param['vrf']['route_dist']
        importRt = vrf_param['vrf']['import']
        exportRt = vrf_param['vrf']['export']
        simpleRouter.register_vrf(dpid, routeDist, importRt, exportRt)
        return {
            'id': '%016d' % dpid,
            'vrf': {
                'route_dist': '%s' % routeDist,
                'import': '%s' % importRt,
                'export': '%s' % exportRt,
            }
        }


    def deleteVrf(self, dpid, vrf_param):
        simpleRouter = self.router_spp
        routeDist = vrf_param['vrf']['route_dist']
        simpleRouter.delete_vrf(dpid, routeDist)
        return {
            'id': '%016d' % dpid,
            'vrf': {
                'route_dist': '%s' % routeDist
            }
        }


    def setInterface(self, dpid, interface_param):
        simpleRouter = self.router_spp
        routerMac = interface_param['interface']['macaddress']
        routerIp = interface_param['interface']['ipaddress']
        netMask = interface_param['interface']['netmask']
        port = interface_param['interface']['port']
        hostIp = interface_param['interface']['opposite_ipaddress']
        asNumber = interface_param['interface']['opposite_asnumber']
        port_offload_bgp = interface_param['interface']['port_offload_bgp']
        bgp_med = interface_param['interface']['bgp_med']
        bgp_local_pref = interface_param['interface']['bgp_local_pref']
        filterAsNumber = interface_param['interface']['bgp_filter_asnumber']
        vrf_routeDist = interface_param['interface']['vrf_routeDist']
        simpleRouter.register_inf(dpid, routerIp, netMask, routerMac, hostIp, asNumber, port, port_offload_bgp, bgp_med, bgp_local_pref, filterAsNumber, vrf_routeDist)
        return {
            'id': '%016d' % dpid,
            'interface': {
                'port': '%s' % port,
                'macaddress': '%s' % routerMac,
                'ipaddress': '%s' % routerIp,
                'netmask': '%s' % netMask,
                'opposite_ipaddress': '%s' % hostIp,
                'opposite_asnumber': '%s' % asNumber,
                'port_offload_bgp': '%s' % port_offload_bgp,
                'bgp_med': '%s' % bgp_med,
                'bgp_local_pref': '%s' % bgp_local_pref,
                'bgp_filter_asnumber': '%s' % filterAsNumber,
                'vrf_routeDist': '%s' % vrf_routeDist
            }
        }


    def redistributeConnect(self, dpid, connect_param):
        simpleRouter = self.router_spp
        redistribute = connect_param['bgp']['redistribute']
        vrf_routeDist = connect_param['bgp']['vrf_routeDist']
        simpleRouter.redistribute_connect(dpid, redistribute, vrf_routeDist)
        return {
            'id': '%016d' % dpid,
            'bgp': {
                'redistribute': '%s' % redistribute,
                'vrf_routeDist': '%s' % vrf_routeDist,
            }
        }


    def updateNeighborMed(self, dpid, neighbor_param):
        simpleRouter = self.router_spp
        peerIp = neighbor_param['neighbor']['peerIp']
        med = neighbor_param['neighbor']['med']
        simpleRouter.update_neighborMed(dpid, peerIp, med)
        return {
            'id': '%016d' % dpid,
            'neighbor': {
                'peerIp': '%s' % peerIp,
                'med': '%s' % med,
            }
        }


    def getBgpNeighbor(self, dpid, show_param):
        simpleRouter = self.router_spp
        routetype = show_param['neighbor']['routetype']
        address = show_param['neighbor']['address']
        nowtime = datetime.datetime.now()
        LOG.info("+++++++++++++++++++++++++++++++")
        LOG.info("%s : Show neighbor " % nowtime.strftime("%Y/%m/%d %H:%M:%S"))
        LOG.info("+++++++++++++++++++++++++++++++")
        result = simpleRouter.get_bgp_neighbor(routetype, address)
        LOG.info("%s" % result)
        return {
          'id': '%016d' % dpid,
          'time': '%s' % nowtime.strftime("%Y/%m/%d %H:%M:%S"),
          'neighbor': '%s' % result,
        }


    def getBgpVrfs(self, dpid):
        simpleRouter = self.router_spp
        nowtime = datetime.datetime.now()
        LOG.info("+++++++++++++++++++++++++++++++")
        LOG.info("%s : Show vrf " % nowtime.strftime("%Y/%m/%d %H:%M:%S"))
        LOG.info("+++++++++++++++++++++++++++++++")
        result = simpleRouter.get_bgp_vrfs()
        LOG.info("%s" % result)
        return {
          'id': '%016d' % dpid,
          'time': '%s' % nowtime.strftime("%Y/%m/%d %H:%M:%S"),
          'vrfs': '%s' % result,
        }


    def getBgpRib(self, dpid):
        simpleRouter = self.router_spp
        nowtime = datetime.datetime.now()
        LOG.info("+++++++++++++++++++++++++++++++")
        LOG.info("%s : Show rib " % nowtime.strftime("%Y/%m/%d %H:%M:%S"))
        LOG.info("+++++++++++++++++++++++++++++++")
        result = simpleRouter.get_bgp_rib()
        LOG.info("%s" % result)
        return {
          'id': '%016d' % dpid,
          'time': '%s' % nowtime.strftime("%Y/%m/%d %H:%M:%S"),
          'rib': '%s' % result,
        }

