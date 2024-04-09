from lark import Lark
import argparse
import pprint
import copy

import type_system_lib as TS
import type_system_lib.label as LATIICE
import type_system_lib.gamma as GM
import logger as LOGGER
import parser_lib.lval as LVAL
import parser_lib.transformer as TRANSFORMER
import type_system_lib.mapping as MP
import policy_parser as POLICIY
import contract_parser as CONTRACT
import type_system_lib.types as TYPE

##################################################
GRAMMAR_FILE = "grammar.lark"
##################################################


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", type=str, help="Address the of the input program.")
    arg_parser.add_argument("-p", type=str, help="Address the of the input policy.")
    arg_parser.add_argument("-o", type=str, help="Address the of the output policy.")
    arg_parser.add_argument("-c", type=str, help="Address the of the contract.")

    args = arg_parser.parse_args()

    #############################################
    #################### AST ####################
    #############################################
    if args.i:
        with open(args.i, 'r') as file:
            input_program = file.read()
    else:
        print()
        print(">>> Please provide the address of the source code")
        print()
        arg_parser.print_help()
        exit(0)

    with open(GRAMMAR_FILE, 'r') as file:
        grammar = file.read()

    parser = Lark(grammar,parser="lalr")
    parse_tree = parser.parse(input_program)
    ast = TRANSFORMER.P4Transformer().transform(parse_tree)
    ast_lst = list(ast)


    #############################################
    ################## Policy ###################
    #############################################
    if args.p:
        with open(args.pin, 'r') as file:
            file_contents = file.read()
        policy_in_list = POLICIY.parse(file_contents)
    else:
        LOGGER.warning("no input policy was provided!")
        policy_in_list = []
        #default_policy = "packet: (0,6) -> ([*], low); (7,13) -> ([*], low); x: (0,2) -> ([1,2], low); | packet: (0,13) -> ([*], high);"
        #policy_in_list = POLICIY.parse(default_policy)

    #############################################
    ################# Contract ##################
    #############################################
    if args.c:
        with open(args.c, 'r') as file:
            file_contents = file.read()
        contracts_list = CONTRACT.parse(file_contents)
    else:
        LOGGER.warning("no contract file was provided!")
        contracts_list = []

    # TODO parse output policy
    C = MP.Contracts()
    if (len(contracts_list) != 0):
        for cont in contracts_list:
            if isinstance(cont, CONTRACT.contract.ExternContract):
                C.add_extern(cont.get_name(), cont)
            elif isinstance(cont, CONTRACT.contract.TableContract):
                C.add_table(cont.get_name(), cont)

    #############################################
    ################## Gamma ####################
    #############################################
    B_g, gamma_g_init = TS.pre_proccess(ast_lst)
    Gamma_g_init = []

    ########## adding policy to gamma_init
    if (len(policy_in_list) != 0):
        for policy in policy_in_list:
            gamma_tmp = copy.deepcopy(gamma_g_init)

            for lval_policy in policy.get_lval_policies():
                lval = lval_policy.get_lval()
                current_type = gamma_tmp.get(lval)
                if (current_type != None):
                    match current_type.get_type():
                        case TYPE.TypesEnum.BIT_STRING:
                            bs_type = lval_policy.get_bit_string().consume_sub_string(current_type.get_size())
                            gamma_tmp.update(lval, bool_type)
                        case TYPE.TypesEnum.STRUCT:
                            struct_type = TS.bs_to_struct(lval_policy.get_bit_string(), current_type)
                            gamma_tmp.update(lval, struct_type)
                        case TYPE.TypesEnum.HEADER:
                            header_type = TS.bs_to_struct(lval_policy.get_bit_string(), current_type)
                            gamma_tmp.update(lval, header_type)
                        case TYPE.TypesEnum.BOOL:
                            bool_type = lval_policy.get_bit_string().consume_sub_string(current_type.get_size(), _bool=True)
                            gamma_tmp.update(lval, bool_type)
                else: # the lavl used in the policy does not have a type in initial gamma
                    gamma_tmp.update(lval_policy.get_lval(), lval_policy.get_bit_string())
            
            Gamma_g_init.append(gamma_tmp)
    else:
        Gamma_g_init.append(gamma_g_init)

    final_Gamma = []
    for gamma_g_init_with_policy in Gamma_g_init:
        Gamma = TS.type_check_ast(ast_lst, gamma_g_init_with_policy, GM.LocalGamma(), LATIICE.Low(), B_g, MP.Local_B() , C)
        final_Gamma.extend(Gamma)

    print()
    for i, (gg, gl) in enumerate(final_Gamma):
        print("########## final gamma " + str(i+1) + ":")
        print(gg)
        #print(gl)


    # # for i in ast_lst:
    # #     print(i)
