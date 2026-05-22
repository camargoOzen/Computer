import os
import re
import sys

INCLUDE_RE = re.compile(r'^\s*INCLUDE\s+("[^"]+"|\'[^\']+\')\s*$', re.IGNORECASE)
DEFINE_RE = re.compile(r'^\s*DEFINE\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.+?)\s*$')


def _default_lib_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lib'))


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


def _preprocess_lines(lines, current_dir, lib_dir, included_files, macros_table):
    output_lines = []

    for raw_line in lines:
        line = raw_line.rstrip('\n')

        include_match = INCLUDE_RE.match(line)
        if include_match:
            include_name = include_match.group(1)[1:-1]
            include_path = resolve_include_path(include_name, current_dir, lib_dir)
            included_lines = preprocess_file(
                include_path,
                lib_dir=lib_dir,
                included_files=included_files,
                macros=macros_table,
            )
            output_lines.extend(included_lines)
            continue

        define_match = DEFINE_RE.match(line)
        if define_match:
            define_name = define_match.group(1)
            define_value = define_match.group(2)
            macros_table[define_name] = define_value
            continue

        processed_line = line
        if macros_table:
            # Reemplaza macros completas sin alterar puntuacion ni espaciado original.
            for name, value in macros_table.items():
                processed_line = re.sub(rf'\b{re.escape(name)}\b', str(value), processed_line)

        output_lines.append(processed_line)

    return output_lines


def preprocess_program(program, current_dir=None, lib_dir=None, included_files=None, macros_table=None):
    """Preprocesa un string ASM y expande las directivas INCLUDE y DEFINE."""
    if current_dir is None:
        current_dir = os.getcwd()

    if lib_dir is None:
        lib_dir = _default_lib_dir()

    if included_files is None:
        included_files = set()

    if macros_table is None:
        macros_table = {}

    return '\n'.join(
        _preprocess_lines(program.splitlines(), current_dir, lib_dir, included_files, macros_table)
    )


def preprocess_file(input_path, lib_dir=None, included_files=None, macros=None):
    """Preprocesa un archivo ASM y expande las directivas INCLUDE y DEFINE."""
    input_path = os.path.abspath(input_path)

    if included_files is None:
        included_files = set()

    if macros is None:
        macros = {}

    if input_path in included_files:
        raise ValueError(f"Ciclo de inclusión detectado: {input_path}")

    included_files.add(input_path)

    if lib_dir is None:
        lib_dir = _default_lib_dir()

    current_dir = os.path.dirname(input_path)

    with open(input_path, 'r', encoding='utf-8') as infile:
        output_lines = _preprocess_lines(
            infile.read().splitlines(),
            current_dir,
            lib_dir,
            included_files,
            macros,
        )

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
