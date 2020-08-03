from sqlalchemy import Table, Column, String, MetaData, BLOB




def campaign():
    meta = MetaData()
    campaign = Table(
        'campaign',meta,
        Column('acid',String(16)),
        Column('record',String(32)),
        Column('module',String(48)),
        Column('timestamp',String(32)),
        Column('job',String(8)),
        Column('campaign',String(64)),
        Column('output',BLOB(64000))
    )
    return meta,campaign

def access():
    meta = MetaData()
    access = Table(
        'access',meta,
        Column('username',String(32)),
        Column('password',String(256)),
        Column('campaigns',BLOB(64000)),
        Column('roles',String(128))
    )
    return meta,access

def metadata():
    meta = MetaData()
    data = Table(
        'metadata',meta,
        Column('acid',String(16)),
        Column('hostname',String(32)),
        Column('ip',BLOB(4096)),
        Column('os',String(32)),
        Column('arch',String(16)),
        Column('integrity',String(8)),
        Column('user',String(32)),
        Column('cwd',String(64)),
        Column('domain',String(64)),
        Column('registered',String(32)),
        Column('status',String(16))
    )
    return meta,data

def build():
    meta = MetaData()
    data = Table(
        'build',meta,
        Column('ctrlKey',String(64)),
        Column('distKey',String(64)),
        Column('ccKey',String(64)),
        Column('password',String(128)),
        Column('acid',String(16)),
        Column('confKey',String(64)),
        Column('pkgCore',BLOB(8000)),
        Column('tempAcid',String(16)),
        Column('regPass',String(128)),
        Column('regKey',String(16)),
        Column('tcKey',String(64)),
        Column('campaign',String(128))
    )
    return meta,data