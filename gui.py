import os
import re
import time
import tkinter as tk
from tkinter import Button, scrolledtext, Menu, PhotoImage, Label
import subprocess
import threading
from datetime import datetime
from tabulate import tabulate
import json

with open('./global.json') as f:
    globalVariable = json.load(f)

def set_network_space(interface="enp1s0",ip="192.168.1.4", namespace="ns_eth0"):

    # create network namespace
    #cmd = ["ip", "netns", "add",namespace]
    #exec_bash(cmd)

    # add interface to network namespace
    #cmd = ["ip", "link", "set", interface, "netns", namespace]
    #exec_bash(cmd)

    # set ip address
    #cmd = ["ip", "netns", "exec", namespace,"ip", "addr", "add", "dev", interface, ip + "/24"]
    cmd = ["ip", "addr", "add", "dev", interface, ip + "/24"]
    exec_bash(cmd)

    # # print information
    # cmd = "ip netns exec " + namespace + " ip a"
    # cmdInformation = subprocess.check_output(cmd, shell=True).decode()
    
def set_network_up(interface="enp1s0", namespace="ns_eth0"):
    # up interface
    #cmd = ["ip", "netns", "exec", namespace, "ip", "link", "set", interface, "up"]
    cmd = ["ip", "link", "set", interface, "up"]
    exec_bash(cmd)


def delete_network_space(ip, interface):
    cmd = ["ip", "addr", "del", ip, interface]
    exec_bash(cmd)

def run_iperf_client(server="192.168.1.1",ip="192.168.1.4",time="5",port="5201"):
    cmd="iperf3 -c " + server + " -B " + ip + " -t "+ time + " -p " + port 
    cmdInformation = subprocess.check_output(cmd, shell=True).decode()

def run_iperf_server(ip="192.168.1.4"):
    cmd="iperf3 -s -B "+ ip + " > iperf3.log 2>&1 &"
    cmdInformation = subprocess.check_output(cmd, shell=True).decode()

def pkill_iperf(namespace="ns_eth0"):
    cmd = ["pkill", "iperf3"]
    exec_bash(cmd)

def extract_gbits_per_sec(input_string):
    match = re.search(r'(\d+\.\d+) Gbits/sec', input_string)
    if match:
        return float(match.group(1))
    return 0.0

def prepare_network():
    ethernet = globalVariable["ethernet"]
    adapters = []
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_line(f"Preparing adapters\nTime: {start_time}\n")
    for pair in ethernet:
        for item in ethernet[pair]:
            try:
                set_network_space(item["interface"],item["ip"],item["name"])
                set_network_up(item["interface"],item["name"])
                time.sleep(3)
            except Exception as e:
                write_line(str(e))
                delete_network_space(item["ip"],item["interface"])

def run_iperf():
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="iPerf Test")
    toggle_menu(False)
    ethernet = globalVariable["ethernet"] 
    testconditions = globalVariable["testCondition"]
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_line(f"Test: Iperf\nTime: {start_time}\n", True)
    prepare_network()
    for idx, pair in enumerate(ethernet):
        run_iperf_server(ethernet[pair][0]["ip"])
        time.sleep(3)
        run_iperf_client(ethernet[pair][0]["ip"], ethernet[pair][1]["ip"])
        pkill_iperf(ethernet[pair][0]["name"])
        time.sleep(2)
        delete_network_space(ethernet[pair][0]["ip"],ethernet[pair][0]["interface"])
        delete_network_space(ethernet[pair][1]["ip"],ethernet[pair][1]["interface"])
        try:
            with open('iperf3.log') as f:
                lines = f.readlines()
                for line in lines:
                    if ('sender' in line) or ('receiver' in line):
                        gbits_per_sec = extract_gbits_per_sec(line)
                        write_line("Speed : %.2f Gbits/sec \n" % (gbits_per_sec))
        except FileNotFoundError:
            write_line("iperf3.log not found")
            update_result(1)
            return
        if gbits_per_sec < testconditions[idx]['bandwidth'] * testconditions[idx]['percent']:
            update_result(1)
            return
    update_result(0)


