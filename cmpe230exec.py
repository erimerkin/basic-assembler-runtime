#####
# erim erkin dogan
# 2019400225
# CMPE230-Project2 cmpe230exec 2021
#####

import sys

# Instruction lists with their accepted operand types, used to check if the instruction is legal
immediate_instructions = ["000010", "000100", "000101", "000110", "000111", "001000", "001001", "001010", "001011", "010001", "010010", "010011", "010100", "010101", "010110", "010111", "011000", "011001", "011010", "011100"]
register_instructions = ["000010", "000011", "000100", "000101", "000110", "000111", "001000", "001001", "001010", "001011", "001100", "001101", "001111", "010000", "010001", "011011", "011100"]
memory_instructions = ["000010", "000011", "000100", "000101", "000110", "000111", "001000", "001001", "001010", "001011", "010001", "011011", "011100"]

memory = ["00"] * 65536 # Creates 64K memory, fills with 00 hex code representing 1 byte 

#Register dictionary A=1, B=2, C=3, D=4, E=5 default values are 0
registers = {1:"0", 2:"0", 3:"0", 4:"0", 5:"0"}

ZF, CF, SF = 0, 0, 0  #Flags
PC = 0      #Program counter points to start of Memory
S = 65534   #Stack pointer, points to end of memory 0xFFFE
program_size = 0    # This var keeps track of program'S size


########################################################
#: I/O OPERATIONS
########################################################

# This function checks if the given value is hexadecimal
def ishex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

# Reading and checking input parameter for file name
inputArg = sys.argv[1] 
fileName = ""

# Checks if the given file is of correct format
if (inputArg.endswith(".bin")):
    fileName = inputArg[0:-4]
else:
    print("[Error] Invalid file type as parameter, quitting program")
    quit()

# File operations instructions of 6 character long hex will be accepted,
# Instructions doesn't need to be on separate lines any whitespace is enough to distinguish them
inputFile = open(fileName+".bin", "r") # Opens file given in arguments

for line in inputFile:
    tokens = line.split()

    for item in tokens:

        #Checks length of instructions and if the instruction is hexadecimal, otherwise throws error and quits program
        if (len(item) == 6 and ishex(item)):
            memory[program_size] = item[0:2]
            memory[program_size+1] = item[2:4]
            memory[program_size+2] = item[4:]
            program_size += 3
        else:
            print("[Error] Invalid input")
            quit()

inputFile.close()

########################################################
#: FUNCTION DEFINITIONS
########################################################

# Prints out error message and quits program
def throw_error():
    print("[Error] Illegal instruction")
    if (output_file):
        output_file.close()
    quit()

# This function is used for NOT instruction, it takes complement of given binary number by
# replacing 1s with 0s and replacing 0s with 1s
def take_complement(operand):
    complement = ""
    for bit in operand:
        if (bit == '1'):
            complement += "0"
        else:
            complement += "1"
    return complement

#Checks the 17 bits of given binary number, sets the flags accordingly
def check_all_flags(binary_number):
    global CF, SF, ZF
    CF = binary_number[0:1]
    check_sf_zf(binary_number[1:])

# Checks given 16 bit binary number, sets SF and ZF flags
def check_sf_zf(binary_number):
    global SF, ZF
    SF = int(binary_number[0:1],2)
    number = int(binary_number,2)
    
    #Checks if the number has value 0, then sets zero flag accordingly
    if (number == 0): 
        ZF = 1
    else:
        ZF = 0


# This function returns result of adding given 2 parameters and checks flags for the result.
def add(operand1, operand2):
    decimal_sum = int(operand1, 2) + int(operand2, 2)
    binary_sum = format(decimal_sum, '017b')
    check_all_flags(binary_sum)
    return binary_sum[1:]


# This function returns result of subtracting given 2 parameters from each other and checks flags for the result.
# Subtraction operation is basically a addition between contents of A register and two's complement of operand
def sub(operand1, operand2):
    normalized_operand = format(int(operand2, 2), '016b')
    int_twos_complement = int(take_complement(normalized_operand),2) + 1
    bin_twos_complement = format(int_twos_complement, '016b') 
    return add(operand1, bin_twos_complement)

# This function jumps to given address by changing PC to address
def jump(address):
    global PC
    PC = int(address, 2)

# This function stores given data in given register
def register_store(data, register):
    global PC, S
    int_register_name = int(register,2)
    register_value = registers.get(int_register_name)
    
    if register_value:  # Register is of type A, B, C, D, E
        registers[int_register_name] = data
    elif (int_register_name == 0):  # Program Counter
        PC = int(data, 2)
    elif (int_register_name == 6):  # Stack Pointer
        S = int(data, 2)
    else:
        throw_error()

