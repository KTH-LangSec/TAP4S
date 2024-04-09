from lark import Lark
import contract_parser.transformer as TRANSFORMER

GRAMMAR_FILE = "contract_parser/contract_grammar.lark"


def parse(_contract_string):
    with open(GRAMMAR_FILE, 'r') as file:
        grammar = file.read()

    parser = Lark(grammar,parser="lalr")
    parse_tree = parser.parse(_contract_string)
    contract_list = TRANSFORMER.ContractTransformer().transform(parse_tree)

    # for i in contract_list:
    #     print(i)

    return contract_list

