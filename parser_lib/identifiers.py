import parser_lib.lval as LVAL

###############################################
class Field():
    def __init__(self, _type, _name):
        self.type = _type
        self.name = LVAL.Variable(_name)
        self.struct = None

    def set_parent(self, _struct):
        self.struct = _struct

    def get_parent(self):
        return self.struct
    def get_type(self):
        return self.type
    def get_name(self):
        return self.name

    def __str__(self):
        return "< field: " + str(self.type) + " \"" + str(self.name) + "\" >"


###############################################
class Parameter():
    def __init__(self, _dir, _type, _name):
        self.direction = _dir
        self.type = _type
        self.name = LVAL.Variable(_name)
        self.function = None

    def set_function(self, _func):
        self.function = _func
    def get_function(self):
        return self.function

    def get_direction(self):
        return self.direction
    def get_type(self):
        return self.type
    def get_variable(self):
        return self.name

    def __str__(self):
        return "< parameter: " + str(self.direction) + " " + str(self.type) + " \"" + str(self.name) + "\" >"