import lycanthropy.sql.interface

def listAgents(arguments,context,connector):
    print(connector)
    agents = []
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    agentData = lycanthropy.sql.interface.filterAgents({})
    for metaObject in agentData:
        buildConf = lycanthropy.sql.interface.filterBuild({'acid':metaObject['acid']})[0]
        
        if buildConf['campaign'] in userData['campaigns'].split(','):
            agents.append(metaObject['acid'])
    return {'output':{'agents':agents}, 'context': 'database(list.agents)', 'form': arguments}

def listRecords(arguments,context,connector):
    records = []
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    recordData = lycanthropy.sql.interface.filterData({})
    for recordObject in recordData:
        if recordObject['campaign'] in userData['campaigns'].split(','):
            records.append(recordObject['record'])
    return {'output':{'records':records}, 'context': 'database(list.records)', 'form': arguments}

def dumpAgent(arguments,context,connector):
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    agentData = lycanthropy.sql.interface.filterAgents({'acid':arguments['acid']})[0]
    buildConf = lycanthropy.sql.interface.filterBuild({'acid': agentData['acid']})[0]
    if buildConf['campaign'] in userData['campaigns'].split(','):
        return {'output': {'metadata':agentData}, 'context': 'database(dump.agent)', 'form':arguments}
    return {'output': {'error':'access denied'}, 'context': 'database(dump.agent)', 'form': arguments}

def dumpRecord(arguments,context,connector):
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    recordData = lycanthropy.sql.interface.filterData({'record':arguments['record']})[0]
    if recordData['campaign'] in userData['campaigns'].split(','):
        return {'output': {'content':recordData}, 'context': 'database(dump.record', 'form':arguments}
    return {'output': {'error':'access denied'}, 'context': 'database(dump.record)', 'form': arguments}

def queryOutput(arguments,context,connector):
    queryMap = []
    queryMatches = []
    apiUser = connector['apiToken']['user']
    userData = lycanthropy.sql.interface.filterUser({'username': apiUser})[0]
    fullData = lycanthropy.sql.interface.filterData({})
    for dataObject in fullData:
        if dataObject['campaign'] in userData['campaigns'].split(','):
            queryMap.append(dataObject)
    for mappedObject in queryMap:
        if arguments['query'] in mappedObject['output']:
            queryMatches.append(mappedObject)
    return {'output':{'matches':queryMatches}, 'context': 'database(query.output)', 'form': arguments}


