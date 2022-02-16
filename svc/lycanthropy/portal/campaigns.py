import lycanthropy.portal.api
import lycanthropy.sql.interface
import lycanthropy.sql.server
import lycanthropy.dist.builder
import lycanthropy.crypto
import json
import secrets
import os
import shutil
import time
import crypt
import subprocess

class util():
    def generateCampaignName(self):
        names = json.load(
            open(
                '../etc/names.json',
                'r'
            )
        )
        while True:
            prefix = names['prefix'][secrets.randbelow(len(names['prefix']))]
            suffix = names['suffix'][secrets.randbelow(len(names['suffix']))]
            candidate = prefix+suffix
            if candidate not in os.listdir('campaign'):
                return candidate
            else:
                continue

    def writeConfig(self,root,config):
        fObj = open('{}/config.json'.format(root),'w')
        json.dump(
            config,
            fObj,
            indent=4
        )
        fObj.close()

def getName(nameField,context):
    legals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-'
    if nameField != '':
        if type(nameField) == str:
            for character in nameField.upper():
                if character not in legals:
                    return {'error':'campaign names may only contain alphanumeric character, underscores, and dashes'}

            return nameField
    else:
        return util().generateCampaignName()

def getCore(coreField,context):

    fullCore = []
    requestedCore = coreField.split(',')
    manifest = json.load(
        open(
            '../etc/dist/manifest.json'
        )
    )
    for package in manifest:
        if package in requestedCore or manifest[package]['default'] == 'True':
            fullCore.append(manifest[package]['id'])
    return fullCore

def mkTree(campaignObject):
    root = 'campaign/{}'.format(campaignObject['moniker'])
    dirTree = [
        'dist',
        'docroot',
        'report',
        'warehouse',
        'build'
    ]
    os.mkdir(root)
    for subDirectory in dirTree:
        os.mkdir('{}/{}'.format(root,subDirectory))
    util().writeConfig(root,campaignObject)


def updateAccess(accessObject,nameObject,context):
    operators = accessObject.split(',')
    accessReturns = []
    for operator in operators:

        try:
            userData = lycanthropy.sql.interface.filterUser({'username':operator})[0]
        except:
            accessReturns.append({'error':'could not resolve user {}'.format(operator)})
        if len(userData['campaigns']) > 1:
            campaigns = userData['campaigns'].split(',')
            campaigns.append(nameObject)
        else:
            campaigns = [nameObject]
        updateAccess = lycanthropy.sql.server.updateAccess(operator,','.join(campaigns))
        accessReturns.append(updateAccess)
    return accessReturns

def buildPackages(campaignObject):
    pkgManifest = lycanthropy.dist.inventory.getManifest()
    config = json.load(
        open(
            '../etc/app.json',
            'r'
        )
    )
    for javaClass in os.listdir('dist/src'):
        lycanthropy.dist.builder.buildMod(
            javaClass.split('.')[0],
            config['javahome'],
            campaignObject['moniker']
        )

def mkServiceAccount(name):
    svcAccountPass = lycanthropy.crypto.mkRandom(14)
    encPass = crypt.crypt(svcAccountPass,"22")
    lyPath = os.getcwd()
    subprocess.Popen(["useradd","-p",encPass,"-d","{}/campaign/{}".format(lyPath,name),name])
    return svcAccountPass

def mkCampaign(arguments,context):
    if 'campaign' not in os.listdir('.'):
        os.mkdir('./campaign')
    errors = []
    campaign = {}
    campaign['moniker'] = getName(arguments['name'],context)
    campaign['core'] = getCore(arguments['core'],context)
    campaign['keys'] = [
        lycanthropy.crypto.mkRandom(8),
        lycanthropy.crypto.mkRandom(8),
        lycanthropy.crypto.mkRandom(8),
        lycanthropy.crypto.mkRandom(8),
        lycanthropy.crypto.mkRandom(8)
    ]
    campaign['buildID'] = lycanthropy.crypto.mkRandom(10)

    mkTree(campaign)
    buildPackages(campaign)

    svcPass = mkServiceAccount(campaign['moniker'])

    for accessStatus in updateAccess(arguments['operators'],campaign['moniker'],context):
        if 'error' in accessStatus:
            errors.append(accessStatus)
    return {
        'name':campaign['moniker'],
        'ftpuser':campaign['moniker'],
        'ftppass':svcPass,
        'state':'deployed',
        'errors':errors
    }

def rmCampaign(arguments,context):
    errors = []
    shutil.rmtree('campaign/{}'.format(arguments['name']))
    users = lycanthropy.sql.interface.filterUser({})
    for user in users:
        userCampaigns = user['campaigns'].split(',')
        if arguments['name'] in userCampaigns:
            userCampaigns.pop(userCampaigns.index(arguments['name']))

            updateAccess = lycanthropy.sql.server.updateAccess(user['username'],','.join(userCampaigns))
            if 'error' in updateAccess:
                errors.append(updateAccess)
    return {
        'name':arguments['name'],
        'state':'removed',
        'errors':errors
    }

