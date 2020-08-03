from sqlalchemy import create_engine,text
import os
import time
import json
import getpass
import lycanthropy.sql.broker
import lycanthropy.sql.server
import lycanthropy.sql.structure
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

def startEngine(password,dbURL):
    engine = create_engine('mysql://root:{}@localhost:3306/{}'.format(password,dbURL))
    return engine

def secureServer(engine):
    #UPDATE mysql.user SET Password=PASSWORD() WHERE User='root';
    #DELETE FROM mysql.user WHERE User='';
    #DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1','::1');
    #FLUSH PRIVILEGES
    newRootPass = getpass.getpass('[>] enter new password for mysql root user :')
    time.sleep(3)
    rootParams = {'password':newRootPass}

    coupling = engine.connect()
    coupling.execute(text("""UPDATE mysql.user SET Password=PASSWORD(:password) WHERE User='root'"""),**rootParams)
    coupling.execute("""DELETE FROM mysql.user WHERE User=''""")
    coupling.execute("""DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1','::1')""")
    coupling.execute("""FLUSH PRIVILEGES""")
    coupling.close()
    engine.dispose()
    newEngine = startEngine(newRootPass,'')
    return newRootPass,newEngine



def addCoreDatabase(engine,password):
    coupling = engine.connect()
    coupling.execute("""CREATE DATABASE lycanthropy""")
    coupling.close()
    setupEngine = startEngine(password,'lycanthropy')
    dbSetup(setupEngine)
    return engine

def dbRootPass():
    while True:
        passStatus = input('[?] does the root account have a password [y/n]? ')

        if passStatus[0].lower() == 'y':
            dbPass = getpass.getpass('[>] enter the root password : ')
            try:
                engine = startEngine(dbPass,'')
                return engine
            except:
                print('[!] the provided credentials were incorrect')
        elif passStatus[0].lower() == 'n':
            print('[!] proceeding with default (blank) password for root')
            try:
                engine = startEngine('','')
                return engine
            except:
                print('[!] ERROR! Blank root password invalid')
        else:
            print('[!] ERROR! invalid option "{}"'.format(passStatus))


def addServiceAccount(engine):
    #this needs to change to vault eventually
    dbConf = json.load(open('../etc/db.json', 'r'))
    svcPass = lycanthropy.crypto.mkRandom(24)
    svcParams = {'password': svcPass}
    coupling = engine.connect()
    coupling.execute(text("""CREATE USER 'lycanthropy'@'localhost' IDENTIFIED BY :password"""),**svcParams)
    coupling.execute("""GRANT ALL PRIVILEGES ON lycanthropy.* TO 'lycanthropy'@'localhost'""")
    coupling.close()
    dbConf['password'] = svcPass
    json.dump(dbConf, open('../etc/db.json','w'), indent=4)
    return engine


def addCliUser(username,password,engine):
    coupling = engine.connect()
    userParams = {'username': username, 'password': password, 'campaigns': '', 'roles': 'manager'}
    coupling.execute(text("""INSERT INTO lycanthropy.access(username, password, campaigns, roles) VALUES(:username, :password, :campaigns, :roles)"""),**userParams)
    coupling.close()

def lycanthropyUser(engine):

    user = input('[>] enter name of admin user: ')
    finalPassword = None
    print('[!] REMINDER! The password you are about to enter will NOT be preserved in plaintext by the server, so remember what you enter')
    time.sleep(3)
    while True:
        password = getpass.getpass('[>] enter password of admin user: ')
        passmatch = getpass.getpass('[>] re-enter password for confirmation: ')
        if password == passmatch:
            finalPassword = lycanthropy.auth.client.mkUser(user,password)
            break
        else:
            print('[!] ERROR! Passwords do not match!')


    addCliUser(user,finalPassword,engine)

def chkStatus():
    serviceStatus = os.popen('service mysql status | grep active').read()

    if 'active (running)' in serviceStatus:
        return True
    else:
        return False

if __name__=='__main__':
    status = chkStatus()
    if not status:
        os.popen('service mysql start')

    print('[!] initializing database ... ')
    engine = dbRootPass()
    print('[!] securing server ... ')
    password,engine1 = secureServer(engine)
    print('[!] adding lycanthropy database ... ')
    addCoreDatabase(engine1,password)
    print('[!] adding lycanthropy service account ... ')
    addServiceAccount(engine1)
    print('[!] adding initial cli user ... ')
    lycanthropyUser(engine1)
    engine1.dispose()