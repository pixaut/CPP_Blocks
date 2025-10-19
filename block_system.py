from enum import Enum


class Block:
    def __init__(self):
        self.connections = []
        self.owner = None
        self.outgoing_connections = []
        self.incoming_connections = []

    def generate_code(self) -> str:
        return ""


class BlockWithType(Block):
    def __init__(self, type=None):
        super().__init__()
        self.type = type


class ReturnBlock(Block):
    def __init__(self, expression=""):
        super().__init__()
        self.expression = expression

    def generate_code(self) -> str:
        return f"return {self.expression};\n"


class Operation(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    EQ = "=="
    NE = "!="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="


class AssignmentBlock(Block):
    def __init__(self, var_name, expression):
        super().__init__()
        self.var_name = var_name
        self.expression = expression

    def generate_code(self) -> str:
        return f"{self.var_name} = {self.expression};\n"


class ExpressionBlock(Block):
    def __init__(self, left, op: Operation, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def generate_code(self) -> str:
        return f"({self.left} {self.op.value} {self.right})"


class VariableBlock(BlockWithType):
    def __init__(self, type, name, value=None):
        super().__init__(type)
        self.name = name
        self.value = value

    def generate_code(self) -> str:
        if self.value is not None:
            return f"{self.type} {self.name} = {self.value};\n"
        return f"{self.type} {self.name};\n"


class Function(BlockWithType):
    def __init__(self, type, name, params=dict()):
        super().__init__(type)
        self.name = name
        self.params = params

    def set_type(self, type):
        self.type = type

    def set_name(self, name):
        self.name = name

    def add_param(self, type, name):
        self.params[name] = type

    def get_body(self) -> str:
        return "".join(conn.generate_code() for conn in self.connections)

    def generate_code(self) -> str:
        params_code = ", ".join(f"{t} {n}" for n, t in self.params.items())
        code = f"{self.type} {self.name}({params_code}) {{\n"
        code += self.get_body()
        code += "}\n"
        return code