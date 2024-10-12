#!/usr/bin/python3
# IMPORTS 
import argparse
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
import subprocess
from time import sleep
import json
import os
from configure import SERVICE_DIRECTORY, FINAL_RESULT_DIRECTORY, IPERF_DIRECTORY
from configure import LOG_DIRECTORY, IFCONFIG_DIRECTORY, PING_DIRECTORY
from configure import init_file_system
# GLOBAL CONSTANTS 
# specify the number of times failed tests will repeat
MAX_ATTEMPTS = 5
# specify the duration of iperf tests
TIME = 10 # redefined in main
# specify network bandwidth restrictions
BW_BOTTLENECK = 10 # redefined in main
BW_OTHER      = 100


# CLASS - LOGGER
class Logger() :
    __log_index         = 0

    def __init__( self, log_file :str = "out.txt" , logging_prefix :str = "[ LOG ] >> ") -> None:
        
        self.__log_file = log_file
        self.__logging_prefix = logging_prefix
    
    def log( self, message :str ) -> None:
        
        message = "{} {} >>  {}\n".format( self.__logging_prefix , self.__log_index , message )
        self.__log_index += 1
        with open ( self.__log_file , 'a' ) as f:
            f.write(message)

def generate_instance_message( message : str ) -> str :
     return "{}-{}-{}".format(
            message,
            BW_BOTTLENECK,
            BW_OTHER
        )
            

init_file_system()

# INSTANTIATE GENERAL SESSION LOGGERS

configuration_logger    = Logger(log_file="{}output-network-config-{}-{}.txt".format(LOG_DIRECTORY,BW_BOTTLENECK,BW_OTHER))
err_logger              = Logger(log_file="{}error-output.txt".format(LOG_DIRECTORY))
success_logger          = Logger(log_file="{}success-output.txt".format(LOG_DIRECTORY))

# DEFINE NETWORK TOPOLOGY
class BottleneckTopo( Topo ):
    "Network topology for bottleneck testing"

    def build( self, bw_bottleneck : int , bw_other : int )  :
        #clients
        client_1    = self.addHost( 'h1' )
        client_2    = self.addHost( 'h2' )
        #servers
        server_1    = self.addHost( 'h3' )
        server_2    = self.addHost( 'h4' )
        #switches
        switch_1    = self.addSwitch( 's1' )
        switch_2    = self.addSwitch( 's2' )
        #links
        # link : h1 (client 1) -to- s1 (switch 1)
        link_1 = self.addLink( client_1 , switch_1 , cls=TCLink , bw=bw_other)
        # link : h2 (client 2) -to- s1 (switch 1)
        link_2 = self.addLink( client_2 , switch_1 , cls=TCLink , bw=bw_other)
        #~~~bottleneck link : s1 (switch 1) -to- s2 (switch 2)
        link_3 = self.addLink( switch_1 , switch_2 , cls=TCLink ,bw=bw_bottleneck)
        # link : s2 (switch 2) -to- h3 (server 1)
        link_4 = self.addLink( switch_2 , server_1 , cls=TCLink , bw=bw_other)
        # link : s2 (switch 2) -to- h4 (server 2)
        link_5 = self.addLink( switch_2 , server_2 , cls=TCLink , bw=bw_other)
    

######################################################################################
# FUNCTIONS & PROCEDURES

def do_node_cmd( network , target_node_name : str , node_cmd : str ) -> str:
    """ 
    Function retrieves a <code>Mininet Node</code> instance and runs a provided
    command at that node.<br>>
    
    Parameters:<br>
    - <strong>network</strong>      : <code>Mininet()</code> instance<br>
    - <strong>target_node_name</strong>  : <code>string</code> name of node where the provided command will run<br>
    - <strong>node_cmd</strong>     : <code>string</code> command to run at provided node name<br>
    
    Returns:<br>
    - <code>string</code> result of command at the node
    """
    return network.get(target_node_name).cmd(node_cmd)



