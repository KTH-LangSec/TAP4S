from enum import Enum

class StatementsEnum(Enum):
    BLOCK = 0
    ASSIGNMET = 1
    FUNCTION_CALL = 2
    IF = 3
    TRANSITION = 4
    APPLY = 5

    FUNCTION_DEFINITION = 100
    CONTROL_BLOCK_DEFINITION = 101
    ACTION_DEFINITION = 102
    PARSER_DEFINITION = 103
    STATE_DEFINITION = 104
    TABLE_DEFINITION = 105

    STRUCT_DECLARATION = 200
    HEADER_DECLARATION = 201
    VARIABLE_DECLARATION = 202
    CONSTANT_DECLARATION = 203
    TYPE_DECLARATION = 204

    MAIN = 1000

################ Parent Class ##############
class Statement():
    def __init__(self, _type):
        self.node_type = _type

    def get_node_type(self):
        return self.node_type

    def __str__(self):
        return "< statement >"


################ Block ##############
class Main(Statement):
    def __init__(self, _arch, _body):
        super().__init__(StatementsEnum.MAIN)
        self.arch = _arch
        self.body = list(_body)

    def __str__(self):
        return "< main \"" + str(self.arch) + "\" with BODY: " + str(self.body) + " >"


################ Block ##############
class Block(Statement):
    def __init__(self, _body):
        super().__init__(StatementsEnum.BLOCK)
        self.body = []
        for stm in _body:
            self.body.append(stm)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.body):
            stm = self.body[self.index]
            self.index += 1
            return stm
        else:
            raise StopIteration

    def __str__(self):
        result = ', '.join(list(map(str, self.body)))
        return "[" + result + "]"

#############################################
################ Rules Classes ##############
#############################################
class Assignment(Statement):
    def __init__(self, _lhs, _rhs):
        super().__init__(StatementsEnum.ASSIGNMET) 
        self.identifier = _lhs
        self.expression = _rhs

    def get_expression(self):
        return self.expression
    def get_identifier(self):
        return self.identifier

    def __str__(self):
        return "< assignment with LHS: " + str(self.identifier) + " and RHS: " + str(self.expression) + " >"

##############
class Call(Statement):
    def __init__(self, _name, _args):
        super().__init__(StatementsEnum.FUNCTION_CALL) 
        self.name = _name
        self.args = list(_args)

    def get_name(self):
        return self.name
    def get_arguments(self):
        return self.args

    def __str__(self):
        if self.args:
            arguments_lst = ', '.join(list(map(str, self.args)))
            arguments = "[" + arguments_lst + "]"
            return "< function call NAME: \"" + str(self.name) + "\" with ARGUMENTS: " + arguments + " >"
        else:
            return "< function call NAME: \"" + str(self.name) + "\" with NO ARGUMENTS >"

##############
class If(Statement):
    def __init__(self, _exp, _then, _else):
        super().__init__(StatementsEnum.IF) 
        self.expression = _exp
        self.then_body = list(_then)
        self.else_body = list(_else)

    def get_expression(self):
        return self.expression
    def get_then_body(self):
        return self.then_body
    def get_else_body(self):
        return self.else_body

    def __str__(self):
        if self.else_body:
            return "< if with GUARD: " + str(self.expression) + " and THEN: " + str(self.then_body) + " and ELSE: " + str(self.else_body) + " >"
        else:
            return "< if with GUARD: " + str(self.expression) + " and THEN: " + str(self.then_body) + " >"

##############
class Transition(Statement):
    def __init__(self, _exp, _def, _states):
        super().__init__(StatementsEnum.TRANSITION) 
        self.default_state = _def
        self.expression = _exp
        self.states = _states # TODO: need to change it to something better


    def __str__(self):
        return "< transition with GUARD: " + str(self.expression) + ", DEFAULT STATE: " + str(self.default_state) + ", and STATES: " + str(self.states) + " >"


