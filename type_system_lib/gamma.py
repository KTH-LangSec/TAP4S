from enum import Enum
import parser_lib.lval as LVAL
import type_system_lib as TS
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

        self.validity = True

    def invalidate(self):
        self.validity = False
    def is_valid(self):
        return self.validity

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

    def project(self, _keys_to_keep):
        return_gamma = GlobalGamma()
        for key, value in self.mapping.items():
            if key in _keys_to_keep:
                return_gamma.add(key, value)
        return return_gamma

    def serialize(self):
        return_gamma = GlobalGamma()
        for key, value in self.mapping.items():
            bs_type = TS.convert_to_bs(value)
            return_gamma.add(key, bs_type)

        return return_gamma


    def __str__(self):
        #result = "gamma_G: \n"
        result = ""
        for var in self.mapping.keys():
            result += "\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        #result += "\n\tIs Valid: " + str(self.validity) + "\n"
        return result

###########################################################
class LocalGamma(Gamma):
    def __init__(self):
        super().__init__(GammaEnum.LOCAL) 
        self.mapping = {}

        self.validity = True

    def invalidate(self):
        self.validity = False
    def is_valid(self):
        return self.validity

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
    
    def project(self, _keys_to_keep):
        return_gamma = LocalGamma()
        for key, value in self.mapping.items():
            if key in _keys_to_keep:
                return_gamma.add(key, value)
        return return_gamma

    def serialize(self):
        return_gamma = LocalGamma()
        for key, value in self.mapping.items():
            bs_type = TS.convert_to_bs(value)
            return_gamma.add(key, bs_type)
        return return_gamma

    def __str__(self):
        #result = "gamma_L: \n"
        result = ""
        for var in self.mapping.keys():
            result += "\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        #result += "\n\tIs Valid: " + str(self.validity) + "\n"
        return result



############################################################
######################### Update ###########################
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
######################## Join ⊔ ############################
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
                        LOGGER.warning("---- joining " + str(_type_1))
                        LOGGER.warning("---- and " + str(_type_2))

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
                    if (_type_1.get_size() == 0):
                        _type_1 = copy.deepcopy(_type_2)
                    elif (_type_2.get_size() == 0):
                        _type_2 = copy.deepcopy(_type_1)
                    else:
                        LOGGER.warning("joining two bit-strings with different lengths is highly overapproximating.")
                        LOGGER.warning("---- joining " + str(_type_1))
                        LOGGER.warning("---- and " + str(_type_2))

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
                    LOGGER.error("join two headers with different fields is not supported!")


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
######################### Refinement #########################
##############################################################
def refine(_gamma_g, _gamma_l, _exp, _label):
    exp_type = T_EXP.type_check_expression(_exp, _gamma_g, _gamma_l)

    if (exp_type.is_false()):
        if (_label.is_low()):
            return None
        else:
            return invalidate_gammas(refinement(_gamma_g, _gamma_l, _exp))
    elif (exp_type.is_true()):
        return [(copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))]
    else:
        return refinement(_gamma_g, _gamma_l, _exp)


############# Transition
def refine_trans(_gamma_g, _gamma_l, _exp, _vals, _states, _default_state, _label):
    res = {}

    if (len(_vals) == 0):
        res[_default_state] = [(copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))]
        return res

    else:
        neg_expressions = []
        for i, val in enumerate(_vals):
            exp = P_EXP.BinaryOP(_exp, "==", val)
            neg_expressions.append(P_EXP.negate(exp))
            temp_Gamma = refine(_gamma_g, _gamma_l, exp, _label)
            if (temp_Gamma != None):
                res[_states[i]] = temp_Gamma

        # Default
        nexp = neg_expressions[0]
        default_Gamma = refine(_gamma_g, _gamma_l, nexp, _label)
        if (default_Gamma != None):
            for i in range(1, len(neg_expressions)):
                nexp = neg_expressions[i]
                temp_Gamma = []
                for (gg, gl) in default_Gamma:
                    ref_Gamma = refine(gg, gl, nexp, _label)
                    if (ref_Gamma != None):
                        temp_Gamma.extend(ref_Gamma)
                default_Gamma = temp_Gamma
        
            res[_default_state] = default_Gamma

        return res

############# Actual refinement
def refinement(_gamma_g, _gamma_l, _exp):
    return_Gamma = []
    if (_exp.get_type() == P_EXP.ExpressionEnum.BINARY):
        if (_exp.is_simple()):
            refined_Gammas = T_EXP.refine_expression(_exp, _gamma_g, _gamma_l)
            return_Gamma.extend(refined_Gammas)
        else:
            if (_exp.get_op() == "&&"):
                lhs_Gamma = refinement(_gamma_g, _gamma_l, _exp.get_lhs())
                for (gg, gl) in lhs_Gamma:
                    refined_Gammas = refinement(gg, gl, _exp.get_rhs())
                    return_Gamma.extend(refined_Gammas)
            elif (_exp.get_op() == "||"):
                lhs_Gamma = refinement(_gamma_g, _gamma_l, _exp.get_lhs())
                rhs_Gamma = refinement(_gamma_g, _gamma_l, _exp.get_rhs())
                return_Gamma.extend(lhs_Gamma)
                return_Gamma.extend(rhs_Gamma)
            else:
                LOGGER.warning("Cannot refine by the expression: " + str(_exp))
                return_Gamma.append((copy.deepcopy(_gamma_g), copy.deepcopy(_gamma_l))) # return without any modifications
            
    return return_Gamma


