

class Interval():
    def __init__(self, _low, _high):
        self.min = _low
        self.max = _high

        # TODO: adjust everytime after creation?

    def get_min(self):
        return self.min
    
    def get_max(self):
        return self.max

    def is_true(self):
        return (self.min == 1) and (self.max == 1)

    def is_false(self):
        return (self.min == 0) and (self.max == 0)

    def adjust(self, _size):
        if (self.max > (2 ** _size) - 1): # TODO, more over flow by overapproximation
            self.max = (2 ** _size) - 1
        if (self.min > self.max):
            self.min = self.max
            
        if (self.min < 0): # TODO: is this something we need?
            self.min = 0
        if (self.max < 0): # TODO: is this something we need?
            self.max = 0

    def __str__(self):
        return "[" + str(self.min) + ", " + str(self.max) + "]"


##################################################################
##################### BS2BS HELPER FUNCTIONS #####################
##################################################################
# TODO: DO WE WANT TO MODELL OVERFLOW?
def sum_operation(_lhs_interval, _rhs_interval):
    n_min = _lhs_interval.get_min() + _rhs_interval.get_min()
    n_max = _lhs_interval.get_max() + _rhs_interval.get_max()
    return Interval(n_min, n_max)


def minus_operation(_lhs_interval, _rhs_interval):
    n_min = _lhs_interval.get_min() - _rhs_interval.get_min()
    n_max = _lhs_interval.get_max() - _rhs_interval.get_max()
    return Interval(n_min, n_max)



##################################################################
################### BS2BOOL HELPER FUNCTIONS #####################
##################################################################
def equal_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()
    if ((lmin == rmin) and (lmax == rmax)):
        return Interval(1, 1)
    elif ((rmin > lmax) or (lmin > rmax)):
        return Interval(0, 0)
    else:
        return Interval(0,1)

def not_equal_operation(_lhs_interval, _rhs_interval):
    equal_op = equal_operation(_lhs_interval, _rhs_interval)
    if (equal_op.is_true()):
        return Interval(0, 0)
    elif (equal_op.is_false()):
        return Interval(1, 1)
    else:
        return Interval(0, 1)

def less_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()

    if (lmax < rmin):
        return Interval(1, 1)
    elif (rmax <= lmin):
        return Interval(0, 0)
    else:
        return Interval(0, 1)

def bigger_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()

    if (rmax < lmin):
        return Interval(1, 1)
    elif (lmax <= rmin):
        return Interval(0, 0)
    else:
        return Interval(0, 1)


def less_equal_operation(_lhs_interval, _rhs_interval):
    less_op = less_operation(_lhs_interval, _rhs_interval)
    equal_op = equal_operation(_lhs_interval, _rhs_interval)

    if (less_op.is_true() or equal_op.is_true()):
        return Interval(1, 1)
    elif (less_op.is_false() and equal_op.is_false()):
        return Interval(0, 0)
    else:
        return Interval(0, 1)


def bigger_equal_operation(_lhs_interval, _rhs_interval):
    bigger_op = bigger_operation(_lhs_interval, _rhs_interval)
    equal_op = equal_operation(_lhs_interval, _rhs_interval)

    if (bigger_op.is_true() or equal_op.is_true()):
        return Interval(1, 1)
    elif (bigger_op.is_false() and equal_op.is_false()):
        return Interval(0, 0)
    else:
        return Interval(0, 1)

##################################################################
################## BOOL2BOOL HELPER FUNCTIONS ####################
##################################################################
def bool_and_operation(_lhs_interval, _rhs_interval):
    if (_lhs_interval.is_false() or _rhs_interval.is_false()):
        return Interval(0, 0)
    elif (_lhs_interval.is_true() and _rhs_interval.is_true()):
        return Interval(1, 1)
    else:
        return Interval(0, 1)

def bool_or_operation(_lhs_interval, _rhs_interval):
    if (_lhs_interval.is_true() or _rhs_interval.is_true()):
        return Interval(1, 1)
    elif (_lhs_interval.is_false() and _rhs_interval.is_false()):
        return Interval(0, 0)
    else:
        return Interval(0, 1)

def bool_equal_operation(_lhs_interval, _rhs_interval):
    if ((_lhs_interval.is_true() and _rhs_interval.is_true()) or (_lhs_interval.is_false() and _rhs_interval.is_false())):
        return Interval(1, 1)
    elif ((_lhs_interval.is_true() and _rhs_interval.is_false()) or (_lhs_interval.is_false() and _rhs_interval.is_true())):
        return Interval(0, 0)
    else:
        return Interval(0, 1)

def bool_not_equal_operation(_lhs_interval, _rhs_interval):
    if ((_lhs_interval.is_true() and _rhs_interval.is_true()) or (_lhs_interval.is_false() and _rhs_interval.is_false())):
        return Interval(0, 0)
    elif ((_lhs_interval.is_true() and _rhs_interval.is_false()) or (_lhs_interval.is_false() and _rhs_interval.is_true())):
        return Interval(1, 1)
    else:
        return Interval(0, 1)

def bool_not(_rhs_interval):
    if (_rhs_interval.is_true()):
        return Interval(0, 0)
    elif (_rhs_interval.is_false()):
        return Interval(1, 1)
    else:
        return Interval(0, 1)