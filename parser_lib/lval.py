from enum import Enum

class LvalEnum(Enum):
    VARIABLE = 1
    ACCESS = 2
    SLICE = 3

################ Parent Class ##############
class Lval():
    def __init__(self, _type):
        self.type = _type

    def get_type(self):
        return self.type

    def get_variables(self):
        return [self]

    def __str__(self):
        return "< lval >"


################ Children Classes ##############
class Variable(Lval):
    def __init__(self, _identifier):
        super().__init__(LvalEnum.VARIABLE) 
        self.identifier = _identifier

    def __str__(self):
        return str(self.identifier)

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.identifier == other.identifier
        return False

    def __hash__(self):
        return hash(self.identifier)


class Access(Lval):
    def __init__(self, _lval_list):
        super().__init__(LvalEnum.ACCESS)
        self.access_order = _lval_list

    def remove_first(self):
        if (len(self.access_order) == 2):
            return (self.access_order[0], self.access_order[1])
        else:
            return (Access(self.access_order[:-1]) , self.access_order[-1])

    def __str__(self):
        access_order_lst = '.'.join(list(map(str, self.access_order)))
        return "(" + access_order_lst + ")"

class Slice(Lval):
    def __init__(self, _lval, _lowbnd, _upbnd):
        super().__init__(LvalEnum.SLICE)
        self.lval = _lval
        self.lower = _lowbnd
        self.upper = _upbnd

    def __str__(self):
        return "( " + str(self.lval) + "[" + str(self.lower) + ":" + str(self.upper) + "] )"