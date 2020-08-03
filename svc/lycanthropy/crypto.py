import hashlib
import time
import codecs
import random
import lycanthropy.sql.interface
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def mkRandom(length):
    randAlpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    final = ''
    for x in range(length):
        final += random.choice(randAlpha)
    return final

def dance(mode,data,key,nonce):
    #nonce will == md5hash(epoch,account,salt)
    dancer = AESGCM(key)
    if mode == 0:
        return encrypt(dancer,nonce,data)
    elif mode == 1:
        return decrypt(dancer,nonce,data)

def encrypt(dancer,nonce,data):
    return dancer.encrypt(nonce,data,None)

def decrypt(dancer,nonce,data):
    return dancer.decrypt(nonce,data,None)

def kex(acid,keyType):
    #find key for acid
    try:
        if keyType == 'tcKey':
            config = lycanthropy.sql.interface.filterBuild({'tempAcid': acid})[0]
        elif keyType == 'ccKey':
            config = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    except:
        config = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
        keyType = 'ccKey'
    return config[keyType]
