

class B():
    def __init__(self):
        self.functions_body = {}
        self.functions_param = {}
        self.states = {}

    def add_function(self, _name, _body, _params):
        self.functions_body[_name] = list(_body)
        self.functions_param[_name] = list(_params)

    def add_state(self, _name, _body):
        self.states[_name] = list(_body)

    def get_function_body(self, _name):
        return self.functions_body[_name]
    def get_function_parameters(self, _name):
        return self.functions_param[_name]

    def get_state(self, _name):
        return self.states[_name]


    def __str__(self):
        result = "B Mapping: \n"

        result += "\tFunctions: \n"
        for name in self.functions_body.keys():
            result += "\t\t" + str(name) + " -> " + str(self.functions_body[name]) + "\n"
        
        result += "\tStates: \n"
        for name in self.states.keys():
            result += "\t\t" + str(name) + " -> " + str(self.states[name]) + "\n"
        
        return result


##########################################################################
class M(): # change to co
    def __init__(self):
        self.param2arg = {}

    def add_relation(self, _param, _arg):
        self.param2arg[_param] = _arg
    def get_relation(self, _param):
        return self.param2arg[_param]
    def get_parameters(self):
        return self.param2arg.keys()

    def __str__(self):
        result = "M Mapping: \n"
        for param in self.param2arg.keys():
            result += "\t" + str(param) + " -> " + str(self.param2arg[param]) + "\n"
        return result
    

