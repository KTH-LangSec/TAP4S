

class Interval():
    def __init__(self, _low, _high, _size):
        self.min = _low
        self.max = _high

        self.size = _size
        self.max_value = ((2 ** _size) - 1)

        self.adjust()

    def get_min(self):
        return self.min
    
    def get_max(self):
        return self.max

    def get_size(self):
        return self.size

    def is_true(self):
        return (self.min == 1) and (self.max == 1)

    def is_false(self):
        return (self.min == 0) and (self.max == 0)

    def is_valid(self):
        return (self.min <= self.max)

    def is_singleton(self):
        return self.min == self.max

    def adjust(self):
        if (self.max > self.max_value):
            self.min = 0
            self.max = self.max_value

        if (self.min < 0):
            self.min = 0
            #self.max = self.max_value

    def __str__(self):
        return "[" + str(self.min) + ", " + str(self.max) + "]"


##################################################################
###################### MISC HELPER FUNCTIONS #####################
##################################################################
def intersect(_lhs_interval, _rhs_interval):
    # Check for non-overlapping intervals
    if (_lhs_interval.max < _rhs_interval.min) or (_rhs_interval.max < _lhs_interval.min):
        return None
    
    # Calculate start and end of the intersection
    n_min = max(_lhs_interval.min, _rhs_interval.min)
    n_max = min(_lhs_interval.max, _rhs_interval.max)

    size = _lhs_interval.get_size()
    
    return Interval(n_min, n_max, size)


##################################################################
##################### BS2BS HELPER FUNCTIONS #####################
##################################################################
def sum_operation(_lhs_interval, _rhs_interval):
    n_min = _lhs_interval.get_min() + _rhs_interval.get_min()
    n_max = _lhs_interval.get_max() + _rhs_interval.get_max()
    size = _lhs_interval.get_size()
    return Interval(n_min, n_max, size)


def minus_operation(_lhs_interval, _rhs_interval):
    n_min = _lhs_interval.get_min() - _rhs_interval.get_min()
    n_max = _lhs_interval.get_max() - _rhs_interval.get_max()
    size = _lhs_interval.get_size()
    return Interval(n_min, n_max, size)



##################################################################
################### BS2BOOL HELPER FUNCTIONS #####################
##################################################################
def equal_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()

    size = 1

    if ((lmin == rmin) and (lmax == rmax)):
        return Interval(1, 1, size)
    elif ((rmin > lmax) or (lmin > rmax)):
        return Interval(0, 0, size)
    else:
        return Interval(0,1, size)

def not_equal_operation(_lhs_interval, _rhs_interval):
    equal_op = equal_operation(_lhs_interval, _rhs_interval)
    size = 1
    if (equal_op.is_true()):
        return Interval(0, 0, size)
    elif (equal_op.is_false()):
        return Interval(1, 1, size)
    else:
        return Interval(0, 1, size)

def less_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()

    size = 1

    if (lmax < rmin):
        return Interval(1, 1, size)
    elif (rmax <= lmin):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)

def bigger_operation(_lhs_interval, _rhs_interval):
    lmin = _lhs_interval.get_min()
    lmax = _lhs_interval.get_max()
    rmin = _rhs_interval.get_min()
    rmax = _rhs_interval.get_max()

    size = 1

    if (rmax < lmin):
        return Interval(1, 1, size)
    elif (lmax <= rmin):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)


def less_equal_operation(_lhs_interval, _rhs_interval):
    less_op = less_operation(_lhs_interval, _rhs_interval)
    equal_op = equal_operation(_lhs_interval, _rhs_interval)

    size = 1

    if (less_op.is_true() or equal_op.is_true()):
        return Interval(1, 1, size)
    elif (less_op.is_false() and equal_op.is_false()):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)


def bigger_equal_operation(_lhs_interval, _rhs_interval):
    bigger_op = bigger_operation(_lhs_interval, _rhs_interval)
    equal_op = equal_operation(_lhs_interval, _rhs_interval)

    size = 1

    if (bigger_op.is_true() or equal_op.is_true()):
        return Interval(1, 1, size)
    elif (bigger_op.is_false() and equal_op.is_false()):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)

##################################################################
################## BOOL2BOOL HELPER FUNCTIONS ####################
##################################################################
def bool_and_operation(_lhs_interval, _rhs_interval):
    size = 1
    if (_lhs_interval.is_false() or _rhs_interval.is_false()):
        return Interval(0, 0, size)
    elif (_lhs_interval.is_true() and _rhs_interval.is_true()):
        return Interval(1, 1, size)
    else:
        return Interval(0, 1, size)

def bool_or_operation(_lhs_interval, _rhs_interval):
    size = 1
    if (_lhs_interval.is_true() or _rhs_interval.is_true()):
        return Interval(1, 1, size)
    elif (_lhs_interval.is_false() and _rhs_interval.is_false()):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)

def bool_equal_operation(_lhs_interval, _rhs_interval):
    size = 1
    if ((_lhs_interval.is_true() and _rhs_interval.is_true()) or (_lhs_interval.is_false() and _rhs_interval.is_false())):
        return Interval(1, 1, size)
    elif ((_lhs_interval.is_true() and _rhs_interval.is_false()) or (_lhs_interval.is_false() and _rhs_interval.is_true())):
        return Interval(0, 0, size)
    else:
        return Interval(0, 1, size)

def bool_not_equal_operation(_lhs_interval, _rhs_interval):
    size = 1 
    if ((_lhs_interval.is_true() and _rhs_interval.is_true()) or (_lhs_interval.is_false() and _rhs_interval.is_false())):
        return Interval(0, 0, size)
    elif ((_lhs_interval.is_true() and _rhs_interval.is_false()) or (_lhs_interval.is_false() and _rhs_interval.is_true())):
        return Interval(1, 1, size)
    else:
        return Interval(0, 1, size)

def bool_not(_rhs_interval):
    size = 1
    if (_rhs_interval.is_true()):
        return Interval(0, 0, size)
    elif (_rhs_interval.is_false()):
        return Interval(1, 1, size)
    else:
        return Interval(0, 1, size)