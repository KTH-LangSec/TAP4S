import parser_lib.ast as AST
import parser_lib.types as Ptypes
import parser_lib.expression as Pexp
import type_system_lib.gamma as GM
import type_system_lib.mapping as MP
import type_system_lib.types as TYPE
import type_system_lib.expression as EXP
import type_system_lib.label as LATTICE
import logger as LOGGER

import copy


DEFINED_TYPES = {} # defined types, structs, headers, and input/output policy

def pre_proccess(_ast):
    get_defined_types(_ast)

    B_g = generate_B_mapping(_ast, _global=True)
    gamma = generate_gamma(_ast, _global=True)
    return B_g, gamma


def type_check_ast(_ast, _gamma_g, _gamma_l, _pc, _B_g, _B_l, _C):
    Gamma = [(_gamma_g, _gamma_l)]
    for stm in _ast:
        Gamma_t = []
        for gamma_g, gamma_l in Gamma:
            returned_Gamma = type_check_statement(stm, gamma_g, gamma_l, _pc, _B_g, _B_l, _C)
            Gamma_t.extend(returned_Gamma)

        Gamma = Gamma_t

    return Gamma


def type_check_statement(_stm, _gamma_g, _gamma_l, _pc, _B_g, _B_l, _C):
    match _stm.get_node_type():
        case AST.StatementsEnum.ASSIGNMET:
            exp_type = EXP.type_check_expression(_stm.get_expression(), _gamma_g, _gamma_l)
            exp_type.raise_label(_pc)
            GM.update(_stm.get_identifier(), exp_type, _gamma_g, _gamma_l)
            return [(_gamma_g, _gamma_l)]

        case AST.StatementsEnum.FUNCTION_CALL:
            f_name = _stm.get_name()
            f_args = _stm.get_arguments()

            ######### local function call #########
            if (_B_l.exists(f_name)):
                f_body, f_params, f_type = _B_l.get(f_name)
                if (f_type == MP.FunctionTypeEnum.CONTROL_BLOCK) or (f_type == MP.FunctionTypeEnum.PARSER):
                    LOGGER.error("Calling local parser or control block is not supported!")
                else:
                    return function_call(_gamma_g, _gamma_l, _pc, _B_g, _C, f_name, f_args, f_body, f_params)

            ######### global function call #########
            elif (_B_g.exists(f_name)):
                f_body, f_params, f_type = _B_g.get(f_name)
                match f_type:
                    case MP.FunctionTypeEnum.PARSER:
                        _stm.update_node_type(AST.StatementsEnum.PARSER_CALL) # updating the node type to indicate the function call was in fact a parser call
                        return type_check_statement(_stm, _gamma_g, _gamma_l, _pc, _B_g, _B_l, _C)
                    case MP.FunctionTypeEnum.CONTROL_BLOCK:
                        _stm.update_node_type(AST.StatementsEnum.CONTROL_BLOCK_CALL) # updating the node type to indicate the function call was in fact a control block call
                        return type_check_statement(_stm, _gamma_g, _gamma_l, _pc, _B_g, _B_l, _C)
                    case MP.FunctionTypeEnum.STATE:
                        LOGGER.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    case _:
                        return function_call(_gamma_g, _gamma_l, _pc, _B_g, _C, f_name, f_args, f_body, f_params)
            
            ######### extern #########
            elif (_C.extern_exists(f_name)):
                cont = _C.get_extern(f_name)
                Gamma_f = []

                for pred, gamma_t in cont.get().items():
                    ref_gamma = GM.refine_cond(_gamma_g, _gamma_l, pred)
                    if (ref_gamma != None):
                        ref_gamma_g = ref_gamma[0]
                        ref_gamma_l = ref_gamma[1]
                        GM.augment(ref_gamma_l, gamma_t, f_args)
                        Gamma_f.append((ref_gamma_g, ref_gamma_l))

                return Gamma_f

            else:
                LOGGER.error("Cannot find the definition of \"" + str(f_name) + "\"!")

        case AST.StatementsEnum.IF:
            exp = _stm.get_expression()
            exp_type = EXP.type_check_expression(exp, _gamma_g, _gamma_l)
            l = exp_type.get_label()
            pc_prime = LATTICE.lup(_pc, l)

            # Cup of Gammas
            Gamma_f = [] 
            
            #### Gamma 1
            ref_gamma_1 = GM.refine_cond(_gamma_g, _gamma_l, exp)
            if (ref_gamma_1 != None):
                for (ref_gamma_g_e, ref_gamma_l_e) in ref_gamma_1:
                    Gamma_1 = type_check_ast(_stm.get_then_body(), ref_gamma_g_e, ref_gamma_l_e, pc_prime, _B_g, _B_l, _C)
                    Gamma_f.extend(Gamma_1)

            #### Gamma 2
            ref_gamma_2 = GM.refine_cond(_gamma_g, _gamma_l, Pexp.negate(exp))
            if (ref_gamma_2 != None):
                for (ref_gamma_g_ne, ref_gamma_l_ne) in ref_gamma_2:
                    Gamma_2 = type_check_ast(_stm.get_else_body(), ref_gamma_g_ne, ref_gamma_l_ne, pc_prime, _B_g, _B_l, _C)
                    Gamma_f.extend(Gamma_2)

            
            if (l.is_high()):
                GM.join_Gammas(Gamma_f)
            
            return Gamma_f

        case AST.StatementsEnum.EXTRACT_CALL:
            packet_in = _stm.get_packet_in()
            argument = _stm.get_argument()

            arg_type = GM.lookup(argument, _gamma_g, _gamma_l)
            size = arg_type.get_size()
            
            arg_type_bs, new_p_type = extract_get(_gamma_g, _gamma_l, packet_in, size)

            new_arg_type = bs_to_struct(arg_type_bs, arg_type)

            GM.update(packet_in, new_p_type, _gamma_g, _gamma_l)
            GM.update(argument, new_arg_type, _gamma_g, _gamma_l)

            return [(_gamma_g, _gamma_l)]

        case AST.StatementsEnum.CONTROL_BLOCK_CALL:
            ct_name = _stm.get_name()
            ct_args = _stm.get_arguments()

            if (_B_g.exists(ct_name)):
                ct_body, ct_params, ct_type = _B_g.get(ct_name)
                ct_apply_body = ct_body[0].get_body()
                ctrl_body = ct_body[1]

                return control_blcok_call(_gamma_g, _gamma_l, _pc, _B_g, _C, ct_name, ct_args, ct_apply_body, ctrl_body, ct_params)
            
            else:
                LOGGER.error("Cannot find the definition of control block \"" + str(f_name) + "\"!")


        case AST.StatementsEnum.PARSER_CALL:
            p_name = _stm.get_name()
            p_args = _stm.get_arguments()
            p_body, p_params, p_type = _B_g.get(p_name)

            B_l = generate_B_mapping(p_body, _global=False)
            start_state_body, _, _ = B_l.get("start")

            return parser_call(_gamma_g, _gamma_l, _pc, _B_g, B_l, _C, p_name, p_args, start_state_body, p_params)

        case AST.StatementsEnum.TRANSITION:
            exp = _stm.get_expression()
            exp_type = EXP.type_check_expression(exp, _gamma_g, _gamma_l)
            l = exp_type.get_label()
            pc_prime = LATTICE.lup(_pc, l)

            values = []
            states = []

            value_state_list = _stm.get_states()
            if (value_state_list != None):
                for value_state in _stm.get_states():
                    values.append(value_state.get_value())
                    states.append(value_state.get_state())

            ref_Gamma = GM.refine_trans(_gamma_g, _gamma_l, exp, values)
            states.append(_stm.get_default_state()) # adding the default state last

            if (len(ref_Gamma) == 1): # there is only a default state
                ref_gamma_g, ref_gamma_l = ref_Gamma[0]
                state_body_d, _, _ = _B_l.get(states[0])
                # We don't support local gamma and local B for states. Please see the Trans rule in the paper.
                Gamma_d = type_check_ast(state_body_d, ref_gamma_g, ref_gamma_l, _pc, _B_g, _B_l, _C)
                Gamma_f = Gamma_d
            else:
                Gamma_f = []
                for i, (ref_gamma_g, ref_gamma_l) in enumerate(ref_Gamma):
                    state_body_i, _, _ = _B_l.get(states[i])
                    # We don't support local gamma and local B for states. Please see the Trans rule in the paper.
                    Gamma_i = type_check_ast(state_body_i, ref_gamma_g, ref_gamma_l, _pc, _B_g, _B_l, _C)
                    Gamma_f.extend(Gamma_i)
            

            if (l.is_high()):
                GM.join_Gammas(Gamma_f)

            return Gamma_f


        case AST.StatementsEnum.APPLY:
            print("here")


            return [(_gamma_g, _gamma_l)]

        case _: #TODO temp
            return [(_gamma_g, _gamma_l)]




