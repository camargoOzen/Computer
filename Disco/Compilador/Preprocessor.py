import os
import ply.lex as lex
import sys

# ========================
# TOKENS
# ========================
tokens = (
    'INCLUDE',
    'DEFINE',
    'STRING',
    'NUMBER',
    'COLON',
    'COMMA',
    'OTHER',

)

# ========================
# STRINGS
# ========================
def t_INCLUDE(t):
    r'INCLUDE'
    return t

def t_DEFINE(t):
    r'DEFINE'
    return t

def t_STRING(t):
    r'"[^"]*"|\'[^\']*\''
    t.value = t.value[1:-1]  # Remove ""
    return t

def t_NUMBER(t):
    r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?'
    raw = t.value
    if ('.' in raw) or ('e' in raw) or ('E' in raw):
        t.value = float(raw)
    else:
        t.value = int(raw)
    return t

def t_COMMENT(t):
    r';[^\n]*'
    pass

def t_COLON(t):
    r':'
    return t

def t_COMMA(t):
    r','
    return t

t_ignore = ' \t'

def t_OTHER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

macros = {}


def resolve_include_path(include_name, current_dir, lib_dir):
    if not include_name.lower().endswith('.asm'):
        include_name = include_name + '.asm'

    candidate_paths = [
        os.path.join(current_dir, include_name),
        os.path.join(lib_dir, include_name) if lib_dir else None,
    ]

    for candidate in candidate_paths:
        if candidate and os.path.isfile(candidate):
            return os.path.abspath(candidate)

    raise FileNotFoundError(
        f"No se encontró el archivo incluido '{include_name}'. "
        f"Buscando en '{current_dir}' y '{lib_dir}'."
    )


def preprocess_file(input_path, lib_dir=None, included_files=None):
    """Preprocesa un archivo ASM y expande las directivas INCLUDE y DEFINE."""
    input_path = os.path.abspath(input_path)

    if included_files is None:
        included_files = set()

    if input_path in included_files:
        raise ValueError(f"Ciclo de inclusión detectado: {input_path}")

    included_files.add(input_path)

    if lib_dir is None:

        base_dir = os.path.dirname(os.path.abspath(__file__))
        lib_dir = os.path.abspath(os.path.join('Disco/Lib'))

    output_lines = []
    current_dir = os.path.dirname(input_path)

    with open(input_path, 'r', encoding='utf-8') as infile:
        for raw_line in infile:
            line = raw_line.rstrip('\n')
            lexer.input(line)
            tokens_list = list(lexer)
            lexer.input(line)
            
            if tokens_list and tokens_list[0].type == 'INCLUDE' and len(tokens_list) > 1 and tokens_list[1].type == 'STRING':
                include_name = tokens_list[1].value
                include_path = resolve_include_path(include_name, current_dir, lib_dir)
                included_lines = preprocess_file(include_path, lib_dir=lib_dir, included_files=included_files)
                output_lines.extend(included_lines)

            elif tokens_list and tokens_list[0].type == 'DEFINE' and len(tokens_list) > 2:
                define_name = tokens_list[1].value
                define_value = tokens_list[2].value
                macros[define_name] = define_value

            elif tokens_list and tokens_list[0].type == 'OTHER' and len(tokens_list) > 3:
                temp_instruction = tokens_list[0].value
                temp_value1 = tokens_list[1].value
                temp_other = tokens_list[2].value
                temp_value2 = tokens_list[3].value

                if tokens_list[1].type == 'OTHER' and temp_value1 in macros:
                    temp_value1 = macros[temp_value1]

                if tokens_list[3].type == 'OTHER' and temp_value2 in macros:
                        temp_value2 = macros[temp_value2]

                output_lines.append(f'{temp_instruction} {temp_value1} {temp_other} {temp_value2}')
            else:
                output_lines.append(line)

    included_files.remove(input_path)
    return output_lines


def write_preprocessed_file(input_path, output_path=None, lib_dir=None):
    lines = preprocess_file(input_path, lib_dir=lib_dir)

    if output_path is None:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f'{base_name}.preprocessed.asm')

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in lines:
            outfile.write(line + '\n')

    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Uso: python Preprocessor.py <archivo_entrada> [<archivo_salida>]')
        sys.exit(1)

    source_file = sys.argv[1]
    target_file = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        salida = write_preprocessed_file(source_file, output_path=target_file)
        print(f'Archivo preprocesado guardado en: {salida}')
    except Exception as exc:
        print(f'Error: {exc}')
        sys.exit(1)
