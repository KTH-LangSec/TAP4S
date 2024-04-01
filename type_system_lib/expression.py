import parser_lib.expression as Pexp
import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL
import type_system_lib.label as LABEL
import parser_lib.lval as LVAL
import helper_functions as HELPER
import type_system_lib.gamma as GM


def type_check_expression(_exp, _gamma_g, _gamma_l):
    match _exp.get_type():
        case LVAL.LvalEnum.VARIABLE:
            return GM.lookup(_exp, _gamma_g, _gamma_l)

        case LVAL.LvalEnum.ACCESS:
            return GM.lookup(_exp, _gamma_g, _gamma_l)

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
            HELPER.error("We do not support binary operations on bit-strings with more than ONE slice!")
    else:
        HELPER.error("The size of the expressions doesn't match!")


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
            HELPER.error("We do not support binary operations on bit-strings with more than ONE slice!")
    else:
        HELPER.error("The size of the expressions doesn't match!")

def convert_binary_bs2bool(_op, _lhs_interval, _rhs_interval):
    match _op:
        case "&&": # TODO: implement
            HELPER.warning(" && is not implemented yet!")
        case "||": # TODO: implement
            HELPER.warning(" || is not implemented yet!")
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
        HELPER.error("We do not support unary operations on bit-strings with more than ONE slice!")

def convert_unary_bs(_op, _rhs_interval):
    match _op:
        case "!": # TODO: implement
            HELPER.warning(" ! is not implemented yet!")