##############################################################
##############################################################
def generate_B_mapping(_ast, _global=True):
    if (_global):
        B = MP.Global_B()
    else:
        B = MP.Local_B()
        
    for stm in _ast:
        if issubclass(type(stm), AST.Statement):
            match stm.get_node_type():
                case AST.StatementsEnum.FUNCTION_DEFINITION:
                    B.add(stm.get_name(), stm.get_body(), stm.get_parameters(), MP.FunctionTypeEnum.FUNCTION)

                case AST.StatementsEnum.ACTION_DEFINITION:
                    B.add(stm.get_name(), stm.get_body(), stm.get_parameters(), MP.FunctionTypeEnum.ACTION)

                case AST.StatementsEnum.CONTROL_BLOCK_DEFINITION:
                    B.add(stm.get_name(), (stm.get_apply_block(), stm.get_body()), stm.get_parameters(), MP.FunctionTypeEnum.CONTROL_BLOCK)

                case AST.StatementsEnum.PARSER_DEFINITION:
                    parameters = []
                    parameters.append(stm.get_packet_in())
                    parameters.append(stm.get_header())
                    if (stm.get_parameters() != None):
                        parameters.extend(stm.get_parameters())

                    B.add(stm.get_name(), stm.get_body(), parameters, MP.FunctionTypeEnum.PARSER)

                case AST.StatementsEnum.STATE_DEFINITION:
                    B.add(stm.get_name(), stm.get_body(), None ,MP.FunctionTypeEnum.STATE)

    return B

