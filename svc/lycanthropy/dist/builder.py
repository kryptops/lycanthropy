#javac -cp ".:<find abspath for jar>;" mod.java
import os
import json
import time
import shutil
import base64
import random
import subprocess
import lycanthropy.crypto
import lycanthropy.auth.login
import lycanthropy.sql.agent

def mkAgent():
    legals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    final = ''
    for x in range(8):
        final += random.choice(legals)
    return final

def generateBuild(campaignName,campaignConfig):
    #make a build tasks item in the api
    buildConf = {
        'acid':mkAgent(),
        'ctrlKey':lycanthropy.crypto.mkRandom(12),
        'distKey':lycanthropy.crypto.mkRandom(12),
        'ccKey':base64.b64encode(os.urandom(32)).decode('utf-8'),
        'password':lycanthropy.crypto.mkRandom(12),
        'confKey':lycanthropy.crypto.mkRandom(12),
        'tempAcid':mkAgent(),
        'pkgCore':','.join(campaignConfig['core']),
        'regPass':lycanthropy.crypto.mkRandom(12),
        'regKey':lycanthropy.crypto.mkRandom(12),
        'tcKey':base64.b64encode(os.urandom(32)).decode('utf-8'),
        'status':'inactive'
    }
    return buildConf

def pareConfig(jsonConfig):
    domainConfig = json.load(
        open(
                '../etc/daemon.json',
                'r'
        )
    )
    domainName = domainConfig['domain']['name'].split('.')
    newConfig = {}
    newConfig['password'] = jsonConfig['regPass']
    newConfig['acid'] = jsonConfig['tempAcid']
    newConfig['ccKey'] = jsonConfig['tcKey']
    newConfig['regKey'] = jsonConfig['regKey']
    newConfig['jitterMin'] = '100'
    newConfig['jitterMax'] = '1000'
    newConfig['threadsMax'] = '4'
    newConfig['tld'] = domainName[2]
    newConfig['domain'] = domainName[1]
    newConfig['subDomain'] = domainName[0]
    return newConfig


def stageBuild(jsonConfig,campaign):
    buildDirs = os.listdir('campaign/{}/build'.format(campaign))
    buildSet = []
    if len(buildDirs) > 0:
        for subDir in buildDirs:
            buildSet.append(int(subDir))
        buildLatest = max(buildSet)
        buildNew = buildLatest + 1
    else:
        buildNew = 1
    finalDir = 'campaign/{}/build/{}'.format(campaign,str(buildNew))
    os.mkdir(finalDir)
    os.mkdir('{}/resources'.format(finalDir))
    configHandle = open('{}/resources/config.json'.format(finalDir),'w')
    print(pareConfig(jsonConfig))
    json.dump(
        pareConfig(jsonConfig),
        configHandle,
        indent=4
    )
    configHandle.close()
    return buildNew,finalDir

def storeBuild(jsonConfig,campaign):
    hashSalt = lycanthropy.crypto.mkRandom(32)
    lycanthropy.sql.agent.storeBuild(
        jsonConfig['acid'],
        jsonConfig['ctrlKey'],
        jsonConfig['distKey'],
        jsonConfig['ccKey'],
        jsonConfig['password'],
        jsonConfig['confKey'],
        jsonConfig['tempAcid'],
        jsonConfig['pkgCore'],
        '{}.{}'.format(hashSalt,
                       lycanthropy.auth.login.genhash(
                           jsonConfig['regPass'],
                           hashSalt
                       )
                       ),
        jsonConfig['regKey'],
        jsonConfig['tcKey'],
        campaign
    )

def runBuild(finalDir):
    cmdLine = 'cd ../agent && gradle clean build -PrscDirPath=../svc/{}/resources -PbuildDir=../svc/{}/final'.format(finalDir,finalDir)
    subprocess.Popen(['/bin/bash','-c',cmdLine])
    print(cmdLine)
    return {'status':'initialized'}

def buildMod(modClass,javaHome,campaign):
    #javahome will be defined at install
    #a gradle build will run at install as well to make sure the jar is there
    buildPath = os.getcwd()
    os.popen("{}/javac -cp {}/dist/refClassPath/libs/buildstub-0.1.jar -d campaign/{}/dist/ {}/dist/src/{}.java".format(javaHome,buildPath,campaign,buildPath,modClass))

def buildAgent(buildKey,buildID):
    #gradle build -PsourceSets.resources.srcDir=<finalDir> -PbuildDir=<finalDir>
    build = {}
    for campaign in os.listdir('campaign'):
        campaignConfig = json.load(
            open(
                'campaign/{}/config.json'.format(campaign),
                'r'
            )
        )
        if buildID == campaignConfig['buildID']:
            if buildKey in campaignConfig['keys']:
                build = generateBuild(campaign,campaignConfig)
                storeBuild(build,campaign)
                buildNum,buildDir = stageBuild(build,campaign)
                runBuild(buildDir)
                return {'buildNum':str(buildNum)}
            else:
                return {'error':'invalid build key'}
    return {'error':'could not find buildID'}

def listBuilds(buildKey,buildID):
    buildApi = {'instructions':"specify id for build in 'buildID' url parameter to download",'finished':[],'queued':[]}
    for campaign in os.listdir('campaign'):
        campaignConfig = json.load(
            open(
                'campaign/{}/config.json'.format(campaign),
                'r'
            )
        )
        if buildID == campaignConfig['buildID']:
            if buildKey in campaignConfig['keys']:
                targetDir = 'campaign/{}/build'.format(campaign)
                for subDir in os.listdir(targetDir):
                    if 'final' in os.listdir('{}/{}'.format(targetDir,subDir)):
                        buildApi['finished'].append(subDir)
                    else:
                        buildApi['queued'].append(subDir)
                return buildApi
            else:
                return {'error':'invalid build key'}
    return {'error':'could not find buildID'}

def chkBuildAccess(buildKey,buildID,campaign):
        campaignConfig = json.load(
            open(
                'campaign/{}/config.json'.format(campaign),
                'r'
            )
        )
        if buildID == campaignConfig['buildID']:
            if buildKey in campaignConfig['keys']:
                return campaignConfig
        return {'error':'not in campaign'}


def retrieveBuilds(buildKey,buildID,target):
    for campaign in os.listdir('campaign'):
        campaignConfig = chkBuildAccess(buildKey, buildID,campaign)
        if 'error' not in campaignConfig:
            targetDir = 'campaign/{}/build/{}'.format(campaign,target)
            if 'final' in os.listdir(targetDir):
                return '{}/final/libs'.format(targetDir)
            else:
                return {'error':'build is not available for retrieval'}
    return {'error':'unable to process request'}

def destroyBuild(path):
    time.sleep(10)
    splinterPath = path.split('/')
    truePath = splinterPath[:-2]
    shutil.rmtree('/'.join(truePath))