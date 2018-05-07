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
from datetime import datetime 

def get_memory_percent(ssh):
    try:
        stdin,stdout,stderr = ssh.exec_command("free -k")
        result = stdout.read()
    except Exception,e:
        logger.error("获取内存信息失败！")
        return None,None,None
    memory = [k for k in result.split()]
    #['total', 'used', 'free', 'shared', 'buffers', 'cached', 'Mem:', '7915092', '6942328', '972764', '0', '754656', '4078556', '-/+', 'buffers/cache:', '2109116', '5805976', 'Swap:', '0', '0', '0']
    mem_total = int(memory[7])*1024
    mem_used_no_cachebuffer = int(memory[15])*1024
    swap_total = int(memory[18])*1024
    swap_used = int(memory[19]) * 1024
    return (round(mem_used_no_cachebuffer*100.0/mem_total,2) if mem_total else 0.0 , round(swap_used*100.0/swap_total,2) if swap_total else 0.0,datetime.now().strftime("%Y%m%d%H%M%S"))

def get_memory_fields():
    return ["mem_used","swap_used"]
