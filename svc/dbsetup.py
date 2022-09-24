from sqlalchemy import create_engine,text
import os
import sys
import time
import json
import getpass
import lycanthropy.sql.broker
import lycanthropy.sql.server
import lycanthropy.sql.structure
import lycanthropy.daemon.util
import lycanthropy.auth.client
import lycanthropy.crypto


def getTables(engine):
    return engine.execute("""SHOW TABLES IN lycanthropy""").fetchall()

def mkTable(table,engine):
    table[0].create_all(engine)

def dbSetup(engine):

    tables = {
        'access': (lycanthropy.sql.structure.access()),
        'metadata': (lycanthropy.sql.structure.metadata()),
        'build': (lycanthropy.sql.structure.build()),
        'campaign': (lycanthropy.sql.structure.campaign())
    }
    tableStates = getTables(engine)
    for table in tables:
        if table not in str(tableStates):
            mkTable(tables[table],engine)

def startEngine(password,dbURL,dbHost):
    engine = create_engine('mysql://root:{}@{}:3306/{}'.format(password,dbHost,dbURL))
    return engine

def secureServer(password,engine):
    #UPDATE mysql.user SET Password=PASSWORD() WHERE User='root';
    #DELETE FROM mysql.user WHERE User='';
    #DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1','::1');
    #FLUSH PRIVILEGES
    coupling = engine.connect()
    coupling.execute("""DELETE FROM mysql.user WHERE User=''""")
    #try creating the database without adding root@%
    #coupling.execute("""CREATE USER root""")
    #coupling.execute("""DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1','::1')""")
    coupling.execute("""SET PASSWORD FOR 'root'@'localhost'=PASSWORD(':password')""",{'password':password})
    
    try:
        coupling.execute("""SET PASSWORD FOR 'root'@'127.0.0.1'=PASSWORD(':password')""",{'password':password})
    except:
        pass
    try:
        coupling.execute("""SET PASSWORD FOR 'root'@'::1'=PASSWORD(':password')""",{'password':password})
    except:
        pass
    try:
        coupling.execute("""SET PASSWORD FOR 'root'@'%'=PASSWORD(':password')""",{'password':password})
    except:
        pass
    try:
        coupling.execute("""SET PASSWORD FOR 'root'@'%'=PASSWORD(':password')""",{'password':password})
    except:
        pass
    

    coupling.execute("""FLUSH PRIVILEGES""")

    
    coupling.close()
    engine.dispose()
    newEngine = startEngine(password,'','localhost')
    return newEngine



def addCoreDatabase(engine,password):
    coupling = engine.connect()
    coupling.execute("""CREATE DATABASE lycanthropy""")
    coupling.close()
    setupEngine = startEngine(password,'lycanthropy','localhost')
    dbSetup(setupEngine)
    return engine


def addServiceAccount(engine):
    #this needs to change to vault eventually
    dbConf = json.load(open('../etc/db.json', 'r'))
    svcPass = '@'
    while '@' in svcPass:
        svcPass = lycanthropy.crypto.mkRandom(24)
    svcParams = {'password': svcPass}
    print(svcParams)

    coupling = engine.connect()
    coupling.execute(text("""CREATE USER lycanthropy IDENTIFIED BY :password"""),**svcParams)
    coupling.execute("""GRANT ALL PRIVILEGES ON lycanthropy.* TO lycanthropy""")
    coupling.close()
    dbConf['password'] = svcPass
    json.dump(dbConf, open('../etc/db.json','w'), indent=4)
    return engine


def addCliUser(username,password,engine):
    coupling = engine.connect()
    userParams = {'username': username, 'password': lycanthropy.auth.client.mkHash(password,lycanthropy.auth.client.mkSalt()), 'campaigns': '', 'roles': 'manager'}
    coupling.execute(text("""INSERT INTO lycanthropy.access(username, password, campaigns, roles) VALUES(:username, :password, :campaigns, :roles)"""),**userParams)
    coupling.close()


def chkStatus():
    serviceStatus = os.popen('service mysql status | grep active').read()

    if 'active (running)' in serviceStatus:
        return True
    else:
        return False

if __name__=='__main__':
    status = chkStatus()
    rootPass = sys.argv[1]
    userA = sys.argv[2]
    passA = sys.argv[3]
    if not status:
        os.popen('service mysql start')

    print('[!] initializing database ... ')
    engine = startEngine('','','localhost')
    print('[!] securing server ... ')
    engine1 = secureServer(rootPass,engine)
    print('[!] adding lycanthropy database ... ')
    addCoreDatabase(engine1,rootPass)
    print('[!] adding lycanthropy service account ... ')
    addServiceAccount(engine1)
    print('[!] adding initial cli user ... ')
    addCliUser(userA,passA,engine1)
    engine1.dispose()
