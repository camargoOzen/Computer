import ply.lex as lex
import sys
import os
import struct

linea = 0
etiquetas = {}

# ========================
# TOKENS
# ========================
tokens = (
    'INSTR',
    'REGISTER',
    'NUMBER',
    'COMMA',
    'ETIQUETA'
)

t_COMMA = r','

# ========================
# INSTRUCCIONES
# ========================
def t_INSTR(t):
    r'LOADV|LOAD|STORE|PUSH|POP|LEA|ADDF|ADD|SUBF|SUB|MULF|MUL|DIVF|DIV|MODF|MOD|CPY|INC|DEC|CMPF|CMP|I2F|F2I|TEST|AND|OR|XOR|NOT|NAND|NOR|SHL|SHR|ROL|ROR|JMP|JZ|JNZ|JP|JN|JC|JNC|JO|JNO|CALL|RET|CLI|STI|NOP|IN|OUT'
    return t

# ========================
# REGISTROS
# ========================
def t_REGISTER(t):
    r'R[0-9]+|SP'
    
    if t.value != "SP":
        t.value = int(t.value[1:])  # R1 → 1
    else:
        t.value = 0
        
    return t

# ========================
# NUMEROS (inmediatos)
# ========================
def t_NUMBER(t):
    r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?'
    raw = t.value
    if ('.' in raw) or ('e' in raw) or ('E' in raw):
        t.value = float(raw)
    else:
        t.value = int(raw)
    return t

def t_ETIQUETA(t):
    r'[A-Za-z_][A-Za-z0-9_]*:|[A-Za-z_][A-Za-z0-9_]*'
    if(t.value.endswith(':')):
        t.value = t.value[:-1]  # Eliminar los dos puntos
    return t

# Ignorar espacios
t_ignore = ' \t'

def t_COMMENT(t):
    r';[^\n]*'
    pass

def t_newline(t):
    r'\n+'
    pass

def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

# ========================
# OPCODES
# ========================
opcodes = {
    'LOAD'  :0x11,
    'LOADV' :0x12,
    'STORE' :0x13,
    'PUSH'  :0x100000000000001,
    'POP'   :0x100000000000002,
    'LEA'   :0x16,
    'ADD'   :0x20000000000001,
    'ADDF'  :0x21000000000001,
    'SUB'   :0x20000000000002,
    'SUBF'  :0x21000000000002,
    'MUL'   :0x20000000000003,
    'MULF'  :0x21000000000003,
    'DIV'   :0x20000000000004,
    'DIVF'  :0x21000000000004,
    'MOD'   :0x20000000000005,
    'MODF'  :0x21000000000005,
    'CPY'   :0x20000000000006,
    'INC'   :0x20000000000007,
    'DEC'   :0x20000000000008,
    'CMP'   :0x2000000000000E,
    'CMPF'  :0x2100000000000E,
    'I2F'   :0x21000000000009,
    'F2I'   :0x2100000000000A,
    'TEST'  :0x2000000000000F,
    'AND'   :0x20000000000011,
    'OR'    :0x20000000000012,
    'XOR'   :0x20000000000013,
    'NOT'   :0x20000000000014,
    'NAND'  :0x20000000000015,
    'NOR'   :0x20000000000016,
    'SHL'   :0x30000000000001,
    'SHR'   :0x30000000000002,
    'ROL'   :0x30000000000003,
    'ROR'   :0x30000000000004,
    'JMP'   :0X700,
    'JZ'    :0X701,
    'JNZ'   :0X702,
    'JP'    :0X703,
    'JN'    :0X704,
    'JC'    :0X705,
    'JNC'   :0X706,
    'JO'    :0X707,
    'JNO'   :0X708,
    'CALL'  :0X709,
    'RET'   :0X70A0000000000000,
    'CLI'   :0X0000000000000001,
    'STI'   :0X0000000000000002,
    'NOP'   :0X0000000000000000,
    'IN'    :0X9000000000000,
    'OUT'   :0X9000000000001
}


def to_unsigned_64(value):
    return value & ((1 << 64) - 1)


def float_to_u64(value: float) -> int:
    packed = struct.pack('>d', float(value))
    return int.from_bytes(packed, byteorder='big', signed=False)


def encode_64(value) -> str:
    if isinstance(value, float):
        return format(float_to_u64(value), '064b')
    return format(to_unsigned_64(int(value)), '064b')


# ========================
# PARSER SIMPLE
# ========================
def parse_etiq(line):
    lexer.input(line)
    
    global linea
    
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)

    if len(tokens_list) == 1:
        if(tokens_list[0].type == 'ETIQUETA'):
            etiqueta = tokens_list[0].value
            etiquetas[str(etiqueta)] = linea
            linea -=1

def parse_line(line):
    lexer.input(line)

    global linea
    
    outputs = []  # Lista para acumular los outputs en lugar de imprimir
    
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)

    if len(tokens_list) == 1:
        if(tokens_list[0].type == 'ETIQUETA'):
            etiqueta = tokens_list[0].value
            etiquetas[str(etiqueta)] = linea
            linea -=1
            
        if(tokens_list[0].type == 'INSTR'):
            instr = tokens_list[0].value
            outputs.append(format(opcodes[instr], '064b'))
            
        if(tokens_list[0].type == 'NUMBER'):
            num = tokens_list[0].value
            outputs.append(encode_64(num))
        
    if len(tokens_list) == 2:
        instr = tokens_list[0].value
        if(tokens_list[1].type == 'REGISTER'):
            r1 = tokens_list[1].value
            outputs.append(format(opcodes[instr], '056b') + format(r1, '04b'))
        if(tokens_list[1].type == 'ETIQUETA'):
            etiqueta = '('+ str(etiquetas[tokens_list[1].value]) +')'
            outputs.append(format(opcodes[instr], '012b') + '' + etiqueta)
        
        
    if len(tokens_list) == 4:
        instr = tokens_list[0].value
        r1 = tokens_list[1].value
        
        if(tokens_list[3].type == 'REGISTER'):
            r2 = tokens_list[3].value
            outputs.append(format(opcodes[instr], '056b') + format(r1, '04b') + format(r2, '04b'))
        
        if(tokens_list[3].type == 'NUMBER'):
            num = tokens_list[3].value
            outputs.append(format(opcodes[instr], '08b') + format(r1, '04b') + encode_64(num))
        
        
        if(tokens_list[3].type == 'ETIQUETA'):
            etiqueta = '('+ str(etiquetas[tokens_list[3].value]) +')'
            outputs.append(format(opcodes[instr], '08b') + format(r1, '04b') + '' + etiqueta)
        
        

    return outputs  # Devolver la lista de outputs

# ========================
# MAIN
# ========================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python Assembler.py <archivo_entrada>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = os.path.join(os.path.dirname(input_file), 'program1.bin')
    
    try:
        with open(input_file, 'r') as infile:
            
            for l in infile:
                l = l.strip()
                if l:  # Si la línea no está vacía
                    parse_etiq(l)
                    linea +=1
                    
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            linea = 0
            for line in infile:
                line = line.strip()  # Remover espacios en blanco
                if line:  # Si la línea no está vacía
                    outputs = parse_line(line)
                    for output in outputs:
                        outfile.write(output + '\n')
                    linea += 1
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {input_file}")
    except Exception as e:
        print(f"Error: {e}")