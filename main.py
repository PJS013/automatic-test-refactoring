import ast
from _ast import FunctionDef

from ClickRemover import ClickRemover

code = open("test.py").read()
tree = ast.parse(code)
print(ast.dump(tree, indent=2))
existing_funcs = dict()

class PageObjectMethod:
    def __init__(self, class_name, name, body_nodes, args):
        self.class_name = class_name
        self.name = name
        self.body_nodes = body_nodes
        self.args = args

class TransformToPageObject(ast.NodeTransformer):
    def __init__(self):
        self.methods = []
        self.transforms = set()

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, FunctionDef):
                if child.name != "__init__":
                    self.methods.append(PageObjectMethod(node.name, child.name, child.body, child.args.args))




transformer = ClickRemover()
modified_tree = transformer.visit(tree)
# ast.fix_missing_locations(modified_tree)


transformer = TransformToPageObject()
transformer.visit(tree)

for i in transformer.methods:
    print(i.name)

with open("test_modified.py", "w") as f:
    f.write(ast.unparse(modified_tree))