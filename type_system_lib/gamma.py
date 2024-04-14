from enum import Enum
import parser_lib.lval as LVAL
import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL
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
            ret_type = lookup(_lval, _gamma_g, _gamma_l)

            match _type.get_type():
                case TYPE.TypesEnum.BIT_STRING:
                    slices = []
                    lower = _lval.get_lower_index()
                    upper = _lval.get_upper_index()
                    for slc in ret_type.get_slices():
                        s_start, s_end = slc.get_slice_indices()
                        if (s_start == lower) or (s_end == upper):
                            slices.extend(_type.get_slices())
                        else:
                            slices.append(slc)

                    new_type = TYPE.BitString(ret_type.get_size(), _slices=slices)
                    update(_lval.get_lval(), new_type, _gamma_g, _gamma_l)
                case _:
                    LOGGER.error("assigning non-bit-strings to slices is NOT supported!")

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
            lval = _lval.get_lval()
            lval_type = lookup(lval, _gamma_g, _gamma_l)
            if (lval_type.get_type() == TYPE.TypesEnum.BIT_STRING):
                slices = []
                lower = _lval.get_lower_index()
                upper = _lval.get_upper_index()

                if (upper >= lval_type.get_size()) or (lower < 0):
                    LOGGER.error("slicing index (" + str(lower) + "," + str(upper) + ") is out of bound!")

                temp_type = copy.deepcopy(lval_type)
                if (lower > 0):
                    first_part_type = temp_type.consume_sub_string(lower)
                    slices.extend(first_part_type.get_slices())
                slice_type = temp_type.consume_sub_string(upper-lower+1)
                slices.extend(slice_type.get_slices())
                slices.extend(temp_type.get_slices())

                return TYPE.BitString(lval_type.get_size(), _slices=slices)
            else:
                LOGGER.error("slicing is only supported for bit-strings!")


            LOGGER.error("lookup slicing!")
            pass # TODO SLICE

############################################################
################## LABEL JOIN $\sqcup$ #####################
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
        LOGGER.error("Cannot join types " + str(_type_1.get_type()) + " and " + str(_type_2.get_type()) + " !")
    else:      
        match _type_1.get_type():
            case TYPE.TypesEnum.BOOL:
                if (_type_1.get_label().is_high() or _type_2.get_label().is_high()):
                    _type_1.raise_label(LATIICE.High())
                    _type_2.raise_label(LATIICE.High())

            case TYPE.TypesEnum.BIT_STRING:
                if (_type_1.get_size() == _type_2.get_size()): # the lengths are the same
                    if (_type_1.has_same_slices_as(_type_2)):
                        for i, slc in enumerate(_type_1.get_slices()):
                            if (slc.get_label().is_high() or _type_2.get_slice(i).get_label().is_high()):
                                slc.raise_label(LATIICE.High())
                                _type_2.get_slice(i).raise_label(LATIICE.High())
                    else:
                        LOGGER.warning("joining two bit-strings with different slices is highly overapproximating.")

                        for slc_1 in _type_1.get_slices():
                            overlaps = _type_2.get_overlapping_slices(slc_1)
                            overlap_label = LATIICE.Low()
                            for ovr in overlaps:
                                overlap_label = LATIICE.lup(overlap_label, ovr.get_label())
                            slc_1.raise_label(overlap_label)

                        for slc_2 in _type_2.get_slices():
                            overlaps = _type_1.get_overlapping_slices(slc_2)
                            overlap_label = LATIICE.Low()
                            for ovr in overlaps:
                                overlap_label = LATIICE.lup(overlap_label, ovr.get_label())
                            slc_2.raise_label(overlap_label)
                else: # the lengths are NOT the same
                    LOGGER.warning("joining two bit-strings with different lengths is highly overapproximating.")

                    for slc_1 in _type_1.get_slices():
                        overlaps = _type_2.get_overlapping_slices(slc_1)
                        overlap_label = LATIICE.Low()
                        for ovr in overlaps:
                            overlap_label = LATIICE.lup(overlap_label, ovr.get_label())
                        slc_1.raise_label(overlap_label)

                    for slc_2 in _type_2.get_slices():
                        overlaps = _type_1.get_overlapping_slices(slc_2)
                        overlap_label = LATIICE.Low()
                        for ovr in overlaps:
                            overlap_label = LATIICE.lup(overlap_label, ovr.get_label())
                        slc_2.raise_label(overlap_label)


            case TYPE.TypesEnum.STRUCT:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.error("join two structs with different fields is not supported!")

            case TYPE.TypesEnum.HEADER:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.warning("join two headers with different fields is not supported!")


