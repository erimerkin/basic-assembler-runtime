	LOAD '#'
LOOP:
	PRINT A
	SUB 000A
	SHL A
	CMP 007E
	JB LOOP
	SHR A
	PRINT A
	HALT