############################################################
###################### Intersect ∩ #########################
############################################################
def is_gamma_intersect_empty(_gamma_1, _gamma_2):
    if not (_gamma_1.has_same_domain_as(_gamma_2)):
        p_gamma_1 = _gamma_1.project(_gamma_2.get_keys())
        p_gamma_2 = _gamma_2.project(_gamma_1.get_keys())
        return is_gamma_intersect_empty(p_gamma_1, p_gamma_2)
    else:
        for lval in _gamma_1.get_keys():
            type_1 = _gamma_1.get(lval)
            type_2 = _gamma_2.get(lval)
            if is_type_intersect_empty(type_1, type_2):
                return True

        return False


def is_type_intersect_empty(_type_1, _type_2):
    if (_type_1.get_type() != _type_2.get_type()):
        return True
    else:
        match _type_1.get_type():
            case TYPE.TypesEnum.BOOL:
                interval_1 = _type_1.get_interval()
                interval_2 = _type_2.get_interval()
                intersect_interval = INTERVAL.intersect(interval_1, interval_2)

                if (intersect_interval == None):
                    return True
                else:
                    return False

            case TYPE.TypesEnum.BIT_STRING:
                if (_type_1.get_size() == _type_2.get_size()): # the lengths are the same
                    if (_type_1.has_same_slices_as(_type_2)):
                        for i, slc in enumerate(_type_1.get_slices()):
                            interval_1 = slc.get_interval()
                            interval_2 = _type_2.get_slice(i).get_interval()
                            intersect_interval = INTERVAL.intersect(interval_1, interval_2)
                            
                            if (intersect_interval == None): # check if there is actually any intersection
                                return True

                        return False
                    
                    else:
                        for i, slc in enumerate(_type_1.get_slices()):
                            overlaps = _type_2.get_overlapping_slices(slc)

                            if (len(overlaps) <= 0):
                                return True
                            
                            elif (len(overlaps) == 1):
                                s_start, s_end = slc.get_slice_indices()
                                o_start, o_end = overlaps[0].get_slice_indices()
                                if (s_start == o_start) and (s_end == o_end):
                                    interval_1 = slc.get_interval()
                                    interval_2 = overlaps[0].get_interval()
                                    intersect_interval = INTERVAL.intersect(interval_1, interval_2)
                            
                                    if (intersect_interval == None): # check if there is actually any intersection
                                        return True
                                    

                                else: # slicing
                                    if (is_empty_intersect_sub_slice(slc, overlaps[0]) == True):
                                        return True
                                    

                            else:
                                for overlap in overlaps:
                                    if (is_empty_intersect_sub_slice(slc, overlap) == True):
                                        return True

                        return False
                    
                else: 
                    # the lengths are NOT the same
                    # intersect of two bit-strings with different lengths will be empty!
                    # Since they are technichally diffrent types
                    # return True

                    # ABSTRACTION 
                    if (_type_1.get_size() > _type_2.get_size()):
                        trimmed_type = _type_1.consume_sub_string(_type_2.get_size())
                        return is_type_intersect_empty(trimmed_type, _type_2)
                    else:
                        trimmed_type = _type_2.consume_sub_string(_type_1.get_size())
                        return is_type_intersect_empty(_type_1, trimmed_type)


            case TYPE.TypesEnum.STRUCT:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    result = False
                    for name, fld in _type_1.get_fields():
                        result = result or is_type_intersect_empty(fld, _type_2.get_field(name))
                    return result
                else:
                    # intersect of two two structs with different fields will be empty!
                    return True

            case TYPE.TypesEnum.HEADER:
                if (_type_1.has_the_same_fields_as(_type_2)):
                    result = False
                    for name, fld in _type_1.get_fields():
                        result = result or is_type_intersect_empty(fld, _type_2.get_field(name))
                    return result
                else:
                    # intersect of two two headers with different fields will be empty!
                    return True


###### helper ######
def is_empty_intersect_sub_slice(_slc, _overlap):
    s_start, s_end = _slc.get_slice_indices()
    o_start, o_end = _overlap.get_slice_indices()

    if o_start == s_start:
        start = o_start
        _, start_split_slc = _slc.split(0)
        _, start_split_overlap = _overlap.split(0)
    elif o_start > s_start:
        start = o_start
        _, start_split_slc = _slc.split(start)
        _, start_split_overlap = _overlap.split(0)
    else:
        start = s_start
        _, start_split_slc = _slc.split(0)
        _, start_split_overlap = _overlap.split(start)

    if o_end == s_end:
        end_split_slc = start_split_slc
        end_split_overlap = start_split_overlap
    elif o_end > s_end:
        end = s_end - start + 1
        end_split_slc = start_split_slc
        end_split_overlap, _ = start_split_overlap.split(end)
    else:
        end = o_end - start + 1
        end_split_slc, _ = start_split_slc.split(end)
        end_split_overlap = start_split_overlap

    interval_1 = end_split_slc.get_interval()
    interval_2 = end_split_overlap.get_interval()
    intersect_interval = INTERVAL.intersect(interval_1, interval_2)

    if (intersect_interval == None): # check if there is actually any intersection
        return True
    
    return False

