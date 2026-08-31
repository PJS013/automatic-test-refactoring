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
                    # print(f"[DEBUG] At position {i}, found {len(matches)} matches: {[m[0].name for m in matches]}")

                    if matches:
                        best_method, best_bindings, best_length = max(matches, key=lambda x: x[2])
                        print(f"[INFO] Substituting {best_method.name}")
                        instance_name = find_class_instance(new_body, best_method.class_name)

                        if instance_name is None:
                            instance_name = retrieve_class_instance(node.body, new_body, best_method.class_name)

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
        keywords = [
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
            args=[],
            keywords=keywords
        )
        return ast.Expr(value=call)


def normalize_node(node):
    normalized = normalize_instruction(node)
    if normalized is None:
        return None
    mod_shape = tuple(m[0] for m in normalized.modifiers)
    return (normalized.action, normalized.locator_method, mod_shape,
            normalized.is_assertion, normalized.is_negated, normalized.is_setup)


def sequences_match_shape(pattern_nodes, candidate_nodes):
    if len(pattern_nodes) != len(candidate_nodes):
        return False
    for p, c in zip(pattern_nodes, candidate_nodes):
        normalized_p = normalize_node(p)
        normalized_c = normalize_node(c)
        if normalized_p != normalized_c or normalized_p is None or normalized_c is None:
            return False
    return True

def find_class_instance(new_body, class_name):
    for node in new_body:
        if isinstance(node, ast.Assign):
            try:
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id == class_name:
                        return node.targets[0].id
            except AttributeError:
                pass
    return None

def retrieve_class_instance(old_body, new_body, class_name):
    for idx, node in enumerate(old_body):
        if isinstance(node, ast.Assign):
            try:
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id == class_name:
                        old_body.pop(idx)
                        new_body.append(node)
                        return node.targets[0].id
            except AttributeError:
                pass
    return None

def extract_bindings(pattern_nodes, candidate_nodes):
    bindings = {}
    for p_node, c_node in zip(pattern_nodes, candidate_nodes):
        p = normalize_instruction(p_node)
        c = normalize_instruction(c_node)
        if p is None or c is None:
            return None

        if p.locator_arguments is not None and len(p.locator_arguments) > 0:
            if c.locator_arguments is not None and len(c.locator_arguments) > 0:
                for p_argument, c_argument in zip(p.locator_arguments, c.locator_arguments):
                    result = match_arg(p_argument, c_argument, bindings)
                    if result is False:
                        return None
            elif c.locator_keywords is not None and len(c.locator_keywords) > 0:
                for p_argument, c_keyword in zip(p.locator_arguments, c.locator_keywords):
                    result = match_arg(p_argument, c.locator_keywords[c_keyword], bindings)
                    if result is False:
                        return None

        if p.locator_keywords is not None and len(p.locator_keywords) > 0:
            if c.locator_arguments is not None and len(c.locator_arguments) > 0:
                for p_keyword, c_argument in zip(p.locator_keywords, c.locator_arguments):
                    result = match_arg(p.locator_keywords[p_keyword], c_argument, bindings)
                    if result is False:
                        return None

            elif c.locator_keywords is not None and len(c.locator_keywords) > 0:
                for key, p_value in p.locator_keywords.items():
                    c_value = c.locator_keywords.get(key)
                    result = match_arg(p_value, c_value, bindings)
                    if result is False:
                        return None

        if p.action_arguments is not None and len(p.action_arguments) > 0:
            if c.action_arguments is not None and len(c.action_arguments) > 0:
                for p_argument, c_argument in zip(p.action_arguments, c.action_arguments):
                    result = match_arg(p_argument, c_argument, bindings)
                    if result is False:
                        return None
            elif c.action_keywords is not None and len(c.action_keywords) > 0:
                for p_argument, c_keyword in zip(p.action_arguments, c.action_keywords):
                    result = match_arg(p_argument, c.action_keywords[c_keyword], bindings)
                    if result is False:
                        return None

        if p.action_keywords is not None and len(p.action_keywords) > 0:
            if c.action_arguments is not None and len(c.action_arguments) > 0:
                for p_keyword, c_argument in zip(p.action_keywords, c.action_arguments):
                    result = match_arg(p.action_keywords[p_keyword], c_argument, bindings)
                    if result is False:
                        return None

            elif c.action_keywords is not None and len(c.action_keywords) > 0:
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
                elif len(p_modifier[1]) > 0 and len(c_modifier[2]) > 0:
                    for p_argument, c_argument in zip(p_modifier[1], c_modifier[2].values()):
                        result = match_arg(p_argument, c_argument, bindings)
                        if result is False:
                            return None
                elif len(p_modifier[2]) > 0 and len(c_modifier[1]) > 0:
                    for p_argument, c_argument in zip(p_modifier[2].values(), c_modifier[1]):
                        result = match_arg(p_argument, c_argument, bindings)
                        if result is False:
                            return None

    return bindings


def match_arg(p_value, c_value, bindings):
    if p_value is None:
        return None

    if isinstance(p_value, str) and p_value.isidentifier():
        bindings[p_value] = c_value
        return None

    if p_value != c_value:
        return False

    return None
