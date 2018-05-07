#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: tanglingling
@contact: tanglingling@maimiaotech.com
@date: 2018-04-27 14:14
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""
import time
from datetime import datetime
from collections import namedtuple

def get_network_info_fields():
    return ["bytes_recv","bytes_sent","packets_recv","packets_sent","errs_in","errs_out","drops_in","drops_out"]
def get_network_info(ssh):
    '''
    bytes: the total number of bytes of data transmitted or received by the interface.
    packets: the  total number of packets of data transmitted or received by the interface.
    errs : the total number of transmit or receive errors detected by the device driver .
    drop: the total number of packets dropped by the device driver.
    fifo : the number of FIFO buffer errors.
    frame : the number of packet framing errors.
    colls: the numbere of collisions detected on the interface. 
    compressed : the number of compressed packets  transmitted or received by the device driver.
    carrier : the number of carrier losses  detected by the device driver .
    multicast: the number of multicast frames transmitted or received by the device driver . 
    '''
    stdin,stdout,stderr = ssh.exec_command("cat /proc/net/dev")
    netinfo = stdout.read().split("\n")[2:-1]
    netinfo_list = []
    for info in netinfo :
        netinfo_list.append(info.split()[1:])
    _fields = get_network_info_fields()
    res = dict(zip(_fields,[0]*len(_fields)))
    for info in netinfo_list:
        res["bytes_recv"] += int(info[0])
        res["bytes_sent"] += int(info[8])
        res["packets_recv"] += int(info[1])
        res["packets_sent"] += int(info[9])
        res["errs_in"] += int(info[2])
        res["errs_out"] += int(info[10])
        res["drops_in"] += int(info[3])
        res["drops_out"] += int(info[11])
    resTuple = namedtuple("netInfos",res.keys())
    return  resTuple(*res.values())

def get_network_bps(ssh,interval = 1):
    net1 = get_network_info(ssh)
    time.sleep(interval)
    net2 = get_network_info(ssh)
    KBps = ((net2.bytes_recv - net1.bytes_recv ) + (net2.bytes_sent - net1.bytes_sent))/1000.0
    return KBps,datetime.now().strftime("%Y%m%d%H%M%S")
