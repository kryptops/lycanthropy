RAND=`python3 -c "import random;x=[];[x.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%*^')) for i in range(23)];print(''.join(x))"`

echo "INSTALLING SYSTEM DEPENDENCIES"
apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle libmysqlclient-dev xterm docker.io
if ! service --status-all | grep -Fq 'mysql'; then
  apt install -y mariadb-server
fi

echo "INSTALLING PIP DEPENDENCIES"
python3 -m pip install -r svc/requirements.txt

echo "COMPILING REFERENCE JAR"
cd agent
gradle clean build -PrscDirPath=src/resources -PbuildDir=../svc/dist/refClassPath
cd ..

echo "PERFORMING DOCKER SETUP"
cd svc
if ! service docker status | grep '\(running\)'; then
  service docker start
fi
docker pull mariadb
docker build -t moonlightsrv - < moonlight.docker
docker build -t squall - < sql.docker
cd ..

echo "PERFORMING DATABASE SETUP"
cd svc
docker run --name squall -p 30306:3306 -e MYSQL_ROOT_PASSWORD=`echo $RAND` -d=true --rm squall 
python3 dbsetup.py $RAND
cd ..

echo "CONFIGURING NS DAEMON"
cd svc
python3 daemonsetup.py
cd ..

echo "SPOOLING BUILD SERVER"
cd svc

docker run --name moonlightsrv -v `pwd`:/opt/svc -v `pwd`/../agent:/opt/agent -p 56111:56111 -d=true moonlightsrv
cd ..
