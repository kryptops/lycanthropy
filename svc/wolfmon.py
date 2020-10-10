import sys
import logging
import threading
import lycanthropy.ui.webClient
import time
import json
from termcolor import colored
from flask import Flask,request,abort,make_response,jsonify

#ditch the welcome mat
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *X : None

app = Flask(__name__)
#suppress logging messages
lumberjack = logging.getLogger('werkzeug')
lumberjack.setLevel(logging.ERROR)

@app.errorhandler(403)
def accessDenied(e):
    return make_response(jsonify({'error':'forbidden'}),403)

@app.errorhandler(400)
def badRequest(e):
    return make_response(jsonify({'error':'bad request'}),400)



class ui():
    def __init__(self):
        self._running = False

    def startMonitorThread(self,sessionData):
        self.username = sessionData['username']
        self.password = sessionData['password']
        self.api = sessionData['api']
        self.token = sessionData['token']
        self.identity = sessionData['identity']
        self.campaigns = self.retrieveCampaignPartitions()
        self.builds = self.retrieveCampaignBuilds()
        self._running = True
        self.agents = self.retrieveCampaignAgents()


        self.enterMonitorLoop()

    def retrieveCampaignBuilds(self):
        #pull database objects at the start
        builds = lycanthropy.ui.webClient.getObj(
            {
                'api': self.api,
                'username': self.username,
                'token': self.token,
                'identity': self.identity,
                'obj':'builds'
            }
        )
        buildSet = json.loads(builds.content.decode('utf-8'))

        return buildSet['builds']

    def retrieveCampaignAgents(self):
        #pull database objects at the start
        agents = lycanthropy.ui.webClient.getObj(
            {
                'api': self.api,
                'username': self.username,
                'token': self.token,
                'identity': self.identity,
                'obj':'agents'
            }
        )
        agentSet = json.loads(agents.content.decode('utf-8'))

        return agentSet['agents']

    def retrieveCampaignPartitions(self):
        campaigns = lycanthropy.ui.webClient.getObj(
            {
                'api':self.api,
                'username':self.username,
                'token':self.token,
                'identity':self.identity,
                'obj':'campaigns'
            }
        )
        campaignSet = json.loads(campaigns.content.decode('utf-8'))

        return campaignSet['partitions']

    def listCampaigns(self):
        print(
            colored(' :  ', 'red') + colored(
                'LISTING ACTIVE CAMPAIGN PARTITIONS ... ',
                'yellow'
            )
        )
        for campaign in self.campaigns:
            print(
                colored('    > ', 'red') + colored(
                    campaign.upper(),
                    'yellow'
                )
            )
        print('')

    def listAgents(self):
        print(
            colored(' :  ', 'red') + colored(
                'LISTING AGENT STATUS ... ',
                'yellow'
            )
        )
        for agent in self.builds:
            for meta in self.agents:
                if agent['acid'] in meta:
                    print(
                        colored('    > ', 'red') + colored(
                            '{} IS {}'.format(agent['acid'],meta['status']),
                            'yellow'
                        )
                    )
            print(
                colored('    > ', 'red') + colored(
                    '{} IS {}'.format(agent['acid'], 'AWAITING INITIALIZATION ... '),
                    'yellow'
                )
            )

    def enterMonitorLoop(self):
        self.listCampaigns()
        self.listCampaigns()
        self.listAgents()
        self.retrieveMonitorLogs()

    def retrieveMonitorLogs(self):
        while True:
            if not wolf._running:
                break
            subscriptions = wolf.subscriptions

            monitorSession = {
                'subscriptions': subscriptions,
                'api': self.api,
                'token': self.token,
                'identity': self.identity,
                'username': self.username
            }

            monitorStream = lycanthropy.ui.webClient.monitorApiBroker(monitorSession)
            if monitorStream.status_code == 401:
                self.token,self.identity = lycanthropy.ui.webClient.authWolfmon({
                    'username':self.username,
                    'password':self.password,
                    'api':self.api
                })
            monitorOut = json.loads(monitorStream.content.decode('utf-8'))
            #need to add a step to push additional subscriptions
            for match in monitorOut:
                if len(match) > 1:
                    match['output'].pop('tags')
                    print(json.dumps(match['output'],indent=4).replace('\\n','\n').replace('\\r','\r'))






