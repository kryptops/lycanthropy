import os
import lycanthropy.sql.interface

def find(acid):
    config = lycanthropy.sql.interface.filterBuild({'acid': acid})[0]
    campaign = config['campaign']
    return campaign