import sys
import logging
import threading
import lycanthropy.ui.webClient
import time
import json
import getpass
from termcolor import colored

class shellManager():
    def __init__(self):
        self.username=''
        self.password=''
        self.token=''
        self.api=''
        self.template={}
        self.subscriptions=[]
        self.prompt=''
        self.exit = False

def getCommand():
    localForm = sessionObject.template
    localForm['command'] = input(
        sessionObject.prompt.replace(sessionObject.template['interpreter'],colored(sessionObject.template['interpreter'],'grey'))
    )

    if localForm['command'] == 'exit':
        sessionObject.exit = True
    elif len(localForm['command']) == 0:
        print('\n')
    else:
        directive = {
            'cmd':'exec.command',
            'args':localForm
        }
        fwdDir = lycanthropy.ui.webClient.sendDirective(directive, 'control', sessionObject)
        sessionObject.subscriptions.append(
            lycanthropy.ui.util.mkSubscription(
                {'field': 'jobID', 'value': json.loads(fwdDir[0][0])['jobID']},
                'data',
                'true'
            )
        )

def startInterface():
    while True:
        getCommand()
        if sessionObject.exit == True:
            retrForm = sessionObject.template
            retrForm.pop('command')
            #this dumps me to control. Why? I don't know.
            return {'output': '\n', 'context': 'control(exec.shell)', 'form': retrForm}
        monitorSession = {
            'subscriptions': sessionObject.subscriptions,
            'api': sessionObject.api,
            'token': sessionObject.monToken,
            'identity': sessionObject.identity,
            'username': sessionObject.username
        }
        monitorStream = lycanthropy.ui.webClient.monitorApiBroker(monitorSession)
        if monitorStream.status_code == 401:
            shellManager.token, shellManager.identity = lycanthropy.ui.webClient.authWolfmon({
                'username': sessionObject.username,
                'password': sessionObject.password,
                'api': sessionObject.api
            })
        monitorOut = json.loads(monitorStream.content.decode('utf-8'))

        for match in monitorOut:
            if 'state' in match:
                if match['state'] == 'true':
                    print(match['output']['output'])

def getAuth(token,acid):
    global sessionObject
    sessionObject = shellManager()
    user = ""
    while True:
        user = input(
            '[{}] User.ID : '.format(acid).replace(acid,colored(acid,'red'))
        )
        if '@' not in user:
            print(colored(
                    'ERROR! ',
                    'yellow',
                    attrs=['bold']
                ) + colored(
                    'User ID is not in the correct format. Re-enter username in the format "username@lycanthropy_server_address" and try again',
                    'grey'
                )
            )
        else:
            break

    password = getpass.getpass(
        '[{}] User.Password : '.format(acid).replace(acid,colored(acid,'red'))
    )
    userid, gateway = user.split('@')
    sessionObject.username = userid
    sessionObject.password = password
    sessionObject.api = gateway
    monObject = lycanthropy.ui.webClient.authWolfmon(
        {
            'api': sessionObject.api,
            'username': sessionObject.username,
            'password': sessionObject.password
        }
    )

    sessionObject.monToken = monObject[0]
    sessionObject.token = token
    sessionObject.identity = monObject[1]

def configureShell(interpreter,acid,host,user):
    sessionObject.template['interpreter'] = interpreter
    sessionObject.template['acid'] = acid
    sessionObject.template['command'] = ''
    sessionObject.prompt = '[{}] {}@{} > '.format(interpreter,user,host)

def initialize(arguments):
    print(
        colored(
            '[>] entering shell interface ... ',
            'red'
        ) + '\n'
    )
    print(
        colored(
            '[>] type exit to return to the console ... ',
            'red'
        ) + '\n'
    )
    print(
        colored(
            '[>] enter your operator credentials to access the shell ... ',
            'red'
        ) + '\n'
    )
    getAuth(arguments['token'],arguments['acid'])
    configureShell(arguments['interpreter'],arguments['acid'],arguments['host'],arguments['user'])
    if 'error' in sessionObject.monToken:
        lycanthropy.ui.util.printColored(sessionObject.monToken)
        return {'output': 'operator ', 'context': 'control(exec.shell)', 'form': sessionObject.template}
    out = startInterface()
    return out
