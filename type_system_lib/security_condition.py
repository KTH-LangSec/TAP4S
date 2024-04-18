import type_system_lib.gamma as GM
import copy



def check(_Gamma_g, _Gamma_o):
    for gamma_o in _Gamma_o:
        for i in range(len(_Gamma_g)):
            for j in range(i+1, len(_Gamma_g)):
                gamma_g_1 = copy.deepcopy(_Gamma_g[i])
                gamma_g_2 = copy.deepcopy(_Gamma_g[j])
                if not (GM.is_gamma_intersect_empty(gamma_o, gamma_g_1) and GM.is_gamma_intersect_empty(gamma_o, gamma_g_2)):
                    GM.join_gamma(gamma_g_1, gamma_g_2)
                    if not GM.is_below(gamma_g_1, gamma_o):
                        print("---------------------"*2)
                        print(GM.is_below(gamma_g_1, gamma_o))
                        print()
                        print("gamma_g1:", gamma_g_1.project(gamma_o.get_keys()))
                        print("gamma_g2:", gamma_g_2.project(gamma_o.get_keys()))
                        print("gamma_o:", gamma_o)
                        print()