class wolfmon():
    def __init__(self):
        self.session = False
        self.subscriptions = [{'filter':{'field':'class','value':'metadata'},'stream':'data','temp':'false'}]
        self._running = True

    def begin(self,sessionData):
        self.tClass = ui()
        self.threader = threading.Thread(target=self.tClass.startMonitorThread,args=(sessionData,))
        self.threader.start()

    def subscribe(self,subscription):
        #a subscription is a reducer for a  map of a particular stream
        self.subscriptions.append(subscription)

    def credentialize(self,username,password):
        self.username = username
        self.password = password

    def prune(self):
        for sub in self.subscriptions:
            currentIdx = self.subscriptions.index(sub)
            if sub['temp'] == 'true':
                self.subscriptions.pop(currentIdx)

    def unsubscribe(self,subID):
        for sub in self.subscriptions:
            currentIdx = self.subscriptions.index(sub)
            if sub['id'] == subID:
                self.subscriptions.pop(currentIdx)

    def halt(self):
        print(
            colored(' :  ', 'red') + colored(
                'EXIT COMMAND RECEIVED ... ',
                'yellow'
            )
        )
        self.tClass.terminateLogging()
        self.threader.join()
        time.sleep(5)
        sys.exit()


@app.route('/wolfmon/api/subscriptions',methods=['POST'])
def updateSubscriptions():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    try:
        subscriptionData = request.json
    except:
        abort(400)
    wolf.subscribe(subscriptionData)
    return make_response(jsonify({'200':'ok'}),200)

@app.route('/wolfmon/api/credentials',methods=['POST'])
def startMonitor():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    if wolf.session != False:
        abort(403)
    sessionData = request.json


    print(
        colored(' :  ','red') + colored(
            'SESSION CREDENTIALS RECEIVED ... ',
            'yellow'
        )
    )
    print(
        colored(' :  ','red') + colored(
            'CONNECTING TO API ... ',
            'yellow'
        )
    )
    wolf.credentialize(sessionData['username'],sessionData['password'])
    token,identity = lycanthropy.ui.webClient.authWolfmon(sessionData)
    sessionData['token'] = token
    sessionData['identity'] = identity

    print(
        colored(' :  ','red') + colored(
            'ACCESSING MONITORING DATA ... ',
            'yellow'
        )
    )
    print('')
    wolf.begin(sessionData)
    return make_response(jsonify({'200':'ok'}),200)

@app.route('/wolfmon/api/shutdown',methods=['POST'])
def shutdownApi():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    try:
        loginData = request.json
    except:
        abort(400)
    if loginData['username'] == wolf.username and loginData['password'] == wolf.password:
        wolf._running = False
        request.environ['werkzeug.server.shutdown']()
        return {'200':'ok'}
    else:
        abort(403)

@app.route('/wolfmon/api/token',methods=['POST'])
def getShellToken():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    try:
        loginData = request.json
    except:
        abort(400)
    #add xoring
    if loginData['username'] == wolf.username and loginData['password'] == wolf.password:
        return {'token':wolf.tClass.token,'identity':wolf.tClass.identity}

def initialize():
    global wolf
    wolf = wolfmon()

if __name__ == "__main__":
    initialize()
    banner = open(
        'lycanthropy/ui/monitor.txt',
        'r'
    ).read()

    print(
        colored(
            banner,
            "green",
            attrs=['bold']
        )
    )
    print(
        colored(' :  ','red') + colored(
            'WAITING FOR USER TO LOGIN WITH LYTTY ... ',
            'yellow'
        )
    )
    app.run(host='127.0.0.1',port=56091,ssl_context='adhoc')
