from block_system import *


if __name__ == '__main__':
    func = Function("int", "main")
    func.add_param("int", "a")
    func.add_param("int", "b")

    # Объявляем переменные
    var_sum = VariableBlock("int", "sum")
    func.connections.append(var_sum)

    # Суммируем a и b
    expr = ExpressionBlock("a", Operation.ADD, "b")
    assign_sum = AssignmentBlock("sum", expr.generate_code())
    func.connections.append(assign_sum)

    # Возвращаем результат
    func.connections.append(ReturnBlock("sum"))

    print(func.generate_code())
