import tkinter as tk
from tkinter import simpledialog, ttk
import json

class Block:
    def __init__(self, block_type, x=50, y=50):
        self.block_type = block_type
        self.x = x
        self.y = y
        self.width = 150
        self.height = 50
        self.rect_id = None
        self.text_id = None
        self.parameters = {}
        self.color = self.get_default_color()
        
    def get_position(self):
        return self.x, self.y
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        
    def get_size(self):
        return self.width, self.height
        
    def get_color(self):
        return self.color
        
    def get_text(self):
        return self.block_type
        
    def set_canvas_ids(self, rect_id, text_id):
        self.rect_id = rect_id
        self.text_id = text_id
        
    def get_canvas_ids(self):
        return self.rect_id, self.text_id
        
    def set_outer_rect_id(self, outer_rect_id):
        """Устанавливает ID внешней рамки (для кастомных функций)"""
        self.outer_rect_id = outer_rect_id
        
    def get_outer_rect_id(self):
        """Возвращает ID внешней рамки"""
        return getattr(self, 'outer_rect_id', None)
        
    def get_default_color(self):
        """Возвращает цвет блока по умолчанию"""
        color_map = {
            "variable": "#FFE4B5",    # Переменные - светло-оранжевый
            "operator": "#98FB98",    # Операторы - светло-зеленый
            "function": "#DDA0DD",    # Функции - светло-фиолетовый
            "custom_function": "#FFB6C1",  # Кастомные функции - светло-розовый
            "return": "#87CEEB"       # Return - светло-голубой
        }
        return color_map.get(self.block_type, "#E0E0E0")
        
    def to_dict(self):
        """Преобразует блок в словарь для сохранения"""
        return {
            "id": id(self),
            "type": self.block_type,
            "x": self.x,
            "y": self.y,
            "parameters": self.parameters
        }
        
    def from_dict(self, data):
        """Загружает блок из словаря"""
        self.block_type = data["type"]
        self.x = data["x"]
        self.y = data["y"]
        self.parameters = data.get("parameters", {})
        self.color = self.get_default_color()

class VariableBlock(Block):
    def __init__(self, x=50, y=50):
        super().__init__("variable", x, y)
        self.width = 200
        self.height = 60
        self.var_type = "int"
        self.var_name = "var"
        self.var_value = "0"
        self.is_expression = False
        
    def get_text(self):
        if self.is_expression:
            return f"{self.var_type} {self.var_name} = {self.var_value}"
        else:
            return f"{self.var_type} {self.var_name} = {self.var_value}"
        
    def configure(self):
        """Открывает диалог настройки переменной"""
        dialog = VariableConfigDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "var_type": self.var_type,
            "var_name": self.var_name,
            "var_value": self.var_value,
            "is_expression": self.is_expression
        })
        return data
        
    def from_dict(self, data):
        super().from_dict(data)
        self.var_type = data.get("var_type", "int")
        self.var_name = data.get("var_name", "var")
        self.var_value = data.get("var_value", "0")
        self.is_expression = data.get("is_expression", False)

class OperatorBlock(Block):
    def __init__(self, x=50, y=50):
        super().__init__("operator", x, y)
        self.width = 180
        self.height = 60
        self.operator = "+"
        self.operand1 = "a"
        self.operand2 = "b"
        self.result_var = "result"
        
    def get_text(self):
        return f"{self.result_var} = {self.operand1} {self.operator} {self.operand2}"
        
    def configure(self):
        dialog = OperatorConfigDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "operator": self.operator,
            "operand1": self.operand1,
            "operand2": self.operand2,
            "result_var": self.result_var
        })
        return data
        
    def from_dict(self, data):
        super().from_dict(data)
        self.operator = data.get("operator", "+")
        self.operand1 = data.get("operand1", "a")
        self.operand2 = data.get("operand2", "b")
        self.result_var = data.get("result_var", "result")

