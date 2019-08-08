#!/usr/bin/env python3
#
# Python program to poll and display the received signal strength for the
# specified device (MAC address)
#
# -Ted

import argparse
import kr
import requests
import signal
import sys
import time

PURPLE = "\033[1;35m"
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED   = "\033[1;31m"  


CYAN  = "\033[1;36m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

def signal_handler(sig, frame):
    print('\n')
    sys.exit(0)

def print_bar(percent):
    width = 40
    fill = int(40 * (percent / 100))
    #print(f"Fill: {fill}")
    
    bar = "["

    blue_amt = int(0.2 * width)
    green_amt = int(.4 * width)
    yellow_amt = int(.6 * width)
    red_amt = int(.8 * width)
    
    for i in range(width):
        color=""

        if i <= fill:
            if i >= red_amt:
                color = RED
            elif i >= yellow_amt:
                color = YELLOW
            elif i >= green_amt:
                color = GREEN
            elif i >= blue_amt:
                color = BLUE
            else:
                color = PURPLE

            bar = bar + f"{color}={RESET}"
        else:
            bar = bar + " "

    bar = bar + "]"

    print(f"{bar}", end='\r')

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="kr_rssi")
    parser.add_argument("-u", dest="user",
            help="a user name to log into Kismet with")
    parser.add_argument("-p", dest="ask_for_password", action="store_true",
            help="tells this program to prompt for a password")
    parser.add_argument("-P", dest="password",
            help="a password to log into Kismet with")
    parser.add_argument("-s", dest="server", default="localhost",
            help="ip/hostname of kismet server (defaults to localhost")
    parser.add_argument("-m", dest="mac", required=True,
            help="MAC Address of the device to monitor")

    args = parser.parse_args()

    mac = args.mac

    username = ""
    if args.user:
        username = args.user

    password = ""
    if args.password:
        password = args.password

    if args.ask_for_password:
        password = getpass.getpass()

    session = requests.Session()
    session.auth = (username, password)

    base_uri = "http://{}:2501".format(args.server)
    print("Connecting to Kismet Server {}".format(base_uri))

    # Verify login
    if not kr.check_session(session, base_uri):
        print("Invalid login")
        sys.exit(1)
    else:
        print("Logged in!")

    rssi_min = -100
    rssi_max = 0

    percent = 0
    while True:

        if not kr.check_session(session, base_uri):
            print("Session check failed")
           
        cmd = {
            "fields": ["kismet.device.base.signal/kismet.common.signal.last_signal"]
        }

        device_json = kr.post_cmd_json(session,
                f"{base_uri}/devices/by-mac/{mac}/devices.json", cmd)
        rssi = device_json[0]['kismet.common.signal.last_signal']

        rssi_pct = (rssi - rssi_min) / (rssi_max - rssi_min) * 100
        #print(rssi_pct)

        print(f"{mac} {rssi} dBm ", end="")
        print_bar(rssi_pct)

        time.sleep(0.1)
