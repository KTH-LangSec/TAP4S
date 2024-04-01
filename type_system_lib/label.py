import helper_functions as HELPER

class Lattice():
    def __init__(self):
        pass


###################################
class Low(Lattice):
    def __init__(self):
        self.val = 0

    def get_val(self):
        return self.val

    def __str__(self):
        return "LOW"

###################################
class High(Lattice):
    def __init__(self):
        self.val = 1

    def get_val(self):
        return self.val

    def __str__(self):
        return "HIGH"


#########################################################
##################### HELPER METHODS ####################
#########################################################
def lup(*args):
    result = 0
    for lbl in args:
        if issubclass(type(lbl), Lattice):
            result += lbl.get_val()
        else:
            HELPER.error(str(lbl) + " is not a lattice lable")
    
    if (result == 0):
        return Low()
    else:
        return High()