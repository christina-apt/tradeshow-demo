import os
import re
import time
import platform
import subprocess
import json
from datetime import datetime


globalVariable = {}
with open('./global.json') as f:
    globalVariable = json.load(f)

def exec_bash(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line)
    process.stdout.close()
    process.wait()
    return process.returncode

def set_network_space(interface="enp1s0",ip="192.168.1.4", namespace="ns_eth0"):

    # create network namespace
    cmd = ["ip", "netns", "add",namespace]
    exec_bash(cmd)

    # add interface to network namespace
    cmd = ["ip", "link", "set", interface, "netns", namespace]
    exec_bash(cmd)

    # set ip address
    cmd = ["ip", "netns", "exec", namespace,"ip", "addr", "add", "dev", interface, ip + "/24"]
    #cmd = ["ip", "addr", "add", "dev", interface, ip + "/24"]
    exec_bash(cmd)

    # # print information
    # cmd = "ip netns exec " + namespace + " ip a"
    # cmdInformation = subprocess.check_output(cmd, shell=True).decode()
    
def set_network_up(interface="enp1s0", namespace="ns_eth0"):
    # up interface
    cmd = ["ip", "netns", "exec", namespace, "ip", "link", "set", interface, "up"]
    #cmd = ["ip", "link", "set", interface, "up"]
    exec_bash(cmd)

def delete_network_space(ip, interface):
    cmd = ["ip", "addr", "del", ip, interface]
    exec_bash(cmd)

def prepare_network(nic):
    ethernet = globalVariable[nic]["ethernet"]
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nPreparing adapters\nTime: {start_time}\n")
    for pair in ethernet:
        for item in ethernet[pair]:
            try:
                set_network_space(item["interface"],item["ip"],item["name"])
                set_network_up(item["interface"],item["name"])
                time.sleep(1)
            except Exception as e:
                print(str(e))
                raise e


for nic in globalVariable.keys():
    prepare_network(nic)
