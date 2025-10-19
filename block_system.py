class Block:

    def __init__(self):
        self.connections = []

    def generate_code() -> str:        
        pass


class BlockWithType(Block):

    def __init__(self,type = None):
        super().__init__()
        self.type = type

class ReturnBlock(Block):
    def __init__(self, expression=""):
        super().__init__()
        self.expression = expression

    def generate_code(self) -> str:
        return f"return {self.expression};\n"

class Function(BlockWithType):

    def __init__(self, type, name, params = dict()):
        super().__init__()
        self.type = type
        self.name = name
        self.params = params
    
    def set_type(self,type):
        self.type = type

    def set_name(self,name):
        self.name = name
    
    def add_param(self,type,name):
        self.params[name] = type

    # def add_param(self,type_name):
    #     parts = type_name.split()
    #     self.params_types[parts[1]] = type[0]

    def get_body(self) -> str:
        return "".join(conn.generate_code() for conn in self.connections)

    def generate_code(self) -> str:
        # Формируем сигнатуру
        params_code = ", ".join(f"{t} {n}" for n, t in self.params.items())
        code = f"{self.type} {self.name}({params_code}) {{\n"
        code += self.get_body()
        code += "}\n"
        return code

if __name__ == '__main__':

    val = Function("int", "main")
    val.add_param('int','x')
    val.add_param('float','y')
    val.add_param('ifstream&','is')
    val.connections.append(ReturnBlock("0"))

    print( val.generate_code() )
