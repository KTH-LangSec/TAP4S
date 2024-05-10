import argparse
import copy
import time

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
import input_process as INPUT

import setting


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", type=str, help="Address the of the input program.")
    arg_parser.add_argument("-p", type=str, help="Address the of the input policy.")
    arg_parser.add_argument("-o", type=str, help="Address the of the output policy.")
    arg_parser.add_argument("-c", type=str, help="Address the of the contract.")
    arg_parser.add_argument("--dir", type=str, help="Address the of the directory containing a P4 program, input and output policy, and contracts.")

    arg_parser.add_argument('-d', action='store_true', help='Debug mode - print the security checks')
    arg_parser.add_argument('-g', action='store_true', help='Debug mode - print final Gamma')
    arg_parser.add_argument('-t', action='store_true', help='Print timing information')

    args = arg_parser.parse_args()

    if args.d:
        setting.show_checks = True

    if args.g:
        setting.show_Gamma = True

    if args.t:
        setting.show_timing = True

    input_program, input_policy, output_policy, contracts = INPUT.arg_process(args.i, args.p, args.o, args.c, args.dir)


    start_time_total = time.perf_counter() # timing

    #################### AST ####################
    ast = PARSER.parse(input_program)

    ################ Policy In ##################
    policy_in_list = POLICIY.parse(input_policy)

    ################ Policy Out #################
    policy_out_list = POLICIY.parse(output_policy)

    Gamma_o = []
    if (len(policy_out_list) != 0):
        for policy in policy_out_list:
            gamma_o = GM.GlobalGamma()

            for lval_policy in policy.get_lval_policies():
                lval = lval_policy.get_lval()
                bs_type = lval_policy.get_bit_string()
                gamma_o.add(lval, bs_type)

            Gamma_o.append(gamma_o)
            
    ################# Contract ##################
    contracts_list = CONTRACT.parse(contracts)

    C = MP.Contracts()
    if (len(contracts_list) != 0):
        for cont in contracts_list:
            if isinstance(cont, CONTRACT.contract.ExternContract):
                C.add_extern(cont.get_name(), cont)
            elif isinstance(cont, CONTRACT.contract.TableContract):
                C.add_table(cont.get_name(), cont)


    ################## Gamma ####################
    start_time_gamma_gen = time.perf_counter() # timing

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

    end_time_gamma_gen = time.perf_counter() # timing

    ################ Main Body ##################
    main_ast = TS.get_main_body(ast)

    ############### Type Check ##################
    start_time_type_check = time.perf_counter() # timing

    final_Gamma = []
    for gamma_g_init_with_policy in Gamma_g_init:
        Gamma = TS.type_check_ast(main_ast, gamma_g_init_with_policy, GM.LocalGamma(), LATIICE.Low(), B_g, MP.Local_B() , C)
        final_Gamma.extend(Gamma)

    end_time_type_check = time.perf_counter() # timing

    pruned_Gamma = GM.prune_invalid_gammas(final_Gamma)
    Gamma_g = [gg for (gg, gl) in pruned_Gamma]


    ############ Print Final Gamma ##############
    if setting.show_Gamma:
        print()
        for i, (gg, gl) in enumerate(pruned_Gamma):
            print("########## Final gamma " + str(i+1) + ":")
            print(gg)

    #############################################
    ############## Security Check ###############
    #############################################
    start_time_security_check = time.perf_counter() # timing

    verdict, gammas, checks = SECURITY.check(Gamma_g, Gamma_o)

    LOGGER.print_blue("\n>>>>>> Generated Gammas: "+ str(len(pruned_Gamma)), end="")
    LOGGER.print_blue("\n>>>>>> Performed Checks: "+ str(checks), end="")
    LOGGER.print_blue("\n>>>>>> Verdict: ", end="")
    if verdict:
        LOGGER.print_green("SECURE ✓")
    else:
        LOGGER.print_red("INSECURE ✗")
        print("-"*21)
        print("gamma_1:\n", gammas[0])
        print("gamma_2:\n", gammas[1])
        print("gamma_o:\n", gammas[2])

    end_time_security_check = time.perf_counter() # timing

    ################## Timing ###################
    end_time_total = time.perf_counter()

    if (setting.show_timing):
        execution_time_total = (end_time_total - start_time_total)  * 1000
        execution_time_gamma_gen = (end_time_gamma_gen - start_time_gamma_gen)  * 1000
        execution_time_type_check = (end_time_type_check - start_time_type_check)  * 1000
        execution_time_security_check = (end_time_security_check - start_time_security_check)  * 1000

        print()
        print("-"*30)
        print("{:<20} {:<10}".format("Task", "Time"))
        print("-"*30)
        print("{:<20} {:<10}".format("Total", round(execution_time_total, 2)))
        print("{:<20} {:<10}".format("Gamma Generation", round(execution_time_gamma_gen, 2)))
        print("{:<20} {:<10}".format("Type Checking", round(execution_time_type_check, 2)))
        print("{:<20} {:<10}".format("Security Check", round(execution_time_security_check, 2)))


