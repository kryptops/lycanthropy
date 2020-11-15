import lycanthropy.ui.webClient

import sys
import json
import inspect

class localDirectives():
    def __init__(self):
        self.functionMap = {
            "show":self.show,
            "set":self.set,
            "run":self.run,
            "go":self.run,
            "exploit":self.run,
            "options":self.show
        }

    def show(self,arguments,context,session):
        retrForm = session.form
        return [json.dumps(retrForm,indent=4),context,None],session

    def set(self,arguments,context,session):
        if session.form == {}:
            return [json.dumps({'error':'no module has been loaded'}),context,None],session
        dictKeys = list(session.form.keys())
        argValue = []
        for valObject in list(arguments.keys()):
            #concat spaced values
            if int(valObject) > 1:
                argValue.append(arguments[valObject])


        session.form[dictKeys[0]][arguments['1']] = ' '.join(argValue)
        return ['\n',context,None],session

    def run(self,arguments,context,session):
        parentContext = context.split('(')[0]
        runForm = {}
        dictKeys = list(session.form.keys())
        try:
            runForm['cmd'] = dictKeys[0]
        except:
            return {'error':'the command form needs to be reloaded','solution':'re-run the \'load\' command and try again'}
        runForm['args'] = session.form[dictKeys[0]]
        fwdDir = lycanthropy.ui.webClient.sendDirective(runForm,parentContext,session)

        if 'jobID' in fwdDir[0][0]:
            lycanthropy.ui.webClient.subscribeWolfmon(
                lycanthropy.ui.util.mkSubscription(
                    {'field':'jobID','value':json.loads(fwdDir[0][0])['jobID']},
                    'data',
                    'true'
                )
            )
        return fwdDir


def process(directive,context,session):
    redirect = {}

    dirLine = directive.split(" ")
    redirect['cmd'] = dirLine[0]
    redirect['args'] = {}
    if len(dirLine) > 1:
        for word in dirLine[1:]:
                redirect['args'][str(dirLine.index(word))] = word
    else:
        redirect['args'] = {}
    return interpret(redirect,context,session)


def interpret(directive,context,session):
    #return output
    if directive['cmd'].lower() not in localDirectives().functionMap:
        return lycanthropy.ui.webClient.sendDirective(directive,context,session)
    else:
        return localDirectives().functionMap[directive['cmd']](directive['args'],context,session)