class FunctionBlock(Block):
    def __init__(self, x=50, y=50):
        super().__init__("function", x, y)
        self.width = 200
        self.height = 60
        self.function_name = "main"
        self.param1 = ""
        self.param2 = ""
        self.result_var = "result"
        
    def get_text(self):
        if self.function_name == "main":
            return "int main()"
        else:
            params = []
            if self.param1:
                params.append(self.param1)
            if self.param2:
                params.append(self.param2)
            param_str = ", ".join(params) if params else ""
            return f"{self.result_var} = {self.function_name}({param_str})"
        
    def configure(self):
        dialog = FunctionConfigDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "function_name": self.function_name,
            "param1": self.param1,
            "param2": self.param2,
            "result_var": self.result_var
        })
        return data
        
    def from_dict(self, data):
        super().from_dict(data)
        self.function_name = data.get("function_name", "main")
        self.param1 = data.get("param1", "")
        self.param2 = data.get("param2", "")
        self.result_var = data.get("result_var", "result")

class CustomFunctionBlock(Block):
    def __init__(self, x=50, y=50):
        super().__init__("custom_function", x, y)
        self.width = 300
        self.height = 200
        self.function_name = "myFunction"
        self.return_type = "int"
        self.parameters = ""
        self.body_blocks = []  # Блоки внутри функции
        
    def get_text(self):
        return f"function {self.function_name}({self.parameters}) -> {self.return_type}"
        
    def configure(self):
        dialog = CustomFunctionConfigDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "function_name": self.function_name,
            "return_type": self.return_type,
            "parameters": self.parameters,
            "body_blocks": [block.to_dict() for block in self.body_blocks]
        })
        return data
        
    def from_dict(self, data):
        super().from_dict(data)
        self.function_name = data.get("function_name", "myFunction")
        self.return_type = data.get("return_type", "int")
        self.parameters = data.get("parameters", "")
        # body_blocks будет восстановлен отдельно

class ReturnBlock(Block):
    def __init__(self, x=50, y=50):
        super().__init__("return", x, y)
        self.width = 150
        self.height = 50
        self.return_value = ""
        self.is_void = False
        
    def get_text(self):
        if self.is_void:
            return "return;"
        else:
            return f"return {self.return_value};"
        
    def configure(self):
        dialog = ReturnConfigDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "return_value": self.return_value,
            "is_void": self.is_void
        })
        return data
        
    def from_dict(self, data):
        super().from_dict(data)
        self.return_value = data.get("return_value", "")
        self.is_void = data.get("is_void", False)

class BlockSystem:
    def __init__(self):
        self.block_types = {
            "variable": VariableBlock,
            "operator": OperatorBlock,
            "function": FunctionBlock,
            "custom_function": CustomFunctionBlock,
            "return": ReturnBlock
        }
        
    def create_block(self, block_type, x=50, y=50):
        """Создает блок указанного типа"""
        if block_type in self.block_types:
            block_class = self.block_types[block_type]
            block = block_class(x, y)
            return block
        return None
        
    def create_block_from_dict(self, data):
        """Создает блок из словаря"""
        block_type = data["type"]
        if block_type in self.block_types:
            block_class = self.block_types[block_type]
            block = block_class()
            block.from_dict(data)
            return block
        return None

