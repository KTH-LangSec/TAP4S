import sys


def error(_input):
    print(">>> ERROR: "+ str(_input))
    sys.exit()

def warning(_input):
    print(">>> WARNING: "+ str(_input))