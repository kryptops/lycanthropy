import os
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
    dnsConfiguration['domain']['name'] = domainStr
    dnsConfiguration['domain']['subdomain'] = domainStr.split('.')[0]
    print('[!] generating secret ... ')
    dnsConfiguration['secret'] = lycanthropy.crypto.mkRandom(32)
    print('[!] writing config to file ... ')
    json.dump(dnsConfiguration,open('../etc/daemon.json','w'),indent=4)


def requestConfig():
    while True:
        domainStr = input('[>] enter the domain string as <sub>.<domain>.<tld> : ')
        domainConfirm = input('[>] re-enter the domain string to confirm : ')
        if domainStr != domainConfirm:
            print('[!] ERROR! The domains do not match')
        else:
            return domainStr

if __name__=='__main__':
    domainStr = requestConfig()
    print('[!] configuring the daemon ... ')
    configDns(domainStr)
