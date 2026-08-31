import json
import os

from ClickRemover import ClickRemover
from ExtractMethods import SequenceMatcher, embed_new_method_in_class
from MethodCollector import MethodCollector
from PageObjectMethod import PageObjectMethod
from TransformToPageObject import TransformToPageObject
from utils import *

def instance_map_generator(test_trees, instance_map):
    for node in ast.walk(test_trees):
        if isinstance(node, ast.Assign):
            try:
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    class_name = node.value.func.id
                    variable_name = node.targets[0].id
                    instance_map[variable_name] = class_name
            except AttributeError:
                pass


def update_instance_parameters(test_tree, arg_dict):
    class UpdateParameters(ast.NodeTransformer):
        def __init__(self, arg_dict):
            self.arg_dict = arg_dict
        def visit_Assign(self, inner_node):
            if inner_node.targets[0].id not in ["page", "context", "browser"]:
                inner_node.value.args = [ast.Name(id=arg.arg, ctx=ast.Load()) for arg in self.arg_dict[inner_node.value.func.id] if arg.arg != "self"]


    updated_node = UpdateParameters(arg_dict)
    for node in test_tree.body:
        if isinstance(node, ast.FunctionDef):
            for body_node in node.body:
                updated_node.visit(body_node)
    return test_tree


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
else:
    generated_tree = ast.parse(
        "from playwright.sync_api import Page, expect\n"
    )
    os.makedirs(os.path.dirname(generated_path), exist_ok=True)
    print(f"[INFO] Generating {generated_path}")

known_classes[config["generated_class"]] = generated_path.replace('/', '.').replace('\\', '.').removesuffix(".py")
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

instance_map = {}
for test_tree in test_trees.values():
    instance_map_generator(test_tree, instance_map)

instance_map['miscclass'] = 'MiscClass'

while True:
    matcher = SequenceMatcher(generated_methods, instance_map, all_methods, config["similarity_threshold"], config["min_method_len"])

    po_trees[generated_path] = generated_tree
    for tree in test_trees.values():
        matcher.visit(tree)

    candidate = matcher.get_candidate()
    if not candidate:
        break
    print(f"[INFO] New method generation...")
    new_method, used_names = matcher.create_new_method(generated_tree)
    new_po_method = PageObjectMethod(
        class_name="MiscClass",
        name=new_method.name,
        body_nodes=new_method.body,
        args=new_method.args.args,
    )

    all_methods.append(new_po_method)
    generated_methods.append(new_po_method)
    generated_tree = embed_new_method_in_class(new_method, generated_tree, used_names)
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
    # generated_tree = TransformToPageObject(all_methods, "MiscClass")
generated_tree = update_imports(generated_tree, known_classes)
write_file(generated_path, ast.unparse(generated_tree))

arg_dict = {}

for elem in generated_tree.body:
    if isinstance(elem, ast.ClassDef):
        for fun in elem.body:
            if isinstance(fun, ast.FunctionDef) and fun.name == "__init__":
                arg_dict[elem.name] = fun.args.args

for tree in po_trees.values():
    for elem in tree.body:
        if isinstance(elem, ast.ClassDef):
            for fun in elem.body:
                if isinstance(fun, ast.FunctionDef) and fun.name == "__init__":
                    arg_dict[elem.name] = fun.args.args

for po_path, tree in po_trees.items():
    tree = update_imports(tree, known_classes)
    write_file(po_path, ast.unparse(tree))

for test_path, tree in test_trees.items():
    tree = update_imports(tree, known_classes)
    tree = update_instance_parameters(tree, arg_dict)
    ast.fix_missing_locations(tree)
    out_path = test_path.replace("tests/", "tests_refactored/")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_file(out_path, ast.unparse(tree))


