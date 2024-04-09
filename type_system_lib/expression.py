import parser_lib.expression as Pexp
import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL
import type_system_lib.label as LABEL
import parser_lib.lval as LVAL
import logger as LOGGER
import type_system_lib.gamma as GM

import copy


def type_check_expression(_exp, _gamma_g, _gamma_l):
    match _exp.get_type():
        case LVAL.LvalEnum.VARIABLE:
            return GM.lookup(_exp, _gamma_g, _gamma_l)

        case LVAL.LvalEnum.ACCESS:
            return GM.lookup(_exp, _gamma_g, _gamma_l)

        case LVAL.LvalEnum.SLICE:
            LOGGER.error("type_check_expression for slice is not implementet!")

        case Pexp.ExpressionEnum.HEX:
            size = _exp.get_size()
            return TYPE.BitString(size, _value=_exp.get_value())

        case Pexp.ExpressionEnum.UNSIGNED:
            size = _exp.get_size()
            return TYPE.BitString(size, _value=_exp.get_value())

        case Pexp.ExpressionEnum.BOOLEAN:
            if (_exp.get_value() == True):
                return TYPE.Bool(_value=1)
            else:
                return TYPE.Bool(_value=0)

        case Pexp.ExpressionEnum.BINARY:
            lhs = type_check_expression(_exp.get_lhs(), _gamma_g, _gamma_l)
            rhs = type_check_expression(_exp.get_rhs(), _gamma_g, _gamma_l)

            if (lhs.get_type() == TYPE.TypesEnum.BIT_STRING and rhs.get_type() == TYPE.TypesEnum.BIT_STRING):
                if (_exp.get_op() == "+" or _exp.get_op() == "-"):
                    return binary_bs2bs(_exp.get_op(), lhs, rhs)
                else:
                    return binary_bs2bool(_exp.get_op(), lhs, rhs)
            
            elif (lhs.get_type() == TYPE.TypesEnum.BOOL and rhs.get_type() == TYPE.TypesEnum.BOOL):
                return binary_bool2bool(_exp.get_op(), lhs, rhs)

        case Pexp.ExpressionEnum.UNARY:
            rhs = type_check_expression(_exp.get_rhs(), _gamma_g, _gamma_l)

            if (rhs.get_type() == TYPE.TypesEnum.BIT_STRING):
                return unary_bs(_exp.get_op(), rhs)

            elif(rhs.get_type() == TYPE.TypesEnum.BOOL):
                return unary_bool(_exp.get_op(), rhs)



##################################################################
######################## HELPER FUNCTIONS ########################
##################################################################
def binary_bool2bool(_op, _lhs, _rhs):
    interval = convert_binary_bool2bool(_op, _lhs.get_interval(), _rhs.get_interval())
    label = LABEL.lup(_lhs.get_label(), _rhs.get_label())
    return TYPE.Bool(_label=label, _interval=interval)

def convert_binary_bool2bool(_op, _lhs_interval, _rhs_interval):
    match _op:
        case "&&":
            return INTERVAL.bool_and_operation(_lhs_interval, _rhs_interval)
        case "||":
            return INTERVAL.bool_or_operation(_lhs_interval, _rhs_interval)
        case "==":
            return INTERVAL.bool_equal_operation(_lhs_interval, _rhs_interval)
        case "!=":
            return INTERVAL.bool_not_equal_operation(_lhs_interval, _rhs_interval)

##################################################################
def binary_bs2bs(_op, _lhs, _rhs):
    # TODO: DO WE WANT TO MODELL OVERFLOW?
    if (_lhs.get_size() == _rhs.get_size()): # check that the length of both sides should be equal
        size = _lhs.get_size()
        if (_lhs.number_of_slices() == 1 and _rhs.number_of_slices() == 1):
            interval = convert_binary_bs2bs(_op, _lhs.get_slice(0).get_interval(), _rhs.get_slice(0).get_interval(), _lhs.get_slice(0).get_slice_indices(), _rhs.get_slice(0).get_slice_indices())
            interval.adjust(size) # TODO: Move into the convert operations
            label = LABEL.lup(_lhs.get_slice(0).get_label(), _rhs.get_slice(0).get_label())
            return TYPE.BitString(size, _label=label, _interval=interval)
        else:
            LOGGER.error("We do not support binary operations on bit-strings with more than ONE slice!")
    else:
        LOGGER.error("The size of the expressions doesn't match!")


