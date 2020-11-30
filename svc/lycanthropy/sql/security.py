
def chkAcid(acid):
    acidLegals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    if len(acid) == 8:
        for ch in acid:
            if ch not in acidLegals:
                return False
        return True
    else:
        return False

def chkJobid(jobID):
    randAlpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    legalLength = 6
    if 'ROTID' in jobID:
        legalLength = 11
    if len(jobID) == legalLength:
        for ch in jobID:
            if ch not in randAlpha:
                return False
        return True
    else:
        return False

def chkOpid(opID):
    opidLegals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
    legalLength = 15
    if len(opID) <= legalLength:
        for ch in opID:
            if ch not in opidLegals:
                return False
        return True
    else:
        return False