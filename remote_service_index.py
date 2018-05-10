#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: tanglingling
@contact: tanglingling@maimiaotech.com
@date: 2018-04-26 14:01
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""
import time
import base64
import paramiko
import gevent
from gevent import  monkey;monkey.patch_all()
import multiprocessing
from cpu import get_cpu_percent,get_cputimes_fields
from network import get_network_bps
from memory import get_memory_percent,get_memory_fields
from disk import get_disk_io_info_by_interval ,get_disk_io_info_fields
from settings import logger,DATA_PATH,privateKeyPath
from figure import DrawPic

class RSPIndexGet(object):

    cpu_first_write = True
    mem_first_write = True
    disk_first_write = True
    net_first_write = True

    def __init__(self,remote_host,username):
        self.remote_host = remote_host
        self.username = username
        self.ssh = None
    #利用公钥登录压测机，提前配置公钥
    def _remote_login(self):
        try:
            pkey = paramiko.RSAKey.from_private_key_file(privateKeyPath)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname =self.remote_host,
                        port = 22,
                        username = self.username,
                        pkey = pkey)
        except Exception ,e :
            logger.exception("登录%s出错！" % (self.remote_host,))
            return None
        else:
            logger.info("登录%s成功！" % (self.remote_host,))
            self.ssh = ssh

    def _remote_logout(self):
        try:
            self.ssh.close()
        except Exception,e:
            logger.exception("退出%s出错！" % (self.remote_host,))
        else:
            logger.info("退出%s成功！" % (self.remote_host,))

    def _get_remote_cpu_info(self,f):
        try:
            cpu_percs,t_cpu = get_cpu_percent(self.ssh,1)
            if cpu_percs:
                if self.cpu_first_write:
                    self.cpu_first_write = False
                    cpu_fields = get_cputimes_fields(len(cpu_percs))
                    f.write("time\t")
                    for field in cpu_fields:
                        f.write(field+"%\t")
                    f.write("\n")
                f.write(t_cpu+"\t")
                for perc in cpu_percs:
                    f.write(str(perc) + "\t")
                f.write("\n")
        except Exception,e:
            logger.exception("获取远程cpu信息失败！")

    def _get_remote_mem_info(self,f):
        try:
            mem_percs,swap_percs,t_memory = get_memory_percent(self.ssh)
            if mem_percs is not None and swap_percs is not None:
                if self.mem_first_write:
                    self.mem_first_write = False
                    memory_fields = get_memory_fields()
                    f.write("time\t")
                    for field in memory_fields:
                        f.write(field+"%\t")
                    f.write("\n")
                f.write(t_memory+"\t"+str(mem_percs)+"\t"+str(swap_percs)+"\t\n")
        except Exception,e:
            logger.exception("获取远程memory信息失败！")

    def _get_remote_disk_info(self,f):
        try:
            diskinfos,t_disk = get_disk_io_info_by_interval(self.ssh,1 ,'b','ms')
            disk_fields = get_disk_io_info_fields()
            if self.disk_first_write:
                self.disk_first_write = False
                f.write("time\t")
                for field in disk_fields:
                    f.write(field + "\t")
                f.write("\n")
            f.write(t_disk+"\t")
            for field in disk_fields:
                if hasattr(diskinfos,field):
                    f.write(str(getattr(diskinfos,field))+"\t")
            f.write("\n")
        except Exception,e:
            logger.exception("获取远程disk信息失败！")

    def _get_remote_network_info(self,f):
        try:
            KBps,t_network = get_network_bps(self.ssh)
            if self.net_first_write:
                self.net_first_write = False
                f.write("time\tKBps\n")
            f.write(t_network+"\t"+ str(KBps)+"\t")
            f.write("\n")
        except Exception,e:
            logger.exception("获取远程network信息失败！")

    def monitor_remote_performance_index(self,b_ssh_run,interval = 1):
        self._remote_login()
        if not self.ssh:
            return
        try:
            f_cpu = open(DATA_PATH['cpu'],"w")
            f_memory = open(DATA_PATH['memory'],"w")
            f_disk = open(DATA_PATH['disk'],"w")
            f_network = open(DATA_PATH['network'],"w")
            while b_ssh_run.value:
                # this is for test:
                #self.get_remote_disk_info(self.ssh,f_disk)
                #b_ssh_run.value=0
                gevent.joinall([gevent.spawn(self._get_remote_cpu_info,f_cpu),
                                gevent.spawn(self._get_remote_mem_info,f_memory),
                                gevent.spawn(self._get_remote_disk_info,f_disk),
                                gevent.spawn(self._get_remote_network_info,f_network)])
            f_cpu.close()
            f_memory.close()
            f_disk.close()
            f_network.close()
        except Exception,e:
            logger.exception("监控远程信息失败！")
            return
        self._remote_logout()

def main_thread_func():
    for i in range(20):
        print "main:",i
        time.sleep(1)

def drawResult():
    drawObj = DrawPic()
    drawObj.draw_figure_by_type("cpu")
    drawObj.draw_figure_by_type("memory")
    drawObj.draw_figure_by_type("network")

    dObj = DrawPic(3,1,sharex=True)
    dObj.draw_disk_figure()

if __name__ == "__main__":
    # this is for test:
    #from collections import namedtuple
    #b_ssh_run = namedtuple("Run","value")
    #b_ssh_run = b_ssh_run(1)
    #obj = RSPIndexGet("mm_dev_in","tangll")
    #obj.monitor_remote_performance_index(b_ssh_run)
    #import pdb; pdb.set_trace()  # XXX BREAKPOINT
    t_start = time.time()
    #启动子进程监控远程服务器指标
    b_ssh_run = multiprocessing.Value("b",1)
    obj = RSPIndexGet("mm_dev_in","tangll")
    child = multiprocessing.Process(target=obj.monitor_remote_performance_index,args=(b_ssh_run,))
    child.start()
    #主方法
    main_thread_func()
    #发送exit信号给子进程
    b_ssh_run.value = 0
    #等待子进程结束
    child.join()
    #绘制结果
    drawResult()

    t_end = time.time()
    print "Cost:{0}".format(t_end-t_start)
