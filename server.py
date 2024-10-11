#!/usr/bin/python3
import argparse
import iperf3
import json
import os
import subprocess
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

    if not os.path.exists("./test-results"):
        subprocess.Popen(["mkdir", "test-results"])
    if not os.path.exists("./test-results/iperf/"):
        subprocess.Popen([ "mkdir", "./test-results/iperf" ] )
    
         
    file_name = "./test-results/iperf/s-iperf-client-{}-to-server-{}-test-{}.json".format(
        result.remote_host,
        result.local_host,
        result.protocol
    )
    
    with open(file_name, 'w') as f:
        json.dump(data, f)

    