from enum import Enum
import parser_lib.lval as LVAL
import type_system_lib.types as TYPE
import type_system_lib.label as LATIICE
import logger as LOGGER
import type_system_lib.expression as T_EXP
import parser_lib.expression as P_EXP

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

    def get_keys(self):
        return self.mapping.keys()

    def has_same_domain_as(self, _other):
        return set(self.mapping.keys()) == set(_other.get_keys())

    def __str__(self):
        result = "gamma_G: \n"
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

    def get_keys(self):
        return self.mapping.keys()

    def has_same_domain_as(self, _other):
        return set(self.mapping.keys()) == set(_other.get_keys())

    def __str__(self):
        result = "gamma_L: \n"
        for var in self.mapping.keys():
            result += "\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        return result



############################################################
######################### UPDATE ###########################
############################################################
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

############################################################
########################### JOIN ###########################
############################################################
def join_Gammas(_Gamma_list):
    for i in range(len(_Gamma_list)):
        for j in range(i + 1, len(_Gamma_list)):
            join_gamma(_Gamma_list[i][0], _Gamma_list[j][0])
            join_gamma(_Gamma_list[i][1], _Gamma_list[j][1])

def join_gamma(_gamma_1, _gamma_2):
    if not (_gamma_1.has_same_domain_as(_gamma_2)):
        LOGGER.error("Cannot join two gammas with different domains!")
    else:
        for lval in _gamma_1.get_keys():
            type_1 = _gamma_1.get(lval)
            type_2 = _gamma_2.get(lval)
            join_type(type_1, type_2)
            _gamma_1.update(lval, type_1)
            _gamma_2.update(lval, type_2)


def join_type(_type_1, _type_2):
    if (_type_1.get_type() != _type_2.get_type()):
        LOGGER.error("Cannot join, the lvals in the gammas have different types!")
    else:      
        match _type_1.get_type():
            case TYPE.TypesEnum.BOOL:
                if (_type_1.get_label().is_high() or _type_2.get_label().is_high()):
                    _type_1.raise_label(LATIICE.High())
                    _type_2.raise_label(LATIICE.High())

            case TYPE.TypesEnum.BIT_STRING:
                if (_type_1.has_same_slices_as(_type_2)):
                    for i, slc in enumerate(_type_1.get_slices()):
                        if (slc.get_label().is_high() or _type_2.get_slice(i).get_label().is_high()):
                            slc.raise_label(LATIICE.High())
                            _type_2.get_slice(i).raise_label(LATIICE.High())
                else:
                    LOGGER.warning("join two bit-strings with different slices, highly overapproximating.")
                    # TODO: can we make it better?
                    if (_type_1.get_label().is_high() or _type_2.get_label().is_high()):
                        _type_1.raise_label(LATIICE.High())
                        _type_2.raise_label(LATIICE.High())

            case TYPE.TypesEnum.STRUCT:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.warning("join two structs with different fields, highly overapproximating.")
                    # TODO: can we make it better?
                    if (_type_1.get_label().is_high() or _type_2.get_label().is_high()):
                        _type_1.raise_label(LATIICE.High())
                        _type_2.raise_label(LATIICE.High())

            case TYPE.TypesEnum.HEADER:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.warning("join two headers with different fields, highly overapproximating.")
                    # TODO: can we make it better?
                    if (_type_1.get_label().is_high() or _type_2.get_label().is_high()):
                        _type_1.raise_label(LATIICE.High())
                        _type_2.raise_label(LATIICE.High())


##############################################################
############################# ++ #############################
##############################################################
def augment(_gamma_l, _gamma_t, _args):
    for lval in _gamma_t.get_keys():
        if lval in _args:
            _gamma_l.update(lval, _gamma_t.get(lval))
        else:
            LOGGER.warning("extern contract wants to update the type of \"" + str(lval) +"\", but is not an aurgument of it!")


##############################################################
########################### REFINE ###########################
##############################################################
def refine_cond(_gamma_g, _gamma_l, _exp):
    exp_type = T_EXP.type_check_expression(_exp, _gamma_g, _gamma_l)

    if (exp_type.is_false()):
        return None
    else:
        return_Gamma = []
        if (_exp.get_type() == P_EXP.ExpressionEnum.BINARY):
            if (not _exp.is_simple()):
                LOGGER.warning("We do not support refininment based on complex binary expressions!, eg: " + str(_exp))
                return_Gamma.append((_gamma_g, _gamma_l)) # return without any modifications
            else:
                refined_Gammas = T_EXP.refine_expression(_exp, _gamma_g, _gamma_l)
                return_Gamma.extend(refined_Gammas)
                
            
        return return_Gamma

###############################################################
def refine_trans(_gamma_g, _gamma_l, _exp, _vals):
    LOGGER.warning("Trans Refine is not implemented yet!")
    # TODO: implement
    res = []
    for i in _vals:
        res.append((copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l)))
    res.append((copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))) # default
    return res