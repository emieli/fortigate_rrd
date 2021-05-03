import paramiko
import time
import rrdtool
import os
import json
from subprocess import Popen, PIPE
from sys import platform

import argparse
argparser = argparse.ArgumentParser()
argparser.add_argument(
    "--ip",
    dest="ip",
    action="store",
    required=True,
    help="Enter Fortigate IP-address",
)
options = argparser.parse_args()

''' Abort script if it is already running '''
if platform == "linux":
    this_process = os.getpid()
    sp = Popen(f"ps a | grep -v {this_process}", shell=True, stdout=PIPE, universal_newlines=True)
    output, error = sp.communicate()
    if options.ip in output:
        exit(f"Another script is already polling {options.ip}, aborting.")

''' Get user credentials '''
import getpass
username = getpass.getuser()
password = getpass.getpass(f"Enter Fortigate password ({username}): ")

''' Create folders if missing '''
data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

''' Connect to Fortigate via SSH '''
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(options.ip, username=username, password=password)
except Exception as e:
    exit(f"SSH connection failed: {e}")

''' The loop that does all the work. Every 15 seconds it scrapes Wi-Fi data from Fortigate CLI and saves it to RRD files '''
while True:

    start = time.time()
    ''' Get client data '''
    stdin, stdout, stderr = ssh.exec_command("diagnose wireless-controller wlac -c sta")
    stdin.close()

    ''' Go through each connected client device, save relevant info to 'clients' '''
    clients = []
    for line in stdout.readlines():
        line = line.strip()
        if "-------------------------------STA" in line:
            clients.append({})
        elif "wtp" in line:
            clients[-1]['ap_ip'] = line.split("0-")[1].split(":")[0] # output is "0-10.70.8.2:5246", we only want "10.70.8.2"
        elif line ==  "rId              : 0":
            clients[-1]['radio'] = "2ghz"
        elif line == "rId              : 1":
            clients[-1]['radio'] = "5ghz"
    
    # print(json.dumps(clients, indent=4))

    ''' Get AP data '''
    stdin, stdout, stderr = ssh.exec_command("diagnose wireless-controller wlac -c wtp")
    stdin.close()

    ''' Sort output per AP '''
    output_per_ap = []
    for line in stdout.readlines():
        line = line.strip()
        if "-------------------------------WTP" in line:
            output_per_ap.append([])
        else:
            output_per_ap[-1].append(line)

    ''' Go through output for each AP, save relevant info to 'access_points' '''
    access_points = []
    for ap_output in output_per_ap:

        access_points.append({})
        for line in ap_output:
            if "name             : " in line:
                ''' Get AP hostname '''
                ap_name = line.split(": ")[1]
                access_points[-1]['name'] = ap_name

            elif "local IPv4 addr" in line:
                ''' Get AP mgmt IP '''
                access_points[-1]['ip'] = line.split(": ")[1]

            elif "connection state" in line:
                ''' Ignore AP if not online '''
                state = line.split(": ")[1]
                if state != "Connected":
                    del access_points[-1]
                    break
            
            elif line == "Radio 1            : AP":
                ''' Get current radio '''
                ap_radio = "2ghz"
                access_points[-1][ap_radio] = {
                    'clients': 0,
                    'ch_util': -1,
                }

            elif line == "Radio 2            : AP":
                ''' Get current radio '''
                ap_radio = "5ghz"
                access_points[-1][ap_radio] = {
                    'clients': 0,
                    'ch_util': -1,
                }

            elif "oper chutil data : " in line:
                ''' Get channel utilization data '''
                try:
                    access_points[-1][ap_radio]['ch_util'] = int(line.split(": ")[1].split(",")[0])
                except:
                    print(f"Unknown channel utilization value: {line}")

    # print(json.dumps(access_points, indent=4))

    ''' Count how many clients are connected to each AP radio '''
    for client in range(len(clients)):
        for ap in range(len(access_points)):
            if clients[client]['ap_ip'] == access_points[ap]['ip']:
                radio = clients[client]['radio']
                access_points[ap][radio]['clients'] += 1

    ''' Write gathered data to RRD file '''
    for ap in access_points:
        filename = f"{data_folder}/{ap['name']}.rrd"
        if not os.path.isfile(filename):
            rrdtool.create(filename, 
                "--start", "now",
                "--step", "15",
                "DS:ch-util-2ghz:GAUGE:60:0:100",
                "DS:ch-util-5ghz:GAUGE:60:0:100",
                "DS:clients-2ghz:GAUGE:60:0:200",
                "DS:clients-5ghz:GAUGE:60:0:200",
                "RRA:MAX:0.25:1m:1M",
                "RRA:AVERAGE:0.25:1m:1M",
                "RRA:AVERAGE:0.25:5m:1y")
        
        update = f"N:{ap['2ghz']['ch_util']}:{ap['5ghz']['ch_util']}:{ap['2ghz']['clients']}:{ap['5ghz']['clients']}"
        rrdtool.update(filename, update)
        print(update)

    end = time.time()
    # print(f"Time taken: {end - start}")

    print("")
    time.sleep(15 - end + start)