def run_read_fru():
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="Read FRU")
    with open("fru.txt") as fru, open("values.txt") as vals:  
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_line(f"Test: Read FRU\nTime: {start_time}\n", False) 
        fields = []     
        for key, value in zip(fru,vals):
            key = key.rstrip()
            value = value.rstrip()
            entry=[key, value]
            fields.append(entry)
        write_line(tabulate(fields, headers=['Field', 'Value'], tablefmt="pretty"))
    return fields

def run_edit_fru():
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="Edit FRU")
    button.pack(pady=5)
    button.config(text="Save")
    with open("fru.txt") as fru, open("values.txt") as vals:  
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_line(f"Test: MAC Addresses\nTime: {start_time}\n", False) 
        fields = []     
        for key, value in zip(fru,vals):
            key = key.rstrip()
            value = value.rstrip()
            entry=[key, value]
            fields.append(entry)
            write_line(key + ': ' + value + "\n", False)
            output_text.insert(tk.END, key + ': ' + value + "\n")
            output_text.see(tk.END)
    return fields

def run_save_fru():
    test_name_label.config(text="Edit FRU")
    button.config(text="")
    button.pack_forget()

def run_mac():
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="MAC Addresses")
    interfaces = []
    net_path = '/sys/class/net/'  
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_line(f"Test: MAC Addresses\nTime: {start_time}\n", False)      
    for interface in os.listdir(net_path):
        if interface == 'lo' or interface.startswith('docker') or interface.startswith('br-'):
            continue
        address_file = os.path.join(net_path, interface, 'address')
        if os.path.exists(address_file):
            entry=[interface]
            with open(address_file) as f:
                mac_address = f.read().strip()
                mac_address = mac_address.upper()
                entry.append(mac_address)
                interfaces.append(entry)
                write_line(interface + ': ' + mac_address + "\n", False)
    write_line(tabulate(interfaces, headers=['Interface', 'MAC'], tablefmt="simple"))
    return interfaces

def run_ping():
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="Ping Test")
    toggle_menu(False)
    #Windows: ping -S -n Ubuntu: ping -I -c
    prepare_network()
    ethernet = globalVariable["ethernet"] 
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_line(f"Test: Ping\nTime: {start_time}\n", True)
    root.update()
    result = 1
    for pair in ethernet:
       result = exec_bash(['ping','-I',ethernet[pair][0]["ip"], '-c', '3',ethernet[pair][1]["ip"] ])
       time.sleep(1)
       delete_network_space(ethernet[pair][0]["ip"],ethernet[pair][0]["interface"])
       delete_network_space(ethernet[pair][1]["ip"],ethernet[pair][1]["interface"])
    toggle_menu(True)
    update_result(result)
    #run_command(['ping', '-S','192.168.96.122', '-n', '4', 'google.com'], "Ping Test")

def update_result(result):
    if result == 0:
        result_label.config(text="PASS", fg="green")
        write_line("Result: PASS\n\n", False)
    else:
        result_label.config(text="FAIL", fg="red")
        write_line(f"Result: FAIL\n\n", False)
    toggle_menu(True)

def lspci_linkstatus(pciebus="15:00.0"):
    cmd = "lspci -vv -s " + pciebus + " | grep LnkSta:"
    cmdInformation = subprocess.check_output(cmd, shell=True).decode()
    return cmdInformation

def lspci_all():
    cmd = "lspci"
    cmdInformation = subprocess.check_output(cmd, shell=True).decode()
    try:
        devices = {}
        for line in cmdInformation.splitlines():
            parts = line.split(' ', 2)
            addr = parts[0]
            name = parts[2] if len(parts) > 2 else 'Unknown'
            devices[addr] = name
        return devices
    except subprocess.CalledProcessError as e:
        write_line(f"Error executing lspci: {e}")
        return {}