# Диалоги конфигурации блоков
class VariableConfigDialog:
    def __init__(self, parent, block):
        self.block = block
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка переменной")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Тип переменной
        tk.Label(self.dialog, text="Тип:").pack(pady=5)
        self.type_var = tk.StringVar(value=block.var_type)
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var,
                                 values=["int", "float", "string", "bool"])
        type_combo.pack(pady=5)
        
        # Имя переменной
        tk.Label(self.dialog, text="Имя:").pack(pady=5)
        self.name_var = tk.StringVar(value=block.var_name)
        name_entry = tk.Entry(self.dialog, textvariable=self.name_var)
        name_entry.pack(pady=5)
        
        # Значение/выражение
        tk.Label(self.dialog, text="Значение или выражение:").pack(pady=5)
        self.value_var = tk.StringVar(value=block.var_value)
        value_entry = tk.Entry(self.dialog, textvariable=self.value_var, width=40)
        value_entry.pack(pady=5)
        
        # Чекбокс для выражения
        self.expression_var = tk.BooleanVar(value=block.is_expression)
        expression_check = tk.Checkbutton(self.dialog, text="Это выражение (можно использовать переменные и функции)", 
                                        variable=self.expression_var)
        expression_check.pack(pady=5)
        
        # Подсказка
        hint_label = tk.Label(self.dialog, text="Примеры выражений: a + b, max(x, y), sqrt(16)", 
                             font=("Arial", 8), fg="gray")
        hint_label.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def ok_clicked(self):
        self.block.var_type = self.type_var.get()
        self.block.var_name = self.name_var.get()
        self.block.var_value = self.value_var.get()
        self.block.is_expression = self.expression_var.get()
        self.dialog.destroy()

