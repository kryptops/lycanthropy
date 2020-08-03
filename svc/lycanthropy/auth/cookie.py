import hashlib
import os
import time
import datetime

def verify(cookie,cookieDough):
    #verify cookie

    for skewer in skew():
        if derive(cookieDough,skewer) == cookie:
            return True
    return False

def skew():
    #get skews
    skewers = []
    currentEpoch = int(time.time())
    diffEpoch = datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(seconds=20)
    earliestEpoch = int(time.mktime(diffEpoch.timetuple()))
    for epoch in range(earliestEpoch,currentEpoch+5):
        skewers.append(epoch)
    return skewers

def derive(cookieDough,epoch):
    #derive session cookie
    hasher = hashlib.sha256()
    hasher.update((str(epoch)+'.'+cookieDough).encode('utf-8'))
    return hasher.hexdigest()[0:16]

def generate(password,acid):
    #cookies are issued on auth
    #cookies will be stored by the dns server as session objects
    #sessions table looks like [{"cookie":<str>,"nonce":<str>,"acid":<str>}]
    #cookies are valid for 30 minutes, at which point auth is re-requested
    #THIS SHOULD BE REPLACED WITH JWT, METHINKS
    hashObj = hashlib.sha256()
    hashObj.update(acid.encode('utf-8'))
    hashObj.update(os.urandom(8))
    hashObj.update(password.encode('utf-8'))
    hashObj.update(os.urandom(8))
    return hashObj.hexdigest()

def apify(token,remote,directive):
    #generate ephemeral cookie for automated api storage
    #added random bytes and time to avoid a collision
    hashObj = hashlib.sha256()
    hashObj.update(os.urandom(64))
    hashObj.update(remote.encode('utf-8'))
    hashObj.update(token.encode('utf-8'))
    hashObj.update(directive.encode('utf-8'))
    hashObj.update(str(int(time.time())).encode('utf-8'))
    return hashObj.hexdigest()


