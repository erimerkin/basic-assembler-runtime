#####
# erim erkin dogan
# 2019400225
# CMPE230-Project2 cmpe230assemble 2021
#####

import sys

# Stores hexcodes for registers
register_hexcodes = {
    "PC": "0000", "A" : "0001", "B" : "0002", "C" : "0003", "D" : "0004", "E" : "0005", "S" : "0006"
}

# Stores instructions that takes register type operands
instructions_type_register = {
    "LOAD": "2",
    "STORE": "3",
    "ADD": "4",
    "SUB": "5",
    "INC": "6",
    "DEC": "7",
    "XOR": "8",
    "AND": "9",
    "OR": "A",
    "NOT": "B",
    "SHL": "C",
    "SHR": "D",
    "PUSH": "F",
    "POP": "10",
    "CMP": "11",
    "READ": "1B",
    "PRINT": "1C"
}

# Stores instructions that takes immediate type operands
instructions_type_immediate = {
    "LOAD": "2",
    "ADD": "4",
    "SUB": "5",
    "INC": "6",
    "DEC": "7",
    "XOR": "8",
    "AND": "9",
    "OR": "A",
    "NOT": "B",
    "CMP": "11",
    "JMP": "12",
    "JZ": "13",
    "JE": "13",
    "JNZ": "14",
    "JNE": "14",
    "JC": "15",
    "JNC": "16",
    "JA": "17",
    "JAE": "18",
    "JB": "19",
    "JBE": "1A",
    "PRINT": "1C"
}

# Stores instructions that takes memory address type operands
instructions_type_memory = {
    "LOAD": "2",
    "STORE": "3",
    "ADD": "4",
    "SUB": "5",
    "INC": "6",
    "DEC": "7",
    "XOR": "8",
    "AND": "9",
    "OR": "A",
    "NOT": "V",
    "CMP": "11",
    "READ": "1B",
    "PRINT": "1C"
}

# Stores instructions that takes no operand
instructions_without_operand = {
    "HALT": "1",
    "NOP": "E"
}

inputArg = sys.argv[1] 
fileName = ""

# Checks if the given file is of correct format
if (inputArg.endswith(".asm")):
    fileName = inputArg[0:-4]
else:
    print("[Error] Invalid file type as parameter, quitting program")
    quit()

input_file = open(fileName+".asm", "r") # Opens file given in arguments


labels = {} # Label dictionary to store memory addresses 
next_memory_address = 0 # A variable to store next memory address of instructions


# This functions outputs invalid instruction error and quits program
def throw_error():
    print("[Error] Invalid instruction")
    quit()

# This function checks if the given value is hexadecimal
def ishex(value):
    try:
        hex_to_int = int(value, 16)

        # Checks if the given hex value is 16 bits
        if (hex_to_int > 65535):
            return False
       
        return True
    except ValueError:
        return False

# This function takes hex values of operation, addressing mode and operand and
# converts them to binary and adds them up. Then converts the result to hexadecimal.
def convert(opcode, addrmode, operand):
    hex_opcode   = int(opcode,16)  
    hex_addrmode = int(addrmode,16) 
    hex_operand  = int(operand,16) 

    bin_opcode = format(hex_opcode, '06b') 
    bin_addrmode = format(hex_addrmode, '02b') 
    bin_operand = format(hex_operand, '016b') 
    bin_instr = '0b' + bin_opcode + bin_addrmode + bin_operand 
    int_instr = int(bin_instr[2:],2) ; 
    return format(int_instr, '06x') 


# Preprocesses input to detect memory addresses which is then stored in a dictionary for Labels
for line in input_file:
    tokens = line.split()
    
    # Checks if the token meets the rules for labels, then stores the memory address in a dictionary
    if (len(tokens) == 1 and tokens[0].endswith(":")):
        item = tokens[0]
        label_name = item[0:-1].upper()

        # If label is used 2 times throws error
        if (label_name in labels.keys()):
            print("[Error] Label defined more than once")
            quit()

        # Checks if first char is ALPHABETIC and label is alphanumeric
        elif (label_name[0:1].isalpha() and label_name.isalnum()):
            labels[label_name] = next_memory_address
        else:
            throw_error()

    # Checks if the semicolon is detached from labelname
    elif (len(tokens) == 2 and tokens[1] == ":"):
        item = tokens[0].upper()

        # If label is used 2 times throws error
        if (item in labels.keys()):
            print("[Error] Label defined more than once")
            quit()

        # Checks if first char is ALPHABETIC and label is alphanumeric
        elif (item[0:1].isalpha() and item.isalnum()):
            labels[item] = next_memory_address
            
        else:
            throw_error()

    # Empty line
    elif (len(tokens) == 0):
        continue

    # If the first token is not a label, there should not be a label declaration in this line. Continues line iteration
    else:
        next_memory_address += 3
        
        
    