class OperatorConfigDialog:
    def __init__(self, parent, block):
        self.block = block
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка оператора")
        self.dialog.geometry("350x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Оператор
        tk.Label(self.dialog, text="Оператор:").pack(pady=5)
        self.operator_var = tk.StringVar(value=block.operator)
        operator_combo = ttk.Combobox(self.dialog, textvariable=self.operator_var,
                                     values=["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"])
        operator_combo.pack(pady=5)
        
        # Первый операнд
        tk.Label(self.dialog, text="Первый операнд:").pack(pady=5)
        self.op1_var = tk.StringVar(value=block.operand1)
        op1_entry = tk.Entry(self.dialog, textvariable=self.op1_var, width=30)
        op1_entry.pack(pady=5)
        
        # Второй операнд
        tk.Label(self.dialog, text="Второй операнд:").pack(pady=5)
        self.op2_var = tk.StringVar(value=block.operand2)
        op2_entry = tk.Entry(self.dialog, textvariable=self.op2_var, width=30)
        op2_entry.pack(pady=5)
        
        # Переменная результата
        tk.Label(self.dialog, text="Переменная результата:").pack(pady=5)
        self.result_var = tk.StringVar(value=block.result_var)
        result_entry = tk.Entry(self.dialog, textvariable=self.result_var, width=30)
        result_entry.pack(pady=5)
        
        # Подсказка
        hint_label = tk.Label(self.dialog, text="Примеры: a, b, 5, max(x, y)", 
                             font=("Arial", 8), fg="gray")
        hint_label.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def ok_clicked(self):
        self.block.operator = self.operator_var.get()
        self.block.operand1 = self.op1_var.get()
        self.block.operand2 = self.op2_var.get()
        self.block.result_var = self.result_var.get()
        self.dialog.destroy()

class FunctionConfigDialog:
    def __init__(self, parent, block):
        self.block = block
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка функции")
        self.dialog.geometry("350x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Имя функции
        tk.Label(self.dialog, text="Функция:").pack(pady=5)
        self.function_var = tk.StringVar(value=block.function_name)
        function_combo = ttk.Combobox(self.dialog, textvariable=self.function_var,
                                     values=["main", "max", "min", "abs", "sqrt", "pow", "sin", "cos", "tan", 
                                            "log", "exp", "floor", "ceil", "round"])
        function_combo.pack(pady=5)
        
        # Первый параметр
        tk.Label(self.dialog, text="Первый параметр:").pack(pady=5)
        self.param1_var = tk.StringVar(value=block.param1)
        param1_entry = tk.Entry(self.dialog, textvariable=self.param1_var, width=30)
        param1_entry.pack(pady=5)
        
        # Второй параметр
        tk.Label(self.dialog, text="Второй параметр:").pack(pady=5)
        self.param2_var = tk.StringVar(value=block.param2)
        param2_entry = tk.Entry(self.dialog, textvariable=self.param2_var, width=30)
        param2_entry.pack(pady=5)
        
        # Переменная результата
        tk.Label(self.dialog, text="Переменная результата:").pack(pady=5)
        self.result_var = tk.StringVar(value=block.result_var)
        result_entry = tk.Entry(self.dialog, textvariable=self.result_var, width=30)
        result_entry.pack(pady=5)
        
        # Подсказка
        hint_label = tk.Label(self.dialog, text="main() не требует параметров. Примеры: max(a, b), sqrt(x)", 
                             font=("Arial", 8), fg="gray")
        hint_label.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def ok_clicked(self):
        self.block.function_name = self.function_var.get()
        self.block.param1 = self.param1_var.get()
        self.block.param2 = self.param2_var.get()
        self.block.result_var = self.result_var.get()
        self.dialog.destroy()

class CustomFunctionConfigDialog:
    def __init__(self, parent, block):
        self.block = block
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка кастомной функции")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Имя функции
        tk.Label(self.dialog, text="Имя функции:").pack(pady=5)
        self.name_var = tk.StringVar(value=block.function_name)
        name_entry = tk.Entry(self.dialog, textvariable=self.name_var, width=30)
        name_entry.pack(pady=5)
        
        # Тип возвращаемого значения
        tk.Label(self.dialog, text="Тип возвращаемого значения:").pack(pady=5)
        self.return_type_var = tk.StringVar(value=block.return_type)
        return_type_combo = ttk.Combobox(self.dialog, textvariable=self.return_type_var,
                                        values=["void", "int", "float", "string", "bool"])
        return_type_combo.pack(pady=5)
        
        # Параметры
        tk.Label(self.dialog, text="Параметры (через запятую):").pack(pady=5)
        self.parameters_var = tk.StringVar(value=block.parameters)
        parameters_entry = tk.Entry(self.dialog, textvariable=self.parameters_var, width=40)
        parameters_entry.pack(pady=5)
        
        # Подсказка
        hint_label = tk.Label(self.dialog, text="Примеры параметров: int x, float y, string name", 
                             font=("Arial", 8), fg="gray")
        hint_label.pack(pady=5)
        
        # Информация о блоках внутри функции
        info_label = tk.Label(self.dialog, text="Блоки внутри функции будут добавлены автоматически", 
                             font=("Arial", 9), fg="blue")
        info_label.pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def ok_clicked(self):
        self.block.function_name = self.name_var.get()
        self.block.return_type = self.return_type_var.get()
        self.block.parameters = self.parameters_var.get()
        self.dialog.destroy()

class ReturnConfigDialog:
    def __init__(self, parent, block):
        self.block = block
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка return")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Чекбокс для void
        self.void_var = tk.BooleanVar(value=block.is_void)
        void_check = tk.Checkbutton(self.dialog, text="void функция (без возвращаемого значения)", 
                                   variable=self.void_var, command=self.toggle_void)
        void_check.pack(pady=10)
        
        # Значение возврата
        tk.Label(self.dialog, text="Возвращаемое значение:").pack(pady=5)
        self.value_var = tk.StringVar(value=block.return_value)
        self.value_entry = tk.Entry(self.dialog, textvariable=self.value_var, width=30)
        self.value_entry.pack(pady=5)
        
        # Подсказка
        hint_label = tk.Label(self.dialog, text="Примеры: 0, result, a + b", 
                             font=("Arial", 8), fg="gray")
        hint_label.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Инициализация состояния
        self.toggle_void()
        
    def toggle_void(self):
        if self.void_var.get():
            self.value_entry.config(state="disabled")
        else:
            self.value_entry.config(state="normal")
            
    def ok_clicked(self):
        self.block.is_void = self.void_var.get()
        self.block.return_value = self.value_var.get()
        self.dialog.destroy()