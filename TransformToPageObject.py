import ast


class TransformToPageObject(ast.NodeTransformer):
    def __init__(self, methods):
        self.methods = methods

    def visit_FunctionDef(self, node):
        if node.name == 'run':
            new_body = []
            i = 0
            while i < len(node.body):
                matched = False
                if isinstance(node.body[i], ast.Expr):
                    for method in self.methods:
                        end = i + len(method.body_nodes)
                        if end > len(node.body):
                            continue

                        candidate = node.body[i:end]

                        if not sequences_match_shape(method.body_nodes, candidate):
                            continue
                        bindings = extract_bindings(method.body_nodes, candidate)
                        if bindings is None:
                            continue

                        instance_name = find_class_instance(node, new_body, method.class_name)
                        if instance_name is None:
                            assign_node = ast.Assign(
                                targets=[ast.Name(id=method.class_name.lower(), ctx=ast.Store())],
                                value=ast.Call(
                                    func=ast.Name(id=method.class_name, ctx=ast.Load()),
                                    args=[ast.Name(id='page', ctx=ast.Load())],
                                    keywords=[]
                                ),
                                lineno=0
                            )
                            ast.copy_location(assign_node, node.body[i])
                            new_body.append(assign_node)
                            instance_name = method.class_name.lower()


                        replacement = self.build_call(method, bindings, instance_name)
                        new_body.append(replacement)
                        i += len(method.body_nodes)
                        matched = True
                        break

                if not matched:
                    new_body.append(node.body[i])
                    i += 1

            node.body = new_body
        return node

    def build_call(self, method, bindings, instance_name):
        args = [
            ast.keyword(arg=arg.arg, value=ast.Constant(value=bindings[arg.arg]))
            for arg in method.args
            if arg.arg != 'self' and arg.arg in bindings
        ]
        call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=instance_name, ctx=ast.Load()),
                attr=method.name,
                ctx=ast.Load()
            ),
            args=args,
            keywords=[]
        )
        return ast.Expr(value=call)


def normalize_node(node):
    try:
        action = node.value.func.attr
        locator = None
        if isinstance(node.value.func.value.func, ast.Name):
            if node.value.func.value.func.id == 'expect':
                locator = node.value.func.value.args[0].func.attr
        else:
            locator = node.value.func.value.func.attr

        return (action, locator)
    except AttributeError:
        return None


def sequences_match_shape(pattern_nodes, candidate_nodes):
    if len(pattern_nodes) != len(candidate_nodes):
        return False
    for p, c in zip(pattern_nodes, candidate_nodes):
        normalized_p = normalize_node(p)
        normalized_c = normalize_node(c)
        if normalized_p != normalized_c or normalized_p is None or normalized_c is None:
            return False
    return True

def extract_bindings(pattern_nodes, candidate_nodes):
    bindings = {}
    for p, c in zip(pattern_nodes, candidate_nodes):
        try:
            p_locator_arg = p.value.func.value.args[0]
            c_locator_arg = c.value.func.value.args[0]

            if isinstance(p_locator_arg, ast.Name):
                bindings[p_locator_arg.id] = ast.unparse(c_locator_arg)[1:-1]
            elif isinstance(p_locator_arg, ast.Constant):
                if isinstance(c_locator_arg, ast.Constant):
                    if p_locator_arg.value != c_locator_arg.value:
                        return None
                else:
                    return None
            elif isinstance(p_locator_arg, ast.Call):
                for arg in p_locator_arg.args:
                    if isinstance(arg, ast.Name):
                        bindings[arg.id] = c_locator_arg.args[0].value
                    elif isinstance(arg, ast.Constant):
                        if isinstance(c_locator_arg, ast.Constant):
                            if arg.value != c_locator_arg.value:
                                return None
                        else:
                            return None

            p_value_arg = p.value.args[0] if p.value.args else None
            c_value_arg = c.value.args[0] if c.value.args else None

            if p_value_arg and c_value_arg:
                if isinstance(p_value_arg, ast.Name):
                    bindings[p_value_arg.id] = ast.unparse(c_value_arg)[1:-1]
                elif isinstance(p_value_arg, ast.Constant):
                    if isinstance(c_value_arg.value, ast.Constant):
                        if p_value_arg.value != c_value_arg.value:
                            return None
                    else:
                        return None
        except (AttributeError, IndexError):
            return None
    return bindings

def find_class_instance(node, new_body, class_name):
    for child in node.body:
        if isinstance(child, ast.Assign):
            if isinstance(child.value.func, ast.Name):
                if child.value.func.id == class_name:
                    return child.targets[0].id
    for child in new_body:
        if isinstance(child, ast.Assign):
            if isinstance(child.value.func, ast.Name):
                if child.value.func.id == class_name:
                    return child.targets[0].id
    return None