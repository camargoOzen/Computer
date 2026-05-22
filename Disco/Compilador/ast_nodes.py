class Node:
    def __init__(self):
        pass

    def __str__(self):
        return "Nodo genérico"
    
    def __repr__(self):
        return self.__str__()
    
    def accept(self, visitor):
        # Este método buscará en el visitor la función que corresponde a esta clase
        method_name = 'visit_' + self.__class__.__name__
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)

    def generic_visit(self, visitor):
        raise Exception(f"No se definió visit_{self.__class__.__name__}")

class Func_node(Node):
    def __init__(self, type, ID, params, Block_node):
        self.type = type
        self.ID = ID
        self.params = params
        self.Block_node = Block_node
    
    def __str__(self):
        return f"Función: {self.ID}, Tipo: {self.type}, Parámetros: {self.params}, Bloque: {self.Block_node}"
    
class Param_node(Node):
    def __init__(self, type, ID, array_opt = None):
        self.type = type
        self.ID = ID
        self.array_opt = array_opt

    def __str__(self):
        return f"Parámetro: {self.ID}, Tipo: {self.type}, Array: {self.array_opt}"

    

class Struct_node(Node):
    def __init__(self, ID, field_list):
        self.ID = ID
        self.field_list = field_list

    def __str__(self):
        return f"Estructura: {self.ID}, Campos: {self.field_list}"

class Field_node(Node):
    def __init__(self, type, ID, Array_size_node = None):
        self.type = type
        self.ID = ID
        self.Array_size_node = Array_size_node

    def __str__(self):
        return f"Campo: {self.ID}, Tipo: {self.type}, Tamaño de Array: {self.Array_size_node}"

class Array_size_node(Node):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return f"Tamaño de Array: {self.size}"

class Typedef_node(Node):
    def __init__(self, ID_alias, field_list = None):
        self.type = "struct"
        self.ID_alias = ID_alias
        self.field_list = field_list

    def __str__(self):
        return f"Alias de Tipo: {self.ID_alias}, Campos: {self.field_list}"

class Struct_node(Node):
    def __init__(self, ID, field_list = None):
        self.ID = ID
        self.field_list = field_list

    def __str__(self):
        return f"Estructura: {self.ID}, Campos: {self.field_list}"

class Var_node(Node):
    def __init__(self, type, ID, Var_suffix_node, init = None):
        self.type = type
        self.ID = ID
        self.Var_suffix_node = Var_suffix_node
        self.init = init

    def __str__(self):
        return f"Variable: {self.ID}, Tipo: {self.type}, Sufijo: {self.Var_suffix_node}, Inicialización: {self.init}"

class Array_suffix_node(Node):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return f"Sufijo de Array: {self.size}"

class Matriz_suffix_node(Node):
    def __init__(self, size1, size2):
        self.size1 = size1
        self.size2 = size2
    
    def __str__(self):
        return f"Sufijo de Matriz: [{self.size1}][{self.size2}]"

class Assign_node(Node):
    def __init__(self, lvalue_node, assign_op, expr_node):
        self.Lvalue_node = lvalue_node
        self.assign_op = assign_op
        self.expr_node = expr_node
    
    def __str__(self):
        return f"Asignación: {self.Lvalue_node} {self.assign_op} {self.expr_node}"

class Lvalue_node(Node):
    def __init__(self, ID, lvalue_tail):
        self.ID = ID
        self.lvalue_tail = lvalue_tail
    
    def __str__(self):
        return f"Lvalue: {self.ID}, Sufijo: {self.lvalue_tail}"
    

class Call_node(Node):
    def __init__(self, ID, args):
        self.ID = ID
        self.args = args
    
    def __str__(self):
        return f"Función llamada: {self.ID}, Argumentos: {self.args}"

class If_node(Node):
    def __init__(self, condition, block, elif_opt = None):
        self.condition = condition
        self.block = block
        self.elif_opt = elif_opt
    
    def __str__(self):
        return f"Estructura If: Condición: {self.condition}, Bloque: {self.block}, Elif opcional: {self.elif_opt}"

class Elif_node(Node):
    def __init__(self, condition, block, elif_opt = None):
        self.condition = condition
        self.block = block
        self.elif_opt = elif_opt

    def __str__(self):
        return f"Estructura Elif: Condición: {self.condition}, Bloque: {self.block}, Elif opcional: {self.elif_opt}"

class Else_node(Node):
    def __init__(self, block):
        self.block = block
    def __str__(self):
        return f"Estructura Else: Bloque: {self.block}"
    

class While_node(Node):
    def __init__(self, conditino, block):
        self.condition = conditino
        self.block = block
    
    def __str__(self):
        return f"Estructura While: Condición: {self.condition}, Bloque: {self.block}"

class For_node(Node):
    def __init__(self, init, condition, update, block):
        self.init = init
        self.condition = condition
        self.update = update
        self.block = block
    
    def __str__(self):
        return f"Estructura For: Inicialización: {self.init}, Condición: {self.condition}, Actualización: {self.update}, Bloque: {self.block}"

class Var_decl_node(Node):
    def __init__(self, type, ID, init_opt = None):
        self.type = type
        self.ID = ID
        self.init_opt = init_opt
    def __str__(self):
        return f"Declaración de Variable: {self.ID}, Tipo: {self.type}, Inicialización opcional: {self.init_opt}"

class Do_while_node(Node):
    def __init__(self, block, while_condition):
        self.block = block
        self.condition = while_condition
    def __str__(self):
        return f"Estructura Do-While: Bloque: {self.block}, Condición: {self.condition}"

class Return_node(Node):
    def __init__(self, expr_opt = None):
        self.expr_opt = expr_opt
    def __str__(self):
        return f"Sentencia Return: Expresión opcional: {self.expr_opt}"

class Break_node(Node):
    def __init__(self):
        pass
    

class Continue_node(Node):
    def __init__(self):
        pass

class Or_node(Node):
    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador OR: {self.left_expr} OR {self.right_expr}"

class And_node(Node):
    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador AND: {self.left_expr} AND {self.right_expr}"

class Equality_node(Node):
    def __init__(self, symbol , left_expr, right_expr):
        self.symbol = symbol
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador de Igualdad: {self.left_expr} {self.symbol} {self.right_expr}"


class Relational_node(Node):
    def __init__(self, symbol , left_expr, right_expr):
        self.symbol = symbol
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador Relacional: {self.left_expr} {self.symbol} {self.right_expr}"

class Additive_node(Node):
    def __init__(self, symbol , left_expr, right_expr):
        self.symbol = symbol
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador Aditivo: {self.left_expr} {self.symbol} {self.right_expr}"

class Term_node(Node):
    def __init__(self, symbol , left_expr, right_expr):
        self.symbol = symbol
        self.left_expr = left_expr
        self.right_expr = right_expr
    
    def __str__(self):
        return f"Operador de Término: {self.left_expr} {self.symbol} {self.right_expr}"

class Unary_node(Node):
    def __init__(self, symbol , expr):
        self.symbol = symbol
        self.expr = expr
    
    def __str__(self):
        return f"Operador Unario: {self.symbol} {self.expr}"

class Postfix_node(Node):
    def __init__(self, primary, postfix_tail):
        self.primary = primary
        self.postfix_tail = postfix_tail
    
    def __str__(self):
        return f"Postfix: {self.primary} {self.postfix_tail}"

class Number_node(Node):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Number: {self.value}"