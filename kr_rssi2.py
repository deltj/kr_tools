#!/usr/bin/env python3
#
# Python program to poll and display the received signal strength for the
# specified device (MAC address) over a one minute period
#
# -Ted

import argparse
import kr
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import requests
import signal
import sys
import time

session = None
base_uri = ""
mac = ""

def animate(i, xs, ys):

    if not kr.check_session(session, base_uri):
        print("Session check failed")
        sys.exit(1)
           
    cmd = {
        "fields": ["kismet.device.base.signal/kismet.common.signal.signal_rrd/kismet.common.rrd.minute_vec"]
    }

    uri = f"{base_uri}/devices/by-mac/{mac}/devices.json"
    print(uri)
    device_json = kr.post_cmd(session, uri, cmd)
    rssi_rrd = device_json[0]['kismet.common.rrd.minute_vec']
    print(rssi_rrd)

    # clean up data
    i = 0
    for rssi in rssi_rrd:
        if rssi == 0:
            # zero actually means no data
            ys[i] = -100
        else:
            ys[i] = rssi
        i = i + 1

    print(ys)

    ax.clear()
    ax.set_title(f"RSSI for {mac}")
    ax.set_xlabel("RRD Samples")
    ax.set_ylabel("dBm")
    ax.plot(xs, ys)

def signal_handler(sig, frame):
    sys.exit(0)

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

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = np.linspace(0, 60, 60)
    ys = np.linspace(-100, -100, 60)

    ani = anim.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
    plt.show()

