from lark import Lark
import argparse
import pprint
import copy

import type_system_lib as TS
import type_system_lib.label as LATIICE
import type_system_lib.gamma as GM
import helper_functions as HELPER
import type_system_lib.parse_policy as POLICIY
import parser_lib.lval as LVAL
import parser_lib.transformer as TRANSFORMER

##################################################
GRAMMAR_FILE = "grammer.lark"
DEFAULY_POLICY = "(0,32) -> ([*], low)"
##################################################

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", type=str, help="Address the of the input program.")
    arg_parser.add_argument("-pin", type=str, help="Address the of the input policy.")
    arg_parser.add_argument("-pout", type=str, help="Address the of the output policy.")

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
    packet_in = POLICIY.pre_proccess(ast_lst)
    if (packet_in != None):
        packet_in_lval = packet_in
    else:
        HELPER.warning("no parser was found!")
        packet_in_lval = LVAL.Variable("packet_in")


    if args.pin:
        with open(args.pin, 'r') as file:
            file_contents = file.read() # Read the entire contents of the file into a string
        input_policy = file_contents.replace('\n', '').strip() # Remove newlines and any trailing whitespace
    else:
        HELPER.warning("no input policy was provided!")
        input_policy = DEFAULY_POLICY
    
    policy_in = POLICIY.process_input_policy(input_policy)


    #############################################
    ################## Gamma ####################
    #############################################
    B, gamma_g_init = TS.pre_proccess(ast_lst)

    Gamma_G_init_with_policy = []
    for policy_in_type in policy_in:
        gamma_tmp = copy.deepcopy(gamma_g_init)
        gamma_tmp.add(packet_in_lval, policy_in_type)
        Gamma_G_init_with_policy.append(gamma_tmp)

    # TODO, contract, output policy
    C = {}

    final_Gamma = []
    for gamma_g_init_with_policy in Gamma_G_init_with_policy:
        Gamma = TS.type_check_ast(ast_lst, gamma_g_init_with_policy, GM.LocalGamma(), LATIICE.Low(), B, C)
        final_Gamma.extend(Gamma)

    print()
    for i, (gg, gl) in enumerate(final_Gamma):
        print("########## final gamma " + str(i+1) + ":")
        print(gg)
        #print(gl)


    # # for i in ast_lst:
    # #     print(i)
