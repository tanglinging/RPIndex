#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: tanglingling
@contact: tanglingling@maimiaotech.com
@date: 2018-05-02 17:13
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""
import time
from collections import namedtuple
from datetime import datetime 

SECTOR_SIZE = 512

def get_disk_io_info_fields():
    return ["read_counts","write_counts","rbytes","wbytes","rtime","wtime"]

def get_disk_io_info(ssh, dunit = "b" , tunit = "s" ):
    '''
    /proc/partitions 各列含义
    major:主设备号。3代表 hda
    minor：次设备号。 0 代表第7分区
    #block ： 设备总块数 （1024 bytes/block ）
    name : 设备名

    /proc/diskstats 各列含义
    第一列：设备号
    第二列：次设备号
    第三列：设备名
    第四列：成功读总次数
    第五列：合并读次数（为了效率合并多次读为一次）
    第六列：读扇区次数
    第七列：所有读所花费的毫秒数ms
    第八列：成功写次数
    第九列：合并写次数
    第十列：写扇区次数
    第十一列：所有写所花费的毫秒数ms
    第十二列：I/O当前进度，这个域应该是0
    第十三列：输入输出所花费的时间ms
    第十四列：输入输出所花费的加权时间ms
    '''
    #调用远程机器，获取磁盘分区信息
    partitions = []
    stdin ,stdout, stderr = ssh.exec_command("cat /proc/partitions")
    try:
        lines = stdout.read().split()
    except Exception,e:
        logger.error("获取磁盘分区失败！")
        return None

    #str格式转换为list格式，方便处理
    lenLine = len(lines)/4
    list_lines = []
    for i in range(1,lenLine):
        list_lines.append(lines[4*i:4*(i+1)])

    #磁盘分区name获取
    for lin in  reversed(list_lines):
        name = lin[-1]
        if name[-1].isdigit():
            partitions.append(name)
        else:
            if not partitions or not partitions[-1].startswith(name):
                partitions.append(name)
    #获取磁盘数据信息。根据分区创建dict返回
    retdict = {}
    stdin ,stdout ,stderr = ssh.exec_command("cat /proc/diskstats")
    try:
        lines = stdout.read()
    except Exception,e:
        logger.error("获取磁盘数据失败！")
        return None
    list_lines = []
    for line in lines.split("\n")[:-1]:
        list_lines.append(line.split())
    #处理单位
    disk_div = 1
    time_div = 1
    dunit = dunit.lower()
    tunit = tunit.lower()
    if dunit == 'k':
        disk_div = 1024
    elif dunit == 'm':
        disk_div = 1024 * 1024
    elif dunit == 'g':
        disk_div = 1024 * 1024 * 1024
    elif dunit == 't':
        disk_div = 1024 * 1024 * 1024 * 1024
    if tunit == 's':
        time_div = 1000
    #磁盘数据处理
    for lin in list_lines:
        _,_,name,read_counts,_,rsector,rtime,write_counts,_,wsector,wtime = lin[:11]
        if name in partitions:
            rbytes = int(rsector)*SECTOR_SIZE/disk_div #读扇区数
            wbytes = int(wsector)*SECTOR_SIZE/disk_div #写扇区数
            read_counts  = int(read_counts) # 读次数
            write_counts  = int(write_counts) # 写次数
            rtime = int(rtime)/time_div # 读花费时间
            wtime = int(wtime)/time_div # 写花费时间
            retdict[name] = (read_counts,write_counts,rbytes,wbytes,rtime,wtime)
    return retdict

def get_disk_io_info_by_namedtuple(ssh,dunit='b',tunit='ms'):
    '''
    dunit: 磁盘数据单位。可传入 b，K，M，G ； 默认是b 即bytes
    tunit：时间单位。可传入ms，s ；默认是ms 即 millisecond
    '''
    #返回磁盘数据信息，以namedtuple对象返回
    _fields = get_disk_io_info_fields()
    diskinfos = namedtuple("diskInfos",_fields) 
    retdict = get_disk_io_info(ssh,dunit,tunit)
    return diskinfos(*[sum(x) for x in zip(* retdict.values())])

def get_disk_io_info_by_interval(ssh,interval = 1 ,dunit = 'b' , tunit = 'ms'):
    def calculate(disk1,disk2):
        _fields = get_disk_io_info_fields()
        res = {}
        for field in _fields:
            if hasattr(disk1,field) and hasattr(disk2,field):
                res[field] = getattr(disk2,field) - getattr(disk1,field)
        dRes = namedtuple("diskInfos",res.keys())
        return dRes(*res.values())
    disk1 = get_disk_io_info_by_namedtuple(ssh,dunit,tunit)
    time.sleep(interval)
    disk2 = get_disk_io_info_by_namedtuple(ssh,dunit,tunit)
    return calculate(disk1,disk2),datetime.now().strftime("%Y%m%d%H%M%S")
