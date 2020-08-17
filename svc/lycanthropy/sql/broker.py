import os

from sqlalchemy import create_engine,text
import json
import uuid
import base64
import lycanthropy.sql.structure
import lycanthropy.sql.agent
import lycanthropy.sql.interface
import lycanthropy.crypto
import lycanthropy.auth.login
import lycanthropy.daemon.util

def mkEngine():
    addrFile = open('../etc/sqladdr.cnf','r')
    addrLocal = addrFile.read()
    addrFile.close()
    sqlConfig = json.load(open('../etc/db.json','r'))
    engine = create_engine('mysql://lycanthropy:{}@{}:3306/lycanthropy'.format(sqlConfig['password'],addrLocal))
    return engine

def getTables():
    return runQuery(
        """SHOW TABLES IN lycanthropy""",
        {}
    )

def mkTable(table):
    engine = mkEngine()
    table[0].create_all(engine)

def runQuery(query,parameters):
    #run raw sql syntax for other functions

    engine = mkEngine()
    coupling = engine.connect()
    dataExec = coupling.execute(text(query),**parameters)
    try:
        dataFlow = dataExec.fetchall()
    except:
        dataFlow = None
    coupling.close()
    engine.dispose()
    return dataFlow

def rmTable(table):
    engine = mkEngine()
    coupling = engine.connect()
    dropTable = """DROP TABLES lycanthropy.:table"""
    coupling.execute(dropTable,**{'table':table})


def dbSetup():

    tables = {
        'access': (lycanthropy.sql.structure.access()),
        'metadata': (lycanthropy.sql.structure.metadata()),
        'build': (lycanthropy.sql.structure.build()),
        'campaign': (lycanthropy.sql.structure.campaign())
    }
    tableStates = getTables()
    for table in tables:
        if table not in str(tableStates):
            mkTable(tables[table])

