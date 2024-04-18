from enum import Enum

class B_Enum(Enum):
    LOCAL = 1
    GLOBAL = 2

class FunctionTypeEnum(Enum):
    FUNCTION = 1
    PARSER = 2
    CONTROL_BLOCK = 3
    STATE = 4
    ACTION = 5

class B():
    def __init__(self, _type):
        self.type = _type

#################
class Global_B(B):
    def __init__(self):
        super().__init__(B_Enum.GLOBAL) 
        self.mapping = {}

    def add(self, _name, _body, _params, _type):
        self.mapping[_name] = (list(_body), _params, _type)

    def get(self, _name):
        return self.mapping[_name]

    def exists(self, _key):
        if self.mapping.get(_key) is not None:
            return True
        else:
            return False

    def __str__(self):
        result = "Global B Mapping: \n"

        for name in self.mapping.keys():
            result += "\t" + str(name) + " -> " + str(self.mapping[name][0]) + "\n"
        
        return result


#################
class Local_B(B):
    def __init__(self):
        super().__init__(B_Enum.LOCAL) 
        self.mapping = {}

        # accept returns from the parser
        self.mapping["accept"] = ([], None , FunctionTypeEnum.STATE)

        # reject drops the packet 
        # #TODO how to handel?

        # handling NoAction action
        self.mapping["NoAction"] = ([], [] , FunctionTypeEnum.ACTION)

    def add(self, _name, _body, _params, _type):
        self.mapping[_name] = (list(_body), _params, _type)

    def get(self, _name):
        return self.mapping[_name]

    def exists(self, _key):
        if self.mapping.get(_key) is not None:
            return True
        else:
            return False

    def __str__(self):
        result = "Local B Mapping: \n"

        for name in self.mapping.keys():
            result += "\t" + str(name) + " -> " + str(self.mapping[name][0]) + "\n"
        
        return result

##########################################################################
##########################################################################
class CO():
    def __init__(self):
        self.param2arg = {}

    def add_relation(self, _param, _arg):
        self.param2arg[_param] = _arg
    def get_relation(self, _param):
        return self.param2arg[_param]
    def get_parameters(self):
        return self.param2arg.keys()

    def __str__(self):
        result = "CO Mapping: \n"
        for param in self.param2arg.keys():
            result += "\t" + str(param) + " -> " + str(self.param2arg[param]) + "\n"
        return result
    

##########################################################################
##########################################################################
class Contracts():
    def __init__(self):
        self.extern_list = []
        self.extern_contracts = {}
        self.table_contracts = {}

    def add_extern(self, _name, _contract):
        self.extern_list.append(_name)
        self.extern_contracts[_name] = _contract

    def get_extern(self, _name):
        return self.extern_contracts[_name]

    def extern_exists(self, _name):
        if self.extern_contracts.get(_name) is not None:
            return True
        else:
            return False

    ############################

    def add_table(self, _name, _contract):
        self.table_contracts[_name] = _contract

    def get_table(self, _name):
        return self.table_contracts[_name]

    def table_exists(self, _name):
        if self.table_contracts.get(_name) is not None:
            return True
        else:
            return False

    def __str__(self):
        result = "\nC Mapping: \n\n"

        result += "#### Externs #### \n"
        for name in self.extern_contracts.keys():
            result += str(self.extern_contracts[name]) + "\n"

        result += "#### Tables #### \n"
        for name in self.table_contracts.keys():
            result += str(self.table_contracts[name]) + "\n"
        
        return result