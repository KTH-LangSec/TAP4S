import os


def arg_process(_arg_input, _arg_pin, _arg_pout, _arg_cont, _arg_dir):
    input_program = ""
    input_policy = ""
    output_policy = ""
    contracts = ""

    if (_arg_dir):
        input_program = open_file_with_extension(_arg_dir, ".p4")
        input_policy = open_file_with_extension(_arg_dir, ".pin")
        output_policy = open_file_with_extension(_arg_dir, ".pout")
        contracts = open_file_with_extension(_arg_dir, ".cont")

        return (input_program, input_policy, output_policy, contracts)
    else:
        ###### input program
        if _arg_input:
            with open(_arg_input, 'r') as file:
                input_program = file.read()
        else:
            print()
            arg_parser.print_help()
            LOGGER.error("\nPlease provide an input program!")
        
        ###### input policy
        if _arg_pin:
            with open(_arg_pin, 'r') as file:
                input_policy = file.read()
        else:
            LOGGER.warning("no input policy was provided!")

        ###### output policy
        if _arg_pout:
            with open(_arg_pout, 'r') as file:
                output_policy = file.read()
        else:
            LOGGER.warning("no output policy was provided!")

        ###### contracts
        if _arg_cont:
            with open(_arg_cont, 'r') as file:
                contracts = file.read()
        else:
            LOGGER.warning("no contract file was provided!")

        return (input_program, input_policy, output_policy, contracts)
        





def open_file_with_extension(directory, extension):
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                return file.read()

    LOGGER.error("no file with " + str(extension) + " extension provided!")