##############################################################
############################# ++ #############################
##############################################################
def augment(_gamma_g, _gamma_l, _gamma_t, _args):
    for lval in _gamma_t.get_keys():
        match lval.get_type():
            case LVAL.LvalEnum.VARIABLE:
                if lval in _args:
                    update(lval, _gamma_t.get(lval), _gamma_g, _gamma_l)
                else:
                    LOGGER.warning("an extern contract wants to update the type of variable \"" + str(lval) +"\", but is not an aurgument of it!")
            
            case LVAL.LvalEnum.ACCESS:
                # TODO add check to ensure updated lval is actualy a passed argument
                update(lval, _gamma_t.get(lval), _gamma_g, _gamma_l)

            case LVAL.LvalEnum.SLICE:
                pass # TODO implement


##############################################################
############################ SAT #############################
##############################################################
def is_sat(_gamma_g, _gamma_l, _exp):
    exp_type = T_EXP.type_check_expression(_exp, _gamma_g, _gamma_l)

    if (exp_type.is_false()):
        return False
    else:
        return True

##############################################################
########################### REFINE ###########################
##############################################################
def refine(_gamma_g, _gamma_l, _exp):
    exp_type = T_EXP.type_check_expression(_exp, _gamma_g, _gamma_l)

    if (exp_type.is_false()):
        return None
    elif (exp_type.is_true()):
        return [(_gamma_g, _gamma_l)]
    else:
        return_Gamma = []
        if (_exp.get_type() == P_EXP.ExpressionEnum.BINARY):
            if (_exp.is_simple()):
                refined_Gammas = T_EXP.refine_expression(_exp, _gamma_g, _gamma_l)
                return_Gamma.extend(refined_Gammas)
            else:
                if (_exp.get_op() == "&&"):
                    lhs_Gamma = T_EXP.refine_expression(_exp.get_lhs(), _gamma_g, _gamma_l)
                    for (gg, gl) in lhs_Gamma:
                        refined_Gammas = T_EXP.refine_expression(_exp.get_rhs(), gg, gl)
                        return_Gamma.extend(refined_Gammas)
                elif (_exp.get_op() == "||"):
                    lhs_Gamma = T_EXP.refine_expression(_exp.get_lhs(), _gamma_g, _gamma_l)
                    rhs_Gamma = T_EXP.refine_expression(_exp.get_rhs(), _gamma_g, _gamma_l)
                    return_Gamma.extend(lhs_Gamma)
                    return_Gamma.extend(rhs_Gamma)
                else:
                    LOGGER.warning("Cannot refine by the expression: " + str(_exp))
                    return_Gamma.append((_gamma_g, _gamma_l)) # return without any modifications
                
                
        return return_Gamma

###############################################################
def refine_trans(_gamma_g, _gamma_l, _exp, _vals):
    if (len(_vals) == 0):
        return [(copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))]

    else:
        neg_expressions = []
        res = []
        for val in _vals:
            exp = P_EXP.BinaryOP(_exp, "==", val)
            neg_expressions.append(P_EXP.negate(exp))
            res.extend(refine(_gamma_g, _gamma_l, exp))

        # Default
        default_Gamma = []
        nexp = neg_expressions[0]
        default_Gamma = refine(_gamma_g, _gamma_l, nexp)
        for i in range(1, len(neg_expressions)):
            nexp = neg_expressions[i]
            temp_Gamma = []
            for (gg, gl) in default_Gamma:
                temp_Gamma.extend(refine(gg, gl, nexp))
            default_Gamma = temp_Gamma
        
        res.extend(default_Gamma)

        return res


###############################################################
def union(_gamma_1, _gamma_2):
    for var in _gamma_1.get_keys():
        if _gamma_2.exists(var) and _gamma_2.get(var).get_type() != _gamma_1.get(var).get_type():
            LOGGER.error("Cannot support same variables with diffrent types when unioning Gammas!")
    
    for var in _gamma_2.get_keys():
        if _gamma_1.exists(var) and _gamma_1.get(var).get_type() != _gamma_2.get(var).get_type():
            LOGGER.error("Cannot support same variables with diffrent types when unioning Gammas!")
                        
    if (not _gamma_1.has_same_domain_as(_gamma_2)):
        for var in _gamma_2.get_keys():
            if not _gamma_1.exists(var):
                _gamma_1.add(var, _gamma_2.get(var))




