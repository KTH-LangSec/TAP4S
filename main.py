import argparse
import copy

import type_system_lib as TS
import type_system_lib.label as LATIICE
import type_system_lib.gamma as GM
import logger as LOGGER
import parser_lib.lval as LVAL
import type_system_lib.mapping as MP
import policy_parser as POLICIY
import contract_parser as CONTRACT
import type_system_lib.types as TYPE
import parser_lib as PARSER
import type_system_lib.security_condition as SECURITY

import setting


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", type=str, help="Address the of the input program.")
    arg_parser.add_argument("-p", type=str, help="Address the of the input policy.")
    arg_parser.add_argument("-o", type=str, help="Address the of the output policy.")
    arg_parser.add_argument("-c", type=str, help="Address the of the contract.")

    arg_parser.add_argument('-d', action='store_true', help='Enable debug mode (prints gammas)')

    args = arg_parser.parse_args()

    if args.d:
        setting.debug = True

    #############################################
    #################### AST ####################
    #############################################
    if args.i:
        with open(args.i, 'r') as file:
            input_program = file.read()
    else:
        print()
        arg_parser.print_help()
        print()
        LOGGER.error("Please provide an input program!")

    ast = PARSER.parse(input_program)


    #############################################
    ################ Policy In ##################
    #############################################
    if args.p:
        with open(args.p, 'r') as file:
            file_contents = file.read()
        policy_in_list = POLICIY.parse(file_contents)
    else:
        LOGGER.warning("no input policy was provided!")
        policy_in_list = []
        #default_policy = "Ipacket: (0,120) -> ([0,0], low);"
        #policy_in_list = POLICIY.parse(default_policy)

    #############################################
    ################ Policy Out ##################
    #############################################
    if args.o:
        with open(args.o, 'r') as file:
            file_contents = file.read()
        policy_out_list = POLICIY.parse(file_contents)
    else:
        LOGGER.warning("no output policy was provided!")
        policy_out_list = []

    Gamma_o = []
    if (len(policy_out_list) != 0):
        for policy in policy_out_list:
            gamma_o = GM.GlobalGamma()

            for lval_policy in policy.get_lval_policies():
                lval = lval_policy.get_lval()
                bs_type = lval_policy.get_bit_string()
                gamma_o.add(lval, bs_type)

            Gamma_o.append(gamma_o)
            
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
    B_g, gamma_g_init = TS.pre_proccess(ast)
    Gamma_g_init = []

    ########## adding policy to gamma_init
    if (len(policy_in_list) != 0):
        for policy in policy_in_list:
            gamma_tmp = copy.deepcopy(gamma_g_init)

            for lval_policy in policy.get_lval_policies():
                lval = lval_policy.get_lval()
                if (gamma_tmp.exists(lval)):
                    current_type = gamma_tmp.get(lval)
                    match current_type.get_type():
                        case TYPE.TypesEnum.BIT_STRING:
                            bs_type = lval_policy.get_bit_string().consume_sub_string(current_type.get_size())
                            gamma_tmp.update(lval, bs_type)
                        case TYPE.TypesEnum.STRUCT:
                            struct_type = TS.bs_to_struct(lval_policy.get_bit_string(), current_type)
                            gamma_tmp.update(lval, struct_type)
                        case TYPE.TypesEnum.HEADER:
                            header_type = TS.bs_to_struct(lval_policy.get_bit_string(), current_type)
                            gamma_tmp.update(lval, header_type)
                        case TYPE.TypesEnum.BOOL:
                            bool_type = lval_policy.get_bit_string().consume_sub_string(current_type.get_size(), _bool=True)
                            gamma_tmp.update(lval, bool_type)
                        case TYPE.TypesEnum.INPUT_PACKET:
                            gamma_tmp.update(lval, lval_policy.get_bit_string())
                else: # the lavl used in the policy does not have a type in initial gamma
                    gamma_tmp.update(lval, lval_policy.get_bit_string())
            
            Gamma_g_init.append(gamma_tmp)
    else:
        Gamma_g_init.append(gamma_g_init)


    #############################################
    ################ Main Body ##################
    #############################################
    main_ast = TS.get_main_body(ast)


    #############################################
    ############### Type Check ##################
    #############################################
    final_Gamma = []
    for gamma_g_init_with_policy in Gamma_g_init:
        Gamma = TS.type_check_ast(main_ast, gamma_g_init_with_policy, GM.LocalGamma(), LATIICE.Low(), B_g, MP.Local_B() , C)
        final_Gamma.extend(Gamma)


    pruned_Gamma = GM.prune_invalid_gammas(final_Gamma)
    Gamma_g = [gg for (gg, gl) in pruned_Gamma]

    # print()
    # for i, (gg, gl) in enumerate(pruned_Gamma):
    #     print("########## final gamma " + str(i+1) + ":")
    #     print(gg)
        # print(gg.get(LVAL.Variable("Opacket")))

    #############################################
    ############## Security Check ###############
    #############################################
    verdict, reason = SECURITY.check(Gamma_g, Gamma_o)

    print("\n>>>>>> VERDICT >>>>>> ", end="")
    if verdict:
        print("\tSECURE ✓")
    else:
        print("\tINSECURE ✗")
        print("-"*20)
        print("gamma_1:\n", reason[0])
        print("gamma_2:\n", reason[1])
        print("gamma_o:\n", reason[2])


