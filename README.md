# A Mininet & IPerf3 Networking Performance Testing Project

## Testing the impact of bottlenecks on networking performance.<br>

### **Author** : Jonathan Boyd



This project utilizes IPerf3 and Mininet to explore the impacts of a potential bottleneck link in a network. The network testing comprises of a four host two switch topology. Via the command line, or module access, an individual may maniplulate the configured bandwidth between two switches on the network, in order to observe the impact of throughput with respect to tcp and udp communications. For the sake of fulfilling requirements of the university assignment associated with this project, accessory ping and ifconfig information is also retrieved in an effort to confirm connectivity. These files may be stored in locations as specified in the files.<br><br>
### The current instance implements a system of directory naming which allows for manipulation of save locations in a single location... (see <code>configure.py</code>)

### Running this project will require the user to properly install mininet and iperf3 for Python3. Various issues may arrise if the necessary components are not installed and utilized in a virtual environment, or if the necessary components are not installed for Python3 system-wide.
 
### Credits<br>
Thanks extended to the providers of documentation for mininet and iperf3, the authors of the mainstream mininet and openflow walkthrough, and the authors of documentation for iperf python bindings.<br>
### Run guide
<p>
To run the main testing module (<code>analyze-perf.py</code>) there are two options...
<ol>
    <li><code>python3 analyze-perf.py -time {duration of iperf tests (sec)} -constraints {bottleneck bandwidths to test}</code></li>
    <li><code>python3 analyze-perf.py</code> : defaults (<code>time=5</code>) (<code>constraints="8 32 64"</code>)</li>
</ol>
This module will utilize all .py modules in the repository... DO NOT MOVE .PY FILES TO SEPARATE DIRECTORIES.<br> 
Test results must be relocated after running the program if multiple instances are to be executed... RESULTS WILL BE OVERWRITTEN UPON EACH EXECUTION OF <code>analyze-perf.py</code> or <code>network_bottleneck.py</code>.<br>
The modules <code>server.py</code> and <code>client.py</code> may be utilized in isolation from the testing modules. <em>(The testing modules may also be run independently...)</em><br>
</p><br>

### constraints argument format : <code>string</code> "%d %d %d %d" <- values (bottleneck bandwidths (Mbps)) separated by spaces.
<p><em>constraints are measured in reference to a static 100 Mbps natural link bandwidth for non-bottlenecked ports. Because of the static natural link bandwidth of 100 Mbps, the constraints should remain below 100 Mbps. Anything equal to, or above, 100 Mbps will result in an assertion failure.</em></p><br>

## See below for instructions on running the <code>server.py</code> and the <code>client.py</code> modules.
<p><em>The <code>client.py</code> and the <code>server.py</code> module can be utilized independently to confirm connection in an environment isolated from mininet. To run these modules...
<ol>
    <li>Run <code>server.py</code>... illustration : <code>server.py -ip {server_ip_addr} -port {service_port}</code></li>
    <li>Run <code>client.py</code>...<strong>FAILURE TO SPECIFY TIME RESULTS IN 60 SECOND TEST... illustration: <code>client.py -ip {client} -port {} -server_ip {server} -test {'tcp' or 'udp'}-time {seconds}</code></li>
</ol></em><br></p>

##### notes (@jonboyd)
###### BUG REPORT
<p>There are known bugs within the try..except blocks that arise in the midst of unsuspected termination (i.e., KeyboardInterrupt). This can be observed in the log files, as the remaining chain of attempts run regardless of the interruption, producing a sequence of logged failed attempts. There are potentially more try..except blocks than necessary... for this, apologies are extended.</p><br>
