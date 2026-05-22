import ast
from _ast import FunctionDef
from PageObjectMethod import PageObjectMethod

class MethodCollector(ast.NodeTransformer):
    def __init__(self):
        self.methods = []

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, FunctionDef):
                if child.name != "__init__":
                    self.methods.append(PageObjectMethod(node.name, child.name, child.body, child.args.args))
        return node

    def extract_method_names(self):
        method_names = set()
        for method in self.methods:
            if method.name != "__init__":
                method_names.add(method.name)
        return method_names