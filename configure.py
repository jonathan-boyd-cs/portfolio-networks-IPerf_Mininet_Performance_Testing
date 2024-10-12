import subprocess
import os

SERVICE_DIRECTORY = "./service/"
RESULTS_DIRECTORY = "./test-results/"
FINAL_RESULT_DIRECTORY = "{}final/".format(RESULTS_DIRECTORY)
IPERF_DIRECTORY = "{}iperf/".format(RESULTS_DIRECTORY)
PING_DIRECTORY = "{}ping/".format(RESULTS_DIRECTORY)
IFCONFIG_DIRECTORY = "{}ifconfig/".format(RESULTS_DIRECTORY)
PLOT_DIRECTORY   : str    = "{}plots/".format(RESULTS_DIRECTORY)
LOG_DIRECTORY = "{}logs/".format(SERVICE_DIRECTORY)

def init_file_system() :
    if not os.path.exists(SERVICE_DIRECTORY):
        subprocess.run(["mkdir", SERVICE_DIRECTORY])
    
    if not os.path.exists(LOG_DIRECTORY):
        subprocess.run(["mkdir", LOG_DIRECTORY])
    
    if not os.path.exists(RESULTS_DIRECTORY):
        subprocess.run(["mkdir", RESULTS_DIRECTORY])
    
    if not os.path.exists(FINAL_RESULT_DIRECTORY):
        subprocess.run(["mkdir", FINAL_RESULT_DIRECTORY])

    if not os.path.exists(IFCONFIG_DIRECTORY):
        subprocess.run(["mkdir", IFCONFIG_DIRECTORY])

    if not os.path.exists(PING_DIRECTORY):
        subprocess.run(["mkdir", PING_DIRECTORY])

    if not os.path.exists(PLOT_DIRECTORY):
        subprocess.run(["mkdir", PLOT_DIRECTORY])

    if not os.path.exists(IPERF_DIRECTORY):
        subprocess.Popen([ "mkdir", IPERF_DIRECTORY ] )
