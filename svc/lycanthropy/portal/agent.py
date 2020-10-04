import base64
import lycanthropy.sql.interface

def derive(epoch,acid,keyType):

    raw = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    derivedBytes = ''.join(
        chr(
            ord(a) ^ ord(b)
        ) for a,b in zip(
            str(
                epoch
            ),
            raw[keyType]
        )
    ).encode('utf-8')
    return base64.urlsafe_b64encode(derivedBytes).decode('utf-8')

def verify(acid,key,keyType):
    for skewer in lycanthropy.auth.cookie.skew():

        if derive(skewer,acid,keyType) == key:
            return True
    return False