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
import os
import time
from datetime import datetime
from  collections import namedtuple

#不准。。应该获取远程机器上的
#但是这里开发机、测试机时钟数一样。所以这样搞了
CLOCK_TICKS = os.sysconf("SC_CLK_TCK")
#获取cpu time的字段
def get_cputimes_fields(vlen):
    """Return a namedtuple of variable fields depending on the
    CPU times available on this Linux kernel version which may be:
    (user, nice, system, idle, iowait, irq, softirq, [steal, [guest,
     [guest_nice]]])
    """
    fields = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq']
    if vlen >= 8:
        # Linux >= 2.6.11
        fields.append('steal')
    if vlen >= 9:
        # Linux >= 2.6.24
        fields.append('guest')
    if vlen >= 10:
        # Linux >= 3.2.0
        fields.append('guest_nice')
    return fields

#获取cpu时间,除以的时钟数
def cpu_times(ssh):
    try:
        stdin,stdout,stderr = ssh.exec_command("head -1 /proc/stat")
        _cpuData = stdout.read().split()[1:]
    except Exception,e:
        logger.error("获取cpu信息失败！")
        return None
    _cpuData = [float(d) / CLOCK_TICKS  for d in _cpuData ]
    _fields = get_cputimes_fields(len(_cpuData))
    cputime =  namedtuple("cpuTime",_fields)
    return cputime(*_cpuData)

#默认阻塞式计算cpu使用率
def get_cpu_percent(ssh,interval):
    def calculate(t1,t2):
        nums = []
        all_delta = sum(t2)- sum(t1)
        for field in t1._fields:
            field_delta = getattr(t2,field) - getattr(t1,field)
            try:
                field_perc = ( field_delta / all_delta ) * 100
            except ZeroDivisionError:
                field_perc = 0.0
            finally:
                field_perc = round(field_perc,2)
            if field_perc > 100.0:
                field_perc = 100.0
            if field_perc < 0.0:
                field_perc = 0.0
            nums.append(field_perc)
        return nums
    t1 = cpu_times(ssh)
    time.sleep(interval)
    t2 = cpu_times(ssh)
    return calculate(t1,t2),datetime.now().strftime("%Y%m%d%H%M%S")
