from .ast_nodes import *

class CodeGenerator:

    def __init__(self):
        self.code = []
        self.data = []
        self.symbol_table = {}
        self.allocated_registers = set()  # Registros actualmente en uso
        self.parameter_registers = set()  # Registros que contienen parámetros (NO se deben liberar)
        self.label_counter = 0
        self.loop_stack = []
        self.current_function = None  # Almacena el nombre de la función actual

    def visit_And_node(self, node):
        # Cortocircuito: si el primero es falso, no evalúa el segundo
        end_label = self.generate_label()
        r1 = node.left_expr.accept(self)
        self.emit("JZ", end_label)
        r2 = node.right_expr.accept(self)
        self.emit("AND", f"R{r1}", f"R{r2}")
        self.emit_label(end_label)
        self.free_register(r2)
        return r1

    def visit_Or_node(self, node):
        # Cortocircuito: si el primero es verdadero, no evalúa el segundo
        end_label = self.generate_label()
        r1 = node.left_expr.accept(self)
        self.emit("JNZ", end_label)
        r2 = node.right_expr.accept(self)
        self.emit("OR", f"R{r1}", f"R{r2}")
        self.emit_label(end_label)
        self.free_register(r2)
        return r1

    def visit_Unary_node(self, node):
        # Solo se implementa NOT y cambio de signo
        if node.op == '!':
            r = node.expr.accept(self)
            self.emit("NOT", f"R{r}")
            return r
        elif node.op == '-':
            r = node.expr.accept(self)
            self.emit("NEG", f"R{r}")
            return r
        else:
            raise Exception(f"Operador unario no soportado: {node.op}")

    def visit_Struct_node(self, node):
        # No se genera código para definiciones de estructuras
        pass

    def generic_visit(self, node):
        raise Exception(f"No se implementó visit_{node.__class__.__name__} en CodeGenerator")

    # ========================
    # UTILIDADES
    # ========================

    def allocate_register(self):
        # Buscar el primer registro disponible en el rango R1-R15 (R0 está reservado para SP)
        for reg in range(1, 16):
            if reg not in self.allocated_registers:
                self.allocated_registers.add(reg)
                return reg
        # raise Exception(f"Error: No hay registros disponibles. Máximo 15 registros (R1-R15). Se agotaron todos los registros.")

    def free_register(self, reg=None):
        """Libera un registro específico o el más recientemente asignado"""
        # NO liberar registros que contienen parámetros
        if reg is not None and reg in self.allocated_registers and reg not in self.parameter_registers:
            self.allocated_registers.remove(reg)

    def generate_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def _qualify_variable_name(self, var_name):
        """Genera un nombre cualificado para una variable dentro de una función"""
        if self.current_function and self.current_function != "main":
            return f"{self.current_function}_{var_name}"
        return var_name

    def emit(self, instr, *args):
        if args:
            self.code.append(f"{instr} {', '.join(map(str, args))}")
        else:
            self.code.append(instr)

    def emit_label(self, label):
        self.code.append(f"{label}:")

    def emit_data(self, instr, *args):
        if args:
            self.data.append(f"{instr} {', '.join(map(str, args))}")
        else:
            self.data.append(instr)

    def emit_data_label(self, label):
        self.data.append(f"{label}:")

    def get_expression_type(self, node):
        """Determina el tipo de una expresión"""
        if isinstance(node, Number_node):
            # Si es un número con punto decimal, es float
            if isinstance(node.value, float) or '.' in str(node.value):
                return "float"
            return "int"
        elif isinstance(node, Lvalue_node):
            # Buscar en la tabla de símbolos
            if node.ID in self.symbol_table:
                return self.symbol_table[node.ID].get("type", "int")
            return "int"
        elif isinstance(node, Var_node):
            # Buscar en la tabla de símbolos
            if node.ID in self.symbol_table:
                return self.symbol_table[node.ID].get("type", "int")
            return "int"
        elif isinstance(node, (Additive_node, Term_node, Relational_node, Equality_node)):
            # Para operaciones binarias, si cualquiera de los operandos es float, el resultado es float
            left_type = self.get_expression_type(node.left_expr)
            right_type = self.get_expression_type(node.right_expr)
            if left_type == "float" or right_type == "float":
                return "float"
            return "int"
        elif isinstance(node, Call_node):
            # Buscar el tipo de retorno de la función
            if node.ID in self.symbol_table:
                return self.symbol_table[node.ID].get("type", "int")
            return "int"
        else:
            return "int"

    def generate(self, ast_root, symbol_table):
        self.code = []
        self.data = []
        self.symbol_table = symbol_table
        self.allocated_registers = set()
        self.parameter_registers = set()
        self.label_counter = 0

        if isinstance(ast_root, list):
            for node in ast_root:
                node.accept(self)
        else:
            ast_root.accept(self)

        # Combinar datos y código
        if self.data:
            result = ["JMP func_main"] + self.data + [""] + self.code
        else:
            result = self.code
        return "\n".join(result)

    # ========================
    # VARIABLES
    # ========================

    def visit_Var_node(self, node):

        info = self.symbol_table[node.ID]
        qualified_name = self._qualify_variable_name(node.ID)

        if node.Var_suffix_node:
            if isinstance(node.Var_suffix_node, Array_suffix_node):
                self.emit_data_label(qualified_name)
                self.emit_data(".SIZE", self.symbol_table[node.ID].get("array_size"))
            elif isinstance(node.Var_suffix_node, Matriz_suffix_node):
                self.emit_data_label(qualified_name)
                self.emit_data(".SIZE", self.symbol_table[node.ID].get("array_size"))
        elif (info["type"] not in ("int", "struct", "float", "void", "string", "char", "bool", "func")):
            

            for field in self.symbol_table[info["type"]]["field_list"]:
                self.emit_data_label(f"{qualified_name}_{field}")
                self.emit_data(".SIZE", self.symbol_table[field]["array_size"] if self.symbol_table[field].get("array_size") else 1)
        else:
            
            self.emit_data_label(qualified_name)
            self.emit_data(".SIZE",1)
        if node.init:
            reg = node.init.accept(self)
            self.emit("STORE", f"R{reg}", qualified_name)
            self.free_register(reg)

    def visit_Var_decl_node(self, node):
        """Visita una declaración de variable inline (usada en for)"""
        info = self.symbol_table[node.ID]
        qualified_name = self._qualify_variable_name(node.ID)
        
        # Reservar espacio para la variable
        self.emit_data_label(qualified_name)
        self.emit_data(".SIZE", 1)
        
        # Si hay inicialización, generar código para asignarla
        if node.init_opt:
            reg = node.init_opt.accept(self)
            self.emit("STORE", f"R{reg}", qualified_name)
            self.free_register(reg)

    def _calculate_array_address(self, lvalue_node):
        """
        Calcula la dirección de un elemento de array.
        Para matrices multidimensionales, usa la fórmula: fila * num_columnas + columna
        Retorna el registro que contiene la dirección calculada.
        Nota: Esta función mantiene todos los registros asignados sin liberar.
        """
        base_reg = self.allocate_register()
        qualified_name = self._qualify_variable_name(lvalue_node.ID)
        self.emit("LEA", f"R{base_reg}", qualified_name)
        
        # Obtener información de dimensiones del símbolo
        array_info = self.symbol_table.get(lvalue_node.ID, {})
        array_dimensions = array_info.get("array_dimensions")
        
        # Procesar cada índice (para arrays multidimensionales)
        indices = []
        for index_access in lvalue_node.lvalue_tail:
            if index_access[0] == '[':
                # index_access es ['[', expr, ']']
                index_expr = index_access[1]
                index_reg = index_expr.accept(self)
                indices.append(index_reg)
        
        # Calcular el offset según las dimensiones
        if array_dimensions and len(array_dimensions) == 2 and len(indices) == 2:
            # Array 2D: offset = fila * num_columnas + columna
            num_cols = array_dimensions[1]
            fila_reg = indices[0]
            col_reg = indices[1]
            
            # Usar un registro temporal para calcular el offset sin modificar los originales
            offset_reg = self.allocate_register()
            self.emit("CPY", f"R{offset_reg}", f"R{fila_reg}")  # offset = fila
            num_cols_reg = self.allocate_register()  # Asignar un registro para num_cols
            self.emit("LOADV", f"R{num_cols_reg}", num_cols)
            self.emit("MUL", f"R{offset_reg}", f"R{num_cols_reg}")  # offset = fila * num_cols
            self.emit("ADD", f"R{offset_reg}", f"R{col_reg}")  # offset += col
            
            # Sumar el offset a la dirección base
            self.emit("ADD", f"R{base_reg}", f"R{offset_reg}")
            
            # Liberar todos los registros
            self.free_register(fila_reg)
            self.free_register(col_reg)
            self.free_register(offset_reg)
            self.free_register(num_cols_reg)
        else:
            # Array 1D o fallback: simplemente sumar todos los índices
            for index_reg in indices:
                self.emit("ADD", f"R{base_reg}", f"R{index_reg}")
                self.free_register(index_reg)
        
        return base_reg

    def _is_array_access(self, lvalue_node):
        """Verifica si un lvalue accede a un array"""
        if lvalue_node.lvalue_tail and len(lvalue_node.lvalue_tail) > 0:
            return lvalue_node.lvalue_tail[0][0] == '['
        return False

    def visit_Lvalue_node(self, node):
        info = self.symbol_table[node.ID]
        qualified_name = self._qualify_variable_name(node.ID)

        # El parámetro ya esta cargado en registro
        if info.get("param") == True and "reg" in info:
            return info["reg"]

        # Acceso a array - retorna el VALOR del elemento
        if self._is_array_access(node):
            addr_reg = self._calculate_array_address(node)
            value_reg = self.allocate_register()
            self.emit("LOADI", f"R{value_reg}", f"R{addr_reg}")
            self.free_register(addr_reg)  # Liberar el registro de dirección
            return value_reg  # El llamador debe liberar este registro cuando termine

        # Acceso a campo de estructura
        if (info["type"] not in ("int", "struct", "float", "void", "string", "char", "bool", "func")):
            field_name = f"{qualified_name}_{node.lvalue_tail[0][1]}"
            reg = self.allocate_register()
            self.emit("LOAD", f"R{reg}", field_name)
            return reg

        # Variable normal en memoria - retorna el VALOR
        reg = self.allocate_register()
        self.emit("LOAD", f"R{reg}", qualified_name)
        return reg

    def visit_Assign_node(self, node):
        reg = node.expr_node.accept(self)
        info = self.symbol_table[node.Lvalue_node.ID]
        lvalue = node.Lvalue_node
        qualified_name = self._qualify_variable_name(lvalue.ID)

        # Asignación a un elemento de array
        if self._is_array_access(lvalue):
            addr_reg = self._calculate_array_address(lvalue)
            self.emit("STOREI", f"R{reg}", f"R{addr_reg}")
            self.free_register(reg)  # Liberar el valor
            self.free_register(addr_reg)  # Liberar la dirección
            return

        # Asignación a campo de estructura
        if (info["type"] not in ("int", "struct", "float", "void", "string", "char", "bool", "func")):
            field_name = f"{qualified_name}_{lvalue.lvalue_tail[0][1]}"
            self.emit("STORE", f"R{reg}", field_name)
            self.free_register(reg)
            return

        # Asignación a variable normal
        # Si es un parámetro, copiar al registro del parámetro
        if info.get("param") == True and "reg" in info:
            param_reg = info["reg"]
            self.emit("CPY", f"R{param_reg}", f"R{reg}")
        else:
            # Si es una variable normal, almacenar en memoria
            self.emit("STORE", f"R{reg}", qualified_name)
        
        self.free_register(reg)

    # ========================
    # LITERALES
    # ========================

    def visit_Number_node(self, node):
        reg = self.allocate_register()
        self.emit("LOADV", f"R{reg}", node.value)
        return reg

    # ========================
    # EXPRESIONES
    # ========================

    def visit_Additive_node(self, node):
        r1 = node.left_expr.accept(self)
        r2 = node.right_expr.accept(self)

        # Determinar si es operación con flotantes
        expr_type = self.get_expression_type(node)
        
        if node.symbol == '+':
            if expr_type == "float":
                self.emit("ADDF", f"R{r1}", f"R{r2}")
            else:
                self.emit("ADD", f"R{r1}", f"R{r2}")
        else:  # '-'
            if expr_type == "float":
                self.emit("SUBF", f"R{r1}", f"R{r2}")
            else:
                self.emit("SUB", f"R{r1}", f"R{r2}")

        self.free_register(r2)
        return r1

    def visit_Term_node(self, node):
        r1 = node.left_expr.accept(self)
        r2 = node.right_expr.accept(self)

        # Determinar si es operación con flotantes
        expr_type = self.get_expression_type(node)

        if node.symbol == '*':
            if expr_type == "float":
                self.emit("MULF", f"R{r1}", f"R{r2}")
            else:
                self.emit("MUL", f"R{r1}", f"R{r2}")
        elif node.symbol == '/':
            if expr_type == "float":
                self.emit("DIVF", f"R{r1}", f"R{r2}")
            else:
                self.emit("DIV", f"R{r1}", f"R{r2}")
        else:  # '%'
            if expr_type == "float":
                self.emit("MODF", f"R{r1}", f"R{r2}")
            else:
                self.emit("MOD", f"R{r1}", f"R{r2}")

        self.free_register(r2)
        return r1

    def visit_Relational_node(self, node):
        r1 = node.left_expr.accept(self)
        r2 = node.right_expr.accept(self)

        # Determinar si es operación con flotantes
        expr_type = self.get_expression_type(node)
        
        if expr_type == "float":
            self.emit("CMPF", f"R{r1}", f"R{r2}")
        else:
            self.emit("CMP", f"R{r1}", f"R{r2}")
        
        self.free_register(r2)
        self.free_register(r1)
        return r1

    def visit_Equality_node(self, node):
        r1 = node.left_expr.accept(self)
        r2 = node.right_expr.accept(self)

        # Determinar si es operación con flotantes
        expr_type = self.get_expression_type(node)
        
        if expr_type == "float":
            self.emit("CMPF", f"R{r1}", f"R{r2}")
        else:
            self.emit("CMP", f"R{r1}", f"R{r2}")
        
        self.free_register(r2)
        self.free_register(r1)
        return r1

    # ========================
    # CONTROL DE FLUJO
    # ========================


    def visit_If_node(self, node):
        end_label = self.generate_label()
        next_label = self.generate_label()  # Para elif o else

        cond = node.condition
        salto_emitido = False
        # Soporte para condiciones relacionales y de igualdad
        if isinstance(cond, Relational_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")

            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '<':
                self.emit("JZ", next_label)
                self.emit("JP", next_label)
                salto_emitido = True
            elif cond.symbol == '>':
                self.emit("JZ", next_label)
                self.emit("JN", next_label)
                salto_emitido = True
            elif cond.symbol == '<=':
                self.emit("JP", next_label)
                salto_emitido = True
            elif cond.symbol == '>=':
                self.emit("JN", next_label)
                salto_emitido = True
        elif isinstance(cond, Equality_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")

            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '==':
                self.emit("JNZ", next_label)
                salto_emitido = True
            elif cond.symbol == '!=':
                self.emit("JZ", next_label)
                salto_emitido = True
        if not salto_emitido:
            cond_reg = cond.accept(self)
            self.emit("JZ", next_label)

        for stmt in node.block:
            stmt.accept(self)

        self.emit("JMP", end_label)
        self.emit_label(next_label)

        if isinstance(node.elif_opt, Elif_node):
            node.elif_opt.end_label = end_label  # Pasar etiqueta de fin
            node.elif_opt.accept(self)
        elif isinstance(node.elif_opt, Else_node):
            node.elif_opt.end_label = end_label
            node.elif_opt.accept(self)

        self.emit_label(end_label)

    def visit_Elif_node(self, node):
        # end_label es pasado desde el if o elif anterior y guardado en el nodo
        next_label = self.generate_label()
        cond = node.condition
        salto_emitido = False
        if isinstance(cond, Relational_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '<':
                self.emit("JZ", next_label)
                self.emit("JP", next_label)
                salto_emitido = True
            elif cond.symbol == '>':
                self.emit("JZ", next_label)
                self.emit("JN", next_label)
                salto_emitido = True
            elif cond.symbol == '<=':
                self.emit("JP", next_label)
                salto_emitido = True
            elif cond.symbol == '>=':
                self.emit("JN", next_label)
                salto_emitido = True
        elif isinstance(cond, Equality_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)

            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '==':
                self.emit("JNZ", next_label)
                salto_emitido = True
            elif cond.symbol == '!=':
                self.emit("JZ", next_label)
                salto_emitido = True
        if not salto_emitido:
            cond_reg = cond.accept(self)
            self.emit("JZ", next_label)

        for stmt in node.block:
            stmt.accept(self)

        self.emit("JMP", node.end_label)
        self.emit_label(next_label)

        if isinstance(node.elif_opt, Elif_node):
            node.elif_opt.end_label = node.end_label  # Pasar etiqueta de fin
            node.elif_opt.accept(self)
        elif isinstance(node.elif_opt, Else_node):
            node.elif_opt.end_label = node.end_label
            node.elif_opt.accept(self)


    def visit_Else_node(self, node):
        # end_label es pasado desde el if o elif anterior y guardado en el nodo
        for stmt in node.block:
            stmt.accept(self)
        self.emit("JMP", node.end_label)
    
    def visit_While_node(self, node):
        start = self.generate_label()
        end = self.generate_label()

        self.loop_stack.append((start, end))

        self.emit_label(start)

        # Soporte para condiciones relacionales
        cond = node.condition
        salto_emitido = False
        if isinstance(cond, Relational_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            # Saltos según el símbolo
            if cond.symbol == '<':
                self.emit("JZ", end)  
                self.emit("JP", end)  
                salto_emitido = True
            elif cond.symbol == '>':
                self.emit("JZ", end)    
                self.emit("JN", end)   
                salto_emitido = True
            elif cond.symbol == '<=':
                self.emit("JP", end)    
                salto_emitido = True
            elif cond.symbol == '>=':
                self.emit("JN", end)  
                salto_emitido = True
        elif isinstance(cond, Equality_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)

            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '==':
                self.emit("JNZ", end)   
                salto_emitido = True
            elif cond.symbol == '!=':
                self.emit("JZ", end)    
                salto_emitido = True
        if not salto_emitido:
            # Condición booleana normal
            cond_reg = cond.accept(self)
            self.emit("JZ", end)

        for stmt in node.block:
            stmt.accept(self)

        self.emit("JMP", start)
        self.emit_label(end)

        self.loop_stack.pop()


    def visit_For_node(self, node):
        # Inicialización del for
        if node.init:
            node.init.accept(self)
        
        start = self.generate_label()
        update = self.generate_label()
        end = self.generate_label()

        self.loop_stack.append((update, end))

        # Etiqueta de inicio del bucle
        self.emit_label(start)

        # Evaluación de la condición
        cond = node.condition
        salto_emitido = False
        if cond:  # Si hay condición (else se ejecuta siempre)
            if isinstance(cond, Relational_node):
                r1 = cond.left_expr.accept(self)
                r2 = cond.right_expr.accept(self)
                expr_type = self.get_expression_type(node)
        
                if expr_type == "float":
                    self.emit("CMPF", f"R{r1}", f"R{r2}")
                else:
                    self.emit("CMP", f"R{r1}", f"R{r2}")
                self.free_register(r2)
                self.free_register(r1)
                if cond.symbol == '<':
                    self.emit("JZ", end)
                    self.emit("JP", end)
                    salto_emitido = True
                elif cond.symbol == '>':
                    self.emit("JZ", end)
                    self.emit("JN", end)
                    salto_emitido = True
                elif cond.symbol == '<=':
                    self.emit("JP", end)
                    salto_emitido = True
                elif cond.symbol == '>=':
                    self.emit("JN", end)
                    salto_emitido = True
            elif isinstance(cond, Equality_node):
                r1 = cond.left_expr.accept(self)
                r2 = cond.right_expr.accept(self)
                expr_type = self.get_expression_type(node)
        
                if expr_type == "float":
                    self.emit("CMPF", f"R{r1}", f"R{r2}")
                else:
                    self.emit("CMP", f"R{r1}", f"R{r2}")
                self.free_register(r2)
                self.free_register(r1)
                if cond.symbol == '==':
                    self.emit("JNZ", end)
                    salto_emitido = True
                elif cond.symbol == '!=':
                    self.emit("JZ", end)
                    salto_emitido = True
            if not salto_emitido:
                cond_reg = cond.accept(self)
                self.emit("JZ", end)

        # Cuerpo del bucle
        for stmt in node.block:
            stmt.accept(self)

        # Etiqueta de actualización (para continue)
        self.emit_label(update)

        # Ejecución de la actualización
        if node.update:
            if isinstance(node.update, list):
                for update_stmt in node.update:
                    update_stmt.accept(self)
            else:
                node.update.accept(self)

        # Salto de vuelta al inicio
        self.emit("JMP", start)
        self.emit_label(end)

        self.loop_stack.pop()

    def visit_Do_while_node(self, node):
        start = self.generate_label()
        condition_label = self.generate_label()
        end = self.generate_label()

        # Para continue en do-while, saltamos a la evaluación de la condición
        self.loop_stack.append((condition_label, end))

        # Etiqueta de inicio del bucle
        self.emit_label(start)

        # Cuerpo del bucle
        for stmt in node.block:
            stmt.accept(self)

        # Etiqueta para continue (evaluar la condición)
        self.emit_label(condition_label)

        # Evaluación de la condición
        cond = node.condition
        if isinstance(cond, Relational_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            # Si la condición es verdadera, volvemos al inicio
            if cond.symbol == '<':
                self.emit("JN", start)  # Si negativo (verdadera)
            elif cond.symbol == '>':
                self.emit("JP", start)  # Si positivo (verdadera)
            elif cond.symbol == '<=':
                # Si A <= B: salta a start si NO positivo
                self.emit("JP", end)     # Si positivo, va a end
                self.emit("JMP", start)  # Si no positivo, vuelve a start
            elif cond.symbol == '>=':
                # Si A >= B: salta a start si NO negativo
                self.emit("JN", end)     # Si negativo, va a end
                self.emit("JMP", start)  # Si no negativo, vuelve a start
        elif isinstance(cond, Equality_node):
            r1 = cond.left_expr.accept(self)
            r2 = cond.right_expr.accept(self)
            expr_type = self.get_expression_type(node)
        
            if expr_type == "float":
                self.emit("CMPF", f"R{r1}", f"R{r2}")
            else:
                self.emit("CMP", f"R{r1}", f"R{r2}")
            self.free_register(r2)
            self.free_register(r1)
            if cond.symbol == '==':
                self.emit("JZ", start)   # Si igual, vuelve
            elif cond.symbol == '!=':
                self.emit("JNZ", start)  # Si no igual, vuelve
        else:
            # Condición booleana normal
            cond_reg = cond.accept(self)
            self.emit("JNZ", start)

        self.emit_label(end)
        self.loop_stack.pop()

    def visit_Break_node(self, node):
        _, end = self.loop_stack[-1]
        self.emit("JMP", end)

    def visit_Continue_node(self, node):
        start, _ = self.loop_stack[-1]
        self.emit("JMP", start)

    # ========================
    # FUNCIONES
    # ========================
    def liberar_registros_parametros(self):
        """Libera todos los registros que contienen parámetros"""
        for reg in self.parameter_registers:
            if reg in self.allocated_registers:
                self.allocated_registers.remove(reg)
        self.parameter_registers.clear()
    
    def visit_Func_node(self, node):
        # Limpiar registros de parámetro del context anterior
        self.liberar_registros_parametros()
        self.parameter_registers.clear()
        
        # Establecer la función actual para generar labels cualificados
        self.current_function = node.ID
        
        self.emit_label(f"func_{node.ID}")

        # Registrar parámetros en la tabla de símbolos
        if node.params:
            if(node.ID != "main"):
                self.emit("POP", "R0")  # Guardar SP para funciones no main

            for param in reversed(node.params):
                reg = self.allocate_register()
                self.emit("POP", f"R{reg}")
                self.symbol_table[param.ID]["param"] = True
                self.symbol_table[param.ID]["reg"] = reg
                self.parameter_registers.add(reg)  # Marcar como registro de parámetro

        for stmt in node.Block_node:
            stmt.accept(self)
        
        # Limpiar función actual al salir
        self.current_function = None

        

    def visit_Call_node(self, node):
        for arg in node.args:
            reg = arg.accept(self)   # ya emite LOADV, LOAD, LOADI, ADD, etc. según el tipo
            self.emit("PUSH", f"R{reg}")
            self.free_register(reg)

        self.emit("CALL", f"func_{node.ID}")
        reg = self.allocate_register()
        return reg

    def visit_Return_node(self, node):
        if node.expr_opt:
            reg = node.expr_opt.accept(self)
            self.emit("CPY", "R1", f"R{reg}")  # Copiar el valor de retorno a R1
            self.free_register(reg)
        self.emit("PUSH", "R0")  # Restaurar SP para main
        self.emit("RET")