def convert_binary_bs2bs(_op, _lhs_interval, _rhs_interval, _slice_lhs, _slice_rhs):
    match _op:
        case "+":
            return INTERVAL.sum_operation(_lhs_interval, _rhs_interval)
        case "-":
            return INTERVAL.minus_operation(_lhs_interval, _rhs_interval)


##################################################################
def binary_bs2bool(_op, _lhs, _rhs):
    if (_lhs.get_size() == _rhs.get_size()): # check that the length of both sides should be equal
        size = _lhs.get_size()
        if (_lhs.number_of_slices() == 1 and _rhs.number_of_slices() == 1):
            interval = convert_binary_bs2bool(_op, _lhs.get_slice(0).get_interval(), _rhs.get_slice(0).get_interval())
            label = LABEL.lup(_lhs.get_slice(0).get_label(), _rhs.get_slice(0).get_label())
            return TYPE.Bool(_label=label, _interval=interval)
        else:
            LOGGER.error("We do not support binary operations on bit-strings with more than ONE slice!")
    else:
        LOGGER.error("The size of the expressions doesn't match!")

def convert_binary_bs2bool(_op, _lhs_interval, _rhs_interval):
    match _op:
        case "&&": # TODO: implement
            LOGGER.error(" && is not implemented!")
        case "||": # TODO: implement
            LOGGER.error(" || is not implemented!")
        case "==":
            return INTERVAL.equal_operation(_lhs_interval, _rhs_interval)
        case "!=":
            return INTERVAL.not_equal_operation(_lhs_interval, _rhs_interval)
        case ">":
            return INTERVAL.bigger_operation(_lhs_interval, _rhs_interval)
        case "<":
            return INTERVAL.less_operation(_lhs_interval, _rhs_interval)
        case "<=":
            return INTERVAL.less_equal_operation(_lhs_interval, _rhs_interval)
        case ">=":
            return INTERVAL.bigger_equal_operation(_lhs_interval, _rhs_interval)
            

##################################################################
def unary_bool(_op, _rhs):
    interval = convert_unary_bool(_op, _rhs.get_interval())
    return TYPE.Bool(_label=_rhs.get_label(), _interval=interval)

def convert_unary_bool(_op, _rhs_interval):
    match _op:
        case "!":
            return INTERVAL.bool_not(_rhs_interval)


##################################################################
def unary_bs(_op, _rhs):
    if (_rhs.number_of_slices() == 1):
        interval = convert_unary_bs(_op, _rhs.get_slice(0).get_interval())
        return TYPE.Bool(_label=_rhs.get_slice(0).get_label(), _interval=interval)
    else:
        LOGGER.error("We do not support unary operations on bit-strings with more than ONE slice!")

def convert_unary_bs(_op, _rhs_interval):
    match _op:
        case "!": # TODO: implement
            LOGGER.warning(" ! is not implemented yet!")



###################################################################################
################################### REFINEMENT ####################################
###################################################################################
def refine_expression(_exp, _gamma_g, _gamma_l):
    match _exp.get_type():
        # case LVAL.LvalEnum.VARIABLE:
        #     return type_check_expression(_exp, _gamma_g, _gamma_l)

        # case LVAL.LvalEnum.ACCESS:
        #     return type_check_expression(_exp, _gamma_g, _gamma_l)

        # case LVAL.LvalEnum.SLICE:
        #     LOGGER.error("refine_expression for slice is not implementet!")

        # case Pexp.ExpressionEnum.HEX:
        #     return type_check_expression(_exp, _gamma_g, _gamma_l)

        # case Pexp.ExpressionEnum.UNSIGNED:
        #     return type_check_expression(_exp, _gamma_g, _gamma_l)

        # case Pexp.ExpressionEnum.BOOLEAN:
        #     return type_check_expression(_exp, _gamma_g, _gamma_l)

        case Pexp.ExpressionEnum.BINARY:
            return refine_binary_expression(_exp, _gamma_g, _gamma_l)

        case Pexp.ExpressionEnum.UNARY:
            LOGGER.error("refine_expression for unary is not implementet!")


