import os
import lycanthropy.sql.interface

def find(acid):
    config = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    campaign = config['campaign']
    return campaign

def findTemp(acid):
    config = lycanthropy.sql.interface.filterBuild({'tempAcid': acid})[0]
    acid = config['acid']
    return acid
