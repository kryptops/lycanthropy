import requests
import urllib3
import json
import base64
import sys
import uuid
import lycanthropy.ui.util

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connectWolfmon(session):
    connector = requests.post(
        'https://127.0.0.1:56091/wolfmon/api/credentials',
        json={
            'username':session.username,
            'password':session.password,
            'api':session.api
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return connector

def deactivateWolfmon(username,password):
    requests.post(
        'https://127.0.0.1:56091/wolfmon/api/shutdown',
        json={
            'username': username,
            'password': password
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )

def mimicWolfmon(username,password):
    requests.post(
        'https://127.0.0.1:56091/wolfmon/api/token',
        json={
            'username': username,
            'password': password
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )

def authWolfmon(session):
    agentID = str(uuid.uuid4())
    authenticator = requests.post(
        'https://{}:56114/lycanthropy/data-handler/tokenizer?lycan={}'.format(session['api'],session['username']),
        json={
            'password': session['password'],
            'wolfmon': agentID
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return authenticator.content.decode('utf-8'),agentID

def subscribeWolfmon(subscription):
    subscriber = requests.post(
        'https://127.0.0.1:56091/wolfmon/api/subscriptions',
        json=subscription,
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return subscriber

def getObj(subscription):
    subscriber = requests.get(
        'https://{}:56114/lycanthropy/data-handler/2?__SOBJTYPE={}'.format(subscription['api'],subscription['obj']),

        cookies={
            'LYSESSID': subscription['token'],
            'APIUSER': base64.b64encode(
                subscription['username'].encode('utf-8')
            ).decode('utf-8'),
            '_wdmID': base64.b64encode(
                subscription['identity'].encode('utf-8')
            ).decode('utf-8')
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return subscriber


def monitorApiBroker(monitoringSession):
    monGet = requests.post(
        'https://{}:56114/lycanthropy/data-handler/0'.format(monitoringSession['api']),
        json={
            'subscriptions': monitoringSession['subscriptions']
        },
        cookies={
            'LYSESSID': monitoringSession['token'],
            'APIUSER': base64.b64encode(
                monitoringSession['username'].encode('utf-8')
            ).decode('utf-8'),
            '_wdmID': base64.b64encode(
                monitoringSession['identity'].encode('utf-8')
            ).decode('utf-8')
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return monGet

def directiveBroker(directive,context,session):
    dirPost = requests.post(
        'https://{}:56114/lycanthropy/ui-handler/{}/{}'.format(session.api,context,directive['cmd']),
        json=directive['args'],
        cookies={
            'LYSESSID':session.token,
            'APIUSER':base64.b64encode(
                session.username.encode('utf-8')
            ).decode('utf-8')
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return dirPost

def processResponse(rspObj):
    #parse output and context out of response
    jsonObj = json.loads(rspObj)
    if type(jsonObj['output']) == dict:
        #if it can be parsed to json
        return json.dumps(jsonObj['output'],indent=4),jsonObj['context'],None
    else:
        return jsonObj.get('output'),jsonObj.get('context'),jsonObj.get('retargs')


def sendDirective(directive,context,session):
    #send directive to backend for interpreting
    dirPost = directiveBroker(directive,context,session)
    if dirPost.status_code == 401:
        session.token = sendAuth(session.username, session.password)
        rePost = directiveBroker(directive,context,session)
        if rePost.status_code == 401:
            print('{"authentication error":"session could not be restored"}')
            sys.exit()
    if 'form' in json.loads(dirPost.content):
        session.form = json.loads(dirPost.content)['form']
    return processResponse(dirPost.content),session

def sendAuth(username,password,gateway):
    authPost = requests.post(
        'https://{}:56114/lycanthropy/ui-handler/auth?lycan={}'.format(gateway,username),
        json={'password':password},
        headers={
            'Content-Type':'application/json'
        },
        verify=False

    )
    return authPost.content

def postFile(session,campaign,file):
    try:
        filePost = requests.post(
            'https://{}:56114/lycanthropy/{}/fileStore/{}'.format(session.api,campaign,file.split('/')[-1]),
            json={"fileData":base64.b64encode(open(file,'rb').read()).decode('utf-8')},
            cookies={
                'LYSESSID':session.token,
                'APIUSER':base64.b64encode(
                    session.username.encode('utf-8')
                ).decode('utf-8')
            },
            headers={
                'Content-Type': 'application/json'
            },
            verify=False
        )
        return filePost
    except:
        return {'error':'could not push file'}

def syncFile(session,campaign,file):
    fileGet = requests.get(
        'https://{}:56114/lycanthropy/{}/fileStore/{}'.format(session.api,campaign,file),
        cookies={
            'LYSESSID': session.token,
            'APIUSER': base64.b64encode(
                session.username.encode('utf-8')
            ).decode('utf-8')
        },
        headers={
            'Content-Type': 'application/json'
        },
        verify=False
    )
    return fileGet