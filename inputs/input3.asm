LOAD 'K'
STORE E 
STORE D 
STORE C
LOAD 0009
INC A
STORE B
LOAD 0000
LOOP1:
INC D
DEC B
CMP B
JNZ LOOP1
LOAD 0008
ADD 0007
STORE B
LOAD 0000
LOOP2:
INC C
DEC B
CMP B
JNE LOOP2
LOAD 0002
SHL A 
STORE B
LOAD 0000
LOOP3:
PUSH D
PUSH C
PUSH D
PUSH E
DEC B
CMP B
JNE LOOP3
XOR 0008
SHR A 
STORE B
STORE C
LOAD 0000
LOOP5:
LOAD C
STORE D
LOAD 0000
LOOP4:
POP E
PRINT E
DEC D
CMP D
JNZ LOOP4
DEC B
CMP B
JNE LOOP5
HALT