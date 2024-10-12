#!/usr/bin/python3
import argparse
import iperf3
import json
import os
import subprocess
from configure import RESULTS_DIRECTORY , IPERF_DIRECTORY
#Handles the server code for the Networking Assignment 3
if __name__ == "__main__" :
   
    #Define the parser
    parser = argparse.ArgumentParser()
    #Set the IP and Port values
    parser.add_argument("-ip", help="Server IP address", type=str, default="127.0.0.1")
    parser.add_argument("-port", help="Server service address", type=int, default=5000)
    #Apply values to the parser
    args = parser.parse_args()

    server = iperf3.Server()
    server.bind_address = str(args.ip)
    server.port         = int(args.port)
    server.verbose      = False
    
    #Start the server!
    result = server.run()
    
    data = result.json

    if not os.path.exists(RESULTS_DIRECTORY):
        p1 = subprocess.Popen(["mkdir", RESULTS_DIRECTORY])
        p1.wait()
    if not os.path.exists(IPERF_DIRECTORY):
        subprocess.Popen([ "mkdir", IPERF_DIRECTORY ] )
    
         
    file_name = "{}s-iperf-client-{}-to-server-{}-test-{}.json".format(
        IPERF_DIRECTORY,
        result.remote_host,
        result.local_host,
        result.protocol
    )
    
    with open(file_name, 'w') as f:
        json.dump(data, f)

    
