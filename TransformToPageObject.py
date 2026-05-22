import ast

from Normalize import normalize_instruction


class TransformToPageObject(ast.NodeTransformer):
    def __init__(self, methods, test_scripts):
        self.methods = methods
        self.test_scripts = test_scripts

    def visit_FunctionDef(self, node):
        if node.name in self.test_scripts:
            new_body = []
            i = 0
            while i < len(node.body):
                matched = False
                if isinstance(node.body[i], ast.Expr):
                    matches = []
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

                        matches.append((method, bindings, len(method.body_nodes)))

                    if matches:
                        best_method, best_bindings, best_length = max(matches, key=lambda x: x[2])
                        instance_name, instance_lineno = find_class_instance(node, new_body, best_method.class_name)
                        if instance_name is None:
                            assign_node = ast.Assign(
                                targets=[ast.Name(id=best_method.class_name.lower(), ctx=ast.Store())],
                                value=ast.Call(
                                    func=ast.Name(id=best_method.class_name, ctx=ast.Load()),
                                    args=[ast.Name(id='page', ctx=ast.Load())],
                                    keywords=[]
                                ),
                                lineno=0
                            )
                            ast.copy_location(assign_node, node.body[i])
                            new_body.append(assign_node)
                            instance_name = best_method.class_name.lower()
                        else:
                            # TODO: Get Back
                            # print("New body " + str(len(new_body)))
                            if instance_lineno > len(new_body)+1:
                                temp = node.body[instance_lineno-1]
                                node.body.remove(temp)
                                new_body.append(temp)


                        replacement = self.build_call(best_method, best_bindings, instance_name)
                        new_body.append(replacement)
                        i += best_length
                        matched = True
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
    normalized = normalize_instruction(node)
    if normalized is None:
        return None
    mod_shape = tuple(m[0] for m in normalized.modifiers)
    return (normalized.action, normalized.locator_method, mod_shape,
            normalized.is_assertion, normalized.is_negated)


def sequences_match_shape(pattern_nodes, candidate_nodes):
    if len(pattern_nodes) != len(candidate_nodes):
        return False
    for p, c in zip(pattern_nodes, candidate_nodes):
        normalized_p = normalize_node(p)
        normalized_c = normalize_node(c)
        if normalized_p != normalized_c or normalized_p is None or normalized_c is None:
            return False
    return True

def find_class_instance(node, new_body, class_name):
    for child in node.body:
        if isinstance(child, ast.Assign):
            if isinstance(child.value.func, ast.Name):
                if child.value.func.id == class_name:
                    # print(child.targets[0].id, child.value.func.id, child.lineno - node.lineno)
                    return child.targets[0].id, child.lineno - node.lineno
    for child in new_body:
        if isinstance(child, ast.Assign):
            if isinstance(child.value.func, ast.Name):
                if child.value.func.id == class_name:
                    # print(child.targets[0].id, child.value.func.id, child.lineno - node.lineno)
                    return child.targets[0].id, child.lineno - node.lineno
    return None, None

def extract_bindings(pattern_nodes, candidate_nodes):
    bindings = {}
    for p_node, c_node in zip(pattern_nodes, candidate_nodes):
        p = normalize_instruction(p_node)
        c = normalize_instruction(c_node)
        if p is None or c is None:
            return None

        if p.locator_arguments is not None and c.locator_arguments is not None:
            for p_argument, c_argument in zip(p.locator_arguments, c.locator_arguments):
                result = match_arg(p_argument, c_argument, bindings)
                if result is False:
                    return None

        if p.locator_keywords is not None and c.locator_keywords is not None:
            for key, p_value in p.locator_keywords.items():
                c_value = c.locator_keywords.get(key)
                result = match_arg(p_value, c_value, bindings)
                if result is False:
                    return None

        if p.action_arguments is not None and c.action_arguments is not None:
            for p_argument, c_argument in zip(p.action_arguments, c.action_arguments):
                result = match_arg(p_argument, c_argument, bindings)
                if result is False:
                    return None

        if p.action_keywords is not None and c.action_keywords is not None:
            for key, p_value in p.action_keywords.items():
                c_value = c.action_keywords.get(key)
                result = match_arg(p_value, c_value, bindings)
                if result is False:
                    return None

        if p.modifiers is not None and c.modifiers is not None:
            for p_modifier, c_modifier in zip(p.modifiers, c.modifiers):
                if len(p_modifier[1]) > 0 and len(c_modifier[1]) > 0:
                    for p_argument, c_argument in zip(p_modifier[1], c_modifier[1]):
                        result = match_arg(p_argument, c_argument, bindings)
                        if result is False:
                            return None
                elif len(p_modifier[2]) > 0 and len(c_modifier[2]) > 0:
                    for p_argument, c_argument in zip(p_modifier[2].values(), c_modifier[2].values()):
                        result = match_arg(p_argument, c_argument, bindings)
                        if result is False:
                            return None

    return bindings


def match_arg(p_value, c_value, bindings):
    if p_value is None:
        return None

    if isinstance(p_value, str) and p_value.isidentifier():
        # This is a parameter
        bindings[p_value] = c_value
        return None

    # Otherwise it's a literal
    if p_value != c_value:
        return False

    return None
