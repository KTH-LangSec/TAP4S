from lark import Transformer, v_args

import parser_lib.lval as LVAL
import type_system_lib.label as LATIICE
import type_system_lib.types as TYPE
import type_system_lib.interval as INTERVAL
import parser_lib.expression as EXP
import contract_parser.contract as CONTRACT


# Transformer
@v_args(inline=True)
class ContractTransformer(Transformer):

    def start(self, *args):
        return args[0]
    
    def contract(self, *args):
        return list(args)

    ######################################################################
    ################################ TABLE ##############################
    ######################################################################
    def table_contract(self, *args):
        name = args[0]
        contract = CONTRACT.TableContract(name)
        for (pred, act, tp) in args[1]:
            contract.add(pred, act, tp)
        return contract

    def predicate_action_type_set(self, *args):
        return list(args)

    def predicate_action_type(self, *args):
        return (args[0], args[1], args[2])

    ######################################################################
    ################################ EXTERN ##############################
    ######################################################################
    def extern_contract(self, *args):
        name = args[0]
        contract = CONTRACT.ExternContract(name)
        for (pred, tp) in args[1]:
            contract.add(pred, tp)
        return contract

    def predicate_type_set(self, *args):
        return list(args)

    def predicate_type(self, *args):
        return (args[0], args[1])

    def lval_type_set(self, *args):
        gamma_t = CONTRACT.gamma_t()
        if (len(args) > 0):
            for (var, var_type) in args:
                gamma_t.add(var, var_type)

        return gamma_t

    def lval_type(self, *args):
        return (args[0], args[1])


    ######################################################################
    ################################ TYPES ###############################
    ######################################################################
    def type(self, *args):
        return args[0]

    def bool_type(self, *args):
        i_min = args[0]
        i_max = args[1]
        lable = args[2]
        return TYPE.Bool(_interval=INTERVAL.Interval(i_min, i_max, 1), _label=lable)

    def bit_string_type(self, *args):
        size = args[0]
        slices = args[1]    
        return TYPE.BitString(size, _slices=slices)

    def slices(self, *args):
        return list(args)        

    def slice(self, *args):
        start, end = args[0]
        slice_size = int(end - start) + 1
        if args[1] == None:
            interval = INTERVAL.Interval(0, (2 ** slice_size) - 1, slice_size)
        else:
            low, high = args[1]
            interval = INTERVAL.Interval(low, high, slice_size)
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

    ######################################################################
    ############################# EXPRESSION #############################
    ###################################################################### 
    def predicate(self, *args):
        return args[0]

    def binary_operation(self, *args):
        return EXP.BinaryOP(args[0], args[1], args[2])

    def boolean_value(self, *args):
        return EXP.Boolean(args[0])

    def unsigned(self, *args):
        return EXP.UnsignedNumber(args[0], args[1])

    def hex_value(self, *args):
        val = "0x" + str(args[1])
        return EXP.Hex(val)


    ######################################################################
    ################################ LVAL ################################
    ###################################################################### 
    def lval(self, *args):
        return args[0]

    def lval_var(self, *args):
        return LVAL.Variable(args[0])

    def lval_slicing(self, *args):
        return LVAL.Slice(args[0], args[2], args[1])

    def lval_access(self, *args):
        lval_list = []
        for l in list(args):
            lval_list.append(LVAL.Variable(l))
        return LVAL.Access(lval_list)


    ##### TERMINALS
    def IDENTIFIER(self, token):
        return token.value
    def NUMBER(self, token):
        return int(token.value)

    def TRUE(self, token):
        return True
    def FALSE(self, token):
        return False

    def HIGH(self, token):
        return "high"
    def LOW(self, token):
        return "low"