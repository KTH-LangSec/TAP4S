from lark import Lark
import policy_parser.transformer as TRANSFORMER

GRAMMAR_FILE = "policy_parser/policy_grammar.lark"


def parse(_policy_string):
    with open(GRAMMAR_FILE, 'r') as file:
        grammar = file.read()

    parser = Lark(grammar,parser="lalr")
    policy_parse_tree = parser.parse(_policy_string)
    policy_list = TRANSFORMER.PolicyTransformer().transform(policy_parse_tree)
    
    # for i in policy_list:
    #     print(i)

    return policy_list