def refine_binary_expression(_exp, _gamma_g, _gamma_l):
    lhs = _exp.get_lhs()
    rhs = _exp.get_rhs()

    op = _exp.get_op()

    left_type = type_check_expression(lhs, _gamma_g, _gamma_l)
    right_type = type_check_expression(rhs, _gamma_g, _gamma_l)

    if (left_type.get_type() == TYPE.TypesEnum.BIT_STRING) and (right_type.get_type() == TYPE.TypesEnum.BIT_STRING):
        match op:
            case ">":
                return refine_bigger(lhs, rhs, _gamma_g, _gamma_l)
            case "<":
                return refine_less(lhs, rhs, _gamma_g, _gamma_l)
            case ">=":
                return refine_bigger_equal(lhs, rhs, _gamma_g, _gamma_l)
            case "<=":
                return refine_less_equal(lhs, rhs, _gamma_g, _gamma_l)
            case "==":
                return refine_equal(lhs, rhs, _gamma_g, _gamma_l)
            case "!=":
                return refine_not_equal(lhs, rhs, _gamma_g, _gamma_l)

    elif (left_type.get_type() == TYPE.TypesEnum.BOOL) and (right_type.get_type() == TYPE.TypesEnum.BOOL):
        match op:
            case "&&":
                return refine_bool_and(lhs, rhs, _gamma_g, _gamma_l)
            case "||":
                return refine_bool_or(lhs, rhs, _gamma_g, _gamma_l)
            case "==":
                return refine_bool_equal(lhs, rhs, _gamma_g, _gamma_l)
            case "!=":
                return refine_bool_not_equal(lhs, rhs, _gamma_g, _gamma_l)
    
    else:
        LOGGER.error("invalid expression" + str(_exp))


##########
def variable_side(_lhs, _rhs):
    if issubclass(type(_lhs), LVAL.Lval):
        if issubclass(type(_rhs), LVAL.Lval):
            return 0
        else:
            return -1
    elif issubclass(type(_rhs), LVAL.Lval):
            return 1
    else:
        LOGGER.error("invalid expression")


##########
def refine_bigger(_lhs, _rhs, _gamma_g, _gamma_l):
    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            cp_gamma_g = copy.deepcopy(_gamma_g)
            cp_gamma_l = copy.deepcopy(_gamma_l)

            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            new_min = right_type.get_slice(0).get_interval().get_max() + 1
            new_interval = INTERVAL.Interval(new_min, left_type.get_slice(0).get_interval().get_max())
            label = left_type.get_slice(0).get_label()
            size = left_type.get_size()
            new_left_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            return refine_less(_rhs, _lhs, _gamma_g, _gamma_l)

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")


##########
def refine_less(_lhs, _rhs, _gamma_g, _gamma_l):
    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            cp_gamma_g = copy.deepcopy(_gamma_g)
            cp_gamma_l = copy.deepcopy(_gamma_l)

            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            new_max = right_type.get_slice(0).get_interval().get_min() - 1
            new_interval = INTERVAL.Interval(left_type.get_slice(0).get_interval().get_min(), new_max)
            label = left_type.get_slice(0).get_label()
            size = left_type.get_size()
            new_left_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            return refine_bigger(_rhs, _lhs, _gamma_g, _gamma_l)

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##########
def refine_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    cp_gamma_g = copy.deepcopy(_gamma_g)
    cp_gamma_l = copy.deepcopy(_gamma_l)

    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            new_max = right_type.get_slice(0).get_interval().get_max()
            new_min = right_type.get_slice(0).get_interval().get_min()

            new_interval = INTERVAL.Interval(new_min, new_max)
            label = left_type.get_slice(0).get_label()
            size = left_type.get_size()
            new_left_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            right_type = GM.lookup(_rhs, cp_gamma_g, _gamma_l)
            left_type = type_check_expression(_lhs, cp_gamma_g, _gamma_l)

            new_max = left_type.get_slice(0).get_interval().get_max()
            new_min = left_type.get_slice(0).get_interval().get_min()

            new_interval = INTERVAL.Interval(new_min, new_max)
            label = right_type.get_slice(0).get_label()
            size = right_type.get_size()
            new_right_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")


##########
def refine_not_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            res = []
            res.extend(refine_bigger(_rhs, _lhs, _gamma_g, _gamma_l))
            res.extend(refine_less(_rhs, _lhs, _gamma_g, _gamma_l))

            return res

        case 1: # only one variable on the right hand side
            res = []
            res.extend(refine_bigger(_rhs, _lhs, _gamma_g, _gamma_l))
            res.extend(refine_less(_rhs, _lhs, _gamma_g, _gamma_l))

            return res

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")


