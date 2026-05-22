JMP endLibrary

gcd:
POP R6; Store ret dir in R6
POP R2; Load B in R2
POP R1; Load A in R2

loop:
CPY R3,R1; Copy A in C
SUB R3,R2; Substract C in B

CMP R2,R1
JZ end
JN minor

SUB R2,R1; Substract B in A
JMP loop

minor:
SUB R1,R2
JMP loop

end:
PUSH R1; Store A in m via stack
PUSH R6; Return ret dir to stack
RET

endLibrary: