import json
import lycanthropy.sql.agent
import lycanthropy.sql.server
import lycanthropy.sql.broker

def tableStruct(tableType):
    tableMap = json.load(open('../etc/tables.json','r'))
    return tableMap[tableType]

def jsonit(sqlOut,tableType):
    tableMap = tableStruct(tableType)
    jsonOut = []
    for row in sqlOut:
        inc = 0
        jsonOut.append({})
        for column in row:
            if type(column) == bytes:
                fmtColumn = column.decode('utf-8')
            else:
                fmtColumn = column
            jsonOut[-1][tableMap[inc]] = fmtColumn
            inc += 1
    return jsonOut



def filterAll(values,map):
    queryMatch = []
    if values == {}:
        return map
    for row in map:
        for key in values:
            if key in row and row[key] == values[key]:
                queryMatch.append(row)
    return queryMatch

def filterAgents(values):
    return filterAll(
        values,
        jsonit(
            lycanthropy.sql.agent.getAgents(),
            'metadata'
        )
    )

def filterData(values):
    campaigns = []
    for table in lycanthropy.sql.agent.getCampaigns():
        campaigns.append(table[0])
    return filterAll(
        values,
        jsonit(
            lycanthropy.sql.agent.getData(),
            'campaign'
        )
    )

def filterUser(values):
    return filterAll(
        values,
        jsonit(
            lycanthropy.sql.agent.getUsers(),
            'access'
        )
    )

def filterBuild(values):
    return filterAll(
        values,
        jsonit(
            lycanthropy.sql.agent.getBuilds(),
            'build'
        )
    )
