#!/usr/bin/python3
import subprocess
import json
from typing import List
import matplotlib.pyplot as plt
import os
import argparse

# specify iperf3 testing duration
TIME        : int
CONSTRAINTS : List[int]

# CREATE OUTPUT DIRECTORIES
RESULT_DIRECTORY    : str = "./test-results/"
FINAL_RESULT_DIRECTORY  : str = "./"
PLOT_DIRECTORY   : str    = "./"



def run_bottleneck_test(bw_bottleneck : int , bw_other : int =100, time_seconds : int = 1) -> dict:
    """
    Function to run network_bottleneck.py with the specified bottleneck bandwidth.<br>
    
    Parameters:<br>
    - <strong>bw_bottleneck</strong>    : <code>int</code>  bottleneck bandwidth in Mbps<br>
    - <strong>bw_other</strong>         : <code>int</code>  bandwidth of other (normal) links, (default 100 Mbps)<br>
    - <strong>time_seconds</strong>             : <code>int</code>  TO BE IMPLEMENTED... modulate the duration of iperf testig (default 1 second)<br>
    <emphasis>The time parameter currently modulates the duration of iperf testing</emphasis><br>
    
    Returns:<br>
    - <code>dict</code> TCP and UDP iperf3 test results from the generated JSON file<br>
    """
    subprocess.run( ["mn", "-c"] )
    # Run the network_bottleneck.py script with the given bandwidths
    subprocess.run( ["python3", "network_bottleneck.py", "-bw_bottleneck",str(bw_bottleneck), "-time", str(time_seconds)] )

    # Load the results from the generated JSON files for both TCP and UDP
    tcp_file = f"{FINAL_RESULT_DIRECTORY}output-tcp-{bw_bottleneck}-{bw_other}.json"
    udp_file = f"{FINAL_RESULT_DIRECTORY}output-udp-{bw_bottleneck}-{bw_other}.json"

    # Initialize results
    # MODULATE THE DESIRED RESULT DATA HERE
    # UTILIZE JSON PRETTY PRINTING TO EXPLORE AVAILABLE DATA IN THE GENERATED TEST FILES
    # RUN DEFAULT FIRST.. THEN USE THE GENERATED JSON TEST FILES TO EXPLORE THE KEYS.
    results = {
        "TCP":
            {
                'total_bytes_sent'        : int,
                'total_bytes_received'    : int,
                'reliability'             : float
            }
        , "UDP": 
            {
                'total_bytes_sent'  : int
            }
        
    }

    # Parse TCP results
    if os.path.exists(tcp_file):
        with open(tcp_file, 'r') as f:
            
            tcp_data = json.load(f)
            
            total_bytes_sent        = 0
            total_bytes_received    = 0
            
            for test_case in tcp_data.keys():
                total_bytes_sent       += tcp_data[test_case]['client']['end']['sum_sent']['bytes']
                total_bytes_received   += tcp_data[test_case]['client']['end']['sum_received']['bytes']
                
                
            results['TCP']['total_bytes_sent']      = total_bytes_sent
            results['TCP']['total_bytes_received']  = total_bytes_received
            results['TCP']['reliability']           = total_bytes_received / total_bytes_sent 

    # Parse UDP results
    if os.path.exists(udp_file):
        with open(udp_file, 'r') as f:
            
            udp_data = json.load(f)
            
            for test_case in udp_data.keys():
                
                total_bytes_sent = udp_data[test_case]['client']['end']['sum']['bytes']

            results['UDP']['total_bytes_sent'] = total_bytes_sent

    return results


def plot_test_results( *, data_sets : List[dict] , title : str , xlabel: str , ylabel: str , labels : List[str] , plot_file_name : str ) -> None:
    """
    Function plots variable inputted data via a key to value dictionary parsing. The dictionaries to be plotted
    should be provided in a list, with their corresponding data already sorted. The labels provided should
    coincide with the dictionary keys ordering (order in which items were added to the dictionary). 
    Returns a line graph<br>
    
    Parameters:<br>
    - <strong>data_sets</strong>             : <code>List</code> list of dictionaries holding data to plot<br>
    - <strong>title</strong>                 : <code>str</code>  the title to be assigned to the plot<br>
    - <strong>xlabel</strong>                : <code>str</code>  the desired x-axis label for the plot<br>
    - <strong>ylabel</strong>                : <code>str</code>  the desired y-axis label for the plot<br>
    - <strong>labels<strong>                 : <code>List</code> the list of assigned plot names ( name the 'line' )<br>
    
    Returns:<br>
    -None
    """
    if not os.path.exists(PLOT_DIRECTORY):
        subprocess.run([ "mkdir", PLOT_DIRECTORY ] )
    
    plt.figure(figsize=(9, 6))

    label_index = 0
    for data_set in data_sets:
        
        # Format data (x-axis keys , y-axis values)
        __data_set = data_set.items()
        x_axis, y_axis = zip(*__data_set)
        
        # Plot data
        plt.plot(x_axis, y_axis,  label=labels[label_index], marker='s')
        label_index += 1
    
    # Adding labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()

    # Save the plot as analysis.png
    plt.savefig(plot_file_name)


