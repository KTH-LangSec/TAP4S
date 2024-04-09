import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL
import type_system_lib.label as LATIICE
import logger as LOGGER
import parser_lib.ast as AST

#######################################################################################
def process_input_policy(_input_policy):
    disjuncts = [s for s in _input_policy.split("|") if s]

    policy_in = []

    for disj in disjuncts:
        slices = [s.strip() for s in disj.split(";") if s]
        type_slices = []
        type_size = 0
        for slc in slices:
            tuples = [s.strip() for s in slc.split("->") if s]
            start, end = process_indices(tuples[0])
            slice_size = int(end - start) + 1
            interval, label = process_type(tuples[1], slice_size)

            type_size += slice_size

            type_slices.append(TYPE.Slice(start, end, interval, label))

        policy_in.append(TYPE.BitString(type_size, _slices=type_slices))

    return policy_in


#######################################################################################
def process_indices(_indices):
    indices = _indices.replace("(", "").replace(")", "").strip() # remove ( and )
    start, end = indices.split(",")
    return (int(start), int(end))

def process_type(_types, _size):
    interval_label = _types.replace("(", "").replace(")", "").strip() # remove ( and )
    interval_label = interval_label.replace("[", "").replace("]", "").strip() # remove [ and ]
    temp = [s.strip() for s in interval_label.split(",") if s]

    if (len(temp) == 2): # it was [*] and label
        interval = INTERVAL.Interval(0, (2 ** _size) - 1)
        if temp[1].lower() == "high":
            label = LATIICE.High()
        else:
            label = LATIICE.Low()
        
    elif (len(temp) == 3): # it was [int,int] and label
        interval = INTERVAL.Interval(int(temp[0]), int(temp[1]))
        if temp[2].lower() == "high":
            label = LATIICE.High()
        else:
            label = LATIICE.Low()
        
    else:
        LOGGER.error("Cannot parse the policy")
        return (None, None)

    return (interval, label)