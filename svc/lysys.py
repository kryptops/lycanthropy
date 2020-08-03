import threading
import subprocess
import ns_daemon
import time

#instantiate dns daemon thread
daemonThread = threading.Thread(target=ns_daemon.runServer,args=('127.0.0.1',))

#create https api process
subprocess.Popen(['/bin/bash','-c','python3 portal.py'])

#wait to start ns_daemon
time.sleep(2)

#start ns_daemon thread
daemonThread.start()
