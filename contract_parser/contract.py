import copy



################# EXTERN #################
class ExternContract():
    def __init__(self, _name):
        self.name = _name
        self.mapping = {}

    def add(self, _predicate, _gamma_t):
        self.mapping[_predicate] = _gamma_t
    def get(self):
        return self.mapping
    def get_name(self):
        return self.name

    def __str__(self):
        result = "Extern \""+ str(self.name) +"\" Contract: \n"
        for key, value in self.mapping.items():
            result += "\t" + str(key) + " -> \n" + str(value) + "\n"
        return result

################# TABLE #################
class TableContract():
    def __init__(self, _name):
        self.name = _name
        self.mapping = {}

    def add(self, _predicate, _action, _gamma_t):
        self.mapping[_predicate] = (_action, _gamma_t)
    def get(self):
        return self.mapping
    def get_name(self):
        return self.name

    def __str__(self):
        result = "Table \""+ str(self.name) +"\" Contract: \n"
        for key, value in self.mapping.items():
            action = "\t\t" + str(value[0])
            gamma = str(value[1])
            result += "\t" + str(key) + " -> \n" + action + "\n" + gamma + "\n"
        return result

#########################################
class gamma_t():
    def __init__(self):
        self.mapping = {}

    def add(self, _var, _type):
        self.mapping[_var] = _type
    def update(self, _var, _type):
        self.mapping[_var] = _type

    def raise_types(self, _lbl):
        for var, tp in self.mapping.items():
            tp.raise_label(_lbl)

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
        result = ""
        for var in self.mapping.keys():
            result += "\t\t" + str(var) + " -> " + str(self.mapping[var]) + "\n"
        return result
