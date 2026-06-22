import ast
import json
import os

from ClickRemover import ClickRemover
from ExtractMethods import SequenceMatcher
from MethodCollector import MethodCollector
from PageObjectMethod import PageObjectMethod
from TransformToPageObject import TransformToPageObject
from utils import *


with open("refactor_config.json") as f:
    config = json.load(f)
print("[INFO] Config file loaded")
all_methods = []
po_trees = {}


known_classes = {}
for po_path in config["page_objects"]:
    tree = ast.parse(read_file(po_path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            known_classes[node.name] = po_path.replace('/', '.').replace('\\', '.').removesuffix(".py")
    collector = MethodCollector()
    collector.visit(tree)
    all_methods.extend(collector.methods)
    po_trees[po_path] = tree

generated_path = os.path.join(config["output_dir"], config["generated_class"] + ".py")
generated_methods = []

if os.path.exists(generated_path):
    generated_tree = ast.parse(read_file(generated_path))
    for node in generated_tree.body:
        if isinstance(node, ast.ClassDef):
            known_classes[node.name] = generated_path.replace('/', '.').replace('\\', '.').removesuffix(".py")

    collector = MethodCollector()
    collector.visit(generated_tree)
    generated_methods = collector.methods
    all_methods.extend(generated_methods)
    print(f"[INFO] All POM classes visited, collected {len(all_methods)} methods")

if not os.path.exists(generated_path):
    generated_tree = ast.parse(
        "from playwright.sync_api import Page, expect\n"
    )
    os.makedirs(os.path.dirname(generated_path), exist_ok=True)
    print(f"[INFO] Generating {generated_path}")

test_trees = {}

for test_path in config["test_scripts"]:
    tree = ast.parse(read_file(test_path))
    test_script_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    transformer = ClickRemover()
    tree = transformer.visit(tree)
    print(f"[INFO] Clicks removed in {test_path}")
    all_methods.extend(generated_methods)
    transformer = TransformToPageObject(all_methods, test_script_names)
    print(f"[INFO] Methods substitution started in {test_path}")
    tree = transformer.visit(tree)
    print(f"[INFO] Methods substitution ended in {test_path}")

    test_trees[test_path] = tree

while True:
    matcher = SequenceMatcher(generated_methods)

    po_trees[generated_path] = generated_tree
    for tree in test_trees.values():
        matcher.visit(tree)

    candidate = matcher.get_candidate()
    if not candidate:
        break
    if candidate:
        print(f"[INFO] New method generation...")
        new_method = matcher.create_new_method(generated_tree)
        new_po_method = PageObjectMethod(
            class_name="MiscClass",
            name=new_method.name,
            body_nodes=new_method.body,
            args=new_method.args.args,
        )

        all_methods.append(new_po_method)
        generated_methods.append(new_po_method)
        generated_tree = matcher.embed_new_method_in_class(new_method, generated_tree)
        ast.fix_missing_locations(generated_tree)
        print(f"[INFO] New method generated")


        for test_path, tree in test_trees.items():
            test_script_names = {
                node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            }
            print(f"[INFO] Methods substitution started in {test_path}")
            transformer = TransformToPageObject(all_methods, test_script_names)

            tree = transformer.visit(tree)
            print(f"[INFO] Methods substitution ended in {test_path}")
            test_trees[test_path] = tree


write_file(generated_path, ast.unparse(generated_tree))

for po_path, tree in po_trees.items():
    tree = update_imports(tree, known_classes)
    write_file(po_path, ast.unparse(tree))

for test_path, tree in test_trees.items():
    ast.fix_missing_locations(tree)
    out_path = test_path.replace("tests/", "tests_refactored/")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_file(out_path, ast.unparse(tree))