import hashlib
import base64
import lycanthropy.sql.agent
import lycanthropy.crypto

def genhash(password,salt):
    generator = hashlib.sha256()
    generator.update(password.encode('utf-8'))
    generator.update(salt.encode('utf-8'))
    return generator.hexdigest()
    

def verify(loginData):
    #agentConf = lycanthropy.sql.agent.retrieveConf(loginData['acid'])
    #loginPass = lycanthropy.crypto.dance(1, loginData['password'], agentConf['key'], loginData['nonce'])
    #if agentConf['password'] == genhash(loginPass,agentConf['salt']):
    #    return True
    #return False
    acid = loginData['acid']
    agentConf = lycanthropy.sql.interface.filterBuild({'tempAcid':acid})[0]
    loginPass = lycanthropy.crypto.dance(1, base64.b64decode(loginData['password']), base64.b64decode(agentConf['tcKey']), loginData['nonce'].encode('utf-8'))
    tableSalt = agentConf['regPass'].split('.')[0]
    if agentConf['regPass'] == '{}.{}'.format(tableSalt,genhash(loginPass.decode('utf-8'), tableSalt)):
        return True
    return False