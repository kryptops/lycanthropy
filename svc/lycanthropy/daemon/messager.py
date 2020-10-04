import binascii

import os
import lycanthropy.daemon.connector
import lycanthropy.crypto
import base64
import random
from textwrap import wrap

class bridgeControl():
    def __init__(self):
        self.functionMap = {
            'data':self.data,
            'auth':self.auth,
            'ctrl':self.ctrl,
            'conf':self.conf,
            'dist':self.dist,
            'kex':self.kex,
            'heartbeat':self.heartbeat
        }

    def data(self,msgObj,gateway):
        return lycanthropy.daemon.connector.postData(
            msgObj['acid'],
            msgObj['secret'],
            msgObj['buffer'],
            gateway
        )

    def auth(self,msgObj,gateway):
        return lycanthropy.daemon.connector.postAuth(
            msgObj['acid'],
            msgObj,
            gateway
        )

    def ctrl(self,msgObj,gateway):
        return lycanthropy.daemon.connector.getCommand(
            msgObj['acid'],
            msgObj['ctrlKey'],
            gateway
        )

    def conf(self,msgObj,gateway):
        return lycanthropy.daemon.connector.getConfig(
            msgObj['confKey'],
            msgObj['acid'],
            gateway
        )

    def dist(self,msgObj,gateway):
        return lycanthropy.daemon.connector.getFile(
            msgObj['acid'],
            msgObj['distKey'],
            msgObj['pkgID'],
            gateway
        )

    def heartbeat(self,msgObj,gateway):
        return lycanthropy.daemon.connector.getHeartbeat(
            msgObj['acid'],
            gateway
        )

    def kex(self,msgObj,gateway):
        return {}


class objStructure():
    def __init__(self):
        self.functionMap = {
            'data':self.data,
            'auth':self.auth,
            'dist':self.dist,
            'ctrl':self.ctrl,
            'conf':self.conf,
            'heartbeat':self.heartbeat,
            'kex':self.kex
        }

    def data(self,msgObj,unpacked):
        print('MESSAGING')
        if unpacked['part'] == '0':
            msgObj['action'] = 'update'
            #initialize the buffer at a set length
            #this is done to ensure indexed assignment is available to preserve order
            msgObj['buffer'] = [None] * int(unpacked['length'])
        elif int(unpacked['part']) == int(unpacked['length'])-1:
            msgObj['action'] = 'teardown'
        else:
            msgObj['action'] = 'update'
        msgObj['buffer'][int(unpacked['part'])] = unpacked['segment']
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def auth(self,msgObj,unpacked):
        msgObj['action'] = 'teardown'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def dist(self,msgObj,unpacked):
        msgObj['action'] = 'teardown'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def ctrl(self,msgObj,unpacked):
        msgObj['action'] = 'teardown'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def conf(self,msgObj,unpacked):
        msgObj['action'] = 'teardown'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def heartbeat(self,msgObj,unpacked):
        msgObj['action'] = 'teardown'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

    def kex(self,msgObj,unpacked):
        msgObj['action'] = 'update'
        for component in unpacked:
            msgObj[component] = unpacked[component]
        return msgObj

def prepRaw(data,acid,nonce,keyType):
    rawKey = lycanthropy.crypto.kex(acid, keyType)
    key = base64.b64decode(rawKey)
    encrypted = lycanthropy.crypto.dance(0,data.encode('utf-8'),key,nonce.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def checkDeDup(array,candidates):
    for candidate in candidates:
        if candidate in array:
            return False
    return True
        
def reFormatDuplicates(record):
    deDup = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 40, 41, 42, 43, 44, 46, 60, 62, 63, 64, 91, 93, 123, 124, 125]
    finalRecords = []
    newRecords = [
            [record[0],record[1],record[2]],
            [record[0],record[1],str(int(record[2]))+1]
            ]
    incrementer = 0
    dataBlock = record[3:9]
    for i in range(len(dataBlock)):
        randomPadding = chr(random.choice(deDup))+chr(random.choice(deDup))
        newSegment = binascii.hexlify(randomPadding.encode('utf-8')).decode('utf-8')
        newRecords[incrementer].append(randomPadding)
        newRecords[incrementer].append(i)
        if len(newRecords[incrementer]) == 8:
            finalRecords.append(':'.join(newRecords[incrementer]))
            incrementer += 1
    return finalRecords

def resolveDuplication(record,array):
    #make sure everything is wrapped in base64
    reFormat = False
    while True:
        reFormat = reFormatDuplicates(record)
        if checkDeDup(array,reFormat):
            return reFormat
        else:
            continue

def makeRecordArray(data,acid,nonce,keyType,prefix):
    #parse to A records
    data = prepRaw(data,acid,nonce,keyType)

    recordArray = []
    currentRecord = []
    hexData = binascii.hexlify(data.encode('utf-8')).decode('utf-8')
    counter = 1

    for dataSegment in wrap(hexData,20):
        incrementer = 1
        currentRecord.append(prefix)
        currentRecord.append(binascii.hexlify(os.urandom(2)).decode('utf-8'))
        currentRecord.append(str(counter))
        dataSets = wrap(dataSegment,4)
        dataLength = len(dataSets)
        if dataLength < 5:
            currentRecord.append('')
        for datum in dataSets:
            currentRecord.append(datum)
        if len(currentRecord) == 8:
            if ':'.join(currentRecord) not in recordArray:
                recordArray.append(':'.join(currentRecord))
            else:
                for recordObject in resolveDuplication(currentRecord,recordArray):
                    recordArray.append(recordObject)
                incrementer += 1
            currentRecord = []
        counter += incrementer

    if len(currentRecord) < 8 and len(currentRecord) > 1:
        recordArray.append(':'.join(currentRecord))

    return recordArray

def remakeObj(msgObj,unpacked):
    #preps the message to be added back
    print(objStructure().functionMap[unpacked['type']])
    return objStructure().functionMap[unpacked['type']](msgObj,unpacked)

def makeResponse(msgObj,gateway):
    #uses the connector to send data to the backend
    #parses backend into array of ip addresses
    return bridgeControl().functionMap[msgObj['type']](msgObj,gateway)