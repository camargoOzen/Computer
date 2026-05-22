"""
Análisis Semántico - Valida tipos, scopes y referencias
Usa el patrón Visitor para recorrer el AST
"""

from .ast_nodes import *

class SemanticAnalyzer:
    """Realiza análisis semántico del programa"""
    
    def __init__(self):
        self.global_scope = {}  # Variables/funciones globales
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]  # Stack de scopes
        self.symbol_table = {}  # Tabla de símbolos global
        self.errors = []
        self.functions = {}
        self.structs = {}
        
    def push_scope(self):
        """Crea un nuevo scope local"""
        new_scope = {}
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
        
    def pop_scope(self):
        """Sale del scope local"""
        self.scope_stack.pop()
        self.current_scope = self.scope_stack[-1]
        
    def declare_symbol(self, name: str, type_info: dict):
        """Declara un símbolo en el scope actual"""
        if name in self.current_scope:
            self.errors.append(f"Error: '{name}' ya fue declarado")
            return False
        self.current_scope[name] = type_info
        return True
    
    def lookup_symbol(self, name: str) -> dict:
        """Busca un símbolo en todos los scopes (de más local a global)"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def analyze(self, ast_root, symbol_table):
        """Comienza el análisis semántico del AST"""
        if not ast_root:
            return False
        self.symbol_table = symbol_table
        
        # Vacía los errores
        self.errors = []
        
        # Recorre el AST usando el patrón Visitor
        if isinstance(ast_root, list):
            for declaration in ast_root:
                declaration.accept(self)
        else:
            ast_root.accept(self)
            
        return len(self.errors) == 0
    
    # ============================================
    # VISITANTES PARA CADA TIPO DE NODO
    # ============================================
    
    def visit_Func_node(self, node: Func_node):
        """Visita una declaración de función"""
        # Registra la función
        func_info = {
            "type": "function",
            "return_type": node.type,
            "params": node.params,
        }
        if not self.declare_symbol(node.ID, func_info):
            return
        self.functions[node.ID] = func_info
        
        # Crea scope local para la función
        self.push_scope()
        
        # Registra parámetros en el scope local
        if node.params:
            for param in node.params:
                if hasattr(param, 'accept'):
                    param.accept(self)
        
        # Analiza el bloque
        if node.Block_node:
            if isinstance(node.Block_node, list):
                for stmt in node.Block_node:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.Block_node, 'accept'):
                node.Block_node.accept(self)
        
        self.pop_scope()
    
    def visit_Param_node(self, node: Param_node):
        """Visita un parámetro de función"""
        param_info = {
            "type": "parameter",
            "data_type": node.type,
            "is_array": node.array_opt is not None,
        }
        self.declare_symbol(node.ID, param_info)
    
    def visit_Struct_node(self, node: Struct_node):
        """Visita una declaración de estructura"""
        struct_info = {
            "type": "struct",
            "fields": {},
        }
        
        # Registra los campos
        if node.field_list:
            for field in node.field_list:
                if hasattr(field, 'accept'):
                    field.accept(self)
                elif isinstance(field, Field_node):
                    field_type = {
                        "data_type": field.type,
                        "is_array": field.Array_size_node is not None,
                    }
                    struct_info["fields"][field.ID] = field_type
        
        self.structs[node.ID] = struct_info
        self.declare_symbol(node.ID, struct_info)
    
    def visit_Var_node(self, node: Var_node):
        """Visita una declaración de variable"""
        # Verifica que el tipo exista
        if isinstance(node.type, str):
            if node.type not in ["int", "float", "char", "bool", "void"] and node.type not in self.structs:
                self.errors.append(f"Error: Tipo '{node.type}' no definido")
        
        var_info = {
            "type": "variable",
            "data_type": node.type,
            "is_array": node.Var_suffix_node is not None,
        }
        
        self.declare_symbol(node.ID, var_info)
        
        # Valida inicialización si existe
        if node.init and hasattr(node.init, 'accept'):
            node.init.accept(self)
    
    def visit_Assign_node(self, node: Assign_node):
        """Visita una asignación"""
        # Valida que la variable exista
        if isinstance(node.Lvalue_node, Lvalue_node):
            symbol = self.lookup_symbol(node.Lvalue_node.ID)
            if symbol is None:
                self.errors.append(f"Error: Variable '{node.Lvalue_node.ID}' no declarada")
        
        # Valida la expresión
        if node.expr_node and hasattr(node.expr_node, 'accept'):
            node.expr_node.accept(self)
    
    def visit_Call_node(self, node: Call_node):
        """Visita una llamada a función"""
        func = self.lookup_symbol(node.ID)
        if func is None or func.get("type") != "function":
            self.errors.append(f"Error: Función '{node.ID}' no declarada")
        
        # Valida argumentos
        if node.args:
            for arg in node.args:
                if hasattr(arg, 'accept'):
                    arg.accept(self)
    
    def visit_If_node(self, node: If_node):
        """Visita una estructura if"""
        # Valida condición
        if node.condition and hasattr(node.condition, 'accept'):
            node.condition.accept(self)
        
        # Valida bloques
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
        
        # Valida elif/else
        if node.elif_opt:
            if isinstance(node.elif_opt, list):
                for elif_node in node.elif_opt:
                    if hasattr(elif_node, 'accept'):
                        elif_node.accept(self)
            elif hasattr(node.elif_opt, 'accept'):
                node.elif_opt.accept(self)
    
    def visit_Elif_node(self, node: Elif_node):
        """Visita un elif"""
        if node.condition and hasattr(node.condition, 'accept'):
            node.condition.accept(self)
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
        if node.elif_opt and hasattr(node.elif_opt, 'accept'):
            node.elif_opt.accept(self)
    
    def visit_Else_node(self, node: Else_node):
        """Visita un else"""
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
    
    def visit_While_node(self, node: While_node):
        """Visita un while"""
        if node.condition and hasattr(node.condition, 'accept'):
            node.condition.accept(self)
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
    
    def visit_For_node(self, node: For_node):
        """Visita un for"""
        self.push_scope()  # Crea scope para variables locales del for
        
        if node.init and hasattr(node.init, 'accept'):
            node.init.accept(self)
        if node.condition and hasattr(node.condition, 'accept'):
            node.condition.accept(self)
        if node.update:
            if isinstance(node.update, list):
                for stmt in node.update:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.update, 'accept'):
                node.update.accept(self)
        
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
        
        self.pop_scope()
    
    def visit_Do_while_node(self, node: Do_while_node):
        """Visita un do-while"""
        if node.block:
            if isinstance(node.block, list):
                for stmt in node.block:
                    if hasattr(stmt, 'accept'):
                        stmt.accept(self)
            elif hasattr(node.block, 'accept'):
                node.block.accept(self)
        if node.condition and hasattr(node.condition, 'accept'):
            node.condition.accept(self)
    
    def visit_Return_node(self, node: Return_node):
        """Visita un return"""
        if node.expr_opt and hasattr(node.expr_opt, 'accept'):
            node.expr_opt.accept(self)
    
    def visit_Or_node(self, node: Or_node):
        """Visita una operación OR"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_And_node(self, node: And_node):
        """Visita una operación AND"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_Equality_node(self, node: Equality_node):
        """Visita un operador de igualdad"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_Relational_node(self, node: Relational_node):
        """Visita un operador relacional"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_Additive_node(self, node: Additive_node):
        """Visita un operador aditivo"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_Term_node(self, node: Term_node):
        """Visita un término"""
        if node.left_expr and hasattr(node.left_expr, 'accept'):
            node.left_expr.accept(self)
        if node.right_expr and hasattr(node.right_expr, 'accept'):
            node.right_expr.accept(self)
    
    def visit_Unary_node(self, node: Unary_node):
        """Visita un operador unario"""
        if node.expr and hasattr(node.expr, 'accept'):
            node.expr.accept(self)
    
    def visit_Postfix_node(self, node: Postfix_node):
        """Visita un postfix"""
        if node.primary and hasattr(node.primary, 'accept'):
            node.primary.accept(self)
    
    def visit_Lvalue_node(self, node: Lvalue_node):
        """Visita un lvalue"""
        symbol = self.lookup_symbol(node.ID)
        if symbol is None:
            self.errors.append(f"Error: Variable '{node.ID}' no declarada")
    
    def visit_Break_node(self, node):
        """Visita un break"""
        pass
    
    def visit_Continue_node(self, node):
        """Visita un continue"""
        pass
    
    def visit_Var_decl_node(self, node: Var_decl_node):
        """Visita una declaración de variable inline"""
        var_info = {
            "type": "variable",
            "data_type": node.type,
        }
        self.declare_symbol(node.ID, var_info)
        
        if node.init_opt and hasattr(node.init_opt, 'accept'):
            node.init_opt.accept(self)
    
    def generic_visit(self, node):
        """Visitante genérico para nodos no reconocidos"""
        pass
