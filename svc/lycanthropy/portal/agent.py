import base64
import lycanthropy.sql.interface
import lycanthropy.auth.cookie

def verify(acid,key,keyType):
    raw = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    for skewer in lycanthropy.auth.cookie.skew():
        if lycanthropy.auth.cookie.derive(raw[keyType],skewer) == key:
            return True
    return False
    #for skewer in lycanthropy.auth.cookie.skew():
    #    derivedKey = derive(skewer,acid,keyType)
    #    if derivedKey == key:
    #        return True
    #return False

def derive(acid,keyType):
    print(lycanthropy.sql.interface.filterBuild({'acid': acid}))
    raw = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    return base64.urlsafe_b64encode(raw[keyType].encode('utf-8')).decode('utf-8')



