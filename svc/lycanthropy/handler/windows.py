import lycanthropy.crypto
import lycanthropy.portal.api

#CLEAN UP PRIORITIZATION

def wmiHotfix(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.hotfix', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.hotfix)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiHotfix',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.hotfix)', 'form': restoredForm}

def wmiService(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.service', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.service)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiService',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.service)', 'form': restoredForm}

def wmiUser(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.user', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.user)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiUser',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.user)', 'form': restoredForm}

def wmiInstalled(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.installed', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.installed)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiInstalled',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.installed)', 'form': restoredForm}

def wmiAutorun(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.autorun', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.autorun)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiAutorun',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.autorun)', 'form': restoredForm}

def wmiProcess(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.process', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.process)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiProcess',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.process)', 'form': restoredForm}

def wmiEnvironment(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.environment', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.environment)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiEnvironment',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.autorun)', 'form': restoredForm}

def wmiShare(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('wmi.share', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(wmi.share)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'wmiShare',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(wmi.share)', 'form': restoredForm}

def asynckeystateLogger(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('asynckeystate.logger', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'windows(asynckeystate.logger)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'asyncKeystatelogger',lycanthropy.crypto.mkRandom(6))
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'windows(asynckeystate.logger)', 'form': restoredForm}