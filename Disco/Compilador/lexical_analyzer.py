import ply.lex as lex

class LexicalAnalyzer:

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
        'else'      : 'ELSE',
        'switch'    : 'SWITCH',
        'case'      : 'CASE',
        'default'   : 'DEFAULT',

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

        # -- Manejo de memoria / pila --
        'push'      : 'PUSH',
        'pop'       : 'POP',
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
        'COLON',            # :

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
    t_COLON     = r':'

    def __init__(self):
        self.lexer = lex.lex(module=self)

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
        print(f"[ERROR LÉXICO] Línea {t.lineno}: carácter ilegal '{t.value[0]}'")
        t.lexer.skip(1)


    def analyze(self, program: str):
        """Tokeniza el código fuente e imprime la tabla de tokens."""
        self.lexer.input(program)
        self.lexer.lineno = 1

        print(f"\n{'='*60}")
        print(f"{'LINE':<8} {'TYPE':<20} {'VALUE'}")
        print(f"{'='*60}")

        for tok in self.lexer:
            print(f"{tok.lineno:<8} {tok.type:<20} {tok.value}")

        print(f"{'='*60}\n")

    
if __name__ == "__main__":
    lex_analyzer = LexicalAnalyzer()

    p = """
    /* Programa de prueba para el analizador léxico
    Máquina Von Neumann 64 bits                  */
    
    struct Punto {
        int x;
        int y;
    }
    
    func int suma(int a, int b) {
        return a + b;
    }
    
    func void main() {
        int resultado = 0;
        float pi = 3.14159;
        bool activo = true;
        char letra = 'A';
        int arr[10];
        int mat[3][3];
    
        struct Punto p;
        p.x = 5;
        p.y = 10;
    
        // Estructura de selección
        if (resultado == 0) {
            resultado = suma(p.x, p.y);
        } else {
            resultado = 0;
        }
    
        // Estructura de iteración
        int i = 0;
        while (i < 10) {
            arr[i] = i * 2;
            i += 1;
        }
    
        for (int j = 0; j < 3; j += 1) {
            mat[j][0] = j;
        }
    
        // Manejo de pila
        push(resultado);
        int valor = pop();
    }
    """

    lex_analyzer.analyze(p)