##########
def refine_less_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            cp_gamma_g = copy.deepcopy(_gamma_g)
            cp_gamma_l = copy.deepcopy(_gamma_l)

            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            new_max = right_type.get_slice(0).get_interval().get_min()
            new_interval = INTERVAL.Interval(left_type.get_slice(0).get_interval().get_min(), new_max)
            label = left_type.get_slice(0).get_label()
            size = left_type.get_size()
            new_left_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            return refine_bigger_equal(_rhs, _lhs, _gamma_g, _gamma_l)

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##########
def refine_bigger_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            cp_gamma_g = copy.deepcopy(_gamma_g)
            cp_gamma_l = copy.deepcopy(_gamma_l)

            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            new_min = right_type.get_slice(0).get_interval().get_max() + 1
            new_interval = INTERVAL.Interval(new_min, left_type.get_slice(0).get_interval().get_max())
            label = left_type.get_slice(0).get_label()
            size = left_type.get_size()
            new_left_type = TYPE.BitString(size, _label=label, _interval=new_interval)

            GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            return refine_less_equal(_rhs, _lhs, _gamma_g, _gamma_l)

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##############################
########## BOOLEANS ##########
##############################
def refine_bool_and(_lhs, _rhs, _gamma_g, _gamma_l):
    cp_gamma_g = copy.deepcopy(_gamma_g)
    cp_gamma_l = copy.deepcopy(_gamma_l)

    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            if (right_type.is_true()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=1, _label=label)

                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            right_type = GM.lookup(_rhs, cp_gamma_g, _gamma_l)
            left_type = type_check_expression(_lhs, cp_gamma_g, _gamma_l)

            if (left_type.is_true()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=1, _label=label)

                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##########
def refine_bool_or(_lhs, _rhs, _gamma_g, _gamma_l):
    cp_gamma_g = copy.deepcopy(_gamma_g)
    cp_gamma_l = copy.deepcopy(_gamma_l)

    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            if (right_type.is_false()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            elif (right_type.is_true()):
                return # no update since left side can be anything and still enter this branch.

            else:
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case 1: # only one variable on the right hand side
            right_type = GM.lookup(_rhs, cp_gamma_g, _gamma_l)
            left_type = type_check_expression(_lhs, cp_gamma_g, _gamma_l)

            if (left_type.is_false()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            elif (left_type.is_true()):
                return # no update since right side can be anything and still enter this branch.
                
            else:
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##########
def refine_bool_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    cp_gamma_g = copy.deepcopy(_gamma_g)
    cp_gamma_l = copy.deepcopy(_gamma_l)

    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            if (right_type.is_false()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=0, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            elif (right_type.is_true()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]    

        case 1: # only one variable on the right hand side
            right_type = GM.lookup(_rhs, cp_gamma_g, _gamma_l)
            left_type = type_check_expression(_lhs, cp_gamma_g, _gamma_l)

            if (left_type.is_false()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=0, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            elif (left_type.is_true()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]    

        case _: # variables on both sides

            # TODO: implement
            LOGGER.error("TODO: variables on both sides")

##########
def refine_bool_not_equal(_lhs, _rhs, _gamma_g, _gamma_l):
    cp_gamma_g = copy.deepcopy(_gamma_g)
    cp_gamma_l = copy.deepcopy(_gamma_l)

    side = variable_side(_lhs, _rhs)
    match side:
        case -1: # only one variable on the left hand side
            left_type = GM.lookup(_lhs, cp_gamma_g, _gamma_l)
            right_type = type_check_expression(_rhs, cp_gamma_g, _gamma_l)

            if (right_type.is_true()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=0, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            elif (right_type.is_false()):
                label = left_type.get_label()
                new_left_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_lhs, new_left_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]    

        case 1: # only one variable on the right hand side
            right_type = GM.lookup(_rhs, cp_gamma_g, _gamma_l)
            left_type = type_check_expression(_lhs, cp_gamma_g, _gamma_l)

            if (left_type.is_true()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=0, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            elif (left_type.is_false()):
                label = right_type.get_label()
                new_right_type = TYPE.Bool(_value=1, _label=label)
                GM.update(_rhs, new_right_type, cp_gamma_g, _gamma_l)

            return [(cp_gamma_g, cp_gamma_l)]    

        case _: # variables on both sides
            # TODO: implement
            LOGGER.error("TODO: variables on both sides")