def log_node_cmd(node_name : str , cmd_to_log : str , file_prefix : str ) -> None :
    """ 
    Writes a command output to a log file specific
    to the provided <code>Mininet Node</code> name, with the specified prefix for
    the file name.<br>
    
    Parameters:<br>
    - <strong>node_name</strong>        :  <code>string</code> name of node<br>
    - <strong>cmd_to_log<strong>   :  <code>string</code> command result from provided node<br>
    - <strong>file_prefix<strong>  :  <code>string</code> prefix for the file which will hold the result<br>
    
    Returns:<br>
    - None
    """
    with open("{}-{}.txt".format(file_prefix, node_name), 'a') as f:
        f.write(cmd_to_log)
    
   
def parse_NodeIP( mininet_node_Node_IP ) -> str:
    """ 
    Extracts the IPv4 address out of the <code>Mininet Node</code> instance
    <code>node.IP</code> method and returns value as string.<br>
    
    <code>mininet.node.Node node.IP</code>
    
    Parameters:<br>
    - <strong>outputIP</strong>  : the output acquired from the <code>.IP</code> method<br>
    
    Returns:<br>
    - <code>string</code> extracted ip address
    
    """ 
    #initial format : <bound method Host.IP of <Host h#: h#-eth#: #.#.#.# pid=####> >
    ipv4address = str(mininet_node_Node_IP).split(':')[2]       # format  :  #.#.#.# pid=####> >
    ipv4address = ipv4address.split()[0]            # format  :  #.#.#.#
    return ipv4address  

# TESTER
def run_topology_tests() -> None:
    """ 
    Network test to confirm capability to retrieve <code>ifconfig</code> information 
    from <code>mininet Node</code> instances and test the <code>ping</code> performance between them.<br>
    
    
    Returns:<br>
    - None
    """   
    #Build topology
    try:
        topo    = BottleneckTopo( BW_BOTTLENECK , BW_OTHER )
        success_logger.log("successfully instantiated BottleneckTopo object in run_topology_tests...")
    except Exception as e:
        err_logger.log(generate_instance_message("[ ERROR ] failed to instantiate network topology."))
        return
    
    #Instantiate network.
    try:
        network = Mininet( topo=topo ) 
        success_logger.log("successfully instantiated Mininet() object in run_topology_tests...")
    except:
        err_logger.log(generate_instance_message("[ ERROR ] failed to instantiate Mininet network."))
        return
    
    # Start network simulation
    try:
        network.start()
        success_logger.log("successfully started a mininet network in run_topology_tests...")
    except:
        err_logger.log(generate_instance_message("[ ERROR ] failed to start network."))
        return

    # Log the parameters configured for the test as requested in assignment specifications.
    configuration_logger.log("Bandwidth for bottleneck link is : {}.".format(BW_BOTTLENECK))
    configuration_logger.log("Bandwidth for standard links is : {}.".format(BW_OTHER))
    
    # STARTING 
    hosts = [x for x in network.keys() if x[0] == 'h']
    # TEST ONE :: ifconfig testing ####################################3 
    for host in hosts : 
        
        # Send command to node.
        try:
            ifconf_cmd_result = do_node_cmd(
                                        network             =   network, 
                                        target_node_name    =   host, 
                                        node_cmd            =   'ifconfig'
                            )
            success_logger.log(generate_instance_message("successfully sent command to node : [{} : ifconfig]".format(host)))
        except:
            err_logger.log(generate_instance_message("[ ERROR ] failure in sending ifconfig command for {}.".format(host)))
            
        # Log command result.
        try:     
            log_node_cmd(
                    node_name   =   host,
                    cmd_to_log  =   ifconf_cmd_result,
                    file_prefix =   '{}output-ifconfig-{}-{}'.format(IFCONFIG_DIRECTORY, BW_BOTTLENECK,BW_OTHER)
            )
            success_logger.log(generate_instance_message("successfully logged command [{} : {}] in run_topology_tests...".format(host,'ifconfig')))
        except:
            err_logger.log(generate_instance_message("[ ERROR ] failure in logging ifconfig command for {}".format(host)))
        
             
        # TEST TWO :: ping testing ###########################################
        for alt_host in hosts:
            if alt_host != host:
                # Ping all others hosts from top level host 
                try:
                    ping_cmd = 'ping -c3 {}'.format( parse_NodeIP(network.get(alt_host).IP))
                    ping_cmd_result = do_node_cmd(
                                            network         =   network,
                                            target_node_name=   alt_host, 
                                            node_cmd        =   ping_cmd
                                    ) 
                    success_logger.log(generate_instance_message("successfully sent command to node : [{} : ping to {}]".format(host,alt_host)))
                except:
                    err_logger.log(generate_instance_message("[ ERROR ] failure in pinging test for {} to {}.".format(host,alt_host)))

                # Logging ping results.
                try:
                    log_node_cmd(
                            node_name   =   host,
                            cmd_to_log  =   ping_cmd_result,
                            file_prefix =   '{}output-ping-{}-{}'.format(PING_DIRECTORY, BW_BOTTLENECK,BW_OTHER)
                    )
                    success_logger.log(generate_instance_message("successfully logged command [{} : ping to {}] in run_topology_tests...".format(host,alt_host)))
                except:
                    err_logger.log(generate_instance_message("[ ERROR ]  failure in logging ping results for {} to {}.".format(host,alt_host)))
    
    # FINISHED
    try:
        network.stop()
        success_logger.log(generate_instance_message("successfully stopped mininet network in run_topology_tests..."))
    except:
        err_logger.log(generate_instance_message("[ ERROR ] failure to gracefully terminate Mininet network simulation."))
        return


