import type_system_lib.gamma as GM
import copy

import logger as LOGGER



def check(_Gamma_g, _Gamma_o):
    for gamma_o in _Gamma_o:
        for i, t_gamma_g_1 in enumerate(_Gamma_g):
            for j, t_gamma_g_2 in enumerate(_Gamma_g):
                if (i != j):
                    gamma_g_1 = t_gamma_g_1.project(gamma_o.get_keys()).serialize()
                    gamma_g_2 = t_gamma_g_2.project(gamma_o.get_keys()).serialize()
                    if ( (not GM.is_gamma_intersect_empty(gamma_o, gamma_g_1)) and (not GM.is_gamma_intersect_empty(gamma_o, gamma_g_2))):
                        LOGGER.debug("---------------------"*2)
                        GM.join_gamma(gamma_g_1, gamma_g_2)
                        LOGGER.debug("gamma_join:\n" + str(gamma_g_1))
                        LOGGER.debug("gamma_o:\n" + str(gamma_o))
                        if not GM.is_below(gamma_g_1, gamma_o):
                            return False, (gamma_g_1, gamma_g_2, gamma_o)

    return True, None

    # for gamma_o in _Gamma_o:
    #     for i, t_gamma_g_1 in enumerate(_Gamma_g):
    #         gamma_g = t_gamma_g_1.project(gamma_o.get_keys()).serialize()
    #         print("---------------------"*2)
    #         print("gamma_g1:\n", gamma_g)
    #         print("gamma_o:\n", gamma_o)
    #         print()
