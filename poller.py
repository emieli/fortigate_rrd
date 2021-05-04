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
    sp = Popen(f"ps x | grep -v {this_process} | grep -v screen | grep -v SCREEN", shell=True, stdout=PIPE, universal_newlines=True)
    output, error = sp.communicate()
    if options.ip in output:
        exit(f"Another script is already polling {options.ip}, aborting.")

''' Get user credentials '''
try:
    from credentials import username
    from credentials import password
except:
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
else:
    print("SSH session connected")

''' The loop that does all the work. Every 15 seconds it scrapes Wi-Fi data from Fortigate CLI and saves it to RRD files '''
while True:

    start = time.time()

    ''' Get AP data '''
    stdin, stdout, stderr = ssh.exec_command("get wireless-controller wtp-status")
    stdin.close()

    access_points = []
    for line in stdout.readlines():
        line = line.strip()

        if "WTP: " in line:
            access_points.append({
                "2ghz": {
                    'antenna-rssi': -1,
                    'bytes-rx': -1,
                    'bytes-tx': -1,
                    'ch-util': -1,
                    'interfering-ap': -1,
                    'tx-retries': -1,
                },
                "5ghz": {
                    'antenna-rssi': -1,
                    'bytes-rx': -1,
                    'bytes-tx': -1,
                    'ch-util': -1,
                    'interfering-ap': -1,
                    'tx-retries': -1,
                }
            })
        
        elif "name             :" in line:
            access_points[-1]['name'] = line.split(": ")[1]

        elif "local-ipv4-addr" in line:
            access_points[-1]['ip'] = line.split(": ")[1]

        elif "connection-state" in line:
            access_points[-1]['state'] = line.split(": ")[1]

        elif line == "Radio 1            : AP":
            radio = "2ghz"

        elif line == "Radio 2            : AP":
            radio = "5ghz"

        elif "client-count" in line:
            access_points[-1][radio]['clients'] = line.split(": ")[1]

        elif "oper-chutil-val" in line:
            ''' Old firmware APs report the value "N/A". If the value is not a valid int, ignore it. '''
            try:
                access_points[-1][radio]['ch-util'] = int(line.split(": ")[1].split(" (")[0])
            except:
                pass

        elif "bytes-rx" in line:
            access_points[-1][radio]['bytes-rx'] = line.split(": ")[1]

        elif "bytes-tx" in line:
            access_points[-1][radio]['bytes-tx'] = line.split(": ")[1]

        elif "tx-retries" in line:
            access_points[-1][radio]['tx-retries'] = line.split(": ")[1].replace("%", "")

        elif "interfering-ap" in line:
            access_points[-1][radio]['interfering-ap'] = line.split(": ")[1]

        elif "antenna RSSI" in line:
            access_points[-1][radio]['antenna-rssi'] = line.split(": ")[1].split(" ")[0]

    # exit(json.dumps(access_points, indent=4))

    ''' Write gathered data to RRD file '''
    for ap in access_points:

        if ap['state'] != "Connected":
            continue

        filename = f"{data_folder}/{ap['name']}.rrd"
        if not os.path.isfile(filename):
            rrdtool.create(filename, 
                "--start", "now",
                "--step", "15",
                "DS:ch-util-2ghz:GAUGE:60:0:100", "DS:clients-2ghz:GAUGE:60:0:200", "DS:tx-retries-2ghz:GAUGE:60:0:100", "DS:interfering-ap-2ghz:GAUGE:60:0:100", "DS:antenna-rssi-2ghz:GAUGE:60:0:100", "DS:bytes-rx-2ghz:COUNTER:60:0:U", "DS:bytes-tx-2ghz:COUNTER:60:0:U",
                "DS:ch-util-5ghz:GAUGE:60:0:100", "DS:clients-5ghz:GAUGE:60:0:200", "DS:tx-retries-5ghz:GAUGE:60:0:100", "DS:interfering-ap-5ghz:GAUGE:60:0:100", "DS:antenna-rssi-5ghz:GAUGE:60:0:100", "DS:bytes-rx-5ghz:COUNTER:60:0:U", "DS:bytes-tx-5ghz:COUNTER:60:0:U",
                "RRA:AVERAGE:0.25:1m:1M",
                "RRA:AVERAGE:0.25:5m:1y")
        
        update = f"N:{ap['2ghz']['ch-util']}:{ap['2ghz']['clients']}:{ap['2ghz']['tx-retries']}:{ap['2ghz']['interfering-ap']}:{ap['2ghz']['antenna-rssi']}:{ap['2ghz']['bytes-rx']}:{ap['2ghz']['bytes-tx']}"
        update += f":{ap['5ghz']['ch-util']}:{ap['5ghz']['clients']}:{ap['5ghz']['tx-retries']}:{ap['5ghz']['interfering-ap']}:{ap['5ghz']['antenna-rssi']}:{ap['5ghz']['bytes-rx']}:{ap['5ghz']['bytes-tx']}"
        rrdtool.update(filename, update)
        print(update)

    end = time.time()
    # print(f"Time taken: {end - start}")

    # print("")
    time.sleep(15 - end + start)