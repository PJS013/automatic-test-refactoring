import ast

from ClickRemover import ClickRemover
from MethodCollector import MethodCollector
from TransformToPageObject import TransformToPageObject

code = open("test.py").read()
tree = ast.parse(code)
print(ast.dump(tree, indent=2))


transformer = ClickRemover()
modified_tree = transformer.visit(tree)

collector = MethodCollector()
collector.visit(tree)

transformer = TransformToPageObject(collector.methods)
modified_tree = transformer.visit(modified_tree)

ast.fix_missing_locations(modified_tree)


# for i in modified_tree.body:
#     print(i)

# print(modified_tree)
with open("test_modified.py", "w") as f:
    f.write(ast.unparse(modified_tree))