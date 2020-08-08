FROM ubuntu:18.04
RUN apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle

#instantiate shared directory for the agent src code
#structure :
# /opt/lycanthropy/<build server goes here>
# /opt/lycanthropy/src/<agent root dir goes here>
# /opt/lycanthropy/build/<campain>/<buildnumber>/<buildstub>


WORKDIR /opt/lycanthropy

python3 build.py