def extract_plot_dataset( *, test_results : dict , subject : str ) -> dict:
    """
        Function extracts the data from the analysis dictionary structure,
        as specified by the <code>subject</code> parameter, and returns the
        data formatted for the plotting function of this module.<br>
        
        Parameters:<br>
        -<strong>test_results</strong>  : the test result set to extract data from
        -<strong>subject</code>         : the key name of the desired test data for plotting
    
    """
    
    cases = test_results.keys()
    
    dataset = { x : test_results[x][subject] for  x in cases }
    
    return dataset

def calculate_throughput( *  , total_bytes_transmitted : int , time_seconds : int ) -> float :
    return ( total_bytes_transmitted ) / time_seconds

def main():
    # Define bottleneck bandwidths to test
    # !!! MODIFYING THIS STRUCTURE DICTATES THE DURATION AND CONTENTS OF THE TEST
    # !!! THIS IS THE ONLY STRUCTURE THAT NEEDS TO BE MODULATED TO MANIPULATE BANDWIDTHS TESTED
    bottleneck_bandwidth_tests = { x:{} for x in CONSTRAINTS }

    # Run tests for each bandwidth and collect test result data
    # Collecting data on...
    #  - throughput
    #  - reliability
    for bw in bottleneck_bandwidth_tests.keys():
        # new test
        test_results = run_bottleneck_test(bw_bottleneck=bw, time_seconds=TIME)

        # throughput calculation
        tcp_throughput : float = calculate_throughput( 
                                                      total_bytes_transmitted= (test_results['TCP']['total_bytes_sent'] + test_results['TCP']['total_bytes_received']),
                                                      time_seconds=TIME
                                                      )
        udp_throughput : float = calculate_throughput( total_bytes_transmitted=test_results['UDP']['total_bytes_sent'],
                                                      time_seconds=TIME
                                                      )
 
        # storage of results
        bottleneck_bandwidth_tests[bw] = {
            'tcp_throughput'   :  tcp_throughput,
            'tcp_reliability'  :  test_results['TCP']['reliability'],
             'udp_throughput'  :  udp_throughput
        }

    # load segregated data for plotting
    tcp_throughput_data     = extract_plot_dataset( test_results=bottleneck_bandwidth_tests , subject='tcp_throughput')
    tcp_reliability_data    = extract_plot_dataset( test_results=bottleneck_bandwidth_tests , subject='tcp_reliability' )
    udp_throughput_data     = extract_plot_dataset( test_results=bottleneck_bandwidth_tests , subject='udp_throughput' )


    #Plot the results
    plot_test_results( 
                 data_sets=[
                    tcp_throughput_data, 
                    udp_throughput_data
                ] ,
                 title="TCP and UDP Throughput vs Bottleneck Bandwidth",
                 xlabel="Bottleneck Bandwidth (Mbps)",
                 ylabel="Throughput (Bytes/Second)",
                 labels=["TCP Throughput" , "UDP Throughput"],
                 plot_file_name="analysis.png"
            )
    plot_test_results( 
                 data_sets=[
                    tcp_reliability_data, 
                ], 
                 title="TCP Reliability vs Bottleneck Bandwidth",
                 xlabel="Bottleneck Bandwidth (Mbps)",
                 ylabel="Link reliability",
                 labels=["Reliability"],
                 plot_file_name="reliability.png"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-time", help="Specify duration of iperf tests... 5 seconds by default", type=int, default=5)
    parser.add_argument("-constraints", help="Specify bandwidth bottlenecks to test in network sumulation. Separate by spaces (ex. '# # #')", type=str, default="8 32 64")
    args = parser.parse_args()
    TIME = args.time
    CONSTRAINTS = [ int(x) for x in args.constraints.split()]
    main()
