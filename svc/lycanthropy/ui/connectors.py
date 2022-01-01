import requests
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from datetime import datetime
import lycanthropy.ui.webClient
import lycanthropy.ui.directiveProcessor
import lycanthropy.ui.graphic
import json
import threading
from flask import Flask,request,abort,make_response,jsonify

app = Flask(__name__)

class sessionManager():
    def __init__(self):
        self.username = ""
        self.password = ""
        self.token = ""
        self.api=""
        self.form={}

class wolfmonVault():
    def __init__(self):
        self._running = False

    def instantiateVault(self,sessionData,handles):
        self.username = sessionData.username
        self.password = sessionData.password
        self.api = sessionData.api
        self.token = sessionData.wolf['token']
        self.identity = sessionData.wolf['id']
        self.campaigns = retrieveCampaignPartitions()
        self.builds = retrieveCampaignBuilds()
        self.agents = retrieveCampaignAgents()
        self.handles = handles
        self.sessionHandle = sessionData
        self.formConfigs = getFormConfigs()
        self.subscriptions = [{'filter':{},'stream':'portal','temp':'false'}]
        self._running = True

def initWolfmon(sessionData,handles):
    global wolfObjInstance
    wolfObjInstance = wolfmonVault()
    threading.Thread(target=app.run,kwargs=({'host':'127.0.0.1', 'port':56091, 'ssl_context':'adhoc','debug':False})).start()
    wolfObjInstance.instantiateVault(sessionData,handles)

@app.errorhandler(403)
def forbidden(e):
    return(make_response(jsonify({'403':'forbidden'})))

@app.route('/wolfmon/api/shutdown', methods=['POST'])
def shutdownApi():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    try:
        loginData = request.json
    except:
        abort(400)
    if loginData['username'] == wolfObjInstance.username and loginData['password'] == wolfObjInstance.password:
        wolfObjInstance._running = False
        print("attempting shutdown")
        request.environ['werkzeug.server.shutdown']()
        return {'200': 'ok'}
    else:
        abort(403)

@app.route('/wolfmon/api/subscriptions', methods=['POST'])
def updateSubscriptions():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    try:
        subscriptionData = request.json
    except:
        abort(400)
    wolfObjInstance.subscriptions.append(subscriptionData)
    print(wolfObjInstance.subscriptions)
    return make_response(jsonify({'200': 'ok'}), 200)

@app.route('/wolfmon/api/formconfig/<viewSet>', methods=['GET'])
def retrieveForms(viewSet):
    if request.remote_addr != '127.0.0.1':
        abort(403)
    return make_response(jsonify(wolfObjInstance.formConfigs[viewSet]))
    #return wolfObjInstance.formConfigs

@app.route('/wolfmon/api/directiveforms/<viewSet>/<directive>')
def directiveForms(viewSet,directive):
    if request.remote_addr != '127.0.0.1':
        abort(403)

    formOut = lycanthropy.ui.directiveProcessor.process(
        "load {}".format(directive),
        viewSet,
        wolfObjInstance.sessionHandle
    )
    return make_response(jsonify(formOut[1].form))

@app.route('/wolfmon/api/monitoring/initiateThread', methods=['GET'])
def startMonitorThread():
    enterMonitorLoop()
    return 200


def getView(rawOutput):
    #code to parse json module configs goes here
    #parses configs, check for module / view to push output towards
    outSplit = rawOutput["output"]["class"]
    return outSplit

def getFormConfigs():
    configSet = {}
    for viewConfig in ['control','windows','posix','manage']:
        viewForm = json.loads(lycanthropy.ui.directiveProcessor.process(
            'help',
            viewConfig,
            wolfObjInstance.sessionHandle
        )[0][0])

        configSet[viewConfig] = viewForm
        lycanthropy.ui.graphic.TabLayout().updateInterface(wolfObjInstance.handles[viewConfig],viewConfig,viewForm,wolfObjInstance.sessionHandle)
        #viewHandle = wolfObjInstance.handles[viewConfig]
        #viewHandle.appendPlainText(json.dumps(viewForm))

    return configSet


def retrieveCampaignBuilds():
    #pull database objects at the start
    builds = lycanthropy.ui.webClient.getObj(
        {
            'api': wolfObjInstance.api,
            'username': wolfObjInstance.username,
            'token': wolfObjInstance.token,
            'identity': wolfObjInstance.identity,
            'obj':'builds'
        }
    )
    buildSet = json.loads(builds.content.decode('utf-8'))

    return buildSet['builds']

def retrieveCampaignAgents():
    #pull database objects at the start
    agents = lycanthropy.ui.webClient.getObj(
        {
            'api': wolfObjInstance.api,
            'username': wolfObjInstance.username,
            'token': wolfObjInstance.token,
            'identity': wolfObjInstance.identity,
            'obj':'agents'
        }
    )
    agentSet = json.loads(agents.content.decode('utf-8'))

    return agentSet['agents']

def retrieveCampaignPartitions():
    campaigns = lycanthropy.ui.webClient.getObj(
        {
            'api':wolfObjInstance.api,
            'username':wolfObjInstance.username,
            'token':wolfObjInstance.token,
            'identity':wolfObjInstance.identity,
            'obj':'campaigns'
        }
    )
    campaignSet = json.loads(campaigns.content.decode('utf-8'))

    return campaignSet['partitions']

