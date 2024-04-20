import sys
import setting


def error(_input):
    print(">>> ERROR: "+ str(_input))
    sys.exit()

def warning(_input):
    if setting.show_warnings:
        print(">>> WARNING: "+ str(_input))

def debug(_input):
    if setting.debug:
        print(_input)