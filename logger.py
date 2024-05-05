import sys
import setting


def error(_input):
    print_red(">>> ERROR: "+ str(_input))
    sys.exit()

def warning(_input):
    if setting.show_warnings:
        print_yellow(">>> WARNING: "+ str(_input))

#################################
def print_red(text, end='\n'):
    print("\033[91m" + text + "\033[0m", end=end)

def print_yellow(text, end='\n'):
    print("\033[93m" + text + "\033[0m", end=end)

def print_blue(text, end='\n'):
    print("\033[94m" + text + "\033[0m", end=end)

def print_green(text, end='\n'):
    print("\033[92m" + text + "\033[0m", end=end)

