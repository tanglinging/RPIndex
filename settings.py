#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: tanglingling
@contact: tanglingling@maimiaotech.com
@date: 2018-05-09 10:54
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""
####
resource = "remote_service_index"
import logging
logger = logging.getLogger(resource)
handler = logging.FileHandler("/alidata1/logs/%s/%s.log" % (resource,resource))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s:%(lineno)-15d %(message)s') 
handler.setFormatter(formatter)
logger.addHandler(handler)
####
DATA_PATH = {
    "cpu":"/home/tangll/cpu_percs.txt",
    "memory":"/home/tangll/mem_percs.txt",
    "disk":"/home/tangll/disk_info.txt",
    "network":"/home/tangll/net_percs.txt",
}
FIG_PATH = {
    "cpu":"/home/tangll/cpu_percs.jpg",
    "memory":"/home/tangll/mem_percs.jpg",
    "disk":"/home/tangll/disk_info.jpg",
    "network":"/home/tangll/net_percs.jpg",
}
TITLES = {
    "cpu":"CPU Performance Infos by Time",
    "memory":"Memory&Swap Utilization by Time",
    "disk":"Disk Read&Write Infos by Time",
    "network":"Network Bandwith by Time",
}
privateKeyPath = "/home/tangll/.ssh/id_rsa"
