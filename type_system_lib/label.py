import logger as LOGGER

class Lattice():
    def __init__(self):
        pass


###################################
class Low(Lattice):
    def __init__(self):
        self.val = 0

    def get_val(self):
        return self.val
    
    def is_high(self):
        return False
    def is_low(self):
        return True

    def is_below(self, _other_label):
        return True

    def __str__(self):
        return "LOW"

###################################
class High(Lattice):
    def __init__(self):
        self.val = 1

    def get_val(self):
        return self.val

    def is_high(self):
        return True
    def is_low(self):
        return False

    def is_below(self, _other_label):
        if _other_label.is_low():
            return False
        else:
            return True

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
            LOGGER.error(str(lbl) + " is not a lattice lable")
    
    if (result == 0):
        return Low()
    else:
        return High()