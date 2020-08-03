import lycanthropy.crypto
import lycanthropy.sql.interface
import requests
import urllib3
import json
import lycanthropy.portal.api
import lycanthropy.handler.database
import lycanthropy.dist.inventory
import lycanthropy.ui.util

def passGeneric(arguments,connector,method):
    print(connector)
    acid = arguments['acid']
    arguments.pop('acid')
    apiDirective = {
        'pkgName':'privs',
        'pkgMeth':method,
        'jobID':lycanthropy.crypto.mkRandom(6),
    }
    for object in arguments:
        apiDirective[object] = arguments[object]
    apiResponse = lycanthropy.portal.api.apiBroker().sendPost(
        'https://{}:{}/lycanthropy/api/{}'.format(
            connector['interface'],
            connector['port'],
            acid
        ),
        apiDirective,
        connector['apiCookie']
    )
    return apiResponse

def linuxProcs(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('linux.procs', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(linux.procs)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'linuxProcs')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(linux.procs)', 'form': restoredForm}

def linuxPackages(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('linux.packages', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(linux.packages)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'linuxPackages')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(linux.packages)', 'form': restoredForm}

def linuxTextpass(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('linux.textpass', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(linux.textpass)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'linuxTextpass')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(linux.textpass)', 'form': restoredForm}

def windowsMsi(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('windows.msi', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(windows.msi)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'windowsMsi')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(windows.msi)', 'form': restoredForm}

def windowsTextpass(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('windows.textpass', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(windows.textpass)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'windowsTextpass')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(windows.textpass)', 'form': restoredForm}

def windowsServices(arguments,context,connector):
    restoredForm = lycanthropy.portal.api.restoreForm('windows.services', context, arguments)
    if not lycanthropy.portal.api.accessChk(connector, 'operator'):
        return {'output': {'error': 'you do not have the correct role to run this command'},
                'context': 'privs(windows.services)', 'form': restoredForm}
    apiResponse = passGeneric(arguments, connector, 'windowsServices')
    return {'output': apiResponse.content.decode('utf-8'), 'context': 'privs(windows.services)', 'form': restoredForm}