import threading
import subprocess
import ns_daemon
import psutil
import time
import json
from termcolor import colored
import sys
import time
import docker




for sock in psutil.net_connections():
    if sock.laddr.port == 53:
        print(colored("error : ","red",attrs=['bold']),colored("a service is running on port 53 - deactivate the service to proceed","red"))
        sys.exit()


#instantiate dns daemon thread
print(colored("STARTING THREADED DNS SERVER ... ","red"))
daemonThread = threading.Thread(target=ns_daemon.runServer,args=('127.0.0.1',))

#create https api process
print(colored("STARTING API AS SUBPROCESSES ... ","red"))
subprocess.Popen(['/bin/bash','-c','python3 portal.py'])

dockerClient = docker.from_env()
dockerPS = dockerClient.containers.list()
finalCount = 0
for running in dockerPS:
    if running.attrs['Config']['Image'] == 'moonlightsrv':
        print(colored("BUILD SERVER IS ALREADY RUNNING","green"))
        finalCount += 1

if finalCount == 0:
    print(colored("STARTING DOCKERIZED BUILD SERVER ... ","red"))
    subprocess.Popen(['/bin/bash','-c','docker run --name moonlightsrv -v `pwd`/..:/opt -p 56111:56111 -d=true --rm moonlightsrv'])

#wait to start ns_daemon
time.sleep(2)

#start ns_daemon thread
daemonThread.start()
