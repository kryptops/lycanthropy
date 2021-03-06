RAND=`python3 -c "import random;x=[];[x.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%*^')) for i in range(23)];print(''.join(x))"`

if ! which netstat; then
  apt install net-tools
fi

echo -e "\e[92mINSTALLING SYSTEM DEPENDENCIES\e[0m"
apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle libmysqlclient-dev xterm docker.io
if ! service --status-all | grep -Fq 'mysql'; then
  apt install -y mariadb-server
fi

echo -e "\e[92mINSTALLING PIP DEPENDENCIES\e[0m"
python3 -m pip install -r svc/requirements.txt
cd svc
LOCALADDR=`python3 -c "import lycanthropy.daemon.util;print(lycanthropy.daemon.util.getAddr())"`
cd ..

echo -e "\e[92mCOMPILING REFERENCE JAR\e[0m"
cd agent
gradle clean build -PrscDirPath=src/resources -PbuildDir=../svc/dist/refClassPath
cd ..

echo -e "\e[92mPERFORMING DOCKER SETUP\e[0m"
cd svc
if ! service docker status | grep '\(running\)'; then
  service docker start
fi
docker build -t moonlightsrv - < moonlight.docker
cd ..

echo -e "\e[92mTHE ROOT PASSWORD FOR THE DATABASE SERVER WILL BE RESET\e[0m"
echo -e "\e[92mNEW PASSWORD FOLLOWS :\e[0m $RAND"
echo -e "\e[92mSLEEPING SO YOU CAN COPY IT\e[0m"
sleep 10

echo -e "\e[92mPERFORMING DATABASE SETUP\e[0m"
cd svc
service mysql stop
if ! cat /etc/mysql/my.cnf | grep '\[mysqld\]'; then
  echo "[mysqld]" >> /etc/mysql/my.cnf
  echo "    bind-address = 0.0.0.0" >> /etc/mysql/my.cnf
fi
echo `echo $LOCALADDR` >> ../etc/sqladdr.cnf
service mysql start
python3 dbsetup.py $RAND
service mysql stop
if ! cat /etc/mysql/my.cnf | grep '\[mysqld\]'; then
  echo "    wait_timeout = 60" >> /etc/mysql/my.cnf
fi
service mysql start
cd ..

echo -e "\e[92mCONFIGURING NS DAEMON\e[0m"
cd svc
python3 daemonsetup.py
cd ..

echo -e "\e[92mSPOOLING BUILD SERVER\e[0m"
cd svc

docker run --name moonlightsrv -v `pwd`/..:/opt -p 56111:56111 -d=true --rm moonlightsrv
cd ..

if netstat -antup | grep 53; then
  echo -e "\e[31m    WARNING!!!\e[0m"
  echo -e "\e[31m    THERE IS A SERVICE RUNNING ON :53. PLEASE HALT THIS SERVICE BEFORE STARTING THE LYCANTHROPY SERVER.\e[0m"
  sleep 2
fi

if cat /etc/resolv.conf | grep 127.0.0; then
  echo -e "\e[31m    WARNING!!!\e[0m"
  echo -e "\e[31m    THERE IS A POINTER TO LOCALHOST IN /etc/resolv.conf. THIS MUST BE CHANGED FOR THE NS_DAEMON TO FUNCTION.\e[0m"
  sleep 2
fi

