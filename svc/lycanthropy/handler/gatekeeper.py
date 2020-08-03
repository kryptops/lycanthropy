import inspect
import sys
import lycanthropy.handler.console
import lycanthropy.handler.control
import lycanthropy.handler.manage
import lycanthropy.handler.monitor
import lycanthropy.handler.database
import lycanthropy.handler.privs


def format(directive):
    if '.' in directive:
        dirSplit = directive.split('.')
        formatted = '{}{}{}'.format(dirSplit[0],dirSplit[1][0].upper(),dirSplit[1][1:])
        return formatted
    return directive

def process(directive,context):
    for module in inspect.getmembers(sys.modules['lycanthropy.handler.{}'.format(context)]):
        if directive in module[0] and '<function' in str(module[1]):
            return module[1]
    return None

def interpret(directive,arguments,context,connector):
    #use context to seek the command
    #you can only access specific commands from a context
    #need to make sure use and others are still available from other contexts
    restoredForm = lycanthropy.portal.api.restoreForm(directive, context, arguments)
    print(directive)
    fieldChk = lycanthropy.portal.api.chkFieldDefaults(context, directive, arguments)
    if 'error' in fieldChk:
        return {'output': fieldChk, 'context': context, 'form': restoredForm}
    else:
        for field in fieldChk['defaults']:
            arguments[field] = ''

    fmtDir = format(directive)
    coreChk = process(fmtDir,'console')
    if coreChk != None:

        return coreChk(arguments,context,connector)
    else:
        procRes = process(fmtDir,context)
        if procRes != None:

            outProc = procRes(arguments,context,connector)
            return outProc
    return {'output':{'error':'directive is non-existent or not available in this console view'},'context':context,'form':restoredForm}
