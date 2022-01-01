import hashlib
import random
import lycanthropy.sql.interface
import lycanthropy.crypto
import jwt

def decodeToken(token,config):
    rawData = jwt.decode(
        token,
        config['secret'],
        algorithms=['HS256']
    )
    return rawData

def monitoringToken(user,config,remote,identity):
    userData = lycanthropy.sql.interface.filterUser({'username':user})[0]
    token = jwt.encode({
        'user':user,
        '_wolfmon':identity,
        'campaigns':userData['campaigns'],
        'roles':userData['roles'],
        '_host':remote
    },
    config['secret'],
    algorithm='HS256'
    )
    try:
        return token.decode('utf-8')
    except:
        return token

def apiToken(user,config,remote):
    userData = lycanthropy.sql.interface.filterUser({'username':user})[0]
    token = jwt.encode({
        'user':user,
        'campaigns':userData['campaigns'],
        'roles':userData['roles'],
        '_host':remote
    },
    config['secret'],
    algorithm='HS256'
    )
    try:
        return token.decode('utf-8')
    except:
        return token

def getCampaignAccess(user,config,token,remote,wolfmon):
    decoded = decodeToken(token,config)
    if decoded['user'] == user and decoded['_host'] == remote and wolfmon == decoded['_wolfmon']:
        userData = lycanthropy.sql.interface.filterUser({'username': user})[0]
        return userData['campaigns'].split(',')
    else:
        return 'error'

def verifyToken(user,config,token,remote):
    decoded = decodeToken(token,config)
    if decoded['user'] == user and decoded['_host'] == remote:
        return True
    else:
        return False

def verifyAuth(user,password):
    userData = lycanthropy.sql.interface.filterUser({'username':user})[0]
    print(userData)
    if userData == []:
        return False
    else:
        reconstruct = mkHash(password,userData['password'].split('.')[0])
        print(reconstruct)
        if reconstruct == userData['password']:
            return True
        else:
            return False

def mkHash(password,salt):
    passHmac = hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt.encode('utf-8'),100000)
    return '{}.{}'.format(salt,passHmac.hex())

def mkSalt():
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    strOut = []
    for i in range(32):
        strOut.append(
            alpha[random.randint(
                0,
                len(alpha)-1
            )]
        )
    return "".join(strOut)

def mkUser(user,password):
    pwdSalt = mkSalt()
    passObj = mkHash(password,pwdSalt)
    return passObj





