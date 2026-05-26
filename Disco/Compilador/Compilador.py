"""
Compilador Principal - Integra todos los pasos de compilación
Flujo: Léxico → Sintáctico → Semántico → Generación de Código → Ensamblador
"""

try:
    from .lexical_analyzer import LexicalAnalyzer
    from .sintactic_analyzer import parse
    from .semantic_analyzer import SemanticAnalyzer
    from .code_generator import CodeGenerator
    from .Assembler import assemble_program
    from .Preprocessor import preprocess_program
except ImportError:
    from lexical_analyzer import LexicalAnalyzer
    from sintactic_analyzer import parse
    from semantic_analyzer import SemanticAnalyzer
    from code_generator import CodeGenerator
    from Assembler import assemble_program
    from Preprocessor import preprocess_program
import sys

class Compiler:
    """Compilador completo"""
    
    def __init__(self):
        self.source_code = None
        self.tokens = None
        self.ast = None
        self.symbol_table = {}
        self.semantic_ok = False
        self.ir_code = None
        self.binary_code = None
        self.errors = []
    
    def get_preprocessed_code(self):
        return self.source_code
    
    def get_assembly_code(self):
        return self.ir_code
    
    def get_reloc_code(self):
        return self.binary_code
    
    def get_errors(self) -> list:
        return self.errors
    
    def compile_file(self, source_file: str) -> bool:
        """Compila un archivo completo"""
        with open(source_file, 'r', encoding='utf-8') as f:
                self.source_code = f.read()

        return self.compile(self.source_code)
    
    def compile(self, source_code: str) -> bool:
        """Compila un archivo completo"""
        try:
            self.source_code = source_code

            # 2. Preprocesamiento
            print("=" * 60)
            print("FASE 1: PREPROCESAMIENTO")
            print("=" * 60)
            self.source_code = preprocess_program(self.source_code)
            
            # 3. Análisis Léxico
            print("=" * 60)
            print("FASE 2: ANÁLISIS LÉXICO")
            print("=" * 60)
            if not self._lexical_analysis():
                return False
            
            # 3. Análisis Sintáctico
            print("\n" + "=" * 60)
            print("FASE 3: ANÁLISIS SINTÁCTICO")
            print("=" * 60)
            if not self._syntactic_analysis():
                return False
            
            # 4. Análisis Semántico
            print("\n" + "=" * 60)
            print("FASE 4: ANÁLISIS SEMÁNTICO")
            print("=" * 60)
            if not self._semantic_analysis():
                return False
            
            # 5. Generación de Código
            print("\n" + "=" * 60)
            print("FASE 5: GENERACIÓN DE CÓDIGO")
            print("=" * 60)
            if not self._code_generation():
                return False
            
            # 6. Ensamblaje
            print("\n" + "=" * 60)
            print("FASE 6: ENSAMBLAJE")
            print("=" * 60)
            if not self._assembly():
                return False
            
            print("\nCompilación exitosa")
            return True
            
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
    
    def _lexical_analysis(self) -> bool:
        """Realiza análisis léxico"""
        lex_analyzer = LexicalAnalyzer()
        self.tokens, errors = lex_analyzer.tokenize(self.source_code)
        
        if errors:
            print("Errores léxicos encontrados:")
            for error in errors:
                print(f"  Línea {error['line']}: {error['message']}")
            self.errors.extend(errors)
            return False
        
        print(f"{len(self.tokens)} tokens generados")
        return True
    
    def _syntactic_analysis(self) -> bool:
        """Realiza análisis sintáctico"""
        
        self.ast, self.symbol_table, errs= parse(self.source_code)
        self.errors.extend(errs)
        if self.ast is None:
            print("Error: No se pudo generar el AST")
            return False
        print("Árbol sintáctico generado exitosamente")
        return True
    
    def _semantic_analysis(self) -> bool:
        """Realiza análisis semántico"""
        semantic_analyzer = SemanticAnalyzer()
        
        self.semantic_ok = semantic_analyzer.analyze(self.ast, self.symbol_table)
        
        
        if semantic_analyzer.errors:
            print("Errores semánticos encontrados:")
            for error in semantic_analyzer.errors:
                print(f"  {error}")
            self.errors.extend(semantic_analyzer.errors)
            return False
        
        if self.semantic_ok:
            print("Análisis semántico correcto")
            print(f"  Funciones: {list(semantic_analyzer.functions.keys())}")
            print(f"  Estructuras: {list(semantic_analyzer.structs.keys())}")
        else:
            return False
        
        return True
    
    def _code_generation(self) -> bool:
        """Realiza generación de código"""
        code_gen = CodeGenerator()
        
        try:
            self.ir_code = code_gen.generate(self.ast, self.symbol_table)
            print("Código intermedio generado:")
            print("-" * 60)
            for i, line in enumerate(self.ir_code.split('\n'), 1):
                print(f"{i:3}: {line}")
            print("-" * 60)
            
            return True
        except Exception as e:
            print(f"Error en generación de código: {e}")
            return False
    
    def _assembly(self) -> bool:
        """Realiza ensamblaje"""
        try:
            self.binary_code = assemble_program(self.ir_code)
            
            print("Código de máquina generado:")
            print("-" * 60)
            for i, line in enumerate(self.binary_code.split('\n')[:20], 1):
                print(f"{i:3}: {line}")
            if len(self.binary_code.split('\n')) > 20:
                print(f"... ({len(self.binary_code.split(chr(10)))} líneas totales)")
            print("-" * 60)
            
            return True
        except Exception as e:
            print(f"Error en ensamblaje: {e}")
            return False
    
    def save_binary(self, output_file: str):
        """Guarda el código binario en un archivo"""
        if self.binary_code:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.binary_code + '\n')
            print(f"Código binario guardado en: {output_file}")

    def clear(self):
        """Reinicia el estado del compilador para una nueva compilación"""
        self.source_code = None
        self.tokens = None
        self.ast = None
        self.symbol_table = {}
        self.semantic_ok = False
        self.ir_code = None
        self.binary_code = None
        self.errors = []

def main():
    if len(sys.argv) not in [2, 3]:
        print("Uso: python Compilador.py <archivo_entrada> [archivo_salida]")
        print("  archivo_entrada: código fuente (*.c o similar)")
        print("  archivo_salida: ejecutable binario (opcional)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else "programa.bin"
    
    compiler = Compiler()
    
    if compiler.compile_file(input_file):
        compiler.save_binary(output_file)
        sys.exit(0)
    else:
        print("\nCompilación fallida")
        sys.exit(1)


if __name__ == "__main__":
    main()
