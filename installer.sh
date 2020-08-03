echo "INSTALLING SYSTEM DEPENDENCIES"
apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle libmysqlclient-dev xterm
if ! service --status-all | grep -Fq 'mysql'; then
  apt install -y mariadb-server
fi

echo "INSTALLING PIP DEPENDENCIES"
python3 -m pip install -r requirements.txt

echo "COMPILING REFERENCE JAR"
cd agent
gradle clean build -PrscDirPath=src/resources -PbuildDir=../svc/dist/refClassPath
cd ..

echo "PERFORMING DATABASE SETUP"
cd svc
python3 dbsetup.py
cd ..

echo "CONFIGURING NS DAEMON"
cd svc
python3 daemonsetup.py
cd ..
