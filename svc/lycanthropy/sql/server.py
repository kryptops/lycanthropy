import lycanthropy.auth.client
import lycanthropy.sql.broker
import lycanthropy.sql.security
import lycanthropy.sql.interface
import os

def rmUser(user):
    if lycanthropy.sql.security.chkOpid(user) == False:
        return {'error':'user cannot be deleted or may not exist'}
    blankQuery = """DELETE FROM access WHERE username = :user"""
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'user':user
            }
        )
        return {'status':'user deleted'}
    except:
        return {'error':'user cannot be deleted or may not exist'}

#this appears to be a defunct method

#def getUser():
#    blankQuery = """SELECT * FROM access WHERE username = :user"""
#    try:
#        return lycanthropy.sql.broker.runQuery(
#            blankQuery,
#            {}
#        )
#    except:
#        return {'error':'users cannot be retrieved'}



def getTables():
    tableRaw = lycanthropy.sql.broker.runQuery("""SHOW TABLES""",{})
    tables = [r for r, in tableRaw]
    return tables

def storeUser(username,password,campaigns,roles):
    print(lycanthropy.sql.interface.filterUser({'username':username}))
    if lycanthropy.sql.interface.filterUser({'username':username}) != []:
        return {'error':'user already exists'}
    if lycanthropy.sql.security.chkOpid(username) == False:
        return {'error':'user does not adhere to character requirements'}
    blankQuery = """INSERT INTO access(username, password, campaigns, roles) VALUES(:username, :password, :campaigns, :roles)"""
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'username':username,
                'password':password,
                'campaigns':campaigns,
                'roles':roles
            }
        )
        return {'status':'user created'}
    except:
        return {'error':'unable to store user'}

def updateAccess(user,campaigns):
    if lycanthropy.sql.interface.filterUser({'username':user})[0] == []:
        return {'error':'user does not exist'}
    if lycanthropy.sql.security.chkOpid(user) == False:
        return {'error':'user does not exist'}
    for campaign in campaigns.split(','):

        if campaign not in os.listdir('campaign'):
            return {'error':'campaign {} does not exist'.format(campaign)}
    blankQuery = """UPDATE access SET campaigns = :campaigns WHERE username = :user"""
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'campaigns':campaigns,
                'user':user
            }
        )
        return {'status':'campaign access updated'}
    except:
        return {'error':'unable to update campaigns'}

def updateStatus(acid,status):
    if lycanthropy.sql.security.chkAcid(acid) == False:
        return {'error':'unable to complete transaction'}
    blankQuery = """UPDATE metadata SET status = :status WHERE acid = :acid"""
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'status':status,
                'acid':acid
            }
        )
        return {'status':'status updated'}
    except:
        return {'error':'unable to update status'}

def updateJob(acid,jobID):
    if lycanthropy.sql.security.chkAcid(acid) == False or lycanthropy.sql.security.chkJobid(jobID) == False:
        return {'error':'unable to complete transaction'}
    blankQuery = """UPDATE metadata SET job = :jobID WHERE acid = :acid"""
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'jobID':jobID,
                'acid':acid
            }
        )
        return {'status':'job updated'}
    except:
        return {'error':'unable to update job'}
