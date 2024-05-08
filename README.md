# P4 Type Checker

## Requirements
- Make sure you have Python installed.
    - This tool was develop using Python `3.11` and it might not work on older versions of Python. 
- This tool relies on the [Lark](https://github.com/lark-parser/lark) parser library which can be installed as follows:
```
pip install lark
```

## How to use:
- The tool should be run as:
```
python main.py [options]
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
```

- The `usecases` directory contains the use cases presented in the paper.
- For example the `basic_tuneling` example can be checked by running the following command:
```
python main.py -i ./use_cases/basic_tunnel/basic_tunnel.p4 -p ./use_cases/basic_tunnel/inputPolicy.pin -c ./use_cases/basic_tunnel/contracts.cont -o ./use_cases/basic_tunnel/outputPolicy.pout
```
