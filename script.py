import paramiko
import time
import json
import rrdtool
import os

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

''' Get user credentials '''
import getpass
username = getpass.getuser()
password = getpass.getpass(f"Enter Fortigate password ({username}): ")

data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

''' Connect to Fortigate via SSH '''
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(options.ip, username=username, password=password)

while True:
    stdin, stdout, stderr = ssh.exec_command("diagnose wireless-controller wlac -c wtp")
    stdin.close()

    ch_util = {}
    for line in stdout.readlines():
        line = line.strip()

        ''' Next AP, clear variable '''
        if "-------------------------------WTP" in line:
            ch_util = {}
        
        ''' Fetch AP name, create RRD file '''
        if "name             : " in line:
            ap_name = line.split(": ")[1]

        ''' Fetch current radio '''
        if line == "Radio 1            : AP":
            ap_radio = "2.4ghz"
        if line == "Radio 2            : AP":
            ap_radio = "5ghz"

        ''' Fetch current channel utilization '''
        if "oper chutil data : " in line:
            try:
                ''' Actual output: 'oper chutil data : 27,44,36,36,30, 33,29,30,29,20, 24,23,20,22,23 ->newer' 
                    We do some ugly string splitting to retrieve the first value, in this case 27. '''
                current_ch_util = int(line.split(": ")[1].split(",")[0])
            except:
                print("Unknown channel utilization value:")
                print(line)
                pass
            else:
                ch_util[ap_radio] = current_ch_util

            ''' If all data has been gathered, write to RRD file '''
            if '2.4ghz' in ch_util and '5ghz' in ch_util:
                filename = f"{data_folder}/{ap_name}.rrd"
                if not os.path.isfile(filename):
                    rrdtool.create(filename, 
                        "--start", "now",
                        "--step", "15",
                        "DS:ch-util-2ghz:GAUGE:60:0:100", # wait up to 60 seconds for input, expect value between 0 and 100
                        "DS:ch-util-5ghz:GAUGE:60:0:100",
                        "RRA:MAX:0.25:4:525600",
                        "RRA:AVERAGE:0.25:4:525600")
                
                rrdtool.update(filename, f"N:{ch_util['2.4ghz']}:{ch_util['5ghz']}")
                print(f"N:{ch_util['2.4ghz']}:{ch_util['5ghz']}")

    print("")
    time.sleep(15)