def generate_server_test_cmd( server_ip : str, service_port : int) -> str :
    """ 
        Function produces command line argument specific to running the <code>server.py</code> script.
        
        Parameters:<br>
        - <strong>host_address</strong> : <code>string</code> the ipv4 address designated for the server<br>
        - <strong>service_port</strong> : <code>int</code> the service port designated for the server<br>
        
        Returns:<br>
        - <code>string<code> the formatted command
    """
    test_cmd_Server = "python3 server.py -ip {} -port {}".format(server_ip,service_port)
    return test_cmd_Server


def generate_client_test_cmd( client_ip : str , service_port : int , server_ip : str , tcp_udp : str ) -> str :
    """ 
        Function produces command line argument specific to running the <code>client.py</code> script.
        
        Parameters:<br>
        - <strong>client_ip</strong>        : <code>string</code> the ipv4 address designated for the client<br>
        - <strong>service_port</strong>     : <code>int</code> the service port designated for the server<br>
        - <strong>server_ip</strong>        : <code>string</code> the ipv4 address designated for the client<br>
        - <strong>tcp_udp</strong>          : <code>string</code> specify tcp or udp iperf test<br>
        
        Returns:<br>
        - <code>string</code> the formatted command
    """
    test_cmd_Client = "python3 client.py -ip {} -port {} -server_ip {} -test {} -time {}".format(
                    client_ip,
                    service_port,
                    server_ip,
                    tcp_udp,
                    TIME)
    return test_cmd_Client


def bottleneck_testing_json_dump( test_type : str , test_results : dict ) -> None:  
    """
        Procedure dumps a provided dictionary to a json file.

        Parameters:<br>
        - <strong>test_type</strong>        : <code>string</code>   specifies udp or tcp test<br>
        - <strong>test_results</strong>     : <code>dict</code>     the results to write to json file<br>
        
        Returns:<br>
        - None
    """
    # Performing the dump into 'output-<test_type>-<bw_bottleneck>-<bw_other>'.
    with open("{}output-{}-{}-{}.json".format( FINAL_RESULT_DIRECTORY, test_type , BW_BOTTLENECK , BW_OTHER ),
            'w') as f:
        json.dump(test_results, f)


