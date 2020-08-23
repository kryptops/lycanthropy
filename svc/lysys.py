import threading
import subprocess
import ns_daemon
import psutil
import time
import json
from termcolor import colored
import sys
import time


for sock in psutil.net_connections():
    if sock.laddr.port == 53:
        print(colored("error : ","red",attrs=['bold']),colored("a service is running on port 53 - deactivate the service to proceed","red"))
        sys.exit()

#instantiate dns daemon thread
print(colored("STARTING THREADED DNS SERVER ... ","RED"))
daemonThread = threading.Thread(target=ns_daemon.runServer,args=('127.0.0.1',))

#create https api process
print(colored("STARTING API AS SUBPROCESSES ... ","RED"))
subprocess.Popen(['/bin/bash','-c','python3 portal.py'])

#wait to start ns_daemon
time.sleep(2)

#start ns_daemon thread
daemonThread.start()
