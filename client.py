#!/usr/bin/python3
import argparse
import iperf3
import json
import subprocess
import os
#Handles the client code for the Networking Homework 3 Assignment.
if __name__ == "__main__" :
    
    #Declare the parser and set arguments for the Client IP, Port, Server IP and what type of connection it is. 
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="Client IP address", type=str, default="127.0.0.2")
    parser.add_argument("-port", help="Server service address", type=int, default=5000)
    parser.add_argument("-server_ip", help="Server IP address", type=str, default="127.0.0.1")
    parser.add_argument("-test", help="TCP or UDP iperf3 connection ('tcp' or 'udp')", type=str)
    parser.add_argument("-time", help="Duration of iperf3 test (seconds)", type=int, default=60)

    args = parser.parse_args()
    #Client details are listed below
    client                  = iperf3.Client()
    client.duration         = int(args.time)
    client.server_hostname  = str(args.server_ip)
    client.bind_address     = str(args.ip)
    client.port             = int(args.port)
    client.protocol         = str(args.test)

    if args.test == 'tcp':
        client.blksize          = 22016
    else :
        client.blksize          = 1234
    
    client.json_output      = True
    
    result = client.run()
    
    data = (result.json)
    
    
    file_name = "./test-results/iperf/c-iperf-client-{}-to-server-{}-test-{}.json".format(
        result.local_host,
        result.remote_host,
        result.protocol
    )
    
    with open(file_name, 'w') as f:
        json.dump(data, f)
  
    