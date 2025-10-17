class CodeGenerator:
    def __init__(self):
        self.includes = set()
        self.variables = {}
        self.functions = {}
        
    def generate_code(self, blocks, connections=None):
        """Генерирует C++ код из списка блоков с учетом связей"""
        self.includes.clear()
        self.variables.clear()
        self.functions.clear()
        
        # Анализируем блоки и собираем информацию
        self.analyze_blocks(blocks)
        
        # Генерируем код
        code_lines = []
        
        # Добавляем заголовки
        code_lines.append("#include <iostream>")
        code_lines.append("#include <string>")
        code_lines.append("#include <cmath>")  # Для математических функций
        code_lines.append("using namespace std;")
        code_lines.append("")
        
        # Добавляем дополнительные заголовки если нужно
        for include in sorted(self.includes):
            if include not in ["iostream", "string", "cmath"]:
                code_lines.append(f"#include <{include}>")
        
        if self.includes:
            code_lines.append("")
            
        # Генерируем функции
        for func_name, func_info in self.functions.items():
            code_lines.extend(self.generate_function(func_info))
            code_lines.append("")
            
        # Генерируем main функцию
        code_lines.append("int main() {")
        
        # Генерируем код внутри main с учетом связей
        main_code = self.generate_main_code(blocks, connections)
        for line in main_code:
            code_lines.append(f"    {line}")
            
        code_lines.append("    return 0;")
        code_lines.append("}")
        
        return "\n".join(code_lines)
        
    def analyze_blocks(self, blocks):
        """Анализирует блоки и собирает информацию о переменных и функциях"""
        for block in blocks:
            if block.block_type == "variable":
                # Переменная
                self.variables[block.var_name] = {
                    'type': block.var_type,
                    'value': block.var_value,
                    'is_expression': block.is_expression
                }
            elif block.block_type == "function" and block.function_name == "main":
                # Функция main
                self.functions["main"] = {
                    'is_main': True,
                    'body': []
                }
            elif block.block_type == "custom_function":
                # Кастомная функция
                self.functions[block.function_name] = {
                    'return_type': block.return_type,
                    'parameters': block.parameters,
                    'body_blocks': block.body_blocks,
                    'is_custom': True
                }
                
    def generate_function(self, func_info):
        """Генерирует код функции"""
        lines = []
        if func_info.get('is_main'):
            return []  # main уже обрабатывается отдельно
        elif func_info.get('is_custom'):
            # Кастомная функция
            return_type = func_info['return_type']
            func_name = list(self.functions.keys())[list(self.functions.values()).index(func_info)]
            parameters = func_info['parameters']
            
            # Сигнатура функции
            signature = f"{return_type} {func_name}({parameters}) {{"
            lines.append(signature)
            
            # Тело функции (пока пустое, будет заполнено блоками)
            lines.append("    // TODO: Add function body")
            
            # Добавляем return если не void
            if return_type != "void":
                lines.append("    // TODO: Add return statement")
            
            lines.append("}")
        else:
            signature = f"// Функция {func_info['name']} будет определена в библиотеке"
            lines.append(signature)
        return lines
        
    def generate_main_code(self, blocks, connections=None):
        """Генерирует код для main функции с учетом связей"""
        lines = []
        
        if connections is None:
            connections = {}
            
        # Сначала объявляем все переменные
        for var_name, var_info in self.variables.items():
            if var_info['is_expression']:
                # Для выражений просто присваиваем значение
                if var_info['type'] == 'string':
                    lines.append(f"{var_info['type']} {var_name} = \"{var_info['value']}\";")
                elif var_info['type'] == 'bool':
                    bool_value = "true" if var_info['value'].lower() in ['true', '1', 'yes'] else "false"
                    lines.append(f"{var_info['type']} {var_name} = {bool_value};")
                else:
                    lines.append(f"{var_info['type']} {var_name} = {var_info['value']};")
            else:
                # Для простых значений
                if var_info['type'] == 'string':
                    lines.append(f"{var_info['type']} {var_name} = \"{var_info['value']}\";")
                elif var_info['type'] == 'bool':
                    bool_value = "true" if var_info['value'].lower() in ['true', '1', 'yes'] else "false"
                    lines.append(f"{var_info['type']} {var_name} = {bool_value};")
                else:
                    lines.append(f"{var_info['type']} {var_name} = {var_info['value']};")
                
        if self.variables:
            lines.append("")
            
        # Генерируем код из блоков с учетом связей
        processed_blocks = set()
        
        # Обрабатываем блоки в порядке связей
        for source_block, target_block in connections.items():
            if source_block not in processed_blocks:
                block_code = self.generate_block_code(source_block)
                if block_code:
                    lines.extend(block_code)
                processed_blocks.add(source_block)
                
            if target_block not in processed_blocks:
                block_code = self.generate_block_code(target_block)
                if block_code:
                    lines.extend(block_code)
                processed_blocks.add(target_block)
        
        # Обрабатываем оставшиеся блоки
        for block in blocks:
            if block not in processed_blocks:
                block_code = self.generate_block_code(block)
                if block_code:
                    lines.extend(block_code)
                    
        return lines
        
    def generate_block_code(self, block):
        """Генерирует код для отдельного блока"""
        lines = []
        
        if block.block_type == "variable":
            # Переменная уже объявлена выше
            pass
            
        elif block.block_type == "operator":
            # Оператор
            if hasattr(block, 'operator') and hasattr(block, 'operand1') and hasattr(block, 'operand2'):
                # Определяем тип результата на основе оператора
                result_type = self.get_result_type(block.operator, block.operand1, block.operand2)
                
                if block.operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
                    # Логические операции
                    operation = f"bool {block.result_var} = ({block.operand1} {block.operator} {block.operand2});"
                else:
                    # Арифметические операции
                    operation = f"{result_type} {block.result_var} = {block.operand1} {block.operator} {block.operand2};"
                lines.append(operation)
                
        elif block.block_type == "function":
            # Функция
            if hasattr(block, 'function_name') and block.function_name != "main":
                params = []
                if block.param1:
                    params.append(block.param1)
                if block.param2:
                    params.append(block.param2)
                param_str = ", ".join(params) if params else ""
                
                # Определяем тип результата функции
                result_type = self.get_function_result_type(block.function_name)
                
                function_call = f"{result_type} {block.result_var} = {block.function_name}({param_str});"
                lines.append(function_call)
                
        elif block.block_type == "return":
            # Return блок
            if hasattr(block, 'is_void') and block.is_void:
                lines.append("return;")
            else:
                return_value = getattr(block, 'return_value', '0')
                lines.append(f"return {return_value};")
                
        elif block.block_type == "custom_function":
            # Кастомная функция уже обработана в analyze_blocks
            pass
                
        return lines
        
    def get_result_type(self, operator, operand1, operand2):
        """Определяет тип результата операции"""
        if operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
            return "bool"
        elif operator in ["+", "-", "*", "/", "%"]:
            # Простая эвристика - если есть float, то результат float
            if "float" in str(operand1) or "float" in str(operand2) or "." in str(operand1) or "." in str(operand2):
                return "float"
            else:
                return "int"
        return "int"
        
    def get_function_result_type(self, function_name):
        """Определяет тип результата функции"""
        function_types = {
            "max": "int",
            "min": "int", 
            "abs": "int",
            "sqrt": "double",
            "pow": "double",
            "sin": "double",
            "cos": "double",
            "tan": "double",
            "log": "double",
            "exp": "double",
            "floor": "double",
            "ceil": "double",
            "round": "double"
        }
        return function_types.get(function_name, "int")