##############################################################
##############################################################
def generate_gamma(_ast, _global, _params=None):
    if (_global == True):
        gamma = GM.GlobalGamma();
    else:
        gamma = GM.LocalGamma();
        if (_params != None):
            for param in _params:
                gamma.add(param.get_variable(), generate_type(param.get_type()))
    
    # TODO: need to check both branches of if as well
    for stm in _ast:
        if issubclass(type(stm), AST.Statement):
            match stm.get_node_type():
                case AST.StatementsEnum.VARIABLE_DECLARATION:
                    gamma.add(stm.get_variable(), generate_type(stm.get_type()))

                case AST.StatementsEnum.CONSTANT_DECLARATION:
                    gamma.add(stm.get_variable(), generate_type(stm.get_type(), stm.get_value()))
    return gamma


##############################################################
##############################################################
def generate_type(_stm_type, _value=None):

    # TODO: Support struct value 

    if issubclass(type(_stm_type), Ptypes.PrimitiveType):
        match _stm_type.get_type():
            case Ptypes.TypesEnum.BIT_STRING:
                return TYPE.BitString(_stm_type.get_size(), _value=_value)

            case Ptypes.TypesEnum.BOOL:
                return TYPE.Bool(_value=_value)   
            
    elif _stm_type in DEFINED_TYPES:
        return DEFINED_TYPES[_stm_type]

##############################################################
##############################################################
def get_defined_types(_ast):
    for stm in _ast:
        if issubclass(type(stm), AST.Statement):
            match stm.get_node_type():
                case AST.StatementsEnum.TYPE_DECLARATION:
                    DEFINED_TYPES[stm.get_name()] = generate_type(stm.get_primitive())

                case AST.StatementsEnum.STRUCT_DECLARATION:
                    struct = TYPE.Struct()
                    for field in stm.get_type().get_fields():
                        struct.add_field(field.get_name(), generate_type(field.get_type()))
                    DEFINED_TYPES[stm.get_name()] = struct

                case AST.StatementsEnum.HEADER_DECLARATION:
                    header = TYPE.Header()
                    for field in stm.get_type().get_fields():
                        header.add_field(field.get_name(), generate_type(field.get_type()))
                    DEFINED_TYPES[stm.get_name()] = header


