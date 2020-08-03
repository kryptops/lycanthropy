import lycanthropy.ui.directiveProcessor
import lycanthropy.ui.webClient
import lycanthropy.ui.util
import getpass
import sys
import json
import time
import readline
import subprocess
from termcolor import colored

class sessionManager():
    def __init__(self):
        self.username = ""
        self.password = ""
        self.token = ""
        self.api=""
        self.form={}



def colorPrompt(context):
    promptPrefix = colored(
        '{}@lycanthropy:/'.format(
            session.username,
        ),
        'red'
    )
    if '(' and ')' in context:
        promptSuffix = '{}{}{}'.format(
            colored(
                context[:context.index('(')+1],
                'red'
            ),
            colored(
                context[context.index('(')+1:-1],
                'white',
                attrs=['bold']
            ),
            colored(
                ') > ',
                'red'
            )
        )
    else:
        promptSuffix = colored(
            '{} > '.format(
                context
            ),
            'red'
        )
    return '{}{}'.format(promptPrefix, promptSuffix)




def sendInput(directive,config):
    #output receiver
    global session
    output,sObj = lycanthropy.ui.directiveProcessor.process(
        directive,
        config['context'],
        session
    )
    config['context'] = output[1]
    session = sObj
    if not lycanthropy.ui.util.chkModLocals(output,session):
        #execute local functions instead
        lycanthropy.ui.util.printColored(output[0])
    getInput(config)

def getInput(config):
    #input receiver
    sendInput(
        input(
            colorPrompt(config['context'])
        ),
        config
    )
    
def getAuth():
    global session
    session = sessionManager()
    user = ""
    while True:
        user = input(
            colored(
                'User.ID : ',
                'red'
            )
        )
        if '@' not in user:
            print(colored(
                    'ERROR! ',
                    'yellow',
                    attrs=['bold']
                ) + colored(
                    'User ID is not in the correct format. Re-enter username in the format "username@lycanthropy_server_address" and try again',
                    'white'

                )
            )
        else:
            break

    password = getpass.getpass(
        colored(
            'User.Password : ',
            'red'
        )
    )
    #make sure exit invalidates the token
    userid,gateway = user.split('@')
    authToken = lycanthropy.ui.webClient.sendAuth(userid,password,gateway).decode('utf-8')

    session.username = userid
    session.password = password
    session.api = gateway
    if not ('error') in authToken:
        session.token = authToken
    else:
        lycanthropy.ui.util.printColored(authToken)
        sys.exit()



if __name__ == "__main__":
    lycanthropy.ui.util.startWolfmon()
    time.sleep(4)
    config = {
        'context':'console'
    }
    print(
        colored(
            open('lycanthropy/ui/banner.txt').read(),
            'red',
            attrs=['bold']
        )
    )
    getAuth()
    lycanthropy.ui.util.forwardSession(session)
    getInput(config)
