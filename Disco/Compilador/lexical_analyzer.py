import ply.lex as lex

class LexicalAnalyzer:

    def __init__(self):
        self.errors = []
        self.symbol_table = {}
        self.lexer = lex.lex(module=self)

    reserved = {
        # -- Tipos de datos primitivos --
        'int'       : 'INT',
        'float'     : 'FLOAT',
        'char'      : 'CHAR',
        'bool'      : 'BOOL',
        'void'      : 'VOID',

        # -- Tipo de Dato Abstracto (TDA) --
        'struct'    : 'STRUCT',
        'typedef'   : 'TYPEDEF',

        # -- Estructuras de selección --
        'if'        : 'IF',
        'elseif'    : 'ELSEIF',
        'else'      : 'ELSE',

        # -- Estructuras de iteración --
        'while'     : 'WHILE',
        'for'       : 'FOR',
        'do'        : 'DO',

        # -- Control de flujo --
        'break'     : 'BREAK',
        'continue'  : 'CONTINUE',
        'return'    : 'RETURN',

        # -- Valores literales booleanos --
        'true'      : 'TRUE',
        'false'     : 'FALSE',

        # -- Declaración de funciones --
        'func'      : 'FUNC',
    }

    tokens = [
        # -- Identificadores y literales --
        'ID',               # nombre de variable, función, TDA
        'INT_LITERAL',      # número entero (64 bits)
        'FLOAT_LITERAL',    # número en punto flotante (64 bits)
        'CHAR_LITERAL',     # carácter individual 
        'STRING_LITERAL',   # cadena de texto    

        # -- Operadores aritméticos --
        'PLUS',             # +
        'MINUS',            # -
        'TIMES',            # *
        'DIVIDE',           # /
        'MODULO',           # %

        # -- Operadores relacionales --
        'EQ',               # ==
        'NEQ',              # !=
        'LT',               # <
        'GT',               # >
        'LEQ',              # <=
        'GEQ',              # >=

        # -- Operadores lógicos --
        'AND',              # &&
        'OR',               # ||
        'NOT',              # !

        # -- Operadores de asignación --
        'ASSIGN',           # =
        'PLUS_ASSIGN',      # +=
        'MINUS_ASSIGN',     # -=
        'TIMES_ASSIGN',     # *=
        'DIVIDE_ASSIGN',    # /=

        # -- Delimitadores --
        'LPAREN',           # (
        'RPAREN',           # )
        'LBRACE',           # {
        'RBRACE',           # }
        'LBRACKET',         # [
        'RBRACKET',         # ]
        'SEMICOLON',        # ;
        'COMMA',            # ,
        'DOT',              # .  
 

    ] + list(reserved.values())

    # Operadores compuestos

    t_EQ            = r'=='
    t_NEQ           = r'!='
    t_LEQ           = r'<='
    t_GEQ           = r'>='
    t_AND           = r'&&'
    t_OR            = r'\|\|'
    t_PLUS_ASSIGN   = r'\+='
    t_MINUS_ASSIGN  = r'-='
    t_TIMES_ASSIGN  = r'\*='
    t_DIVIDE_ASSIGN = r'/='


    # Operadores simples

    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'
    t_DIVIDE    = r'/'
    t_MODULO    = r'%'
    t_LT        = r'<'
    t_GT        = r'>'
    t_NOT       = r'!'
    t_ASSIGN    = r'='

    # Delimitadores

    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACE    = r'\{'
    t_RBRACE    = r'\}'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_SEMICOLON = r';'
    t_COMMA     = r','
    t_DOT       = r'\.'

    def t_FLOAT_LITERAL(self, t):
        r'[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?'
        # Extensión regular: dígitos '.' dígitos  con exponente opcional
        t.value = float(t.value)
        return t

    def t_INT_LITERAL(self, t):
        r'(0[xX][0-9a-fA-F]+|0[bB][01]+|[0-9]+)'
        # Definición regular: decimal | hexadecimal (0x...) | binario (0b...)
        if t.value.startswith(('0x','0X')):
            t.value = int(t.value, 16)
        elif t.value.startswith(('0b','0B')):
            t.value = int(t.value, 2)
        else:
            t.value = int(t.value)
        return t

    def t_CHAR_LITERAL(self, t):
        r"'(\\.|[^\\'])'"
        # Extensión regular: carácter simple 
        t.value = t.value[1:-1]  
        return t

    def t_STRING_LITERAL(self, t):
        r'"(\\.|[^\\"])*"'
        # Extensión regular: cualquier carácter o escape entre comillas dobles
        t.value = t.value[1:-1]   
        return t


    # Identificadores y palabras reservadas

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Definición regular: LETTER (LETTER | DIGIT)*
        # Si el lexema está en la tabla de reservadas, cambia el tipo
        t.type = self.reserved.get(t.value, 'ID')

        # Agrega a la tabla de símbolos si es un identificador
        if t.type == 'ID':
            if t.value not in self.symbol_table:
                self.symbol_table[t.value] = {
                    "name": t.value,
                    "type": None,
                    "scope": None,
                    "param": False,
                    "array_size": None,
                    "array_dimensions": None,
                }

        return t


    # Comentarios 

    def t_COMMENT_BLOCK(self, t):
        r'/\*(.|\n)*?\*/'
        # Comentario de bloque: /* ... */
        t.lexer.lineno += t.value.count('\n')
        # No retorna → el token se descarta

    def t_COMMENT_LINE(self, t):
        r'//[^\n]*'
        # Comentario de línea: // ...
        # No retorna → el token se descarta

    #Caracteres ignorados
    t_ignore = ' \t\r'   # espacios, tabuladores

    # Saltos de línea 

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        # No retorna → no genera token

    # Manejo de errores

    def t_error(self, t):
        self.errors.append(
            {
                "line": t.lineno,
                "char": t.value[0],
                "message": f"Caracter ilegal '{t.value[0]}'",
            }
        )
        t.lexer.skip(1)

    def tokenize(self, program: str):
        """Tokeniza el codigo fuente y retorna (tokens, errores)."""
        self.lexer.input(program)
        self.lexer.lineno = 1
        self.errors = []

        tokens = []
        for tok in self.lexer:
            tokens.append(
                {
                    "line": tok.lineno,
                    "type": tok.type,
                    "value": tok.value,
                }
            )

        return tokens, list(self.errors)


    def analyze(self, program: str):
        """Tokeniza el código fuente e imprime la tabla de tokens."""
        tokens, errors = self.tokenize(program)

        print(f"\n{'='*60}")
        print(f"{'LINE':<8} {'TYPE':<20} {'VALUE'}")
        print(f"{'='*60}")

        for tok in tokens:
            print(f"{tok['line']:<8} {tok['type']:<20} {tok['value']}")

        if errors:
            print("\nErrores lexicos:")
            for error in errors:
                print(f"  - Linea {error['line']}: {error['message']}")

        print(f"{'='*60}\n")

    
if __name__ == "__main__":
    lex_analyzer = LexicalAnalyzer()