import ply.yacc as yacc
from .lexical_analyzer import LexicalAnalyzer
from . import ast_nodes as ast

# Crea instancia del lexer
lex_analyzer = LexicalAnalyzer()
lexer = lex_analyzer.lexer

# Obtiene los tokens del lexer
tokens = lex_analyzer.tokens
errores = list()
symbol_table = lex_analyzer.symbol_table

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'LT', 'GT', 'LEQ', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'NOT'),
)
# -------------------------------------------------
# PROGRAMA
# -------------------------------------------------

def p_program(p):
    'program : declaration_list'
    p[0] = p[1]

# -------------------------------------------------
# DECLARATIONS
# -------------------------------------------------

def p_declaration_list_multi(p):
    'declaration_list : declaration_list declaration'
    p[0] = p[1] + [p[2]]

def p_declaration_list_single(p):
    'declaration_list : declaration'
    p[0] = [p[1]]

def p_declaration(p):
    '''declaration : func_decl
                   | struct_decl
                   | typedef_decl
                   | var_decl'''
    p[0] = p[1]

# -------------------------------------------------
# FUNCTION
# -------------------------------------------------

def p_func_decl(p):
    'func_decl : FUNC type ID LPAREN param_list_opt RPAREN block'
    symbol_table[p[3]]["type"] = f"func_{p[2]}"
    symbol_table[p[3]]["scope"] = "global"
    p[0] = ast.Func_node(p[2], p[3], p[5], p[7])

def p_param_list_opt(p):
    '''param_list_opt : param_list
                      | empty'''
    p[0] = p[1]

def p_param_list_multi(p):
    'param_list : param_list COMMA param'
    p[0] = p[1] + [p[3]]

def p_param_list_single(p):
    'param_list : param'
    p[0] = [p[1]]

def p_param(p):
    'param : type ID array_opt'
    symbol_table[p[2]]["type"] = p[1]
    symbol_table[p[2]]["param"] = True
    p[0] = ast.Param_node(p[1], p[2], p[3])

def p_array_opt(p):
    '''array_opt : LBRACKET RBRACKET
                 | empty'''
    p[0] = ast.Array_size_node(0) if len(p) > 1 else None

# -------------------------------------------------
# STRUCT
# -------------------------------------------------

def p_struct_decl(p):
    'struct_decl : STRUCT ID LBRACE field_list RBRACE SEMICOLON'
    symbol_table[p[2]]["type"] = p[1]
    symbol_table[p[2]]["field_list"] = [field.ID for field in p[4]]
    p[0] = ast.Struct_node(p[2], p[4])
    

def p_field_list_multi(p):
    'field_list : field_list field_decl'
    p[0] = p[1] + [p[2]]

def p_field_list_single(p):
    'field_list : field_decl'
    p[0] = [p[1]]

def p_field_decl(p):
    'field_decl : type ID array_size_opt SEMICOLON'
    symbol_table[p[2]]["type"] = p[1]
    if isinstance(p[3], ast.Matriz_suffix_node):
        symbol_table[p[2]]["array_size"] = p[3].size1 * p[3].size2 if p[3] else None
        # Guardar las dimensiones para acceso multidimensional
        symbol_table[p[2]]["array_dimensions"] = (p[3].size1, p[3].size2) if p[3] else None
    elif isinstance(p[3], ast.Array_suffix_node):
        symbol_table[p[2]]["array_size"] = p[3].size if p[3] else None
        symbol_table[p[2]]["array_dimensions"] = (p[3].size,) if p[3] else None

    p[0] = ast.Field_node(p[1], p[2], p[3])

def p_array_size_opt(p):
    '''array_size_opt : LBRACKET INT_LITERAL RBRACKET
                      | empty'''
    
    p[0] = ast.Array_size_node(p[2]) if len(p) > 2 else None

def p_typedef_decl(p):
    'typedef_decl : TYPEDEF STRUCT LBRACE field_list RBRACE ID SEMICOLON'
    p[0] = ast.Typedef_node(p[6], p[4])


# -------------------------------------------------
# TYPES
# -------------------------------------------------

def p_type_primitive(p):
    '''type : INT
            | FLOAT
            | CHAR
            | BOOL
            | VOID'''
    p[0] = p[1]