##############
class Apply(Statement):
    def __init__(self, _tname, _keys):
        super().__init__(StatementsEnum.APPLY) 
        self.table_name = _tname
        self.keys = _keys

    def __str__(self):
        if self.keys:
            keys_lst = ', '.join(list(map(str, self.keys)))
            keys = "[" + keys_lst + "]"
            return "< apply TABLE \"" + str(self.table_name) + "\" with KEYS: " + keys + " >"
        else:
            return "< apply TABLE \"" + str(self.table_name) + "\" with NO KEYS >"

##################################################
################ Definition Classes ##############
##################################################
class FunctionDefinition(Statement):
    def __init__(self, _name, _ret, _params, _body):
        super().__init__(StatementsEnum.FUNCTION_DEFINITION) 
        self.name = _name
        self.retrun_type = _ret
        self.parameters = list(_params)
        self.body = list(_body)

    def get_name(self):
        return self.name
    def get_body(self):
        return self.body
    def get_parameters(self):
        return self.parameters

    def __str__(self):
        if self.parameters:
            params_lst = ', '.join(list(map(str, self.parameters)))
            params = "[" + params_lst + "]"
            return "< function definition with NAME: " + str(self.name) + ", RETURN TYPE: " + str(self.retrun_type) + ", PARAMETERS: " + params + ", and BODY: " + str(self.body) + " >"
        else:
            return "< function definition with NAME: " + str(self.name) + ", RETURN TYPE: " + str(self.retrun_type) + ", NO PARAMETERS, and BODY: " + str(self.body) + " >"


##############
class ControlBlcokDefinition(Statement):
    def __init__(self, _name, _params, _body):
        super().__init__(StatementsEnum.CONTROL_BLOCK_DEFINITION) 
        self.name = _name
        self.parameters = list(_params)
        self.body = list(_body)

    def get_name(self):
        return self.name
    def get_body(self):
        return self.body
    def get_parameters(self):
        return self.parameters

    def __str__(self):
        if self.parameters:
            params_lst = ', '.join(list(map(str, self.parameters)))
            params = "[" + params_lst + "]"
            return "< control block definition with NAME: " + str(self.name) + ", PARAMETERS: " + params + ", and BODY: " + str(self.body) + " >"
        else:
            return "< control block definition with NAME: " + str(self.name) + ", NO PARAMETERS, and BODY: " + str(self.body) + " >"

##############
class ActionDefinition(Statement):
    def __init__(self, _name, _params, _body):
        super().__init__(StatementsEnum.ACTION_DEFINITION) 
        self.name = _name
        self.parameters = list(_params)
        self.body = list(_body)

    def get_name(self):
        return self.name
    def get_body(self):
        return self.body
    def get_parameters(self):
        return self.parameters

    def __str__(self):
        if self.parameters:
            params_lst = ', '.join(list(map(str, self.parameters)))
            params = "[" + params_lst + "]"
            return "< action definition with NAME: " + str(self.name) + ", PARAMETERS: " + params + ", and BODY: " + str(self.body) + " >"
        else:
            return "< action definition with NAME: " + str(self.name) + ", NO PARAMETERS, and BODY: " + str(self.body) + " >"

##############
class ParserDefinition(Statement):
    def __init__(self, _name, _packetin, _header, _params, _body):
        super().__init__(StatementsEnum.PARSER_DEFINITION) 
        self.name = _name
        self.packet_in = _packetin
        self.header = _header
        self.parameters = list(_params)
        self.body = list(_body)

    def get_name(self):
        return self.name
    def get_body(self):
        return self.body
    def get_parameters(self):
        return self.parameters
    def get_packet_in(self):
        return self.packet_in

    def __str__(self):
        if self.parameters:
            params_lst = ', '.join(list(map(str, self.parameters)))
            params = "[" + params_lst + "]"
            return "< parser definition with NAME: " + str(self.name) + ", PACKET IN: " + str(self.packet_in) + ", HEADER: " + str(self.header) + ", PARAMETERS: " + params + ", and BODY: " + str(self.body) + " >"
        else:
            return "< parser definition with NAME: " + str(self.name) + ", PACKET IN: " + str(self.packet_in) + ", HEADER: " + str(self.header) + ", NO PARAMETERS, and BODY: " + str(self.body) + " >"


