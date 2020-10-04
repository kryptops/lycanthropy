import lycanthropy.crypto
import lycanthropy.portal.api

def systemSudoers(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('system.sudoers', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'posix(system.sudoers)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'systemSudoers',lycanthropy.crypto.mkRandom(6),'posix')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'posix(system.sudoers)', 'form': restoredForm}

def systemGroups(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('system.groups', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'posix(system.groups)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'systemGroups',lycanthropy.crypto.mkRandom(6),'posix')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'posix(system.groups)', 'form': restoredForm}

def systemUsers(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('system.users', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'posix(system.users)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'systemUsers',lycanthropy.crypto.mkRandom(6),'posix')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'posix(system.users)', 'form': restoredForm}

def systemNetstat(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('system.netstat', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'posix(system.netstat)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'systemNetstat',lycanthropy.crypto.mkRandom(6),'posix')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'posix(system.netstat)', 'form': restoredForm}

def fileSensitive(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('file.sensitive', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector,'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'}, 'context': 'posix(file.sensitive)', 'form': restoredForm}
    apiResponse = lycanthropy.portal.api.apiBroker().passGeneric(arguments,connector,'fileSensitive',lycanthropy.crypto.mkRandom(6),'posix')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'posix(file.sensitive)', 'form': restoredForm}