def generate_iperf_client_server_file_name( network, client_name : str, server_name : str , protocol : str, cli_or_srv : chr ) -> str:
    """
        Function produces the iperf test result file name specific to the provided parameters as specified by the application instance.

        Parameters:<br>
        - <strong>network</strong>            :   <code>mininet.net.Mininet</code>    the network simulation instance<br>
        - <strong>client_name</strong>        :   <code>string</code>                 the name of the client<br>
        - <strong>server_name</strong>        :   <code>string</code>                 the name of the server<br>
        - <strong>protocol</strong>           :   <code>string</code>                 specifies tcp or udp test<br>
        - <strong>cli_or_srv</strong>         :   <code>string</code>                 specifies whether the client or server data is desired<br>

        Returns:<br>
        -<code>string</code>  the formatted file name
    """
    client_ip = parse_NodeIP( mininet_node_Node_IP = network.get(client_name).IP )
    server_ip = parse_NodeIP( mininet_node_Node_IP = network.get(server_name).IP )
    
    file_name = "{}{}-iperf-client-{}-to-server-{}-test-{}.json".format(
        IPERF_DIRECTORY,
        cli_or_srv,
        client_ip,
        server_ip,
        protocol.upper()
    )
    
    new_file_name = file_name[:len(file_name)-5]
    new_file_name += "-{}-{}.json".format(BW_BOTTLENECK,BW_OTHER)
    
    if os.path.exists(file_name) :
        subprocess.run( ["mv", file_name, new_file_name])

    
    return new_file_name
    
     

def load_client_server_JSON_data( network, client_name : str, server_name : str, protocol : str) -> dict:
    """
        Function loads json formatted iperf test data and returns a dictionary.
        The paramaters specify the test case instance.<br>
        
        Parameters:<br>
        - <strong>network</strong>          : <code>mininet.net.Mininet</code>  the network simulation instance.<br>
        - <strong>client_name</strong>      : <code>string</code>               the name of the client in the test case<br>
        - <strong>server_name</strong>      : <code>string</code>               the name of the server in the test case<br>
        - <strong>protocol</strong>         : <code>string</code>               specifies the protocol of the test<br>
        
        Returns:<br>
        -<code>dict</code>  the test data for the specified test case
    """
    
    # generate desired file name ( client data )
    file_name = generate_iperf_client_server_file_name( 
                    network      = network ,
                    client_name  = client_name,
                    server_name  = server_name, 
                    protocol     = protocol, 
                    cli_or_srv   ='c'
                )
    # load json
    data_client = {}
    with open(file_name, 'r') as f :
        data_client = json.load(f)
    # generate desired file name ( server data )    
    file_name = generate_iperf_client_server_file_name( 
                    network      = network ,
                    client_name  = client_name,
                    server_name  = server_name, 
                    protocol     = protocol, 
                    cli_or_srv   ='s'
                )
    # load json
    data_server = {}
    with open(file_name, 'r') as f :
        data_server = json.load(f)
    # return concatenated dictionary of client and server results
    return {
                "client": data_client,
                "server": data_server
            }


