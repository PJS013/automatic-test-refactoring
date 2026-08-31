import ast


def update_imports(tree, known_classes):
    used_class_instances = set()
    classes_in_file = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes_in_file.add(node.name)
    # print(classes_in_file)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in known_classes:
            used_class_instances.add(node.id)

    already_imported_classes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                already_imported_classes.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                already_imported_classes.add(alias.name)

    new_imports = []
    for class_name in used_class_instances:
        if class_name not in already_imported_classes and class_name not in classes_in_file:
            new_import = ast.ImportFrom(
                module=known_classes[class_name],
                names=[ast.alias(name=class_name, asname=None)],
                level=0
            )
            ast.fix_missing_locations(new_import)
            new_imports.append(new_import)

    if not new_imports:
        return tree

    last_import_id = 0
    for id, node in enumerate(tree.body):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            last_import_id = id

    for i, imports in enumerate(new_imports):
        tree.body.insert(i + last_import_id + 1, imports)

    return tree

def read_file(path):
    with open(path) as f:
        print(f"[INFO] Reading {path}")
        return f.read()

def write_file(path, content):
    with open(path, "w") as f:
        print(f"[DONE] Writing {path}")
        f.write(content)