##############
class StateDefinition(Statement):
    def __init__(self, _name, _body):
        super().__init__(StatementsEnum.STATE_DEFINITION) 
        self.name = _name
        self.body = list(_body)

    def get_name(self):
        return self.name
    def get_body(self):
        return self.body

    def __str__(self):
        return "< state definition with NAME: " + str(self.name) + ", and BODY: " + str(self.body) + " >"

##############
class TableDefinition(Statement):
    def __init__(self, _name, _keys, _actions, _size, _def):
        super().__init__(StatementsEnum.TABLE_DEFINITION) 
        self.name = _name
        self.keys = list(_keys)
        self.actions = list(_actions)
        self.size = _size
        self.default_action = _def


    def __str__(self):
        keys_str = ""
        if self.keys:
            keys = []
            for k in self.keys:
                keys.append(k["name"])
            keys_lst = ', '.join(list(map(str, keys)))
            keys_str = ", and KEYS: [" + keys_lst + "]"

        actions_str = ""
        if self.actions:
            actions_str = ", and ACTIONS: " + str(self.actions)

        size_str = ""
        if self.size:
            size_str = ", and SIZE: " + str(self.size)

        default_str = ""
        if self.default_action:
            default_str = ", and DEFAULT ACTION: " + str(self.default_action)

        return "< table definition with NAME: " + str(self.name) + keys_str + actions_str + size_str + default_str + " >"



##################################################
################ Declaration Classes ##############
##################################################
class VariableDeclaration(Statement):
    def __init__(self, _type, _var):
        super().__init__(StatementsEnum.VARIABLE_DECLARATION) 
        self.variable = _var
        self.type = _type

    def get_variable(self):
        return self.variable
    def get_type(self):
        return self.type

    def __str__(self):
        return "< variable declaration: " + str(self.type) + " \"" + str(self.variable) + "\" >"

##############
class ConstantDeclaration(Statement):
    def __init__(self, _type, _var, _value):
        super().__init__(StatementsEnum.CONSTANT_DECLARATION) 
        self.type = _type
        self.variable = _var
        self.value = _value

    def get_variable(self):
        return self.variable
    def get_type(self):
        return self.type
    def get_value(self):
        return self.value

    def __str__(self):
        return "< constant declaration: " + str(self.type) + " \"" + str(self.variable) + "\" = " + str(self.value) + " >"


##############
class StructDeclaration(Statement):
    def __init__(self, _name, _type):
        super().__init__(StatementsEnum.STRUCT_DECLARATION) 
        self.name = _name
        self.type = _type

    def get_name(self):
        return self.name
    def get_type(self):
        return self.type

    def __str__(self):
        return "< struct declaration: \"" + str(self.name) + "\" with TYPE: " + str(self.type) + " >"


##############
class HeaderDeclaration(Statement):
    def __init__(self, _name, _type):
        super().__init__(StatementsEnum.HEADER_DECLARATION) 
        self.name = _name
        self.type = _type

    def get_name(self):
        return self.name
    def get_type(self):
        return self.type

    def __str__(self):
        return "< header declaration: \"" + str(self.name) + "\" with TYPE: " + str(self.type) + " >"

##############
class TypeDeclaration(Statement):
    def __init__(self, _primitive , _name):
        super().__init__(StatementsEnum.TYPE_DECLARATION) 
        self.name = _name
        self.primitive = _primitive

    def get_name(self):
        return self.name
    def get_primitive(self):
        return self.primitive

    def __str__(self):
        return "< type decleration: \"" + str(self.name) + "\" with PRIMITVE TYPE: "+ str(self.primitive) +" >"