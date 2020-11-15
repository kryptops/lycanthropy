import subprocess
import uuid
import sys
import time
import lycanthropy.ui.webClient
import lycanthropy.ui.shellClient
import json
import base64
from termcolor import colored

class interpreterFormatting():
    def __init__(self):
        self.functionMap = {
            'powershell':self.powershell,
            'cmd':self.cmd,
            '/bin/bash':self.bash,
            '/bin/sh':self.bash,
            'python':self.pycli
        }

    def bash(self,command):
        return '-c',command

    def cmd(self,command):
        return '/c',command

    def powershell(self,command):
        return '',command

    def pycli(self,command):
        return '-c',command

class modLocals():
    def __init__(self):
        self.functionMap = {
            'exit':self.exit,
            'restartWolfmon':self.restartWolfmon,
            'execShell':self.execShell,
            'fileStage':self.fileStage,
            'fileSync':self.fileSync
        }

    def exit(self,arguments,session):
        lycanthropy.ui.webClient.deactivateWolfmon(session.username,session.password)
        time.sleep(1)
        sys.exit()

    def restartWolfmon(self,arguments,session):
        startWolfmon()
        time.sleep(2)
        forwardSession(session)

    def execShell(self,arguments,session):
        out = lycanthropy.ui.shellClient.initialize(arguments)
        return out

    def fileStage(self,arguments,session):
        out = lycanthropy.ui.webClient.postFile(session,arguments['campaign'],arguments['file'])
        return json.loads(out.content)

    def fileSync(self,arguments,session):
        out = lycanthropy.ui.webClient.syncFile(session,arguments['campaign'],arguments['file'])
        lycanthropy.ui.util.writeFile(json.loads(out.content))

        return {'success':'wrote {} to the working directory'.format(arguments['file'])}

def writeFile(fileObj):

    filePath = fileObj['path']
    fileData = base64.b64decode(fileObj['data'])
    fileHandle = open(filePath,'wb')
    fileHandle.write(fileData)
    fileHandle.close()


def processDownloads(arguments):
    for fileObj in arguments['files']:
        if arguments['files'][fileObj] != 'buildTimeoutError':
            fileBytes = base64.decode(arguments['files'][fileObj])
            agentHandle = open('{}/{}/buildstub-0.1.jar'.format(arguments['form']['destination'],fileObj),'wb')
            agentHandle.write(fileBytes)
            agentHandle.close()
            print(colored(' ... saved build number {} to {}'.format(fileObj,arguments['form']['destination']),'red'))
        else:
            print(colored(' ... build number {} failed to finish'.format(fileObj),'yellow'))

def mkSubscription(filter,stream,temp):
    reducer = {}
    reducer['filter'] = filter
    reducer['stream'] = stream
    reducer['temp'] = temp
    reducer['id'] = str(uuid.uuid4())
    return reducer

def startWolfmon():
    subprocess.Popen(['/bin/bash', '-c', "xterm -maximized -sl 10000 -fa 'Monospace' -fs 11 -e /bin/bash -c 'python3 wolfmon.py'"])

def chkModLocals(output,session):
    retargs = output[2]
    outFunc = output[0]
    if type(outFunc) == dict:
        return False
    if outFunc in modLocals().functionMap:
        print(json.dumps(modLocals().functionMap[outFunc](retargs,session),indent=4))
        return True
    return False

def forwardSession(session):
    connector = lycanthropy.ui.webClient.connectWolfmon(session)
    if connector.status_code != 200:
        printColored(
            json.dumps({'error':'unable to forward session to monitoring window'})
        )
        sys.exit()

def printColored(output):
    errorString = 'error'
    if 'errors' in output:
        errorString = 'errors'
    newOutput = output.replace(
        '{',colored('{','white',attrs=['bold'])
    ).replace(
        '}',colored('}','white',attrs=['bold'])
    ).replace(
        errorString,colored(errorString,'yellow')
    ).replace(
        ':',colored(':','white',attrs=['bold'])
    ).replace(
        'warning',colored('warning','red',attrs=['bold'])
    )
    print(newOutput)