############################################################
############### INTERVAL INTERSET $\cap$ ###################
############################################################
def intersect_Gammas(_Gamma_list):
    result = []
    for i in range(len(_Gamma_list)):
        for j in range(len(_Gamma_list)):
            if (i != j):
                (gg_1, gg_2) = intersect_gamma(_Gamma_list[i][0], _Gamma_list[j][0])
                if (gg_1 != None) and (gg_2 != None):
                    (gl_1, gl_2) = intersect_gamma(_Gamma_list[i][1], _Gamma_list[j][1])
                    if (gl_1 != None) and (gl_2 != None):
                        result.append((gg_1, gl_1)) # to avoid duplication, just the first gammas are added
                    else:
                        return []
                else:
                    return [] 

    return result
            

def intersect_gamma(_gamma_1, _gamma_2):
    if not (_gamma_1.has_same_domain_as(_gamma_2)):
        LOGGER.error("Cannot intersect two gammas with different domains!")
    else:
        cp_gamma_1 = copy.deepcopy(_gamma_1)
        cp_gamma_2 = copy.deepcopy(_gamma_2)
        for lval in cp_gamma_1.get_keys():
            type_1 = cp_gamma_1.get(lval)
            type_2 = cp_gamma_2.get(lval)
            t1, t2 = intersect_type(type_1, type_2)
            if (t1 != None) and (t2 != None):
                cp_gamma_1.update(lval, t1)
                cp_gamma_2.update(lval, t2)
            else:
                return (None, None)

        return (cp_gamma_1, cp_gamma_2)


def intersect_type(_type_1, _type_2):
    if (_type_1.get_type() != _type_2.get_type()):
        LOGGER.warning("intersect of " + str(_type_1.get_type()) + " and " + str(_type_2.get_type()) + " will be empty!")
        return (None, None)
    else:
        match _type_1.get_type():
            case TYPE.TypesEnum.BOOL:
                interval_1 = _type_1.get_interval()
                interval_2 = _type_2.get_interval()
                intersect_interval = INTERVAL.intersect(interval_1, interval_2)
                if (intersect_interval != None):
                    _type_1.set_interval(intersect_interval)
                    _type_2.set_interval(intersect_interval)
                    return(_type_1, _type_2)
                else:
                    return (None, None)

            case TYPE.TypesEnum.BIT_STRING:
                if (_type_1.get_size() == _type_2.get_size()): # the lengths are the same
                    if (_type_1.has_same_slices_as(_type_2)):
                        for i, slc in enumerate(_type_1.get_slices()):
                            interval_1 = slc.get_interval()
                            interval_2 = _type_2.get_slice(i).get_interval()
                            intersect_interval = INTERVAL.intersect(interval_1, interval_2)
                            
                            if (intersect_interval == None): # check if there is actually any intersection
                                return (None, None)
                            slc.set_interval(intersect_interval)
                            _type_2.get_slice(i).set_interval(intersect_interval)

                        return(_type_1, _type_2)
                    else:
                        LOGGER.warning("intersect of two bit-strings with different slices is highly overapproximating!")
                        size = _type_1.get_size()
                        intersect_interval = INTERVAL.Interval(0, ((2 ** size) - 1), size)
                        if (intersect_interval == None): # check if there is actually any intersection
                            return (None, None)
                        
                        label_1 = _type_1.get_label()
                        slice_1 = TYPE.Slice(0, size-1, intersect_interval, label_1)
                        _type_1.update_slices([slice_1])

                        label_2 = _type_2.get_label()
                        slice_2 = TYPE.Slice(0, size-1, intersect_interval, label_2)
                        _type_2.update_slices([slice_2])

                        return(_type_1, _type_2)
                else: # the lengths are NOT the same
                    LOGGER.warning("intersect of two bit-strings with different lengths will be empty!")
                    return (None, None)


            case TYPE.TypesEnum.STRUCT:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.warning("intersect of two two structs with different fields will be empty!")
                    return (None, None)

            case TYPE.TypesEnum.HEADER:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    for name, fld in _type_1.get_fields():
                        join_type(fld, _type_2.get_field(name))
                else:
                    LOGGER.warning("intersect of two two headers with different fields will be empty!")
                    return (None, None)