def p_type_struct(p):
    'type : STRUCT ID'
    
    symbol_table[p[2]]["type"] = p[1]
    
    p[0] = ast.Struct_node(p[2])

def p_type_id(p):
    'type : ID'
    p[0] = p[1]

# -------------------------------------------------
# VARIABLES
# -------------------------------------------------

def p_var_decl(p):
    'var_decl : type ID var_suffix_opt init_opt SEMICOLON'
    
    
    if isinstance(p[1], ast.Struct_node):
        symbol_table[p[2]]["type"] = p[1].ID
    else:
        symbol_table[p[2]]["type"] = p[1]
        if isinstance(p[3], ast.Matriz_suffix_node):
            symbol_table[p[2]]["array_size"] = p[3].size1 * p[3].size2 if p[3] else None
            # Guardar las dimensiones para acceso multidimensional
            symbol_table[p[2]]["array_dimensions"] = (p[3].size1, p[3].size2) if p[3] else None
        else:
            symbol_table[p[2]]["array_size"] = p[3].size if p[3] else None
            symbol_table[p[2]]["array_dimensions"] = (p[3].size,) if p[3] else None
    
    p[0] = ast.Var_node(p[1], p[2], p[3], p[4])

def p_var_suffix_opt(p):
    '''var_suffix_opt : array_suffix
                      | matrix_suffix
                      | empty'''
    p[0] = p[1]

def p_array_suffix(p):
    'array_suffix : LBRACKET INT_LITERAL RBRACKET'
    p[0] = ast.Array_suffix_node(p[2])

def p_matrix_suffix(p):
    'matrix_suffix : LBRACKET INT_LITERAL RBRACKET LBRACKET INT_LITERAL RBRACKET'
    p[0] = ast.Matriz_suffix_node(p[2], p[5])

def p_init_opt(p):
    '''init_opt : ASSIGN expr
                | empty'''
    p[0] = p[2] if len(p) > 2 else None

# -------------------------------------------------
# BLOCK & STATEMENTS
# -------------------------------------------------

def p_block(p):
    'block : LBRACE stmt_list RBRACE'
    p[0] = p[2]

def p_stmt_list_multi(p):
    'stmt_list : stmt_list statement'
    p[0] = p[1] + [p[2]]

def p_stmt_list_single(p):
    'stmt_list : statement'
    p[0] = [p[1]]

def p_statement(p):
    '''statement : var_decl
                 | assign_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | do_while_stmt
                 | return_stmt
                 | break_stmt
                 | continue_stmt
                 | func_call_stmt
                 | block'''
    p[0] = p[1]

# -------------------------------------------------
# ASSIGN
# -------------------------------------------------

def p_assign_stmt(p):
    'assign_stmt : lvalue assign_op expr SEMICOLON'
    p[0] = ast.Assign_node(p[1], p[2], p[3])

def p_assign_op(p):
    '''assign_op : ASSIGN
                 | PLUS_ASSIGN
                 | MINUS_ASSIGN
                 | TIMES_ASSIGN
                 | DIVIDE_ASSIGN'''
    p[0] = p[1]

# -------------------------------------------------
# LVALUE
# -------------------------------------------------

def p_lvalue(p):
    'lvalue : ID lvalue_tail'
    p[0] = ast.Lvalue_node(p[1], p[2])

def p_lvalue_tail_multi(p):
    'lvalue_tail : lvalue_tail lvalue_access'
    p[0] = p[1] + [p[2]]

def p_lvalue_tail_empty(p):
    'lvalue_tail : empty'
    p[0] = []

def p_lvalue_access(p):
    '''lvalue_access : DOT ID
                     | LBRACKET expr RBRACKET'''
    p[0] = p[1:]


# -------------------------------------------------
# FUNC CALL
# -------------------------------------------------

def p_func_call_stmt(p):
    'func_call_stmt : func_call SEMICOLON'
    p[0] = p[1]

def p_func_call(p):
    'func_call : ID LPAREN arg_list_opt RPAREN'
    p[0] = ast.Call_node(p[1], p[3])

