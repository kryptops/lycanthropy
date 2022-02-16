from textwrap import wrap
import jwt
import time
import psutil
import base64
import hashlib

def getHash(data):
    hashifer = hashlib.sha256()
    hashifer.update(data.encode('utf-8'))
    return hashifer.hexdigest()


def chkRtype(fileRaw):
    rtype = 'null'
    file = base64.b64decode(fileRaw.split('|')[0].encode('utf-8')).decode('utf-8')
    uuidLegal = 'abcdef0123456789-|PIR'

    if (len(file) == 36 or len(file) == 40) and len(file.split('-')) == 5 and '.' not in file:
        for character in file:
            if character not in uuidLegal:

                if 'PIR' in fileRaw.split('|'):

                    return 'pull.queue'
                return 'pull'
        if 'PIR' in fileRaw.split('|'):
            return 'load.queue'
        return 'load'

    else:
        if 'PIR' in fileRaw.split('|'):

            return 'pull.queue'
        return 'pull'

def mkToken(data,acid,key,type):
    #the key is the ccKey of the agent

    token = jwt.encode({
        '_expiry':(int(time.time()) + 10),
        '_stream':type,
        '_hash':getHash(str(data)),
        '_acid':acid
    },
    key,
    algorithm='HS256'
    ).decode('utf-8')
    return token


def chunkString(data):
    if len(data) > 150:
        wrapped = wrap(data,150)
    else:
        wrapped = wrap(data,10)
    return wrapped

def getAddr():
    interfaceSet = psutil.net_if_addrs()
    for ifAddr in interfaceSet:
        if 'eth' in ifAddr or 'ens' in ifAddr or 'enp' in ifAddr:
            return interfaceSet[ifAddr][0].address


