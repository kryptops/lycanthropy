import datetime
import sys
import time
import threading
import traceback
import socketserver
import struct
import ast
import json
import random
from dnslib import *
import lycanthropy.daemon.parser
import lycanthropy.daemon.messager
import lycanthropy.daemon.util
import lycanthropy.crypto
import lycanthropy.auth.cookie


# based on https://gist.github.com/andreif/6069838
# GoggleHeadedHacker told me I needed to comment my code

class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        # now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        # print("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0],self.client_address[1]))
        try:
            data = self.get_data()
            self.send_data(werewolf.dns_response(data))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0]

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


class coreServer():
    def __init__(self):
        # change to pull from config
        self.config = json.load(open('../etc/daemon.json', 'r'))
        self.D = DomainName(
            self.config['domain']['name']
        )
        self.IP = lycanthropy.daemon.util.getAddr()
        self.TTL = 60 * 5
        self.D.home = A(self.IP)

        self.soa_record = SOA(
            mname=self.D.ns1,  # primary name server
            
            times=(
                201307231,  # serial number
                60 * 60 * 1,  # refresh
                60 * 60 * 3,  # retry
                60 * 60 * 24,  # expire
                60 * 60 * 1,  # minimum
            )
        )
        self.archive = {}
        self.ns_records = [NS(self.D.ns1), NS(self.D.ns2)]
        self.records = {
            self.D: [A(self.IP), AAAA((0,) * 16), MX(self.D.mail), self.soa_record] + self.ns_records,
            self.D.ns1: [A(self.IP)],
            self.D.ns2: [A(self.IP)],
            self.D.mail: [A(self.IP)],
        }
        # holds tokens
        self.sessions = {}
        # buffers inbound requests by message id
        self.messages = {}
        self.handlerMap = {
            'kex':self.kex,
            'auth':self.auth,
            'dist':self.dist,
            'heartbeat':self.heartbeat,
            'ctrl':self.ctrl,
            'conf':self.conf,
            'data':self.data
        }
        self.responseBuffer = {}

    def makeAuthFail(self,unpackedReq):
        return lycanthropy.daemon.messager.makeRecordArray(
            '{"error":"bad authentication request"}',
            self.messages[unpackedReq['msgID']]['acid'],
            self.messages[unpackedReq['msgID']]['nonce'],
            self.config['keytypes'][unpackedReq['type']],
            random.choice(self.config['prefixes'])
        )

    def makeAuthSuccess(self,unpackedReq):

        try:
            acid = unpackedReq['acid']
            if lycanthropy.auth.cookie.verify(unpackedReq['cookie'], self.sessions[acid]) == False:
                # return error, encrypted using the acid and nonce associated with the message ID
                # make this so that it will try several times
                print("invalid token : {}".format(unpackedReq['cookie']))
                return 1,lycanthropy.daemon.messager.makeRecordArray('{"error":"invalid token"}',
                                                                acid,
                                                                self.messages[unpackedReq['msgID']]['nonce'],
                                                                self.config['keytypes'][unpackedReq['type']],
                                                                random.choice(self.config['prefixes'])
                                                               )
            unpackedReq['acid'] = acid
            return 0,unpackedReq
        except:
            print(json.dumps({'error':'hit exception during auth cycle'},indent=4))
            traceback.print_exc()

    def makeResponseGeneric(self,msgStatus,msgResponse):
