from lark import Lark

import parser_lib.transformer as TRANSFORMER

##################################################
GRAMMAR_FILE = "parser_lib/grammar.lark"
##################################################



def parse(_input_program):
    with open(GRAMMAR_FILE, 'r') as file:
        grammar = file.read()

    parser = Lark(grammar,parser="lalr")
    parse_tree = parser.parse(_input_program)
    ast = TRANSFORMER.P4Transformer().transform(parse_tree)
    
    return list(ast)
