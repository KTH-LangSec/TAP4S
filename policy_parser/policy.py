import type_system_lib.types as TYPE

class PolicyDisjunct():
    def __init__(self):
        self.policy_list = []

    def add_lval_policy(self, _lval_policy):
        self.policy_list.append(_lval_policy)

    def get_lval_policies(self):
        return self.policy_list

    def __str__(self):
        result = "Policy Disjunct:\n"
        for plc in self.policy_list:
            result += "\t" + str(plc) + "\n"
        return result


class LvalPolicy():
    def __init__(self, _lval, _slices):
        self.lval = _lval
        self.size = 0
        for slc in _slices:
            self.size += slc.get_size()

        self.bit_string = TYPE.BitString(self.size, _slices=_slices)

    def get_lval(self):
        return self.lval
    def get_bit_string(self):
        return self.bit_string

    def __str__(self):
        return str(self.lval) + " ==> " + str(self.bit_string)