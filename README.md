# TAP4S

## About
TAP4S (**T**ype-based **A**nalysis for **P4** **S**ecurity) is a prototype tool that uses security types and interval analysis to check the security of P4 programs.

## Requirements
- Make sure you have Python installed.
    - This tool was develop using Python `3.11` and it might not work on older versions of Python. 
- This tool relies on the [Lark](https://github.com/lark-parser/lark) parser library which can be installed via pip:
```
pip install lark
```

## How to use:
- TAP4S can be run as:
```
python main.py [options] [p4 code]
```
- The following options are available:
```
-h, --help  show this help message and exit
-i I        Address the of the input program.
-p P        Address the of the input policy.
-o O        Address the of the output policy.
-c C        Address the of the contract.
--dir DIR   Address the of the directory containing a P4 program, input and output policy, and contracts.
-d          Debug mode - print the security checks
-g          Debug mode - print final Gamma
-t          Debug mode - print timing information
-w          Debug mode - print warnings
```

- The `use_cases` directory contains the use cases presented in the paper.
- For example the `basic_tuneling` example can be checked by running the following command:
```
python main.py -i ./use_cases/basic_tunnel/basic_tunnel.p4 -p ./use_cases/basic_tunnel/inputPolicy.pin -c ./use_cases/basic_tunnel/contracts.cont -o ./use_cases/basic_tunnel/outputPolicy.pout
```
