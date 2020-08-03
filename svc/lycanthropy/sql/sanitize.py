import os

def strValidate(string):
    legalChar = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for char in string:
        if char not in legalChar and char not in legalChar.lower():
            return False
    return True
