import parser_lib.ast as AST
import parser_lib.types as Ptypes
import parser_lib.expression as Pexp
import type_system_lib.gamma as GM
import type_system_lib.mapping as MP
import type_system_lib.types as TYPE
import type_system_lib.expression as EXP
import type_system_lib.label as LATTICE

import copy


DEFINED_TYPES = {} # mapping from name to the primitive

def pre_proccess(_ast):
    get_defined_types(_ast)
    B = generate_mappings(_ast)
    gamma = generate_gamma(_ast)
    return B, gamma


def type_check_ast(_ast, _gamma_g, _gamma_l, _pc, _B, _C):
    Gamma = [(_gamma_g, _gamma_l)]
    for stm in _ast:
        Gamma_t = []
        for gamma_g, gamma_l in Gamma:
            returned_Gamma = type_check_statement(stm, gamma_g, gamma_l, _pc, _B, _C)
            Gamma_t.extend(returned_Gamma)

        Gamma = Gamma_t

    return Gamma


def type_check_statement(_stm, _gamma_g, _gamma_l, _pc, _B, _C):
    match _stm.get_node_type():
        case AST.StatementsEnum.ASSIGNMET:
            exp_type = EXP.type_check_expression(_stm.get_expression(), _gamma_g, _gamma_l)
            exp_type.raise_label(_pc)
            GM.update(_stm.get_identifier(), exp_type, _gamma_g, _gamma_l)
            return [(_gamma_g, _gamma_l)]

        case AST.StatementsEnum.FUNCTION_CALL:
            f_name = _stm.get_name()
            f_args = _stm.get_arguments()
            f_body = _B.get_function_body(f_name)
            
            gamma_l_f, m = function_call_preprocess(_gamma_g, _gamma_l, _pc, _B, f_name, f_args)

            returned_Gamma = type_check_ast(f_body, _gamma_g, gamma_l_f, _pc, _B, _C)

            Gamma_n = []
            for (gg, gl) in returned_Gamma:
                Gamma_n.append(function_call_postprocess(gg, gl, _pc, m, _gamma_l))

            return Gamma_n

        case AST.StatementsEnum.IF:
            exp = _stm.get_expression()
            exp_type = EXP.type_check_expression(exp, _gamma_g, _gamma_l)
            l = exp_type.get_label()
            pc_prime = LATTICE.lup(_pc, l)
            
            #### Gamma 1
            (ref_gamma_g_e, ref_gamma_l_e) = GM.refine(_gamma_g, _gamma_l, exp)
            Gamma_1 = type_check_ast(_stm.get_then_body(), ref_gamma_g_e, ref_gamma_l_e, pc_prime, _B, _C)

            (ref_gamma_g_ne, ref_gamma_l_ne) = GM.refine(_gamma_g, _gamma_l, Pexp.negate(exp))
            Gamma_2 = type_check_ast(_stm.get_else_body(), ref_gamma_g_ne, ref_gamma_l_ne, pc_prime, _B, _C)
            return GM.cup(Gamma_1, Gamma_2)

        case _: #TODO temp
            return [(_gamma_g, _gamma_l)]




##############################################################
##############################################################
def generate_mappings(_ast, B=None):
    if (not B):
        B = MP.B()
    for stm in _ast:
        if issubclass(type(stm), AST.Statement):
            match stm.get_node_type():
                case AST.StatementsEnum.FUNCTION_DEFINITION:
                    B.add_function(stm.get_name(), stm.get_body(), stm.get_parameters())
                    generate_mappings(stm.get_body(), B)

                case AST.StatementsEnum.ACTION_DEFINITION:
                    B.add_function(stm.get_name(), stm.get_body(), stm.get_parameters())
                    generate_mappings(stm.get_body(), B)

                case AST.StatementsEnum.CONTROL_BLOCK_DEFINITION:
                    B.add_function(stm.get_name(), stm.get_body(), stm.get_parameters())
                    generate_mappings(stm.get_body(), B)

                case AST.StatementsEnum.PARSER_DEFINITION:
                    B.add_function(stm.get_name(), stm.get_body(), stm.get_parameters())
                    generate_mappings(stm.get_body(), B)

                case AST.StatementsEnum.STATE_DEFINITION:
                    B.add_state(stm.get_name(), stm.get_body())
                    generate_mappings(stm.get_body(), B)

    return B

##############################################################
##############################################################
def generate_gamma(_ast, _params=None):
    if (_params == None):
        gamma = GM.GlobalGamma();
    else:
        gamma = GM.LocalGamma();
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
##############################################################
def function_call_preprocess(_gamma_g, _gamma_l, _pc, _B, _f_name, _args):
    ## local gamma
    gamma_l = generate_gamma(_B.get_function_body(_f_name), _B.get_function_parameters(_f_name))
    for i, param in enumerate(_B.get_function_parameters(_f_name)):
        if (param.get_direction() == "in" or param.get_direction() == "inout"):
            exp_type = EXP.type_check_expression(_args[i], _gamma_g, _gamma_l)
            exp_type.raise_label(_pc)
            # TODO: what if parameter definition is not a variable?
            GM.update(param.get_variable(), exp_type, _gamma_g, gamma_l)

    # parameter to argument mapping
    m = MP.M()
    for i, param in enumerate(_B.get_function_parameters(_f_name)):
        if (param.get_direction() == "out" or param.get_direction() == "inout"):
            # TODO check type equality
            # TODO what if nothing is passed for some parameters
            m.add_relation(param.get_variable(), _args[i])

    return gamma_l, m


def function_call_postprocess(_gamma_g, _gamma_l, _pc, _m, _gamma_l_old):
    for param in _m.get_parameters():
        exp_type = EXP.type_check_expression(param, _gamma_g, _gamma_l)
        exp_type.raise_label(_pc)
        GM.update(_m.get_relation(param), exp_type, _gamma_g, _gamma_l_old)

    return (_gamma_g, _gamma_l_old)