# This function loads value from given register
def register_load(register):
    int_register_name = int(register,2)
    register_value = registers.get(int_register_name)
    
    if register_value:  # Register is of type A, B, C, D, E
        return register_value
    elif (int_register_name == 0):  # Program counter
        return format(PC, '016b')
    elif (int_register_name == 6):  # Stack pointer
        return format(S, '016b')
    else:
        throw_error()

# This function loads data from given memory address
def memory_load(address):
    int_address = int(address, 2)

    # Checking bounds of memory and stack
    if (int_address < S):
        hex_memory_data = memory[int_address] + memory[int_address+1]
        bin_memory_data = format(int(hex_memory_data, 16), '016b')
        return bin_memory_data
    else:
        throw_error()

# This function stores data to given address
def memory_store(address, data):
    int_address = int(address, 2)

    # Making sure we don't overwrite instructions
    if (int_address >= program_size):
        hex_data = format(int(data, 2), '04x')
        memory[int_address] = hex_data[0:2]
        memory[int_address+1] = hex_data[2:]
    else:
        print("[Error] This part of the memory is read-only, it contains program information(instructions)")
        quit()

# This function checks if the given instruction is valid and retrieves data from given operand 
def retrieve_data(instr, data_type, operand):

    if (data_type == "00" and instr in immediate_instructions): #Immediate data
        return operand

    elif (data_type == "01" and instr in register_instructions):    #Register data
        return register_load(operand)

    elif (data_type == "10" and instr in memory_instructions):  #Memory address is on register
        address = register_load(operand)
        return memory_load(address)

    elif (data_type == "11" and instr in memory_instructions):  #Memory address is operand
        return memory_load(operand)

    else:
        throw_error()

# This function stores data to operand with given instr, data type, if the instruction pair is correct
def store_data(instr, data_type, operand, data):
    
    if (data_type == "00" and instr in immediate_instructions): #Immediate data
        throw_error()

    elif (data_type == "01" and instr in register_instructions):    #Register data
        register_store(data, operand)

    elif (data_type == "10" and instr in memory_instructions):  #Memory address is on register
        address = register_load(operand)
        memory_store(address, data)

    elif (data_type == "11" and instr in memory_instructions):  #Memory address is operand
        memory_store(operand, data)

    else:
        throw_error()
   

########################################################
#: PROGRAM LOOP
########################################################
output_file = open(fileName+".txt", 'w')