# TESTER
def run_iperf_client_server_test( client_name : str , server_name : str, network , service_port : int , tcp_udp : str ) -> dict:
    """ 
    Function performs <code>iperf3</code> testing between two <code>Mininet Node</code> instances.<br>
    
    Parameters:<br>
    - <strong>client_name</strong>  : <code>string</code> name of the node to act as the client<br>
    - <strong>server_name</strong>  : <code>string</code> name of the node to act as the server<br>
    - <strong>network</strong>      : <code>Mininet()</code> instance<br>
    - <strong>service_port</strong> : <code>int</code> service port to be used for server connections<br>
    - <strong>tcp_udp</strong>      : <code>string</code> specifier of udp or tcp iperf testing<br>
    
    Returns:<br>
    - <code>dict</code> dictionary holding test results fo client and server
    """

    # Denotes number of attempts to achieve successful iperf test
    attempts = MAX_ATTEMPTS
    # Retreive the ipv4 addresses of the test client.
    try:
        server_ip       = parse_NodeIP(network.get(server_name).IP)
        client_ip       = parse_NodeIP(network.get(client_name).IP)
    except:
        err_logger.log(generate_instance_message("[ ERROR ] failure to extract IP addresses from test subjects in run_iperf_client_server_test"))
        return None
    # Latch will be used to skip over procedures, in the case of a failure.
    result = {}
    # Denotes successful iperf test
    success = False
    while not success and attempts:
        success_latch = 1
        # iperf3 server set        
        try:
            # Initiate the server on a separate thread.
            command =   generate_server_test_cmd(
                                    server_ip   =   server_ip,
                                    service_port=   service_port
                        )
            # Server initiated here...
            p1 = network.get(server_name).popen( command )

            success_logger.log(generate_instance_message("successfully initiated server [@{}] in run_iperf_client_server_test...".format(server_name)))
        # failed to initiate server
        except:
            err_logger.log(generate_instance_message("[ ERROR ] failure in initiating server in run_iperf_client_server_test({%s}) @ attempt %d".format(
                server_name, MAX_ATTEMPTS-attempts+1 )))
            # jump to next attempt
            success_latch = 0            
        
        # successfully initiated server...
        if success_latch:
            try:
                # iperf3 client connection & testing
                command = generate_client_test_cmd(
                                                client_ip   =   client_ip,
                                                service_port=   service_port, 
                                                server_ip   =   server_ip,
                                                tcp_udp     =   tcp_udp
                                            )
                # Client connects here...
                network.get(client_name).cmd(command)

                success_logger.log(generate_instance_message("successfully initiated client in iperf test [@server {} : @client {}] in run_iperf_client_server_test...".format(
                                        server_name, 
                                        client_name)))
            # failed to run client connection to server
            except:
                err_logger.log(generate_instance_message("[ ERROR ] failure in client connection in run_iperf_client_server_test ({%s}) @ attempt %d".format( 
                                    client_name, 
                                    MAX_ATTEMPTS-attempts+1 ))
                            )
                
                # jump to next attempt
                success_latch = 0
        
        # successful test was potentially performed
        if success_latch:
            # Successful test ?
            # Ensures that result data is present.
            try:
                # Ensure that server.py and client.py have time to write results
                sleep(1)
                result = load_client_server_JSON_data(
                            network     = network,
                            client_name = client_name,
                            server_name = server_name,
                            protocol    = tcp_udp
                )
                # Data is calculated and loaded... ready to abort operation.
                success = True
                success_logger.log(generate_instance_message("successfully performed server client test & exited iperf test [@server {} : @client {}] in run_iperf_client_server_test...".format(
                                        server_name,
                                        client_name
                                    ))
                                )
                
            # results are missing
            except: # will try again
                err_logger.log(generate_instance_message("failed attempt({}) in run_iperf_client_server_test (client:{} server{})".format(
                                            MAX_ATTEMPTS-attempts+1,
                                            client_name,
                                            server_name
                )))

        attempts -= 1
        # iperf3 server clear
        # necessary for repetative testing
        p1.terminate()
        # reset succes_latch flag
        success_latch = 1
    # END WHILE

    # Indicates failure in iperf test where no attempts are remaining.
    if not attempts :
        err_logger.log(generate_instance_message("failure to complete testing (ATTEMPTS EXCEEDED) [@server {} : @client {}] in run_iperf_client_server_test...".format(server_name,client_name)))
        return None
    
    # RETURNING
    else :
        return result
    