############################################################
###################### Ordering ⊑ ##########################
############################################################
def is_below(_gamma_left, _gamma_right):
    gamma_left = _gamma_left.project(_gamma_right.get_keys())

    if not (_gamma_right.has_same_domain_as(gamma_left)):
        LOGGER.print_red("cannot check γ_g ⊑ γ_o -- there are some variables in \"γ_o\" that are not in \"γ_g\"!")
        return False
    else:
        for lval in gamma_left.get_keys():
            type_left = gamma_left.get(lval)
            type_right = _gamma_right.get(lval)
            if not is_type_below(type_left, type_right):
                return False

        return True

def is_type_below(_type_left, _type_right):
    if (_type_left.get_type() != _type_right.get_type()):
        if _type_left.get_label().is_below(_type_right.get_label()):
            return True
        else:
            LOGGER.print_red("The types are NOT the same!")
            LOGGER.print_red(str(_type_left))
            LOGGER.print_red("\u2291\u0338")
            LOGGER.print_red(str(_type_right))
            return False
    else:
        match _type_left.get_type():
            case TYPE.TypesEnum.BOOL:
                result = _type_left.get_label().is_below(_type_right.get_label())
                if not result:
                    LOGGER.print_red(str(_type_left) + " \u2291\u0338 " + str(_type_right) + "\n")
                return result

            case TYPE.TypesEnum.BIT_STRING:
                if (_type_left.get_size() == _type_right.get_size()): # the lengths are the same
                    if (_type_left.has_same_slices_as(_type_right)):
                        for i, slc in enumerate(_type_left.get_slices()):
                            lebel_left = slc.get_label()
                            lebel_right = _type_right.get_slice(i).get_label()
                            
                            if (not lebel_left.is_below(lebel_right)):
                                LOGGER.print_red(str(slc) + " \u2291\u0338 " + str(_type_right.get_slice(i)) + "\n")
                                return False

                        return True
                    
                    else:
                        for i, slc in enumerate(_type_left.get_slices()):
                            overlaps = _type_right.get_overlapping_slices(slc)

                            if (len(overlaps) <= 0):
                                LOGGER.print_red("For slice " + str(slc) + " no overlap was found in the " + str(_type_right))
                                return False
                            else:
                                for overlap in overlaps:
                                    if (not slc.get_label().is_below(overlap.get_label())):
                                        LOGGER.print_red(str(slc) + " \u2291\u0338 " + str(overlap) + "\n")
                                        return False

                        return True
                    
                else: # the lengths are NOT the same
                    if _type_left.get_label().is_below(_type_right.get_label()):
                        return True
                    else:
                        LOGGER.print_red("The lengths of bit-strings is NOT the same")
                        LOGGER.print_red(str(_type_left))
                        LOGGER.print_red("\u2291\u0338")
                        LOGGER.print_red(str(_type_right))
                        return False


            case TYPE.TypesEnum.STRUCT:
                if (_type_left.has_the_same_fields_as(_type_right)):
                    result = True
                    for name, fld in _type_left.get_fields():
                        result = result and is_type_below(fld, _type_right.get_field(name))
                    return result
                else:
                    return _type_left.get_label().is_below(_type_right.get_label())

            case TYPE.TypesEnum.HEADER:
                if (_type_left.has_the_same_fields_as(_type_right)):
                    result = True
                    for name, fld in _type_left.get_fields():
                        result = result and is_type_below(fld, _type_right.get_field(name))
                    return result
                else:
                    return _type_left.get_label().is_below(_type_right.get_label())


############################################################
#################### Prune Invalid #########################
############################################################
def prune_invalid_gammas(_Gamma):
    result_Gamma = []
    for gamma in _Gamma:
        if (type(gamma) is tuple): # it's a tuple of (gg, gl)
            gg = gamma[0]
            gl = gamma[1]
            if (gg.is_valid() and gl.is_valid()):
                result_Gamma.append((gg,gl))
        else:
            if (gamma.is_valid()):
                result_Gamma.append(gamma)

    return result_Gamma

############################################################
###################### Invalidate ##########################
############################################################
def invalidate_gammas(_Gamma):
    result_Gamma = []
    for gamma in _Gamma:
        if (type(gamma) is tuple): # it's a tuple of (gg, gl)
            gg = gamma[0]
            gg.invalidate()
            gl = gamma[1]
            gl.invalidate()
            result_Gamma.append((gg, gl))
        else:
            result_Gamma.append(gamma.invalidate())

    return result_Gamma


############################################################
################### Union of gammas ########################
############################################################
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