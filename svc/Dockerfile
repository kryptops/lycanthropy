FROM ubuntu:18.04
RUN apt update && apt install -y python3 python3-pip openjdk-8-jdk gradle
RUN python3 -m pip install pyjwt sqlalchemy termcolor flask cryptography

#instantiate shared directory for the agent src code
#structure :
# /opt/service
# /opt/agent


WORKDIR /opt/svc

ENTRYPOINT python3 moonlight.py
