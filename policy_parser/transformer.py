from lark import Transformer, v_args

import parser_lib.lval as LVAL
import type_system_lib.label as LATIICE
import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL

import policy_parser.policy as POLICIY_CLASS

# Transformer
@v_args(inline=True)
class PolicyTransformer(Transformer):

    def start(self, *args):
        return args[0]
    
    def policy(self, *args):
        return list(args)

    def policy_disj(self, *args):
        disjunct = POLICIY_CLASS.PolicyDisjunct()
        for lval_plc in args:
            if isinstance(lval_plc, POLICIY_CLASS.LvalPolicy):
                disjunct.add_lval_policy(lval_plc)
        return disjunct


    def lval_policy(self, *args):
        return POLICIY_CLASS.LvalPolicy(args[0], args[1])

    def slices(self, *args):
        return list(args)

    def slice(self, *args):
        start, end = args[0]
        slice_size = int(end - start) + 1
        if args[1] == None:
            interval = INTERVAL.Interval(0, (2 ** slice_size) - 1)
        else:
            low, high = args[1]
            interval = INTERVAL.Interval(low, high)
        label = args[2]

        return TYPE.Slice(start, end, interval, label)

    def indices(self, *args):
        start = args[0]
        end = args[1]
        return (start, end)

    def interval(self, *args):
        if (len(args) == 2):
            interval_min = args[0]
            interval_max = args[1]
            return (interval_min, interval_max)
        else:
            return None

    def label(self, *args):
        if (args[0] == "high"):
            return LATIICE.High()
        else:
            return LATIICE.Low()


    ##### TERMINALS
    def IDENTIFIER(self, token):
        return LVAL.Variable(token.value)
    def NUMBER(self, token):
        return int(token.value)

    def HIGH(self, token):
        return "high"
    def LOW(self, token):
        return "low"