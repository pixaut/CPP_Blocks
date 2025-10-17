#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности C++ Block Programming App
"""

import sys
import os

def test_imports():
    """Тестирует импорт всех модулей"""
    try:
        from block_system import BlockSystem, Block, VariableBlock, OperatorBlock, FunctionBlock
        from code_generator import CodeGenerator, AdvancedCodeGenerator
        print("Все модули успешно импортированы")
        return True
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        return False

def test_block_creation():
    """Тестирует создание блоков"""
    try:
        from block_system import BlockSystem
        
        block_system = BlockSystem()
        
        # Тестируем создание различных типов блоков
        test_blocks = ["variable", "operator", "function"]
        
        for block_type in test_blocks:
            block = block_system.create_block(block_type)
            if block is None:
                print(f"Не удалось создать блок типа: {block_type}")
                return False
            print(f"Блок {block_type} создан успешно")
            
        return True
    except Exception as e:
        print(f"Ошибка создания блоков: {e}")
        return False

def test_code_generation():
    """Тестирует генерацию кода"""
    try:
        from block_system import BlockSystem
        from code_generator import CodeGenerator
        
        block_system = BlockSystem()
        code_generator = CodeGenerator()
        
        # Создаем несколько тестовых блоков
        blocks = []
        
        # Переменная
        var_block = block_system.create_block("variable")
        if hasattr(var_block, 'var_type'):
            var_block.var_type = "int"
            var_block.var_name = "test_var"
            var_block.var_value = "42"
        blocks.append(var_block)
        
        # Оператор
        op_block = block_system.create_block("operator")
        if hasattr(op_block, 'operand1'):
            op_block.operand1 = "a"
            op_block.operand2 = "b"
            op_block.operator = "+"
            op_block.result_var = "result"
        blocks.append(op_block)
        
        # Генерируем код
        cpp_code = code_generator.generate_code(blocks)
        
        if cpp_code and len(cpp_code) > 0:
            print("Генерация кода работает")
            print("Пример сгенерированного кода:")
            print("-" * 40)
            print(cpp_code[:200] + "..." if len(cpp_code) > 200 else cpp_code)
            print("-" * 40)
            return True
        else:
            print("Генерация кода не работает")
            return False
            
    except Exception as e:
        print(f"Ошибка генерации кода: {e}")
        return False

def test_gui_availability():
    """Проверяет доступность tkinter"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        root.destroy()
        print("GUI (tkinter) доступен")
        return True
    except Exception as e:
        print(f"GUI недоступен: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Запуск тестов C++ Block Programming App")
    print("=" * 50)
    
    tests = [
        ("Импорт модулей", test_imports),
        ("Создание блоков", test_block_creation),
        ("Генерация кода", test_code_generation),
        ("Доступность GUI", test_gui_availability)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nТест: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"Тест '{test_name}' не пройден")
    
    print("\n" + "=" * 50)
    print(f"Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("Все тесты пройдены! Приложение готово к использованию.")
        print("\nДля запуска приложения выполните:")
        print("python main.py")
    else:
        print("Некоторые тесты не пройдены. Проверьте установку зависимостей.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
