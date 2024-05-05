from lark import Lark
import policy_parser.transformer as TRANSFORMER

GRAMMAR_FILE = "policy_parser/policy_grammar.lark"


def parse(_policy_string):
    if (_policy_string == ""):
        return []
    else:
        with open(GRAMMAR_FILE, 'r') as file:
            grammar = file.read()

        parser = Lark(grammar,parser="lalr")
        policy_parse_tree = parser.parse(_policy_string)
        policy_list = TRANSFORMER.PolicyTransformer().transform(policy_parse_tree)

        return policy_list

