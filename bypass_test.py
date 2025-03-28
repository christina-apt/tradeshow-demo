import os
import re
import time
import platform
import tkinter as tk
from tkinter import Button, scrolledtext, Menu, PhotoImage, Label, Frame, ttk
from PIL import Image, ImageTk
import subprocess
import threading
from datetime import datetime
from tabulate import tabulate
import json

class BypassTest(Frame):

    def write_line(self, line, *args, console=True, clear=False):
        with open("network_test.log", "a") as log_file:
            log_file.write(line)
            if clear:
                self.output_text.delete(1.0, tk.END)
            if console:
                self.output_text.insert(tk.END, line, args)
                self.output_text.see(tk.END)

    def exec_bash(self, command, log=True):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if log:
            for line in process.stdout:
                self.write_line(line, console=True)
        process.stdout.close()
        process.wait()
        return process.returncode

    def set_network_space(self,interface="enp1s0",ip="192.168.1.4", namespace="ns_eth0"):

        # create network namespace
        cmd = ["ip", "netns", "add",namespace]
        self.exec_bash(cmd)

        # add interface to network namespace
        cmd = ["ip", "link", "set", interface, "netns", namespace]
        self.exec_bash(cmd)

        # set ip address
        cmd = ["ip", "netns", "exec", namespace,"ip", "addr", "add", "dev", interface, ip + "/24"]
        #cmd = ["ip", "addr", "add", "dev", interface, ip + "/24"]
        self.exec_bash(cmd)

        # # print information
        # cmd = "ip netns exec " + namespace + " ip a"
        # cmdInformation = subprocess.check_output(cmd, shell=True).decode()
        
    def set_network_up(self,interface="enp1s0", namespace="ns_eth0"):
        # up interface
        cmd = ["ip", "netns", "exec", namespace, "ip", "link", "set", interface, "up"]
        #cmd = ["ip", "link", "set", interface, "up"]
        self.exec_bash(cmd)

    def delete_network_space(self,ip, interface):
        cmd = ["ip", "addr", "del", ip, interface]
        self.exec_bash(cmd)

    def run_iperf_client(self,namespace="ns1",ip="192.168.1.4",time="5",port="5201"):
        cmd="ip netns exec " + namespace + " iperf3 -c " + ip + " -t " + time + " -p " + port + " --connect-timeout 3000"
        #cmd="iperf3 -c " + server + " -B " + ip + " -t "+ time + " -p " + port 
        cmdInformation = subprocess.check_output(cmd, shell=True).decode()
        return cmdInformation

    def run_iperf_server(self, namespace="ns1"):#ip="192.168.1.4"):
        cmd="ip netns exec " + namespace + " iperf3 -s > iperf3.log 2>&1 & "
        #cmd="iperf3 -s -B "+ ip + " > iperf3.log 2>&1 &"
        cmdInformation = subprocess.check_output(cmd, shell=True).decode()
        return cmdInformation

    def pkill_iperf(self,namespace="ns0"):
        cmd = "sudo ip netns exec " + namespace + " pkill iperf3"
        #cmd = ["pkill", "iperf3"]
        cmdInformation = subprocess.check_output(cmd, shell=True).decode()
        return cmdInformation

    def extract_gbits_per_sec(self,input_string):
        match = re.search(r'(\d+\.\d+) Gbits/sec', input_string)
        if match:
            return float(match.group(1))
        return 0.0

    def prepare_network(self):
        ethernet = self.globalVariable["ethernet"]
        adapters = []
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_line(f"\nPreparing adapters\nTime: {start_time}\n")
        for pair in ethernet:
            for item in ethernet[pair]:
                try:
                    self.set_network_space(item["interface"],item["ip"],item["name"])
                    self.set_network_up(item["interface"],item["name"])
                    time.sleep(1)
                except Exception as e:
                    self.write_line(str(e))
                    raise e

    def run_iperf(self):
        self.update_progress("test_3.png")
        self.update_text("Network Bandwidth Test: ","bold",clear=True)
        self.update_text("Measures maximum TCP/UDP bandwidth to identify bottlenecks in heavy traffic scenarios, ensuring the network infrastructure can handle peak throughput in data-intensive environments.")
        self.write_line("",clear=True)
        testconditions = self.globalVariable["testCondition"]
        self.update_result("Bandwidth Test\n", clear=True)
        ethernet = self.globalVariable["ethernet"] 
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_line(f"Test: Bandwidth\nTime: {start_time}\n", True)
        self.toggle_menu(False)
        def target():
            #self.prepare_network()
            speed = []
            expected = []
            result = True
            for idx, pair in enumerate(ethernet):
                try:    #self.run_iperf_server(ethernet[pair][0]["ip"])
                    output = self.run_iperf_server(ethernet[pair][0]["name"])
                    self.write_line(output)
                    time.sleep(3)
                    output = self.run_iperf_client(ethernet[pair][1]["name"], ethernet[pair][0]["ip"])
                    self.write_line(output)
                    time.sleep(2)
                except Exception as e:
                    self.write_line(str(e) + "\n")
                    self.update_result("ERROR: test did not complete successfully - " + str(e), "red", clear=True)
                    self.toggle_menu(True)
                    self.update_progress("check 3.png")
                    return
                finally:
                    try:
                        self.pkill_iperf(ethernet[pair][0]["name"])
                    except Exception as e:
                        self.write_line(str(e) + "\n")
                try:
                    with open('iperf3.log') as f:
                        lines = f.readlines()
                        for line in lines:
                            if ('sender' in line) or ('receiver' in line):
                                gbits_per_sec = self.extract_gbits_per_sec(line)
                                speed.append(gbits_per_sec)
                                self.write_line("Speed : %.2f Gbits/sec \n" % (gbits_per_sec))
                except FileNotFoundError:
                    self.write_line("iperf3.log not found")
                    self.update_result("ERROR: Log file deleted before test completed.", "red", clear=False)
                    result = False
                    break
                condition = testconditions[idx]['bandwidth'] * testconditions[idx]['percent']
                expected.append(condition)
                if gbits_per_sec < condition:
                    result = False
            if result:
                self.update_result("PASS", "green", clear=True)
                self.update_result(": Network bandwith " + str(speed) + " Gbits/sec > " + str(expected) + " Gbits/sec", clear=False)
            else:
                self.update_result("FAIL", "red", clear=True)
                self.update_result(" : " + str(speed) + " Gbits/s < " + str(expected) + " Gbits/s",  clear=False)
            self.update_progress("check 3.png")
            #for pair in ethernet:
            #    self.delete_network_space(ethernet[pair][0]["ip"], ethernet[pair][0]["interface"])
            #    self.delete_network_space(ethernet[pair][1]["ip"], ethernet[pair][1]["interface"])
            self.toggle_menu(True)

        thread = threading.Thread(target=target)
        thread.start()
        self.toggle_menu(True)



    def run_read_fru(self):
        self.update_progress("test_4.png")
        self.write_line("",clear=True)
        self.update_result("Read FRU\n", clear=True)
        self.update_text("OCP 3.0 FRU Information Display:", "bold", clear=True) 
        self.update_text(" Provides detailed hardware data for transparency and traceability, enabling quick identification and replacement of faulty components to minimize downtime.", clear=False) 
        #sudo ipmitool fru print 0x01
        try:
            cmd = ["ipmitool", "fru", "print", self.slot]
            if self.slot == "0x02":
                result = self.exec_bash(cmd, log=False)
            else:
                result = self.exec_bash(cmd)
            if result != 0 and self.slot != "0x02":
                self.update_result("FAIL", "red", clear=True)
                self.update_result(" : FRU Format incorrect, check error code.", clear=False)
                self.update_progress("check 4.png")
                return
        except Exception as e:
            self.write_line(str(e))
            self.update_result("Error getting FRU information - " + str(e), "red", clear=True)
        
        with open("fru.txt") as fru, open(self.fru) as vals:  
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.write_line(f"Test: Read FRU\nTime: {start_time}\n", False) 
            fields = []     
            for key, value in zip(fru,vals):
                key = key.rstrip()
                value = value.rstrip()
                entry=[key, value]
                fields.append(entry)
            self.write_line(tabulate(fields, headers=['Field', 'Value'], tablefmt="simple"))
            
        self.update_progress("check 4.png")

    def run_edit_fru(self):
        self.write_line("",clear=True)
        self.update_result("Edit FRU\n", clear=True)
        self.button.pack(pady=5)
        self.button.config(text="Save")
        with open("fru.txt") as fru, open("values.txt") as vals:  
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.write_line(f"Test: MAC Addresses\nTime: {start_time}\n", False) 
            fields = []     
            for key, value in zip(fru,vals):
                key = key.rstrip()
                value = value.rstrip()
                entry=[key, value]
                fields.append(entry)
                self.write_line(key + ': ' + value + "\n",clear=False)
        return fields

    def run_save_fru(self):
        self.button.config(text="")
        self.button.pack_forget()

    def run_mac(self):
        self.write_line("",clear=True)
        self.update_result("MAC Addresses\n", clear=True)
        interfaces = []
        net_path = '/sys/class/net/'  
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_line(f"Test: MAC Addresses\nTime: {start_time}\n", False)    
        try:  
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
                        self.write_line(interface + ': ' + mac_address + "\n", console=False, clear=False)
            self.write_line(tabulate(interfaces, headers=['Interface', 'MAC'], tablefmt="simple"))
            return interfaces
        except Exception as e:
            self.write_line(str(e))
    

    def run_ping(self):
        self.update_progress("test_2.png")
        self.update_text("Network Connectivity Test: ","bold",clear=True)
        self.update_text("Verifies connectivity, focusing on network responsiveness and stability. This test quickly identifies latency issues or packet loss, ensuring the system is ready for performance-sensitive deployments.")
        self.write_line("",clear=True)
        self.update_result("Network Connectivity Test\n", clear=True)
        self.toggle_menu(False)
        #Windows: ping -S -n Ubuntu: ping -I -c
        def target():
            try:
                ethernet = self.globalVariable["ethernet"] 
                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.write_line(f"Test: Connectivity\nTime: {start_time}\n", True)
                result = 0
                #self.prepare_network()
                for pair in ethernet:
                    result += self.exec_bash(['ip','netns','exec', ethernet[pair][0]["name"],'ping','-I',ethernet[pair][0]["ip"], '-c', '3',ethernet[pair][1]["ip"] ])
                time.sleep(1)
                if result == 0:
                    self.update_result("PASS", "green", clear=True)
                    self.update_result(" : All packets transmitted and received successfully.", clear=False)
                else:
                    self.update_result("FAIL", "red", clear=True)
                    self.update_result(" : Packets lost in transmission. Please check network connections and test again", clear=False)
            except Exception as e:
                self.write_line(str(e))
                self.update_result("ERROR: test did not complete successfully - " + str(e), "red", clear=True)
            finally:
                self.update_progress("check 2.png")
                self.toggle_menu(True)
                #for pair in ethernet:
                #    self.delete_network_space(ethernet[pair][0]["ip"], ethernet[pair][0]["interface"])
                #    self.delete_network_space(ethernet[pair][1]["ip"], ethernet[pair][1]["interface"])
            #run_command(['ping', '-S','192.168.96.122', '-n', '4', 'google.com'], "Ping Test")
        thread = threading.Thread(target=target)
        thread.start()
        
    def update_result(self,text,*args, clear=False):
        if clear:
            self.text_left_box.delete(1.0, tk.END)
        self.text_left_box.insert(tk.END, text, args)

    def lspci_linkstatus(self,pciebus="15:00.0"):
        cmd = "lspci -vv -s " + pciebus + " | grep LnkSta:"
        cmdInformation = subprocess.check_output(cmd, shell=True).decode()
        return cmdInformation

    def lspci_all(self):
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
            self.write_line(f"Error executing lspci: {e}")
            return {}

    def lspci_name(self,pciebus="15:00.0"):
        try:
            result = subprocess.check_output(f"lspci -s {pciebus}", shell=True).decode().strip()
            name = ' '.join(result.split()[1:]) 
            return name
        except subprocess.CalledProcessError as e:
            self.write_line(f"Error getting PCIe name for {pciebus}: {e}")
            return "Unknown"

    def extract_values(self, input_string):
        match = re.search(r'LnkSta:\s*Speed\s*(\d+)GT/s\s*\(ok\),\s*Width\s*x(\d+)\s*\(ok\)', input_string)
        if match:
            speed = int(match.group(1))
            width = int(match.group(2))
            return str(speed), str(width)
        return None, None
    
    def blink_adapter(self, namespace, adapter, length=3):
        cmd = ["ip", "netns","exec", namespace, "ethtool", "-p", adapter, str(length)]
        result = self.exec_bash(cmd, False)
        if result != 0:
            time.sleep(2)

    def run_pcie(self):
        self.update_progress("test_1.png")
        self.update_result("PCIe Test", clear=True)
        self.update_text("PCIe Lane Margining Test: ","bold",clear=True)
        self.update_text("Assesses signal integrity for high-speed PCIe connections, detecting potential issues early to ensure robust and reliable performance under stress.")
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_line(f"Test: PCIe\nTime: {start_time}\n", console=True, clear=True)
        def target():
            test=True
            try:
                speeds = []
                widths = []
                exp_speed = []
                exp_width = []
                ethernet=self.globalVariable['ethernet']
                for pair in ethernet:
                    self.write_line("Testing PCIe for interface: " + ethernet[pair][0]["interface"] +"\n")
                    self.blink_adapter(ethernet[pair][0]["name"], ethernet[pair][0]["interface"], 5)
                    self.write_line("Testing PCIe for interface: " + ethernet[pair][1]["interface"]+ "\n")
                    self.blink_adapter(ethernet[pair][1]["name"], ethernet[pair][1]["interface"], 5)
                for addr ,condition in zip(self.globalVariable['pcie']['address'] , self.globalVariable['pcie']['testCondition']):
                    result = self.lspci_linkstatus(addr)
                    speed, width = self.extract_values(result)
                    name = self.lspci_name(addr)
                    self.write_line(f"PCIe name: {name}\n")
                    self.write_line(f"PCIe address: {addr}\n")
                    self.write_line(f"Speed: {speed} GT/s, Width: x{width}\n")
                    speeds.append(speed)
                    widths.append(width)
                    self.write_line(f"PCIe condition: {condition}\n")
                    exp_speed.append(condition['speed']) 
                    exp_width.append(condition['width'])
                    if speed == condition['speed'] and width == condition['width']:
                        continue
                    else:
                        test=False
                if test:
                    self.update_result("PASS", "green", clear=True)
                    self.update_result(" : Actual equals expected: "+ str(speeds) + "GT/s x" + str(widths) , clear=False)
                else:
                    self.update_result("FAIL", "red", clear=True) 
                    self.update_result(" : Actual: " + str(speeds) + "GT/s x" + str(widths), " Expected: "  + str(exp_speed) + "GT/s x" + str(exp_width), clear=False) 
            except Exception as e:
                self.write_line(f"Error getting PCIe info: {str(e)}\n")
                self.update_result(f"Error getting PCIe info: {str(e)}", "red", clear=True)
            self.update_progress("check 1.png")
        thread = threading.Thread(target=target)
        thread.start()
        
    def update_text(self, text, *args, clear=False):
        if clear:
            self.text_box.delete(1.0, tk.END)
        self.text_box.insert("end",text, args)
    
    def update_progress(self, image):
        self.progress_bar = PhotoImage(file=image)
        self.progress_bar_label.config(image=self.progress_bar)
    
    def quit(self):
        self.root.destroy()
    
    def delete_menu(self):
        self.menu_bar.delete(0,tk.END)
    
    def run_all(self):
        if not self.tests:
            return
        next=self.tests.pop(0)
        self.root.after(0, next[1])
        self.root.after(next[0], self.run_all)


    def toggle_menu(self,status):
        if self.menu_bar.index(tk.END) == 0:
            return
        if status:
            value=tk.ACTIVE
        else:
            value=tk.DISABLED
        self.menu_bar.entryconfig("Start Tests", state=value)
        self.menu_bar.entryconfig("PCIe Test", state=value)
        self.menu_bar.entryconfig("Connectivity Test", state=value)
        self.menu_bar.entryconfig("Bandwidth Test", state=value)
        self.menu_bar.entryconfig("Read FRU", state=value)

    
    def __init__(self, master, background="background1.jpg"):
        self.slot = "0x00"
        with open('./global.json') as f:
            self.globalVariable = json.load(f)

        match background:
            case "page 2.png":
                self.globalVariable = self.globalVariable['nic1']
                self.slot = "0x00"
                self.fru = "values1.txt"
            case "page 3.png":
                self.globalVariable = self.globalVariable['nic2']
                self.slot = "0x01"
                self.fru = "values2.txt"
            case "page 4.png":
                self.globalVariable = self.globalVariable['nic3']  
                self.slot = "0x02"
                self.fru = "values3.txt"     

        self.is_windows = platform.system() == 'Windows'
        # Create the main window
        self.root = master
        #if self.is_windows:
        #    root.state('zoomed')
        #else:
        #    root.attributes('-zoomed', True)
        width=1600 #root.winfo_screenwidth() 
        height=900 #root.winfo_screenheight()
        #setting tkinter window size
        self.root.geometry("%dx%d" % (width, height))
        self.root.title("APT OCP NIC 3.0 Network Test")

        # Load the icon image
        icon = PhotoImage(file="portwell_logo.png")
        self.root.iconphoto(False, icon)


        # Load the background image
        bg_image = Image.open(background)
        bg_image.resize((width,height))
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a canvas to place the background image
        canvas = tk.Canvas(self.root, width=width, height=height)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        self.progress_bar = PhotoImage(file="test_0.png")

        self.progress_bar_label = tk.Label(canvas, image=self.progress_bar, bd=0)
        self.progress_bar_label.pack(side=tk.BOTTOM, pady=(0,15))


        self.frame1 = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        self.frame1.pack(side=tk.LEFT,pady=(350,15), padx=(50,0))
        self.text_box = tk.Text(self.frame1, borderwidth=0, highlightthickness=0, wrap="word", width=27, height=18, font=("Calibri", 25))
        self.text_box.pack(fill="both", padx=10, pady=10)
        self.text_box.tag_configure("bold", font=("Calibri", 25, "bold"))
        
        self.left_frame = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        self.left_frame.pack(side=tk.TOP,pady=(50,0), padx=(40,40))
        self.test_output_label = Label(self.left_frame, text="Test Status", font=("Calibri", 14, "bold"), bg="white")
        self.test_output_label.pack(anchor="nw", pady=(5,0), padx=(10,5))
        self.text_left_box = tk.Text(self.left_frame, borderwidth=0, highlightthickness=0, wrap="word",
                        width=120, height=1, font=("Calibri", 14))
        self.text_left_box.pack(fill="both", expand=True, padx=5, pady=10)
        self.text_left_box.tag_configure("bold", font=("Calibri", 14, "bold"))
        self.text_left_box.tag_configure("red", foreground="red")
        self.text_left_box.tag_configure("green", foreground="green")

        # Create a button to execute command
        self.button = Button(canvas, text="", command=self.run_save_fru, font=("Calibri", 10))

        # Create a menu bar
        self.menu_bar = Menu(canvas)
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_command(label="Start Tests", command=self.run_all)
        self.menu_bar.add_command(label="PCIe Test", command=self.run_pcie)
        self.menu_bar.add_command(label="Connectivity Test", command=self.run_ping)
        self.menu_bar.add_command(label="Bandwidth Test", command=self.run_iperf)
        self.menu_bar.add_command(label="Read FRU", command=self.run_read_fru)

        self.right_frame = ttk.Frame(canvas, style="RoundedFrame")
        self.right_frame.pack(side=tk.RIGHT,pady=(30,15), padx=(0,40))

        # Create a scrolled text box to display the output
        self.output_label = Label(self.right_frame, text="Test Console", font=("Calibri", 14, "bold"), bg="white")
        self.output_label.pack(anchor="nw", pady=(10,0), padx=(15,5))
        self.output_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=103, height=60, bg="black", fg="white")
        self.output_text.pack(expand=False, padx=(5,10), pady=(5,7))

        
        self.tests = [(0, self.delete_menu),(30000,self.run_pcie), (25000,self.run_ping), (50000,self.run_iperf), (10000,self.run_read_fru), (0,self.quit)]

        # Run the Tkinter event loop
        self.root.mainloop()




            


