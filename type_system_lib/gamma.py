from enum import Enum
import parser_lib.lval as LVAL
import helper_functions as HELPER
import copy

class GammaEnum(Enum):
    LOCAL = 1
    GLOBAL = 2

class Gamma():
    def __init__(self, _type):
        self.type = _type

###########################################################
class GlobalGamma(Gamma):
    def __init__(self):
        super().__init__(GammaEnum.GLOBAL) 
        self.mapping = {}

    def add(self, _var, _type):
        self.mapping[_var] = _type
    def update(self, _var, _type):
        self.mapping[_var] = _type

    def get(self, _var):
        return copy.deepcopy(self.mapping[_var])

    def exists(self, _key):
        if self.mapping.get(_key) is not None:
            return True
        else:
            return False

    def __str__(self):
        result = "Gamma_G: \n"
        for var in self.mapping.keys():
            result += "\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        return result

###########################################################
class LocalGamma(Gamma):
    def __init__(self):
        super().__init__(GammaEnum.LOCAL) 
        self.mapping = {}

    def add(self, _var, _type):
        self.mapping[_var] = _type
    def update(self, _var, _type):
        self.mapping[_var] = _type

    def get(self, _var):
        return copy.deepcopy(self.mapping[_var])

    def exists(self, _key):
        if self.mapping.get(_key) is not None:
            return True
        else:
            return False


    def __str__(self):
        result = "Gamma_L: \n"
        for var in self.mapping.keys():
            result += "\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        return result



############## HELPER FUNCTIONS ########################
def update(_lval, _type, _gamma_g, _gamma_l):
    match _lval.get_type():
        case LVAL.LvalEnum.VARIABLE:
            if _gamma_l.exists(_lval):
                    _gamma_l.update(_lval, _type)
            elif _gamma_g.exists(_lval):
                    _gamma_g.update(_lval, _type)

        case LVAL.LvalEnum.ACCESS:
            (lval, x) = _lval.remove_first()
            ret_type = lookup(lval, _gamma_g, _gamma_l)
            ret_type.update_field(x, _type)
            update(lval, ret_type, _gamma_g, _gamma_l)

        case LVAL.LvalEnum.SLICE:
            pass # TODO

def lookup(_lval, _gamma_g, _gamma_l):
    match _lval.get_type():
        case LVAL.LvalEnum.VARIABLE:
            if _gamma_l.exists(_lval):
                return _gamma_l.get(_lval)
            elif _gamma_g.exists(_lval):
                return _gamma_g.get(_lval)
        
        case LVAL.LvalEnum.ACCESS:
            (lval, x) = _lval.remove_first()
            ret_type = lookup(lval, _gamma_g, _gamma_l)
            return ret_type.get_field(x)
        
        case LVAL.LvalEnum.SLICE:
            pass # TODO

###############################################################
def cup(*args):
    res_Gamma = []
    for Gamma in args:
        res_Gamma.extend(Gamma)

    return res_Gamma

###############################################################
def refine(_gamma_g, _gamma_l, _phi):
    HELPER.warning("refine is not implemented yet!")
    # TODO: implement
    return (copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))