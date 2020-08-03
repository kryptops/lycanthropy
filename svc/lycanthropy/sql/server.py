import lycanthropy.auth.client
import lycanthropy.sql.broker
import os


def rmUser(user):
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

def getUser(user):
    blankQuery = """SELECT * FROM access WHERE username = :user"""
    try:
        return lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'user':user
            }
        )
    except:
        return {'error':'user cannot be retrieved or may not exist'}




def getTables():
    tableRaw = lycanthropy.sql.broker.runQuery("""SHOW TABLES""",{})
    tables = [r for r, in tableRaw]
    return tables

def storeUser(username,password,campaigns,roles):
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
    print(campaigns)
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