def p_arg_list_opt(p):
    '''arg_list_opt : arg_list
                    | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_arg_list_multi(p):
    'arg_list : arg_list COMMA expr'
    p[0] = p[1] + [p[3]]

def p_arg_list_single(p):
    'arg_list : expr'
    p[0] = [p[1]]


# -------------------------------------------------
# IF, ELSE IF, ELSE
# -------------------------------------------------

def p_if_stmt(p):
    'if_stmt : IF LPAREN expr RPAREN block else_if_opt'
    p[0] = ast.If_node(p[3], p[5], p[6])

def p_else_if_opt(p):
    '''else_if_opt : else_if_list
                   | else_opt
                   | empty'''
    p[0] = p[1]

def p_else_if_list(p):
    'else_if_list : ELSE IF LPAREN expr RPAREN block else_if_list'
    p[0] = ast.Elif_node(p[4], p[6], p[7])

def p_else_if_single(p):
    'else_if_list : ELSE IF LPAREN expr RPAREN block else_if_opt'
    p[0] = ast.Elif_node(p[4], p[6], p[7])

def p_else_opt(p):
    '''else_opt : ELSE block
                | empty'''
    p[0] = ast.Else_node(p[2]) if len(p) > 2 else None

# -------------------------------------------------
# WHILE, FOR, DO-WHILE
# -------------------------------------------------

def p_while_stmt(p):
    'while_stmt : WHILE LPAREN expr RPAREN block'
    p[0] = ast.While_node(p[3], p[5])

def p_for_stmt(p):
    'for_stmt : FOR LPAREN for_init SEMICOLON expr_opt SEMICOLON for_update RPAREN block'
    p[0] = ast.For_node(p[3], p[5], p[7], p[9])

def p_for_init(p):
    '''for_init : var_decl_inline
                | assign_stmt_inline
                | empty'''
    p[0] = p[1]

def p_for_update(p):
    '''for_update : assign_stmt_inline_list
                  | empty'''
    p[0] = p[1]

def p_assign_stmt_inline_list(p):
    'assign_stmt_inline_list : assign_stmt_inline_list COMMA assign_stmt_inline'
    p[0] = p[1] + [p[3]]

def p_assign_stmt_inline_single(p):
    'assign_stmt_inline_list : assign_stmt_inline'
    p[0] = [p[1]]

def p_assign_stmt_inline(p):
    'assign_stmt_inline : lvalue assign_op expr'
    p[0] = ast.Assign_node(p[1], p[2], p[3])

def p_var_decl_inline(p):
    'var_decl_inline : type ID init_opt'
    symbol_table[p[2]]["type"] = p[1]
    p[0] = ast.Var_decl_node(p[1], p[2], p[3])

def p_do_while_stmt(p):
    'do_while_stmt : DO block WHILE LPAREN expr RPAREN SEMICOLON'
    
    p[0] = ast.Do_while_node(p[2], p[5])


# -------------------------------------------------
# RETURN, BREAK, CONTINUE
# -------------------------------------------------

def p_return_stmt(p):
    'return_stmt : RETURN expr_opt SEMICOLON'
    p[0] = ast.Return_node(p[2])

def p_break_stmt(p):
    'break_stmt : BREAK SEMICOLON'
    p[0] = ast.Break_node()
def p_continue_stmt(p):
    'continue_stmt : CONTINUE SEMICOLON'
    p[0] = ast.Continue_node()

def p_expr_opt(p):
    '''expr_opt : expr
                | empty'''
    p[0] = p[1]


# -------------------------------------------------
# EXPRESSIONS
# -------------------------------------------------

def p_expr(p):
    'expr : logic_or'
    p[0] = p[1]

def p_logic_or(p):
    '''logic_or : logic_or OR logic_and
                | logic_and'''
    p[0] = p[1] if len(p) == 2 else ast.Or_node(p[1], p[3])

def p_logic_and(p):
    '''logic_and : logic_and AND equality
                 | equality'''
    p[0] = p[1] if len(p) == 2 else ast.And_node(p[1], p[3])

def p_equality(p):
    '''equality : equality EQ relational
                | equality NEQ relational
                | relational'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.Equality_node(p[2], p[1], p[3])

def p_relational(p):
    '''relational : relational LT additive
                  | relational GT additive
                  | relational LEQ additive
                  | relational GEQ additive
                  | additive'''
    p[0] = p[1] if len(p) == 2 else ast.Relational_node(p[2], p[1], p[3])

