import random
import json

def generateName():
    generatorConf = json.load(open('../etc/names.json'))
    pref = random.choice(generatorConf['prefix'])
    suff = random.choice(generatorConf['suffix'])
    return (pref+suff).upper()