currentInstruction = ""
# Runs program, increments PC by 3 every loop. Quits when HALT instruction is read, otherwise
# continues till PC encounters S(Stack Pointer)
while (currentInstruction != "040000"):

    # Checks if program is out of bounds
    if (PC >= S):
        print("Segmentation fault")
        quit()

    # Reading instruction from memory
    currentInstruction = memory[PC] + memory[PC+1] + memory[PC+2]
    PC += 3

    # Spliting instruction
    hex_operand = currentInstruction[2:]
    hex_instr = currentInstruction[0:2]

    # Converts instruction to binary and splits it accordingly
    bin_operand = format(int(hex_operand, 16), '016b')
    bin_instr_type = format(int(hex_instr, 16), '08b')
    bin_instr = bin_instr_type[0:6]
    bin_dataType = bin_instr_type[6:]

    if (bin_instr == "000001"): #HALT, this instruction quits the program
        quit()

    elif (bin_instr == "000010"): #LOAD, loads given operand or value in operand to A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_store(operand_data, '1')

    elif (bin_instr == "000011"): #STORE, stores the content of A register to given operand

        register_data = register_load('1')
        store_data(bin_instr, bin_dataType, bin_operand, register_data)
    
    elif (bin_instr == "000100"): #ADD, adds content of A register with given operand, result is stored in A register again

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        result = add(register_data, operand_data)
        register_store(result, '1')
    
    elif (bin_instr == "000101"): #SUB, subtracts operand from content of A register, result is stored in A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        result = sub(register_data, operand_data)
        register_store(result, '1')

    elif (bin_instr == "000110"): #INC, increments given operand by 1 and stores the result in according register or memory address

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        result = add(operand_data, "1")

        # If it is immediate data, don't store it
        if (bin_dataType != "00"):
            store_data(bin_instr, bin_dataType, bin_operand, result)

    elif (bin_instr == "000111"): #DEC, decrements given operand by 1 and stores the result in according register or memory address

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        result = sub(operand_data, "1")

        # If it is immediate data, don't store it
        if (bin_dataType != "00"):
            store_data(bin_instr, bin_dataType, bin_operand, result)

    elif (bin_instr == "001000"): #XOR, takes bitwise XOR of operand and content of A register, stores the result in A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        int_operand1 = int(operand_data, 2)
        int_operand2 = int(register_data, 2)
        xor_result = int_operand1 ^ int_operand2
        bin_result = format(xor_result, '016b')
        register_store(bin_result, '1')

    elif (bin_instr == "001001"): #AND, takes bitwise AND of operand and content of A register, stores the result in A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        int_operand1 = int(operand_data, 2)
        int_operand2 = int(register_data, 2)
        and_result = int_operand1 & int_operand2
        bin_result = format(and_result, '016b')
        register_store(bin_result, '1')

    elif (bin_instr == "001010"): #OR, takes bitwise OR of operand and content of A register, stores the result in A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        int_operand1 = int(operand_data, 2)
        int_operand2 = int(register_data, 2)
        or_result = int_operand1 | int_operand2
        bin_result = format(or_result, '016b')
        register_store(bin_result, '1')


    elif (bin_instr == "001011"): #NOT, takes the complement of operand by interchanging 1s and 0s, stores result in A register

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        complement = take_complement(operand_data)

        # If the operand is not immediate, stores the result in operand
        if (bin_dataType != "00"):
            store_data(bin_instr, bin_dataType, bin_operand, complement)

    elif (bin_instr == "001100" and bin_dataType == "01"): #SHL shifts the operand/content of operand to 1 bit left, sets flags accordingly

        register_data = register_load(bin_operand)
        shifted_left = register_data + "0"
        check_all_flags(shifted_left)
        register_store(shifted_left[1:], '1')

    elif (bin_instr == "001101" and bin_dataType == "01"): #SHR, shifts the operand/content of operand to 1 bit right, sets flags accordingly

        register_data = register_load(bin_operand)
        shifted_right = "0" + register_data
        check_sf_zf(shifted_right)
        register_store(shifted_right[:-1], '1')

    elif (bin_instr == "001110"): #NOP, does nothing
        continue

    elif (bin_instr == "001111" and bin_dataType == "01"): #PUSH, pushes content of given register to stack
        
        register_data = register_load(bin_operand)
        hex_data = format(int(register_data, 2), '04x')
        memory[S+1] = hex_data[2:]
        memory[S] = hex_data[0:2]
        S -= 2

        # Checks if stack borders program or meets PC
        if (S <= PC or S <= program_size):
            print("[Error] Stack overflow")
            quit()
      
    elif (bin_instr == "010000" and bin_dataType == "01"): #POP, pops the element from stack to given register
            
        S += 2  # Incrementing stack pointer by 2

        # Checks if S is in bounds of memory
        if (S < len(memory)):
            hex_data = memory[S] + memory[S+1]
            bin_data = format(int(hex_data, 16), '016b')
            register_store(bin_data, bin_operand)
        else:
            print("[Error] Stack underflow")
            quit()

    elif (bin_instr == "010001"): #CMP, compares operand and content of A register, sets flags accordingly

        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        register_data = register_load('1')
        sub(register_data, operand_data) 

    elif (bin_instr == "010010" and bin_dataType == "00"): #JMP unconditional jump
        jump(bin_operand)

    elif (bin_instr == "010011" and bin_dataType == "00"): #JZ & JE, jump if ZF is true
            
        if (ZF == 1):
            jump(bin_operand)

    elif (bin_instr == "010100" and bin_dataType == "00"): #JNZ & JNE, jump if ZF is false   
           
        if (ZF == 0):
            jump(bin_operand)

    elif (bin_instr == "010101" and bin_dataType == "00"): #JC, jump if CF is true
        
        if (CF == 1):
            jump(bin_operand)

    elif (bin_instr == "010110" and bin_dataType == "00"): #JNC, jump if CF is false
        
        if (CF == 0):
            jump(bin_operand)

    elif (bin_instr == "010111" and bin_dataType == "00"): #JA, jump if A > operand

        if (SF == 0 and ZF == 0):
            jump(bin_operand)

    elif (bin_instr == "011000" and bin_dataType == "00"): #JAE, jump if A >= operand

        if (SF == 0 or ZF == 1):
            jump(bin_operand)

    elif (bin_instr == "011001" and bin_dataType == "00"): #JB, jump if A < operand

        if (SF == 1 and ZF == 0):
            jump(bin_operand)

    elif (bin_instr == "011010" and bin_dataType == "00"): #JBE, jump if A <= operand

        if (SF == 1 or ZF == 1):
            jump(bin_operand)       
        
    elif (bin_instr == "011011"): #READ, takes input from user char by char. If more than 1 char is inputted takes the first char and stores it
        user_input = ""

        # Take input till it is not new line
        while (len(user_input) == 0):
            user_input = input()

        ascii_value = ord(user_input[0])
        bin_value = format(ascii_value, '016b')
        store_data(bin_instr, bin_dataType, bin_operand, bin_value)


    elif (bin_instr == "011100"): #PRINT, prints data from given operand using ASCII conversion
        
        operand_data = retrieve_data(bin_instr, bin_dataType, bin_operand)
        output_file.write(chr(int(operand_data, 2)))
        output_file.write('\n')

    else:
        throw_error()

