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
    'ETIQUETA',
    'SIZE',
    "DATA",
    "CODE"
)

t_COMMA = r','

# ========================
# INSTRUCCIONES
# ========================
def t_INSTR(t):
    r'LOADV|LOADI|LOAD|STOREI|STORE|PUSH|POP|LEA|ADDF|ADD|SUBF|SUB|MULF|MUL|DIVF|DIV|MODF|MOD|CPY|INC|DEC|CMPF|CMP|I2F|F2I|TEST|AND|OR|XOR|NOT|NAND|NOR|SHL|SHR|ROL|ROR|JMP|JZ|JNZ|JP|JN|JC|JNC|JO|JNO|CALL|RET|CLI|STI|NOP|IN|OUT'
    return t

def t_SIZE(t):
    r'\.SIZE'
    return t

def t_DATA(t):
    r'\.DATA'
    return t

def t_CODE(t):
    r'\.CODE'
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
    'LOADI' :0x14000000000000,
    'LOADV' :0x12,
    'STORE' :0x13,
    'STOREI':0x15000000000000,
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


def reserve_size(n, outputs: list):
    for size in range(n):
        outputs.append(format(0, '064b'))


def to_unsigned_64(value):
    return value & ((1 << 64) - 1)


def float_to_u64(value: float) -> int:
    packed = struct.pack('>d', float(value))
    return int.from_bytes(packed, byteorder='big', signed=False)


def encode_64(value) -> str:
    if isinstance(value, float):
        return format(float_to_u64(value), '064b')
    return format(to_unsigned_64(int(value)), '064b')


def _reset_state():
    global linea
    etiquetas.clear()
    linea = 0


def _strip_comment(line):
    return line.split(';', 1)[0].strip()


def _strip_label_prefix(line):
    if ':' not in line:
        return line.strip()

    _, _, remainder = line.partition(':')
    return remainder.strip()


def _tokenize(line):
    lexer.input(line)

    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)

    return tokens_list


def _collect_labels(lines):
    global linea

    linea = 0
    etiquetas.clear()

    for raw_line in lines:
        line = _strip_comment(raw_line)
        if not line:
            continue

        if ':' in line:
            label, _, remainder = line.partition(':')
            label = label.strip()
            if label:
                etiquetas[label] = linea
            line = remainder.strip()
            if not line:
                continue

        tokens_list = _tokenize(line)
        if len(tokens_list) == 1 and tokens_list[0].type == 'ETIQUETA':
            etiquetas[str(tokens_list[0].value)] = linea
            continue

        if tokens_list:
            # Check if this is a .SIZE directive that reserves multiple lines
            if len(tokens_list) == 2 and tokens_list[0].type == 'SIZE':
                size_count = int(tokens_list[1].value)
                linea += size_count
            else:
                linea += 1


def _assemble_line(line):
    outputs = []
    tokens_list = _tokenize(line)

    if len(tokens_list) == 1:
        if tokens_list[0].type == 'INSTR':
            instr = tokens_list[0].value
            outputs.append(format(opcodes[instr], '064b'))

        if tokens_list[0].type == 'NUMBER':
            num = tokens_list[0].value
            outputs.append(encode_64(num))

    if len(tokens_list) == 2:
        instr = tokens_list[0].value
        if tokens_list[1].type == 'REGISTER':
            r1 = tokens_list[1].value
            outputs.append(format(opcodes[instr], '056b') + format(r1, '04b'))
        if tokens_list[1].type == 'ETIQUETA':
            etiqueta = '(' + str(etiquetas[tokens_list[1].value]) + ')'
            outputs.append(format(opcodes[instr], '012b') + etiqueta)
        if tokens_list[0].type == 'SIZE':
            reserve_size(int(tokens_list[1].value),outputs)

    if len(tokens_list) == 4:
        instr = tokens_list[0].value
        r1 = tokens_list[1].value

        if tokens_list[3].type == 'REGISTER':
            r2 = tokens_list[3].value
            outputs.append(format(opcodes[instr], '056b') + format(r1, '04b') + format(r2, '04b'))

        if tokens_list[3].type == 'NUMBER':
            num = tokens_list[3].value
            outputs.append(format(opcodes[instr], '08b') + format(r1, '04b') + encode_64(num))

        if tokens_list[3].type == 'ETIQUETA':
            etiqueta = '(' + str(etiquetas[tokens_list[3].value]) + ')'
            outputs.append(format(opcodes[instr], '08b') + format(r1, '04b') + etiqueta)

    return outputs


def assemble_program(program: str) -> str:
    lines = program.splitlines()
    _collect_labels(lines)

    global linea
    linea = 0

    outputs = []
    for raw_line in lines:
        line = _strip_comment(raw_line)
        if not line:
            continue

        if ':' in line:
            _, _, line = line.partition(':')
            line = line.strip()
            if not line:
                continue

        line_outputs = _assemble_line(line)
        outputs.extend(line_outputs)
        if line_outputs:
            linea += 1

    return '\n'.join(outputs)


def assemble_file(input_file: str) -> str:
    with open(input_file, 'r', encoding='utf-8') as infile:
        return assemble_program(infile.read())


def parse_etiq(line):
    _collect_labels([line])


def parse_line(line):
    return _assemble_line(_strip_label_prefix(_strip_comment(line)))

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
        program = assemble_file(input_file)
        with open(output_file, 'w', encoding='utf-8') as outfile:
            if program:
                outfile.write(program + '\n')
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {input_file}")
    except Exception as e:
        print(f"Error: {e}")