def p_additive(p):
    '''additive : additive PLUS term
                | additive MINUS term
                | term'''
    p[0] = p[1] if len(p) == 2 else ast.Additive_node(p[2], p[1], p[3])

def p_term(p):
    '''term : term TIMES unary
            | term DIVIDE unary
            | term MODULO unary
            | unary'''
    p[0] = p[1] if len(p) == 2 else ast.Term_node(p[2], p[1], p[3])

def p_unary(p):
    '''unary : NOT unary
             | MINUS unary
             | postfix'''
    p[0] = ast.Unary_node(p[1], p[2]) if len(p) == 3 else p[1]

def p_postfix(p):
    'postfix : primary postfix_tail'
    if p[2]:
        p[0] = ast.Postfix_node(p[1], p[2])
    else:
        p[0] = p[1]

def p_postfix_tail_multi(p):
    'postfix_tail : postfix_tail postfix_access'
    p[0] = p[1] + [p[2]]

def p_postfix_tail_empty(p):
    'postfix_tail : empty'
    p[0] = []

def p_postfix_access(p):
    '''postfix_access : DOT ID
                      | LBRACKET expr RBRACKET'''
    p[0] = p[1:]

def p_primary(p):
    '''primary : literal
               | func_call
               | lvalue
               | LPAREN expr RPAREN'''
    p[0] = p[1] if len(p) == 2 else p[2]


# -------------------------------------------------
# LITERALS
# -------------------------------------------------

def p_literal(p):
    '''literal : INT_LITERAL
               | FLOAT_LITERAL'''
    p[0] = ast.Number_node(p[1])


def p_literal_bool(p):
    '''literal : TRUE
               | FALSE'''
    p[0] = ast.Number_node(1 if p[1] == 'true' else 0)


def p_literal_char(p):
    'literal : CHAR_LITERAL'
    p[0] = ast.Number_node(ord(p[1]))


def p_literal_string(p):
    'literal : STRING_LITERAL'
    p[0] = p[1]


# -------------------------------------------------
# EMPTY
# -------------------------------------------------

def p_empty(p):
    'empty :'
    pass

# -------------------------------------------------
# MANEJO DE ERRORES
# -------------------------------------------------

def p_error(p):
    if p:
        print(f"Error sintáctico en línea {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})")
        errores.append(f"Error sintáctico en línea {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})")
    else:
        print("Error sintáctico: fin de archivo inesperado")

# -------------------------------------------------
# CONSTRUCCIÓN DEL PARSER
# -------------------------------------------------

# Crea el parser (solo una vez)
parser = yacc.yacc(debug=False, write_tables=False, module=None)

# -------------------------------------------------
# FUNCIÓN PARA ANALIZAR
# -------------------------------------------------

def parse(code: str):
    """
    Analiza código fuente y retorna el AST.
    
    Args:
        code (str): Código fuente a analizar
        
    Returns:
        Árbol sintáctico o None si hay errores
    """
    
    errores.clear()
    # Tokeniza el código
    tokens, lex_errors = lex_analyzer.tokenize(code)
    
    # Si hay errores léxicos, imprime y retorna
    if lex_errors:
        print("Errores léxicos encontrados:")
        for error in lex_errors:
            print(f"  Línea {error['line']}: {error['message']}")
        return None
    
    # Parsea el código
    ast = parser.parse(code, lexer=lexer)
    return ast, symbol_table, errores

if __name__ == "__main__":
    # Código de prueba
    code = """
    struct Punto {
        int x;
        int y;
    };
    
    func int suma(int a, int b) {
        return a + b;
    }
    
    func void main() {
        int resultado = 0;
        float pi = 3.14159;
        bool activo = true;
        char letra = 'A';
        string mensaje = "hola, mundo";
        int arr[10];
        int mat[3][3];
    
        // Estructura de selección
        if (resultado == 0) {
            resultado = suma(p.x, p.y);
        }

        while (x < 10){
            i = 0;
            i = i + 1;}
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
        
    }
"""
    
    result = parse(code)
    if result:
        print("\nÁrbol sintáctico generado exitosamente")
        print(result.__str__())