input_file.close()                           # Closes input_file as its preprocessed
input_file = open(fileName+".asm", "r")      # Opens same file again to process

program = []    # A list to hold hex code for instructions

# Parses file for assembly code
for line in input_file:
    tokens = line.split()
    size = len(tokens)

    # Empty line, continue loop
    if (size == 0):
        continue

    # Parses intructions with no operands
    elif (size == 1):
        currToken = tokens[0]

        # Checks if it is a label, then loop continues
        if (currToken.endswith(":") and currToken[0:-1] in labels.keys()):
            continue

        # Checks if it is NOP or HALT
        elif(currToken in instructions_without_operand.keys()):
            current_instruction = convert(instructions_without_operand[currToken], "0", "0")
            program.append(current_instruction.upper())

        else:
            throw_error()

    # Parses instructions with an operand
    elif (size == 2):
        instr = tokens[0].upper()       # First token is instruction
        operand = tokens[1]             # Second token is operand

        # Parses instruction with memory address operand type
        if (operand.startswith('[') and operand.endswith(']')):
            addressLocation = operand[1:-1].upper()
            addressing_mode = ""
            hex_operand = ""

            # Memory address of Register
            if (addressLocation in register_hexcodes.keys()):
                addressing_mode = "2"
                hex_operand = register_hexcodes[addressLocation]
            # Memory address of HEX
            elif (ishex(addressLocation)):
                addressing_mode = "3"
                hex_operand = addressLocation
            else:
                throw_error()
            
            # Checks if instruction takes memory address as its operand, then creates hexcode for instruction
            if (instr in instructions_type_memory.keys()):
                current_instruction = convert(instructions_type_memory[instr], addressing_mode, hex_operand)
                program.append(current_instruction)
            else:
                throw_error()

        # Parses instruction with register operand type
        elif(operand.upper() in register_hexcodes.keys()):
            
            # Checks if instruction can take register_hexcodes as operand
            if (instr in instructions_type_register.keys()):
                current_instruction = convert(instructions_type_register[instr], "1", register_hexcodes[operand.upper()])
                program.append(current_instruction)
            
            # Instruction cannot take register type operands, throws error
            else:
                throw_error()

        # Parses instruction with immediate operand which is character of type 'X'
        elif(operand.startswith('\'') and operand.endswith('\'')):
            character = operand[1:-1]
            char_size = len(character)

            # Checks if operand is valid by having 1 character inside it
            if(char_size == 1):
                
                # Checks if instruction takes immediate type for its operands and creates hexcode for instruction
                if(instr in instructions_type_immediate.keys()):
                    hex_operand = hex(ord(character))
                    current_instruction = convert(instructions_type_immediate[instr], "0", hex_operand)
                    program.append(current_instruction)
                else:
                    throw_error()

            # If there is more than one character in '', throws error and exits loop
            else:
                throw_error()

        # Parses intruction with label as an operand
        elif(operand.upper() in labels.keys()):

            # Checks if instruction takes immediate type for its operands and creates hexcode for instruction
            if (instr in instructions_type_immediate.keys()):
                current_instruction = convert(instructions_type_immediate[instr], "0", hex(labels[operand.upper()]))
                program.append(current_instruction)
            else:
                throw_error()

        # Parses instruction with an immediate hexadecimal operand
        elif(operand[0].isnumeric() and ishex(operand)):

            # Checks if instruction takes immediate type for its operands and creates hexcode for instruction
            if (instr in instructions_type_immediate.keys()):
                current_instruction = convert(instructions_type_immediate[instr], "0", operand)
                program.append(current_instruction)
            else:
                print("[Error] Forbidden operand type")
                quit()
        else:
            throw_error()

    # There is no instructions with multiple operands so throws error, exits loop
    else:
        print("[Error] Excess element/s in instruction\n")
        quit()
    
input_file.close()

# Opens the output file with same name as input_file and writes program
with open(fileName+'.bin', 'w+') as outputFile:
      
    # Writes hex instructions in program list
    for items in program:
        uppercased = items.upper()
        outputFile.write('%s\n' %uppercased)
      
    print("Output file ./%s is generated." %(fileName+'.bin'))
  
  
# Closes the file
outputFile.close()