##############################################################
####################### PARSER CALL #########################
##############################################################
def parser_call(_gamma_g, _gamma_l, _pc, _B_g, _B_l, _C, _p_name, _p_args, _start_body, _p_params):
    gamma_l_p, co = function_call_preprocess(_gamma_g, _gamma_l, _p_name, _p_args, _start_body, _p_params)
    returned_Gamma = type_check_ast(_start_body, _gamma_g, gamma_l_p, _pc, _B_g, _B_l, _C)

    Gamma_n = []
    for (g_g, g_l) in returned_Gamma:
        Gamma_n.append(function_call_postprocess(g_g, g_l, co, _gamma_l))

    return Gamma_n                

##############################################################
#################### CONTROL BLOCK CALL ######################
##############################################################
def control_blcok_call(_gamma_g, _gamma_l, _pc, _B_g, _C, _ct_name, _ct_args, _ct_apply_body, _ct_body, _ct_params):
    B_l = generate_B_mapping(_ct_body, _global=False)
    
    gamma_l_f, co = function_call_preprocess(_gamma_g, _gamma_l, _ct_name, _ct_args, _ct_body, _ct_params)
    returned_Gamma = type_check_ast(_ct_apply_body, _gamma_g, gamma_l_f, _pc, _B_g, B_l, _C)

    Gamma_n = []
    for (g_g, g_l) in returned_Gamma:
        Gamma_n.append(function_call_postprocess(g_g, g_l, co, _gamma_l))

    return Gamma_n

##############################################################
###################### FUNCTION CALL #########################
##############################################################
def function_call(_gamma_g, _gamma_l, _pc, _B_g, _C, _f_name, _f_args, _f_body, _f_params):
    B_l = generate_B_mapping(_f_body, _global=False)  
    gamma_l_f, co = function_call_preprocess(_gamma_g, _gamma_l, _f_name, _f_args, _f_body, _f_params)
    returned_Gamma = type_check_ast(_f_body, _gamma_g, gamma_l_f, _pc, _B_g, B_l, _C)

    Gamma_n = []
    for (g_g, g_l) in returned_Gamma:
        Gamma_n.append(function_call_postprocess(g_g, g_l, co, _gamma_l))

    return Gamma_n


def function_call_preprocess(_gamma_g, _gamma_l, _f_name, _f_args, _f_body, _f_params):
    ## local gamma
    gamma_l = generate_gamma(_f_body, _global=False, _params=_f_params)
    for i, param in enumerate(_f_params):
        if (param.get_direction() == "in" or param.get_direction() == "inout"):
            exp_type = EXP.type_check_expression(_f_args[i], _gamma_g, _gamma_l)
            GM.update(param.get_variable(), exp_type, _gamma_g, gamma_l)

    # parameter to argument mapping
    co = MP.CO()
    for i, param in enumerate(_f_params):
        if (param.get_direction() == "out" or param.get_direction() == "inout"):
            # TODO check type equality
            co.add_relation(param.get_variable(), _f_args[i])

    return gamma_l, co


def function_call_postprocess(_gamma_g, _gamma_l, _co, _gamma_l_old):
    for param in _co.get_parameters():
        exp_type = EXP.type_check_expression(param, _gamma_g, _gamma_l)
        GM.update(_co.get_relation(param), exp_type, _gamma_g, _gamma_l_old)

    return (_gamma_g, _gamma_l_old)

##############################################################
####################### EXTERN CALL ##########################
##############################################################
def extern_call():
    pass

##############################################################
###################### EXTRACT CALL ##########################
##############################################################
def extract_get(_gamma_g, _gamma_l, _packet_in_lval, _size):
    p_type = GM.lookup(_packet_in_lval, _gamma_g, _gamma_l)
    arg_type = p_type.consume_sub_string(_size)

    return (arg_type, p_type)


def bs_to_struct(_bs_type, _struct_type):
    struct_type = copy.deepcopy(_struct_type)

    for fld_n, fld_type in struct_type.get_fields():
        match fld_type.get_type():
            case TYPE.TypesEnum.STRUCT:
                struct_type = bs_to_struct(_bs_type, fld_type)
            case TYPE.TypesEnum.HEADER:
                struct_type = bs_to_struct(_bs_type, fld_type)
            case TYPE.TypesEnum.BIT_STRING:
                fld_type = _bs_type.consume_sub_string(fld_type.get_size())
                struct_type.update_field(fld_n, fld_type)
            case TYPE.TypesEnum.BOOL:
                fld_type_bool = _bs_type.consume_sub_string(fld_type.get_size(), _bool=True)
                struct_type.update_field(fld_n, fld_type_bool)

    return struct_type

