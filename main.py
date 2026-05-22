import ast

from ClickRemover import ClickRemover
from ExtractMethods import SequenceMatcher
from MethodCollector import MethodCollector
from TransformToPageObject import TransformToPageObject

code = open("test.py").read()
tree = ast.parse(code)
# print(ast.dump(tree, indent=2))
test_scripts = set()
test_scripts.add("run")

transformer = ClickRemover()
modified_tree = transformer.visit(tree)

collector = MethodCollector()
collector.visit(tree)
method_names = collector.extract_method_names()


transformer = TransformToPageObject(collector.methods, test_scripts)
modified_tree = transformer.visit(modified_tree)

test_scripts.update(method_names)

sequenceMatcher = SequenceMatcher()

sequenceMatcher.visit(modified_tree)
new_tree = sequenceMatcher.create_new_method(modified_tree)
if new_tree is not None:
    # print("Not none")
    modified_tree = new_tree
    collector.visit(modified_tree)

    transformer = TransformToPageObject([method for method in collector.methods if method.class_name == "MiscClass"], test_scripts)
    modified_tree = transformer.visit(modified_tree)
# else:
#     print("None")
ast.fix_missing_locations(modified_tree)
# sequenceMatcher.print()

# for i in modified_tree.body:
#     print(i)

print(modified_tree)
with open("test_modified.py", "w") as f:
    f.write(ast.unparse(modified_tree))