#        if self.messages[unpackedReq['msgID']]['garbage'] == 1:
#            self.messages.pop(unpackedReq['msgID'])
        try:
            if 'nonce' in msgStatus:
                nonce = msgStatus['nonce']
            else:
                nonce = self.messages[msgStatus['msgID']]['nonce']
            acid = msgStatus['acid']
            type = msgStatus['type']
            return lycanthropy.daemon.messager.makeRecordArray(
                str(msgResponse),
                acid,
                nonce,
                self.config['keytypes'][type],
                random.choice(self.config['prefixes'])
            )
        except:
            print(json.dumps({'error':'hit exception making generic response'},indent=4))
            traceback.print_exc()

    def makeResponseBuffered(self,unpackedReq,msgResponse):
        #store buffers under the message id
        #pkgID in unpackedReq will be the indicator of continuation
        #DistKey is messageID
        buffers = lycanthropy.daemon.util.chunkString(str(msgResponse))

        bufferLength = int(len(buffers))
        self.responseBuffer[unpackedReq['msgID']] = {}
        self.responseBuffer[unpackedReq['msgID']]['data'] = buffers
        self.responseBuffer[unpackedReq['msgID']]['index'] = 0

        return self.makeResponseGeneric(
            unpackedReq,
            json.dumps(
                {
                    'bufferSize':bufferLength,
                    'bufferKey':unpackedReq['msgID']
                }
            )

        )

    def kex(self,unpackedReq,msgStatus):
        garbageDisposal = []
        msgResponse = self.getResponse(unpackedReq)
        msgStamped = msgStatus
        msgStamped['archived'] = str(int(time.time()))
        self.archive[unpackedReq['msgID']] = msgStamped


        for oldMsg in self.archive:
            if int(self.archive[oldMsg]['archived']) < int(time.time())-10:
                garbageDisposal.append(oldMsg)
        
        for archivedMsg in garbageDisposal:
            if archivedMsg in self.archive:
                self.archive.pop(archivedMsg)
                garbageDisposal.pop(garbageDisposal.index(archivedMsg))

        return self.makeResponseGeneric(unpackedReq,msgResponse)

    def auth(self,unpackedReq,msgStatus):
        if 'nonce' not in msgStatus:
            print(json.dumps({'error':'nonce unavailable, retrieving from archive'},indent=4))
            msgStatus['nonce'] = self.archive[msgStatus['msgID']]['nonce']
        else:
            if msgStatus['acid'] not in self.sessions:
                self.sessions [msgStatus['acid']] = []
            msgResponse = self.getResponse(msgStatus)
            jsonMsg = json.loads(msgResponse)

            
            #if unpackedReq['acid'] not in self.sessions and 'cookieDough' in jsonMsg:
            self.sessions[unpackedReq['acid']].append(jsonMsg['cookieDough'])

            return self.makeResponseGeneric(msgStatus,msgResponse)

    def dist(self,unpackedReq,msgStatus):
        #ADD BUFFERING FEATURES
        if 'cookie' not in unpackedReq:
            return self.makeAuthFail(
                unpackedReq
            )


        #self.archive[msgStatus['msgID']]['index'] =
        status,referencedReq = self.makeAuthSuccess(msgStatus)

        if status == 1:
            return referencedReq

        if unpackedReq['pkgID'] != 'PCR' and unpackedReq['pkgID'] != 'PBC' and 'PIR' not in unpackedReq['pkgID'].split('|') and 'PRR' not in unpackedReq['pkgID'].split('|'):
            msgResponse = self.getResponse(referencedReq)
            #first response is buffer descriptor:
            #{'bufferSize':len(buffer),'bufferKey':msgID}
            return self.makeResponseBuffered(referencedReq, msgResponse)

        elif 'PIR' in unpackedReq['pkgID'].split('|'):
            #queue build
            #msgResponse = self.getResponse(referencedReq)
            msgThread = threading.Thread(target=self.getResponse,args=(referencedReq,))
            msgThread.start()
            #return self.makeResponseGeneric(referencedReq, msgResponse)
            return self.makeResponseGeneric(referencedReq,{'dist':'ok'})
        elif unpackedReq['pkgID'] == 'PBC':
            self.responseBuffer.pop(referencedReq['distKey'])
            return self.makeResponseGeneric(msgStatus, '{"index":-1}')
        elif 'PRR' in unpackedReq['pkgID'].split('|'):
            requiredIndex = int(unpackedReq['pkgID'].split('|')[1])
            responseBuffer = self.responseBuffer[referencedReq['distKey']]
            if requiredIndex >= len(responseBuffer['data']):
                #segment final, send conclusion
                return self.makeResponseGeneric(msgStatus, '{"index":-1}')
            nextBuffer = responseBuffer['data'][int(requiredIndex)]
            msgResponse = {'index':requiredIndex,'data':nextBuffer}
            return self.makeResponseGeneric(msgStatus, msgResponse)
        elif unpackedReq['pkgID'] == 'PCR':
            responseBuffer = self.responseBuffer[referencedReq['distKey']]
            len(responseBuffer['data'])
            #find the next buffer segment and tag it with its position in the buffer
            if 'index' in self.archive[msgStatus['msgID']]:
                requiredIndex = int(self.archive[msgStatus['msgID']]['index'])
            else:
                requiredIndex = int(responseBuffer['index'])
                self.responseBuffer[referencedReq['distKey']]['index'] += 1
            if requiredIndex >= len(responseBuffer['data'])-1:
                #segment final, send conclusion
                return self.makeResponseGeneric(msgStatus, '{"index":-1}')
            nextBuffer = responseBuffer['data'][requiredIndex]
            msgResponse = {'index':str(requiredIndex),'data':nextBuffer}

            self.archive[msgStatus['msgID']]['index'] = str(requiredIndex)
            return self.makeResponseGeneric(msgStatus, msgResponse)


    def heartbeat(self,unpackedReq,msgStatus):
        if 'cookie' not in unpackedReq:
            return self.makeAuthFail(
                unpackedReq
            )
        print(json.dumps({'alert':'received heartbeat from {}'.format(msgStatus['acid'])},indent=4))
        status,referencedReq = self.makeAuthSuccess(msgStatus)
        if status == 1:
            return referencedReq
        msgResponse = self.getResponse(referencedReq)
        return self.makeResponseGeneric(msgStatus,msgResponse)

    def ctrl(self,unpackedReq,msgStatus):
        if 'cookie' not in unpackedReq:
            return self.makeAuthFail(
                unpackedReq
            )
        status,referencedReq = self.makeAuthSuccess(msgStatus)
        if status == 1:
            return referencedReq
        msgResponse = self.getResponse(referencedReq)
        return self.makeResponseGeneric(msgStatus,msgResponse)

    def conf(self,unpackedReq,msgStatus):
        if 'cookie' not in unpackedReq:
            return self.makeAuthFail(
                unpackedReq
            )

        status,referencedReq = self.makeAuthSuccess(msgStatus)
        if status == 1:
            return referencedReq

        confObj = unpackedReq['confKey'].split('|')

        if confObj[0] != '_PCR' and confObj[0] != '_PBC':
            msgResponse = self.getResponse(referencedReq)
            #first response is buffer descriptor:
            #{'bufferSize':len(buffer),'bufferKey':msgID}

            return self.makeResponseBuffered(msgStatus, msgResponse)
        elif confObj[0] == '_PBC':

            jsonMsg = json.loads(''.join(self.responseBuffer[confObj[1]]['data']))
            self.responseBuffer.pop(confObj[1])
            cookieDough = self.sessions[referencedReq['acid']]
            self.sessions.pop(referencedReq['acid'])
            self.sessions[jsonMsg['acid']] = cookieDough
            return self.makeResponseGeneric(msgStatus, '{"index":-1}')
        elif confObj[0] == '_PCR':
            responseBuffer = self.responseBuffer[confObj[1]]
            #find the next buffer segment and tag it with its position in the buffer
            #if 'index' in self.archive[msgStatus['msgID']]:
                #requiredIndex = int(self.archive[msgStatus['msgID']]['index'])
            #else:
                #requiredIndex = int(responseBuffer['index'])
                #self.responseBuffer[confObj[1]]['index'] += 1
            requiredIndex = int(confObj[2])


            #if requiredIndex >= len(responseBuffer['data']):
                #segment final, send conclusion

              #  return self.makeResponseGeneric(msgStatus, '{"index":-1}')
            print("configuration progress: {}/{}".format(requiredIndex+1,len(responseBuffer['data'])))
            nextBuffer = responseBuffer['data'][requiredIndex]
            msgResponse = {'index':str(requiredIndex),'data':nextBuffer}

            #pop the buffer segment off the buffer

            self.archive[msgStatus['msgID']]['index'] = str(requiredIndex)
            return self.makeResponseGeneric(referencedReq, msgResponse)


    def data(self,unpackedReq,msgStatus):
        if 'cookie' not in unpackedReq:
            return self.makeAuthFail(
                unpackedReq
            )
        if 'rawKey' not in self.messages[unpackedReq['msgID']]:
            rawKey = lycanthropy.crypto.kex(self.messages[unpackedReq['msgID']]['acid'], 'ccKey')
            self.messages[unpackedReq['msgID']]['rawKey'] = rawKey
        status,referencedReq = self.makeAuthSuccess(msgStatus)
        if status == 1:
            return referencedReq
        if msgStatus['action'] == 'teardown':
            referencedReq['buffer'] = ast.literal_eval(''.join(msgStatus['buffer']).replace('\n','\\n'))
            referencedReq['secret'] = self.config['secret']

            msgResponse = self.getResponse(referencedReq)
        else:
            msgResponse = '{"streamStatus":"continue"}'
        return self.makeResponseGeneric(msgStatus,msgResponse)

    def getResponse(self, request):
        return lycanthropy.daemon.messager.makeResponse(request,self.gateway)

    def processRequest(self, query):
        # MISSING VERIFICATION STEPS NEED TO BE ADDED
        # MAKE SURE YOU CAN INVALIDATE COOKIES AND ALSO DON'T ALLOW SESSIONS TO BE ARBITRARILY OVERWRITTEN

        # parse out for message type and fields

        acid = None
        unpackedReq = lycanthropy.daemon.parser.dispatchParse(query, self.messages)

        # add new message ids
        if unpackedReq['msgID'] not in self.messages:
            if unpackedReq['type'] != 'kex':
                print(json.dumps({'error':'msgID {} not in message table, backing up from archive'.format(unpackedReq['msgID'])},indent=4))
                try:
                    unpackedReq['nonce'] = self.archive[unpackedReq['msgID']]['nonce']
                except:
                    print(json.dumps({'error':'hit exception while trying to retrieve archived nonce'},indent=4))
                unpackedReq['acid'] = self.archive[unpackedReq['msgID']]['acid']
            self.messages[unpackedReq['msgID']] = unpackedReq
        # convert delimited fields to table


        msgStatus = lycanthropy.daemon.messager.remakeObj(self.messages[unpackedReq['msgID']], unpackedReq)


        processedMessage = self.handlerMap[unpackedReq['type']](unpackedReq,msgStatus)
        if msgStatus['action'] == 'update':
            self.messages[unpackedReq['msgID']] = msgStatus
        elif msgStatus['action'] == 'teardown':
            if unpackedReq['msgID'] in self.messages:
                try:
                    self.messages.pop(unpackedReq['msgID'])
                except KeyError:
                    print(json.dumps({'error':'unable to pop msgID from messages'},indent=4))
        #print('processed:' + processedMessage)
        return processedMessage

    def dns_response(self, data):
        request = DNSRecord.parse(data)
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        #reply = DNSRecord()


        qname = request.q.qname
        qn = str(qname)
        print(qn)
        qtype = request.q.qtype
        qt = QTYPE[qtype]
        qa = qn.split('.')

        #reply.add_question(DNSQuestion(qn))

        try:
            replyData = self.processRequest(
                qa[0:qa.index(
                    self.config['domain']['subdomain']
                )
                ]
            )
        
        except:
            traceback.print_exc()
            replyData = ['::1']

        for rdata in replyData:
            reply.add_answer(RR(rname=qn, rtype=QTYPE.AAAA, rclass=1, ttl=self.TTL, rdata=AAAA(rdata)))
        reply.add_answer(RR(rname=self.D, rtype=QTYPE.SOA, rclass=1, ttl=self.TTL, rdata= self.soa_record))
        return reply.pack()

def runServer(apiBackend):
    global werewolf
    werewolf = coreServer()
    werewolf.gateway = apiBackend
    srvThreads = [socketserver.ThreadingUDPServer(('', 53), UDPRequestHandler)]

    for tObj in srvThreads:
        threadObj = threading.Thread(target=tObj.serve_forever)
        threadObj.daemon = True
        threadObj.start()

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        threadObj.shutdown()
