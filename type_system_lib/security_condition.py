import type_system_lib.gamma as GM
import parser_lib.lval as LVAL
import type_system_lib.types as TYPES
import type_system_lib.interval as INTERVAL
import type_system_lib.label as LATTICE
import copy

import logger as LOGGER
import setting

Opacket = LVAL.Variable("Opacket")

# def check(_Gamma_g, _Gamma_o):
#     checks_counter = 0
#     for gamma_o in _Gamma_o:
#         for i, t_gamma_g_1 in enumerate(_Gamma_g):
#             for j, t_gamma_g_2 in enumerate(_Gamma_g):
#                 if (i != j):
#                     if (t_gamma_g_1.get(Opacket).get_type() == TYPES.TypesEnum.OUTPUT_PACKET):
#                         LOGGER.warning("gamma skipped because no output packet was emitted!")
#                     elif (t_gamma_g_2.get(Opacket).get_type() == TYPES.TypesEnum.OUTPUT_PACKET):
#                         LOGGER.warning("gamma skipped because no output packet was emitted!")
#                     else:
#                         gamma_g_1 = t_gamma_g_1.project(gamma_o.get_keys()).serialize()
#                         gamma_g_2 = t_gamma_g_2.project(gamma_o.get_keys()).serialize()
#                         if ( (not GM.is_gamma_intersect_empty(gamma_o, gamma_g_1)) and (not GM.is_gamma_intersect_empty(gamma_o, gamma_g_2))):
#                             GM.join_gamma(gamma_g_1, gamma_g_2)
#                             if setting.show_checks:
#                                 print("---------------------"*2)
#                                 print("gamma_join:\n" + str(gamma_g_1))
#                                 print("gamma_o:\n" + str(gamma_o))
#                             checks_counter += 1
#                             if not GM.is_below(gamma_g_1, gamma_o):
#                                 return False, (gamma_g_1, gamma_g_2, gamma_o), checks_counter

#     return True, None, checks_counter


def check(_Gamma_g, _Gamma_o):
    checks_counter = 0
    for gamma_o in _Gamma_o:
        for i, t_gamma_g_1 in enumerate(_Gamma_g):
            for j, t_gamma_g_2 in enumerate(_Gamma_g):
                if (i != j):
                    if (t_gamma_g_1.get(Opacket).get_type() == TYPES.TypesEnum.OUTPUT_PACKET):
                        LOGGER.warning("gamma skipped because no output packet was emitted!")
                    elif (t_gamma_g_2.get(Opacket).get_type() == TYPES.TypesEnum.OUTPUT_PACKET):
                        LOGGER.warning("gamma skipped because no output packet was emitted!")
                    else:
                        gamma_g_1 = t_gamma_g_1.project(gamma_o.get_keys()).serialize()
                        gamma_g_2 = t_gamma_g_2.project(gamma_o.get_keys()).serialize()
                        if ((not GM.is_gamma_intersect_empty(gamma_o, gamma_g_1))):
                            checks_counter += 1
                            if not (gamma_2_is_consistent(gamma_g_1, gamma_g_2, gamma_o)):
                                return False, (gamma_g_1, gamma_g_2, gamma_o), checks_counter
                            else:
                                if not lub_is_below(gamma_g_1, gamma_g_2, gamma_o):
                                    return False, (gamma_g_1, gamma_g_2, gamma_o), checks_counter

    return True, None, checks_counter



###### helper ######
def lub_is_below(_gamma_1, _gamma_2, _gamma_o):
    if ((GM.is_gamma_intersect_empty(_gamma_o, _gamma_2))):
        return True
    else:
        gamma_1 = copy.deepcopy(_gamma_1)
        gamma_2 = copy.deepcopy(_gamma_2)
        GM.join_gamma(gamma_1, gamma_2)
        if GM.is_below(gamma_1, _gamma_o):
            return True
        else:
            LOGGER.print_blue("\n>>>>>> CHECKS FAIL:")
            LOGGER.print_red("γ_1 ⊔ γ_2 \u2291\u0338 γ_o")
            return False


###### helper ######
def gamma_2_is_consistent(_gamma_1, _gamma_2, _gamma_o):
    gamma_join = copy.deepcopy(_gamma_1)
    GM.join_gamma(gamma_join, copy.deepcopy(_gamma_2))

    for x in _gamma_2.get_keys():
        for g2_slc in _gamma_2.get(x).get_slices():
            overlaping_slices = gamma_join.get(x).get_overlapping_slices(g2_slc)
            if not slice_list_get_label(overlaping_slices).is_low():
                go_slcs = _gamma_o.get(x).get_overlapping_slices(g2_slc)
                if (len(go_slcs) == 1):
                    if (not is_subset_subslice(g2_slc,go_slcs[0])):
                        # both checks failed
                        LOGGER.print_blue("\n>>>>>> CHECKS FAIL:")
                        LOGGER.print_red("γ_1 ⊔ γ_2 for " + str(g2_slc) +" is not LOW!")
                        LOGGER.print_red(str(gamma_join.get(x)))
                        print()
                        LOGGER.print_red("γ_2("+str(x)+") \u2286\u0338 γ_o("+str(x)+")!")
                        LOGGER.print_red(str(g2_slc) + " \u2286\u0338 " + str(go_slcs[0]))
                        print()
                        return False
                else:
                    # TODO we need to go the other way and implement the slicing of gamma_2 slice for each overlap in gamma_o
                    LOGGER.error("merge of slices is not implemented!")

    return True


###### helper ######
def slice_list_get_label(_list_slcs):
    for slc in _list_slcs:
        if slc.get_label().is_high():
            return LATTICE.High()
        
    return LATTICE.Low()


###### helper ######
def is_subset_subslice(_slc, _overlap):
    s_start, s_end = _slc.get_slice_indices()
    o_start, o_end = _overlap.get_slice_indices()

    if o_start == s_start:
        start = o_start
        _, start_split_slc = _slc.split(0, _conservative=True)
        _, start_split_overlap = _overlap.split(0, _conservative=True)
    elif o_start > s_start:
        start = o_start
        _, start_split_slc = _slc.split(start, _conservative=True)
        _, start_split_overlap = _overlap.split(0, _conservative=True)
    else:
        start = s_start
        _, start_split_slc = _slc.split(0, _conservative=True)
        _, start_split_overlap = _overlap.split(start, _conservative=True)

    if o_end == s_end:
        end_split_slc = start_split_slc
        end_split_overlap = start_split_overlap
    elif o_end > s_end:
        end = s_end - start + 1
        end_split_slc = start_split_slc
        end_split_overlap, _ = start_split_overlap.split(end, _conservative=True)
    else:
        end = o_end - start + 1
        end_split_slc, _ = start_split_slc.split(end, _conservative=True)
        end_split_overlap = start_split_overlap

    interval_1 = end_split_slc.get_interval()
    interval_2 = end_split_overlap.get_interval()
    return INTERVAL.is_subset(interval_1, interval_2)