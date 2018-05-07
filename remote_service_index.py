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
####
resource = "service_index"
import logging
logger = logging.getLogger(resource)
handler = logging.FileHandler("/alidata1/logs/%s/%s.log" % (resource,resource))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s:%(lineno)-15d %(message)s') 
handler.setFormatter(formatter)
logger.addHandler(handler)
####
#利用公钥登录压测机，提前配置公钥
def remote_login(remote_host,username):
    pkey = paramiko.RSAKey.from_private_key_file("/home/tangll/.ssh/id_rsa")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname =remote_host,
                port = 22,
                username = username,
                pkey = pkey)
    return ssh

cpu_first_write = True
mem_first_write = True
disk_first_write = True
net_first_write = True

def get_remote_cpu_info(ssh,f):
    print "before get_remote_cpu_info..."
    global cpu_first_write
    cpu_percs,t_cpu = get_cpu_percent(ssh,1)
    if cpu_percs:
        if cpu_first_write:
            cpu_first_write = False
            cpu_fields = get_cputimes_fields(len(cpu_percs)-1)
            f.write("time\t")
            for field in cpu_fields:
                f.write(field+"%\t")
            f.write("\n")
        f.write(t_cpu+"\t")
        for perc in cpu_percs:
            f.write(str(perc) + "\t")
        f.write("\n")
    print "after get_remote_cpu_info ..."

def get_remote_mem_info(ssh,f):
    print "before get_remote_mem_info ..."
    global mem_first_write
    mem_percs,swap_percs,t_memory = get_memory_percent(ssh)
    if mem_percs is not None and swap_percs is not None:
        if mem_first_write:
            mem_first_write = False
            memory_fields = get_memory_fields()
            f.write("time\t")
            for field in memory_fields:
                f.write(field+"%\t")
            f.write("\n")
        f.write(t_memory+"\t"+str(mem_percs)+"\t"+str(swap_percs)+"\n")
    print "after get_remote_mem_info ..."

def get_remote_disk_info(ssh,f):
    print "before get_remote_disk_info ..."
    global disk_first_write
    diskinfos,t_disk = get_disk_io_info_by_interval(ssh,1 ,'b','ms')
    disk_fields = get_disk_io_info_fields()
    if disk_first_write:
        disk_first_write = False
        f.write("time\t")
        for field in disk_fields:
            f.write(field + "\t")
        f.write("\n")
    f.write(t_disk+"\t")
    for field in disk_fields:
        if hasattr(diskinfos,field):
            f.write(str(getattr(diskinfos,field))+"\t")
    f.write("\n")
    print "after get_remote_disk_info .."

def get_remote_network_info(ssh,f):
    print "before get_remote_network_info .."
    global net_first_write
    KBps,t_network = get_network_bps(ssh)
    if net_first_write:
        net_first_write = False
        f.write("time\tKBps\n")
    f.write(t_network+"\t"+ str(KBps)+"\n")
    print "after get_remote_network_info  ..."

def remote_load_index(b_ssh_run,interval = 1 , remote_host="mm_dev_in",username="tangll"):
    try:
        ssh = remote_login(remote_host,username)
    except Exception ,e :
        logger.error("登录%s出错！%s" % (remote_host,e))
    else:
        logger.info("登录%s成功！" % (remote_host,))
        f_cpu = open("/home/tangll/cpu_percs.txt","w")
        f_memory = open("/home/tangll/mem_percs.txt","w")
        f_disk = open("/home/tangll/disk_info.txt","w")
        f_network = open("/home/tangll/net_percs.txt","w")
        while b_ssh_run.value:
            # this is test:
            #get_remote_disk_info(ssh,f_disk)
            #b_ssh_run.value=0
            gevent.joinall([gevent.spawn(get_remote_cpu_info,ssh,f_cpu),
                            gevent.spawn(get_remote_mem_info,ssh,f_memory),
                            gevent.spawn(get_remote_disk_info,ssh,f_disk),
                            gevent.spawn(get_remote_network_info,ssh,f_network)])
        f_cpu.close()
        f_memory.close()
        f_disk.close()
        f_network.close()
    finally:
        logger.info("退出%s成功！" % (remote_host,))
        ssh.close()

def main_thread_func():
    for i in range(3):
        print "main:",i
        time.sleep(1)
if __name__ == "__main__":
    # this is test:
    #from collections import namedtuple
    #b_ssh_run = namedtuple("Run","value")
    #b_ssh_run = b_ssh_run(1)
    #remote_load_index(b_ssh_run)
    t_start = time.time()
    b_ssh_run = multiprocessing.Value("b",1)
    child = multiprocessing.Process(target=remote_load_index,args=(b_ssh_run,))
    child.start()

    main_thread_func()
    b_ssh_run.value = 0
    child.join()
    t_end = time.time()
    print "Cost:{0}".format(t_end-t_start)
