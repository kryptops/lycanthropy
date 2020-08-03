import base64
import binascii
import lycanthropy.crypto
import lycanthropy.portal.api


class protoDefs():
    def __init__(self):
        self.functionMap = [
            self.data,
            self.auth,
            self.dist,
            self.heartbeat,
            self.kex,
            self.ctrl,
            self.conf
        ]

    def kex(self,q,msgTable):
        return {
            'nonce':q[0],
            'acid':q[1],
            'checksum':q[2],
            'type':'kex',
            'msgID':q[4]
        }


    def data(self,q,msgTable):
        return {
            'cookie':q[0],
            'segment':lycanthropy.crypto.dance(
                1,
                base64.b64decode(q[1]),
                base64.b64decode(lycanthropy.crypto.kex(
                    msgTable[q[5]]['acid'],
                    'ccKey'
                )),
                msgTable[q[5]]['nonce'].encode('utf-8')
            ).decode('utf-8'),
            'part':q[2],
            'length':q[3],
            'type':'data',
            'msgID':q[5]
        }

    def auth(self,q,msgTable):
        return {
            'password':q[0],
            'acid':q[1],
            'type':'auth',
            'msgID':q[3]
        }

    def ctrl(self,q,msgTable):
        return {
            'cookie':q[0],
            'ctrlKey':q[1],
            'type':'ctrl',
            'msgID':q[3]
        }

    def dist(self,q,msgTable):
        return {
            'cookie':q[0],
            'distKey':q[1],
            'pkgID':q[2],
            'type':'dist',
            'msgID':q[4]
        }

    def heartbeat(self,q,msgTable):
        return {
            'cookie':q[0],
            'type':'heartbeat',
            'msgID':q[3]
        }

    def conf(self,q,msgTable):
       return {
           'cookie': q[0],
           'confKey': q[1],
           'type': 'conf',
           'msgID': q[3]
       }

def parseIdentify(q):
    query = ''.join(q)
    unwrapped = binascii.unhexlify(query)
    return unwrapped.decode('utf-8').split('.')

def dispatchParse(q,msgTable):
    splitReq = parseIdentify(q)
    return protoDefs().functionMap[int(splitReq[-2])](splitReq,msgTable)
