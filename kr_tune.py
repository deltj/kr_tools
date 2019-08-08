#!/usr/bin/env python3
#
# Python program to tune one or more Kismet Data Sources
#
# -Ted

import argparse
import kr
import requests
import signal
import sys
import time

# This object stores information about a data source we're tracking
class SourceInfo:
    name = ""       # The name of this data source
    uuid = 0        # Kismet's UUID for this data source
    count = 0       # The number of frames observed by this data source
    last_count = 0  # The previous number of frames observed by this data source
    offset = 0      # Frame count offset (to account for sync time)
    hardware = ""

def signal_handler(sig, frame):
    print('\n')
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
    parser.add_argument("-c", dest="channel", required=True,
            help="the channel to monitor")
    parser.add_argument("sources", metavar="SRC", nargs="+",
            help="data sources to tune")

    args = parser.parse_args()

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

    sources_by_name = dict()

    for source in args.sources:
        if not kr.have_source(session, base_uri, source):
            print(f"Source {source} not found")
            print(f"Checking for interface named {source}")
            if not kr.have_interface(session, base_uri, source):
                print(f"No interface named {source}, ignoring")
                continue

            # Add the interface as a datasource
            print(f"Interface {source} found, adding as a datasource")
            kr.add_source(session, base_uri, source)

        else:
            print(f"Source found")

        si = SourceInfo()
        si.name = source
        sources_by_name[source] = si

    # Make sure some data sources were configured
    if len(sources_by_name) == 0:
        print("No sources configured, exiting")
        sys.exit(1)

    # Update data source UUIDs
    datasources = kr.get_sources(session, base_uri)
    for ds in datasources:
        name = ds['kismet.datasource.name']
        sources_by_name[name].uuid = ds['kismet.datasource.uuid']
        sources_by_name[name].hardware = ds['kismet.datasource.hardware']

    # Tune data sources to the specified channel
    for source_name, source in sources_by_name.copy().items():
        print("Tuning data source {} to channel {}".format(source_name, args.channel))
        kr.set_channel(session, base_uri, source.uuid, args.channel)
