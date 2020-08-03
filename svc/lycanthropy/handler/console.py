import json
import lycanthropy.handler.gatekeeper

def use(arguments,context,connector):
    #this needs to change because this is no longer how it works
    legalCon = ['console','control','manage','database','monitor','privs']
    if arguments['1'] in legalCon:
        return {'output':'\n','context':arguments['1']}
    else:
        return {'output':{'error':'invalid console view not found',
                           'the following views are available':str(legalCon)},
                'context':context}

def back(arguments,context,connector):
    return {'output':'\n','context':'console','form':''}

def help(arguments,context,connector):
    fmtContext = context.split('(')[0]
    if 'function' not in arguments:
        helpMsg = {}
        helpMsg['console'] = {}
        coreDoc = json.load(
            open(
                '../etc/console.json',
                'r'
            )
        )
        for command in coreDoc:
            helpMsg['console'][command] = coreDoc[command]['description']
        if fmtContext != 'console':
            helpMsg[fmtContext] = {}
            contextDoc = json.load(
                open(
                    '../etc/{}.json'.format(fmtContext),
                    'r'
                )
            )
            for command in contextDoc:
                helpMsg[fmtContext][command] = contextDoc[command]['description']

    else:
        helpMsg = json.load(
            open(
                '../etc/{}.json'.format(fmtContext),
                'r'
            )
        )[arguments['function']]['arguments']
    return {'output':helpMsg,'context':context}

def exit(arguments,context,connector):
    return {'output':'exit','context':'none','retargs':{}}

def load(arguments,context,connector):
    fmtContext = context.split('(')[0]
    contextFuncs = json.load(
        open(
            '../etc/{}.json'.format(fmtContext),
            'r'
        )
    )

    if arguments['1'] not in contextFuncs:
        return {'output':{'error':'directive is non-existent or not available in this console view'},'context':fmtContext}
    deepContext = '{}({})'.format(fmtContext,arguments['1'])
    return {'output':'\n','context':deepContext,'form':{arguments['1']:contextFuncs[arguments['1']]['arguments']}}