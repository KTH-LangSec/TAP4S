from enum import Enum
from copy import copy

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

    def __str__(self):
        return "( " + str(self.op) + " " + str(self.rhs) + " )"



################################################################
################################################################
def negate(_exp):
    if (_exp.get_type() == ExpressionEnum.BINARY):
        rhs = copy(_exp.get_rhs())
        lhs = copy(_exp.get_lhs())
        match _exp.get_op():
            case "==":
                op = "!="
            case "!=":
                op = "=="
            case "<":
                op = ">"
            case ">":
                op = "<"
            case "<=":
                op = ">="
            case ">=":
                op = "<="
        return BinaryOP(lhs, op, rhs)
    if (_exp.get_type() == ExpressionEnum.UNARY):
        return copy(_exp)