RAND=`python3 -c "import random;x=[];[x.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%*^')) for i in range(23)];print(''.join(x))"`
cd svc
LOCALADDR=`python3 -c "import lycanthropy.daemon.util;print(lycanthropy.daemon.util.getAddr())"`
cd ..

echo -e "\e[92mINSTALLING SYSTEM DEPENDENCIES\e[0m"
apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle libmysqlclient-dev xterm docker.io
if ! service --status-all | grep -Fq 'mysql'; then
  apt install -y mariadb-server
fi

echo -e "\e[92mINSTALLING PIP DEPENDENCIES\e[0m"
python3 -m pip install -r svc/requirements.txt

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

echo -e "\e[92mPERFORMING DATABASE SETUP\e[0m"
cd svc
if ! cat /etc/mysql/my.cnf | grep '[mysqld]'; then
  echo "[mysqld]" >> /etc/mysql/my.cnf
  echo "    bind-address = 0.0.0.0" >> /etc/mysql/my.cnf
fi
echo `echo $LOCALADDR` >> ../etc/sqladdr
service mysql start
python3 dbsetup.py $RAND
cd ..

echo -e "\e[92mCONFIGURING NS DAEMON\e[0m"
cd svc
python3 daemonsetup.py
cd ..

echo -e "\e[92mSPOOLING BUILD SERVER\e[0m"
cd svc

docker run --name moonlightsrv -v `pwd`/..:/opt -p 56111:56111 -d=true --rm moonlightsrv
cd ..
