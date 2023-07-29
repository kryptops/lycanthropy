import os
import sys
import json
import binascii
import lycanthropy.crypto

def generatePrefixes():
    prefixes = []
    for rSet in range(31):
        prefixes.append(binascii.hexlify(os.urandom(2)).decode('utf-8'))
    return prefixes

def getConfig():
    dnsConf = json.load(open('../etc/daemon.json', 'r'))
    return dnsConf

def configDns(domainStr):
    dnsConfiguration = getConfig()
    dnsConfiguration['prefixes'] = generatePrefixes()
    
    dnsObj = {}
    for lbDomain in domainStr:
        dnsObj['name'] = domainStr
	    dnsObj['subdomain'] = domainStr.split('.')[0]
        dnsConfiguration['domain'].append(dnsObj)

    print('[!] generating secret ... ')
    dnsConfiguration['secret'] = lycanthropy.crypto.mkRandom(32)
    print('[!] writing config to file ... ')
    json.dump(dnsConfiguration,open('../etc/daemon.json','w'),indent=4)


if __name__=='__main__':
    domainStr = sys.argv[1]
    print('[!] configuring the daemon ... ')
    configDns(domainStr)