def run_perf_tests() -> None :
    """
    Procedure creates a <code>Mininet</code> network instance and performs <code>iperf3</code>
    testing, given specified constraints on bandwidth.<br>
    
    Returns:<br>
    - <code>list</code> : result of iperf3 testing ( sent/received bytes )<br>
        - [ (tcp) h1-h3, (tcp) h3-h1, (udp) h2-h4, (udp) h4-h2 ]
    """
    
    # Build topology.
    try:
        topo    = BottleneckTopo( BW_BOTTLENECK, BW_OTHER )
    except:
        err_logger.log(generate_instance_message("failure to initiate topology in run_perf_tests - {}-{}".format(
            BW_BOTTLENECK,
            BW_OTHER
        )))
    
    # Instantiate Mininet object.
    try:
        network = Mininet( topo=topo ) 
    except:
        err_logger.log(generate_instance_message("failure to initiate mininet.net.Mininet network in run_perf_tests - {}-{}".format(
            BW_BOTTLENECK,
            BW_OTHER
        )))
    
    # Start the network simulation.
    try:
        network.start()
    except:
        err_logger.log(generate_instance_message("failure to start mininet simulation in run_perf_tests - {}-{}".format(
            BW_BOTTLENECK,
            BW_OTHER
        )))
    
    # maximum number of times to try again
    attempts = MAX_ATTEMPTS
    # flag marks successful aquisition of data
    success = False
    while not success and attempts :
        try :    

            # TESTING h1 to h3 
            iperf_h1_Client_h3_Server_result = run_iperf_client_server_test( 
                                            client_name     =   'h1' , 
                                            server_name     =   'h3' , 
                                            network         =   network , 
                                            service_port    =   5000, 
                                            tcp_udp         =   'tcp' 
                                        )
            
            iperf_h3_Client_h1_Server_result = run_iperf_client_server_test( 
                                            client_name     =   'h3' , 
                                            server_name     =   'h1' , 
                                            network         =   network , 
                                            service_port    =   5000, 
                                            tcp_udp         =   'tcp' 
                                        )
            
            # Concatenate results
            iperf_test_results_h1_h3 = {
                1: iperf_h1_Client_h3_Server_result,
                2: iperf_h3_Client_h1_Server_result
            }
            
            # TESTING h2 to h4
            iperf_h2_Client_h4_Server_result = run_iperf_client_server_test( 
                                            client_name     =   'h2' , 
                                            server_name     =   'h4' , 
                                            network         =   network , 
                                            service_port    =   5000, 
                                            tcp_udp         =   'udp' 
                                        )
            iperf_h4_Client_h2_Server_result = run_iperf_client_server_test( 
                                            client_name     =   'h4' , 
                                            server_name     =   'h2' , 
                                            network         =   network , 
                                            service_port    =   5000, 
                                            tcp_udp         =   'udp' 
                                        )
            
            # Concatenate results
            iperf_test_results_h2_h4 = {
                1: iperf_h2_Client_h4_Server_result,
                2: iperf_h4_Client_h2_Server_result
            }

            # exit procedure
            success = True
        except :        
            err_logger.log(generate_instance_message("[ ERROR ] Failure in run_perf_tests @ attempt #{}".format(MAX_ATTEMPTS-attempts+1)))
            attempts -= 1
                
    try:
        network.stop()
    except:
        err_logger.log(generate_instance_message("failure to properly halt mininet.net.Mininet network in run_perf_tests - {}-{}".format(
            BW_BOTTLENECK,
            BW_OTHER
        )))

    # Producing final json files for test result ( output-<test>-<BW_BOTTLENECK>-<bw_other>.json ).
    # files requested per assignment specifications
    try:
        bottleneck_testing_json_dump( 
                                test_type       =   'tcp', 
                                test_results    =   iperf_test_results_h1_h3
                    )   
        bottleneck_testing_json_dump( 
                                test_type       =   'udp', 
                                test_results    =   iperf_test_results_h2_h4
                    )   
    except:        
        return None
if __name__ == "__main__" :

    # parsing command-line
    parser = argparse.ArgumentParser()
    parser.add_argument("-bw_bottleneck",  help="The bandwidth (Mbps) constraint on a bottleneck link",type=int, default=10)
    parser.add_argument("-bw_other",       help="The bandwidth constraint on non-bottleneck  links",type=int, default=100)
    parser.add_argument("-time",           help="Duration of the traffic simulation (s)", type=int, default=10)
    args = parser.parse_args()
    assert(args.bw_bottleneck < args.bw_other)
    TIME            = args.time
    BW_BOTTLENECK   = args.bw_bottleneck
    BW_OTHER        = args.bw_other
    
    configuration_logger.log(generate_instance_message("Preparing run_topology_tests..."))
    configuration_logger.log("Simulation (s) run duration is : {}.".format(TIME))
    run_topology_tests()
    configuration_logger.log(generate_instance_message("Preparing run_perf_tests..."))
    run_perf_tests()
 
    
    