class AdvancedCodeGenerator(CodeGenerator):
    """Расширенный генератор кода с поддержкой связей между блоками"""
    
    def __init__(self):
        super().__init__()
        self.block_connections = {}
        
    def analyze_block_connections(self, blocks):
        """Анализирует связи между блоками на основе их позиций"""
        # Сортируем блоки по Y координате (сверху вниз)
        sorted_blocks = sorted(blocks, key=lambda b: b.y)
        
        # Простая эвристика: блоки, расположенные близко друг к другу, связаны
        for i, block in enumerate(sorted_blocks):
            connections = []
            for j, other_block in enumerate(sorted_blocks):
                if i != j:
                    # Проверяем, находится ли блок ниже и близко по X
                    if (other_block.y > block.y and 
                        abs(other_block.x - block.x) < 200 and
                        other_block.y - block.y < 100):
                        connections.append(other_block)
            self.block_connections[block] = connections
            
    def generate_structured_code(self, blocks):
        """Генерирует структурированный код с учетом связей между блоками"""
        self.analyze_block_connections(blocks)
        
        # Генерируем базовый код
        base_code = super().generate_code(blocks)
        
        # Добавляем улучшения на основе связей
        enhanced_lines = base_code.split('\n')
        
        # Добавляем комментарии для группировки связанных блоков
        for i, line in enumerate(enhanced_lines):
            if line.strip().startswith('// TODO'):
                # Добавляем более детальные комментарии
                enhanced_lines[i] = line.replace('// TODO', '// TODO: Implement block logic')
                
        return '\n'.join(enhanced_lines)
        
    def generate_block_code(self, block):
        """Переопределяем для более детального кода"""
        lines = super().generate_block_code(block)
        
        # Добавляем дополнительные детали в зависимости от типа блока
        if block.block_type == "function" and block.function_name == "main" and not lines:
            lines.append("cout << \"Program started\" << endl;")
            
        return lines