from enum import Enum
from copy import copy

import parser_lib.lval as LVAL
import logger as LOGGER

class ExpressionEnum(Enum):
    HEX = 1
    IDENTIFIER = 2
    BINARY = 3
    UNARY = 4
    ACCESS = 5
    SLICE = 6
    UNSIGNED = 7
    BOOLEAN = 8

################ Parent Class ##############
class Expression():
    def __init__(self, _type):
        self.type = _type

    def get_type(self):
        return self.type

    def __str__(self):
        return "< expression of type \"" + str(self.type) + "\" >"


################ Children Classes ##############
class Hex(Expression):
    def __init__(self, _hex_value):
        super().__init__(ExpressionEnum.HEX)
        self.value = int(_hex_value, 16)
        self.size = (len(_hex_value) - 2) * 4 # removes 0x, then multiply by 4 to get bit length

    def get_value(self):
        return self.value
    def get_size(self):
        return self.size

    def get_variables(self):
        return []

    def __str__(self):
        return str(self.value)


class UnsignedNumber(Expression):
    def __init__(self, _length, _value):
        super().__init__(ExpressionEnum.UNSIGNED) 
        self.value = int(_value)
        self.size = int(_length)

    def get_value(self):
        return self.value
    def get_size(self):
        return self.size

    def get_variables(self):
        return []

    def __str__(self):
        return str(self.size) + "w" + str(self.value)


class Boolean(Expression):
    def __init__(self, _value):
        super().__init__(ExpressionEnum.BOOLEAN)
        self.value = _value
        self.size = 1

    def get_value(self):
        return self.value
    def get_size(self):
        return self.size

    def get_variables(self):
        return []

    def __str__(self):
        return str(self.value)

class BinaryOP(Expression):
    def __init__(self, _lhs, _op, _rhs):
        super().__init__(ExpressionEnum.BINARY) 
        self.lhs = _lhs
        self.op = _op
        self.rhs = _rhs

    def get_lhs(self):
        return self.lhs
    def get_op(self):
        return self.op
    def get_rhs(self):
        return self.rhs

    def get_variables(self):
        return self.lhs.get_variables() + self.rhs.get_variables()

    def is_simple(self):
        lhs_type = self.lhs.get_type() 
        lhs_b = False or (lhs_type == ExpressionEnum.BOOLEAN) or (lhs_type == ExpressionEnum.UNSIGNED) or (lhs_type == ExpressionEnum.HEX) or (lhs_type == LVAL.LvalEnum.ACCESS) or (lhs_type == LVAL.LvalEnum.SLICE) or (lhs_type == LVAL.LvalEnum.VARIABLE) 

        rhs_type = self.rhs.get_type()
        rhs_b = False or (rhs_type == ExpressionEnum.BOOLEAN) or (rhs_type == ExpressionEnum.UNSIGNED) or (rhs_type == ExpressionEnum.HEX) or (rhs_type == LVAL.LvalEnum.ACCESS) or (rhs_type == LVAL.LvalEnum.SLICE) or (rhs_type == LVAL.LvalEnum.VARIABLE) 

        return lhs_b and rhs_b

    def __str__(self):
        return "( " + str(self.lhs) + " " + str(self.op) + " " + str(self.rhs) + " )"


class UnaryOP(Expression):
    def __init__(self, _op, _rhs):
        super().__init__(ExpressionEnum.UNARY)
        self.op = _op
        self.rhs = _rhs

    def get_op(self):
        return self.op
    def get_rhs(self):
        return self.rhs

    def get_variables(self):
        return self.rhs.get_variables()

    def __str__(self):
        return "( " + str(self.op) + " " + str(self.rhs) + " )"



################################################################
################################################################
def negate(_exp):
    match _exp.get_type():
        case ExpressionEnum.BINARY:
            rhs = copy(_exp.get_rhs())
            lhs = copy(_exp.get_lhs())
            match _exp.get_op():
                case "==":
                    return BinaryOP(lhs, "!=", rhs)
                case "!=":
                    return BinaryOP(lhs, "==", rhs)
                case "<":
                    return BinaryOP(lhs, ">=", rhs)
                case ">":
                    return BinaryOP(lhs, "<=", rhs)
                case "<=":
                    return BinaryOP(lhs, ">", rhs)
                case ">=":
                    return BinaryOP(lhs, "<", rhs)
                case "&&":
                    return BinaryOP(negate(lhs), "||", negate(rhs))
                case "||":
                    return BinaryOP(negate(lhs), "&&", negate(rhs))
        
        case ExpressionEnum.UNARY:
            return copy(_exp.get_rhs())

        case ExpressionEnum.BOOLEAN:
            if (_exp.get_value()):
                return Boolean(False)
            else:
                return Boolean(True)

        case LVAL.LvalEnum.VARIABLE:
            return UnaryOP("!", _exp)

        case LVAL.LvalEnum.ACCESS:
            return UnaryOP("!", _exp)
            # TODO implement
            # LOGGER.error("negating access is not implemented!")

        case LVAL.LvalEnum.SLICE:
            # TODO implement
            LOGGER.error("negating slice is not implemented!")