def lspci_name(pciebus="15:00.0"):
    try:
        result = subprocess.check_output(f"lspci -s {pciebus}", shell=True).decode().strip()
        name = ' '.join(result.split()[1:]) 
        return name
    except subprocess.CalledProcessError as e:
        write_line(f"Error getting PCIe name for {pciebus}: {e}")
        return "Unknown"

def extract_values(input_string):
    match = re.search(r'LnkSta:\s*Speed\s*(\d+)GT/s\s*\(ok\),\s*Width\s*x(\d+)\s*\(ok\)', input_string)
    if match:
        speed = int(match.group(1))
        width = int(match.group(2))
        return str(speed), str(width)
    return None, None

def run_pcie():
    test=0
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    test_name_label.config(text="PCIe Test")
    try:
        for addr ,condition in zip(globalVariable['pcie']['address'] , globalVariable['pcie']['testCondition']):
            result = lspci_linkstatus(addr)
            speed, width = extract_values(result)
            name = lspci_name(addr)
            write_line(f"PCIe name: {name}\n")
            write_line(f"PCIe address: {addr}\n")
            write_line(f"Speed: {speed} GT/s, Width: x{width}\n")
            write_line(f"PCIe condition: {condition}\n")
            if speed == condition['speed'] and width == condition['width']:
                continue
            else:
                test=1
        update_result(test)
    except (TypeError, KeyError) as e:
        write_line("Listing all PCIe devices:")
        for device in lspci_all():
            write_line(f"PCIe name: {lspci_name(device)}\n")
            write_line(f"PCIe address: {device}\n")
        update_result(1)
    except Exception as e:
        write_line(f"Error getting PCIe info: {str(e)}\n")
        update_result(1)
    
def write_line(line, console=True):
    with open("network_test.log", "a") as log_file:
        log_file.write(line)
        if console:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)

def exec_bash(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        write_line(line, True)
    process.stdout.close()
    process.wait()
    return process.returncode

def run_command(command):
    def target():
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_line(f"Test: {test_name}\nTime: {start_time}\n", False)
        update_result(exec_bash(command))
    output_text.delete(1.0, tk.END)
    result_label.config(text="")  # Clear previous result
    thread = threading.Thread(target=target)
    thread.start()

def toggle_menu(status):
    if status:
        value=tk.ACTIVE
    else:
        value=tk.DISABLED
    menu_bar.entryconfig("iPerf Test", state = value)
    menu_bar.entryconfig("Ping Test", state = value)
    menu_bar.entryconfig("MAC Addresses", state = value)
    menu_bar.entryconfig("Read FRU", state = value)
    menu_bar.entryconfig("PCIe Test", state = value)



# Create the main window
root = tk.Tk()
#root.state('zoomed')
root.attributes('-zoomed', True)
root.title("Network Test")

# Load the icon image
icon = PhotoImage(file="portwell_logo.png")
root.iconphoto(False, icon)

# Load the logo image
logo = PhotoImage(file="logo.png")

# Create a label to display the logo image
logo_label = Label(root, image=logo)
logo_label.pack(pady=10)

# Create a label to display the test name
test_name_label = Label(root, text="", font=("Arial", 30))
test_name_label.pack(pady=5)

# Create a label to display the test result
result_label = Label(root, text="", font=("Arial", 30))
result_label.pack(pady=5)

# Create a button to execute command
button = Button(root, text="", command=run_save_fru, font=("Arial", 10))

# Create a menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)
menu_bar.add_command(label="iPerf Test", command=run_iperf)
menu_bar.add_command(label="PCIe Test", command=run_pcie)
menu_bar.add_command(label="Ping Test", command=run_ping)
menu_bar.add_command(label="MAC Addresses", command=run_mac)
menu_bar.add_command(label="Read FRU", command=run_read_fru)

# Create a scrolled text box to display the output
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=150, height=30)
output_text.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
