import ast
import json
import os

from ClickRemover import ClickRemover
from ExtractMethods import SequenceMatcher
from MethodCollector import MethodCollector
from TransformToPageObject import TransformToPageObject

# def read_file(path):
#     with open(path) as f:
#         return f.read()


with open("refactor_config.json") as f:
    config = json.load(f)

all_methods = []
po_trees = {}

for po_path in config["page_objects"]:
    with open(po_path) as f:
        tree = ast.parse(f.read())
    collector = MethodCollector()
    collector.visit(tree)
    all_methods.extend(collector.methods)
    po_trees[po_path] = tree

generated_path = os.path.join(config["output_dir"], config["generated_class"] + ".py")

if os.path.exists(generated_path):
    with open(generated_path) as f:
        generated_tree = ast.parse(f.read())
else:
    generated_tree = ast.parse(
        "from playwright.sync_api import Page, expect\n"
    )
    os.makedirs(os.path.dirname(generated_path), exist_ok=True)

collector = MethodCollector()
collector.visit(generated_tree)
generated_methods = collector.methods
# all_methods.extend(collector.methods)
# po_trees[po_path] = tree

test_trees = {}

for test_path in config["test_scripts"]:
    with open(test_path) as f:
        tree = ast.parse(f.read())
    test_script_names = {
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    transformer = ClickRemover()
    tree = transformer.visit(tree)
    all_methods.extend(generated_methods)
    transformer = TransformToPageObject(all_methods, test_script_names)
    tree = transformer.visit(tree)

    test_trees[test_path] = tree
matcher = SequenceMatcher(generated_methods)


po_trees[generated_path] = generated_tree
for tree in test_trees.values():
    matcher.visit(tree)

candidate = matcher.get_candidate()
if candidate:
    generated_tree = matcher.create_new_method(generated_tree)
    ast.fix_missing_locations(generated_tree)
    with open(generated_path, "w") as f:
        f.write(ast.unparse(generated_tree))

    new_collector = MethodCollector()
    new_collector.visit(generated_tree)
    all_methods.extend(new_collector.methods)

    for test_path, tree in test_trees.items():
        test_script_names = {
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        transformer = TransformToPageObject(new_collector.methods, test_script_names)

        tree = transformer.visit(tree)
        test_trees[test_path] = tree

for test_path, tree in test_trees.items():
    ast.fix_missing_locations(tree)
    out_path = test_path.replace("tests/", "tests_refactored/")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(ast.unparse(tree))

# code = open("tests/test.py").read()
# tree = ast.parse(code)
# # print(ast.dump(tree, indent=2))
# test_scripts = set()
# test_scripts.add("run")
#
# transformer = ClickRemover()
# modified_tree = transformer.visit(tree)
#
# collector = MethodCollector()
# collector.visit(tree)
# method_names = collector.extract_method_names()
#
#
# transformer = TransformToPageObject(collector.methods, test_scripts)
# modified_tree = transformer.visit(modified_tree)

# test_scripts.update(method_names)
# while True:
#     sequenceMatcher = SequenceMatcher()
#
#     sequenceMatcher.visit(modified_tree)
#     new_tree = sequenceMatcher.create_new_method(modified_tree)
#     if new_tree is not None:
#         # print("Not none")
#         modified_tree = new_tree
#         collector.visit(modified_tree)
#
#         transformer = TransformToPageObject([method for method in collector.methods if method.class_name == "MiscClass"], test_scripts)
#         modified_tree = transformer.visit(modified_tree)
#     else:
#         print("None")
#         break
#     ast.fix_missing_locations(modified_tree)
#     # sequenceMatcher.print()
#
#     # for i in modified_tree.body:
#     #     print(i)
#
# print(modified_tree)
# with open("test_modified.py", "w") as f:
#     f.write(ast.unparse(modified_tree))