def parseAgents(cmpAgents):
    strAgent = []
    for agent in cmpAgents:
        acidField = "{}{}".format(agent['acid'],"   ")
        campaignField = "{}{}".format(agent['campaign']," "*(16-len(agent['campaign'])))
        osField = "{}[{}]{}".format(agent['os'],agent['arch']," "*(36-(len(agent['os'])+5)))
        userField = "{}{}".format(agent['user']," "*(23-len(agent['user'])))
        intField = "{}{}".format(agent['integrity']," "*(12-len(agent['integrity'])))
        hostField = "{}".format(agent['hostname'])

        agentFmt = "{}{}{}{}{}{}".format(acidField,campaignField,osField,userField,intField,hostField)
        strAgent.append(agentFmt)
    return strAgent

def enterMonitorLoop():
    outHandle = wolfObjInstance.handles['wolfmon'].wolfmon
    cmpAgents = retrieveCampaignAgents()
    strAgent = parseAgents(cmpAgents)
    for fmtAgent in strAgent:
        outHandle.appendPlainText(fmtAgent)
    retrieveMonitorLogs()

def retrieveMonitorLogs():
    print("entering loop")
    while True:
        if wolfObjInstance._running == False:
            print("breaking loop")
            break

        monitorSession = {
            'subscriptions': wolfObjInstance.subscriptions,
            'api': wolfObjInstance.api,
            'token': wolfObjInstance.token,
            'identity': wolfObjInstance.identity,
            'username': wolfObjInstance.username
        }

        monitorStream = lycanthropy.ui.webClient.monitorApiBroker(monitorSession)
        #print(monitorStream)
        if monitorStream.status_code == 401:
            wolfObjInstance.token,wolfObjInstance.identity = lycanthropy.ui.webClient.authWolfmon({
                'username':wolfObjInstance.username,
                'password':wolfObjInstance.password,
                'api':wolfObjInstance.api
            })
        monitorOut = json.loads(monitorStream.content.decode('utf-8'))
        print("monitor: {}".format(monitorOut))
        #need to add a step to push additional subscriptions
        for match in monitorOut:
            if len(match) > 1:
                match['output'].pop('tags')
                try:
                    parsedOutput = json.loads(match['output']['output'])
                    match['output']['output'] = parsedOutput
                except:
                    pass

                if match['stream'] == 'portal':
                    wolfObjInstance.handles["alerts"].insertPlainText("[ {} ]: {} ".format(match['output']['timestamp'],match['output']['alert']))
                    wolfObjInstance.handles["alerts"].insertPlainText('\n')
                    #this will eventually go to the alertDataBox

                elif 'SEJID' in match['output']['jobID']:
                    getHandle = wolfObjInstance.handles['shell']
                    getHandle.output.insertPlainText('[ {} ]'.format(datetime.now().strftime("%m/%d/%Y - %H:%M:%S")))
                    getHandle.output.insertPlainText('\n')
                    getHandle.output.insertPlainText(match['output']['output'])
                    getHandle.output.insertPlainText('\n')

                    shellMeta = getHandle.shellMeta
                    if match['output']['acid'] not in shellMeta.toPlainText():
                        acidMeta = retrieveCampaignAgents()
                        finalMeta = ""
                        for objMeta in acidMeta:
                            if objMeta['acid'] == match['output']['acid']:
                                finalMeta = objMeta
                        shellMeta.clear()
                        shellMeta.insertPlainText("[ Agent Metadata ]")
                        shellMeta.insertPlainText("\n")
                        shellMeta.insertPlainText("------------------------------------------------------")
                        shellMeta.insertPlainText("\n")
                        shellMeta.insertPlainText(json.dumps(finalMeta,indent=4))

                else:

                    view = getView(match)
                    if view != 'metadata':
                        getHandle = wolfObjInstance.handles[view]
                #print(json.dumps(match['output'],indent=4).replace('\\n','\n').replace('\\r','\r'))

                        getHandle.output.insertPlainText(json.dumps(match['output'],indent=4).replace('\\n','\n').replace('\\r','\r'))


class ui():
    def authenticate(self,user,password):
        session = sessionManager()

        if '@' not in user:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("Error! User ID is not in the correct format. Re-enter username in correct format and try again")
            msg.setWindowTitle("Invalid Username")
            msg.setDetailedText("The Lycanthropy UI needs the IP of your server to log you in, provided in the format <username>@<ip>. If you have not yet set up the server for lycanthropy, you will be unable to use the application.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            msg.exec()
            return False,None
        # make sure exit invalidates the token
        userid, gateway = user.split('@')
        try:
            authToken = lycanthropy.ui.webClient.sendAuth(userid, password, gateway).decode('utf-8')
            wolfToken, wolfId = lycanthropy.ui.webClient.authWolfmon({
                'username':userid,
                'password':password,
                'api':gateway
            })
        except (requests.exceptions.ConnectionError):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Error! Server failed to respond to authentication attempt!")
            msg.setWindowTitle("Connection Error")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            msg.exec()
            return False,None

        session.username = userid
        session.password = password
        session.wolf = {"id":wolfId,"token":wolfToken}
        session.api = gateway
        if not ('error') in authToken:
            session.token = authToken
            return True,session
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("Error! Server rejected authentication attempt!")
            msg.setWindowTitle("Authentication Error")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            msg.exec()
            return False,None


class console():
    def __init__(self):
        pass

class control():
    def __init__(self):
        pass
