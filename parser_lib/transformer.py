from lark import Transformer, v_args

from parser_lib import types, identifiers, ast, expression, lval

# Transformer
@v_args(inline=True)
class P4Transformer(Transformer):
    ######################################################################
    ############################# PROGRAM ################################
    ###################################################################### 
    def start(self, *args):
        return args[0]
    
    def block(self, *args):
        return ast.Block(list(args))


    ######################################################################
    ############################### MAIN #################################
    ###################################################################### 
    def main(self, *args):
        return ast.Main(args[0], args[1])

    def main_body(self, *args):
        return ast.Block(list(args))
    
    def main_body_call(self, *args):
        name = args[0]
        arguments = None
        if len(args) > 1:
            arguments = args[1]
        return ast.Call(name, arguments)

    ######################################################################
    ############################# EXPRESSION #############################
    ###################################################################### 
    def expression(self, *args):
        return args[0] # TODO might cause bugs

    # def slicing(self, *args):
    #     return expression.Slice(args[0], args[2], args[1])

    def binary_operation(self, *args):
        return expression.BinaryOP(args[0], args[1], args[2])

    def unary_operation(self, *args):
        return expression.UnaryOP(args[0], args[1])

    # def access(self, *args):
    #     return expression.Access(list(args))

    def boolean_value(self, *args):
        return expression.Boolean(args[0])

    def unsigned(self, *args):
        return expression.UnsignedNumber(args[0], args[1])

    def hex_value(self, *args):
        val = "0x" + str(args[1])
        return expression.Hex(val)


    ######################################################################
    ################################ LVAL ################################
    ###################################################################### 
    def lval(self, *args):
        return args[0]

    def lval_var(self, *args):
        return lval.Variable(args[0])

    def lval_slicing(self, *args):
        return lval.Slice(args[0], args[2], args[1])

    def lval_access(self, *args):
        lval_list = []
        for l in list(args):
            lval_list.append(lval.Variable(l))
        return lval.Access(lval_list)


    ######################################################################
    ############################### RULES ################################
    ######################################################################
    def assignment(self, *args):
        return ast.Assignment(args[0], args[1])

    def call(self, *args):
        name = args[0]
        arguments = None
        if len(args) > 1:
            arguments = args[1]
        match name.lower():
            case "extract":
                return ast.Extract(arguments)
            case "emit":
                return ast.Emit(arguments)
            case _:
                return ast.Call(name, arguments)

    def arguments(self, *args):
        return list(args)

    def if_statement(self, *args):
        else_body = None
        if (len(args) == 3):
            else_body = args[2]
        return ast.If(args[0], args[1], else_body)

    def transition(self, *args):
        if len(args) == 3:
            exp = args[0]
            val_states = args[1]
            def_state = args[2]
        else:
            exp = None
            val_states = args[0]
            def_state = args[1]
        if len(val_states)==0:
            val_states = None
        return ast.Transition(exp, def_state, val_states)

    def value_state(self, *args):
        return ast.ValueState(args[0], args[1])

    def value_states(self, *args):
        return list(args)

    def default_state(self, *args):
        return args[0]

    def parameters(self, *args):
        return list(args)

    def parameter(self, *args):
        pdirection, ptype, pname = args
        if (pdirection == None):
            pdirection = "in"
        return identifiers.Parameter(pdirection, ptype, pname)

    def apply(self, *args):
        if len(args) == 1:
            table_name = args[0]
            keys = None
        else:
            table_name = args[0]
            keys = args[1]
        return ast.Apply(table_name, keys)

    def keys(self, *args):
        return list(args)

    ######################################################################
    ############################ DECLARATIONS ############################
    ######################################################################
    def variable_declaration(self, *args):
        return ast.VariableDeclaration(args[0], args[1])

    def header_definition(self, *args):
        name = args[0]
        theader = types.Header()
        for fld in args[1]:
            fld.set_parent(theader)
            theader.add_field(fld)
        return ast.HeaderDeclaration(name, theader)

    def struct_definition(self, *args):
        name = args[0]
        tstruct = types.Struct()
        for fld in args[1]:
            fld.set_parent(tstruct)
            tstruct.add_field(fld)
        return ast.StructDeclaration(name, tstruct)

    def field_declarations(self, *args):
        return list(args)

    def field_declaration(self, *args):
        return identifiers.Field(args[0], args[1])

    def constant(self, *args):
        ctype, cvar, cvalue = args
        return ast.ConstantDeclaration(ctype, cvar, cvalue)
        
    
    ######################################################################
    ############################ DEFINITIONS #############################
    ######################################################################
    def function_definition(self, *args):
        if len(args) == 3:
            ret_type = args[0]
            name = args[1]
            parameters = None
            body = args[3]
        else:
            ret_type = args[0]
            name = args[1]
            parameters = args[2]
            body = args[3]
        return ast.FunctionDefinition(name, ret_type, parameters, body)
        #return {"stm_type" : "function_def", "name": name, "return_type": ret_type , "parameters": parameters , "body" : body}

    def action_definition(self, *args):
        if len(args) == 2:
            name = args[0]
            parameters = None;
            body = args[1]
        else:
            name = args[0]
            parameters = args[1]
            body = args[2]
        return ast.ActionDefinition(name, parameters, body)
        #return {"stm_type" : "action_definition", "name": name, "parameters": parameters , "body" : body}

    ###################################
    def parser_definition(self, *args):
        name = args[0]
        packetin = identifiers.Parameter("inout", "packet_in", args[1])
        if len(args[2]) == 1:
            header = args[2][0]
            parameters = None
        else:
            header = args[2][0]
            parameters = list(args[2][1:])
        body = args[3]
        return ast.ParserDefinition(name, packetin, header, parameters, body)
        #return {"stm_type" : "parser_definition", "name": name, "packet_in": packetin , "header": header, "parameters": parameters , "body" : body}


    def state_definition(self, *args):
        name = args[0]
        body = args[1]
        return ast.StateDefinition(name, body)
        #return {"stm_type" : "state_definition", "name": name, "body" : body}

    #########################################
    def controlblock_definition(self, *args):
        if len(args) == 2:
            name = args[0]
            parameters = None;
            body, apply_block = args[1]
        else:
            name = args[0]
            parameters = args[1]
            body, apply_block = args[2]

        return ast.ControlBlcokDefinition(name, parameters, apply_block, body)


    def controlblock_body(self, *args):
        body = []
        apply_block = None
        for arg in args:
            match arg.get_node_type():
                case ast.StatementsEnum.APPLY_BLOCK_DEFINITION:
                    apply_block = arg
                case _:
                    body.append(arg)

        if len(body) == 0:
            body = None
        
        return (body, apply_block)

    def apply_block_definition(self, *args):
        if (len(args) == 0):
            body = None
        else:
            body = args[0]
        return ast.ApplyBlcokDefinition(body)

    def apply_block_body(self, *args):
        if (len(args) == 0):
            body = None
        else:
            body = list(args)
        return body

    #################################
    def table_definition(self, *args):
        if len(args) == 3:
            name = args[0]
            keys = args[1]
            actions = args[2]
            size = None
            default_action = None
        elif (len(args) == 4):
            if (type(args[4]) == int):
                name = args[0]
                keys = args[1]
                actions = args[2]
                size = args[3]
                default_action = None
            else:
                name = args[0]
                keys = args[1]
                actions = args[2]
                size = None
                default_action = args[3]
        else:
            name = args[0]
            keys = args[1]
            actions = args[2]
            size = args[3]
            default_action = args[4]
        return ast.TableDefinition(name, keys, actions, size, default_action)
        #return {"stm_type" : "table_definition", "name": name, "keys": keys , "actions": actions, "size": size, "default_action":default_action}

    def table_keys_definition(self, *args):
        if (len(args) == 0):
            return None
        return list(args)

    def key_definition(self, *args):
        kname, kmatch = args
        return {"name": kname, "match": kmatch}
    
    def table_actions_definition(self, *args):
        if (len(args) == 0):
            return None
        return list(args)

    def table_size_definition(self, *args):
        return args[0]

    def table_default_definition(self, *args):
        return args[0]

    ######################################################################
    ############################### TYPES ################################
    ######################################################################
    def primitive_type(self, *args):
        return args[0]

    def bit_string_prim(self, *args):
        return types.BitString(args[0])

    def boolean_prim(self, *args):
        return types.Bool()

    def type_definition(self, *args):
        return ast.TypeDeclaration(args[0], args[1])

    def ttype(self, *args):
        _type = args[0]
        return _type

    def direction(self, *args):
        return args[0]

    ##### TERMINALS
    def term(self, token):
        return token
    def IDENTIFIER(self, token):
        return token.value
    def OPERATOR(self, token):
        return token.value
    def NUMBER(self, token):
        return int(token.value)

    def TRUE(self, token):
        return True
    def FALSE(self, token):
        return False
        

    def IN(self, token):
        return token.value
    def OUT(self, token):
        return token.value
    def INOUT(self, token):
        return token.value