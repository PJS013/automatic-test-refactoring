import ast
from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizedInstruction:
    root: str
    locator_method: Optional[str]
    locator_arguments: list
    locator_keywords: dict
    modifiers: list
    action: str
    action_arguments: list
    action_keywords: dict
    is_assertion: bool
    is_negated: bool
    operation_type: str
    assign_target: str
    is_setup: bool

def normalize_instruction(node):
    is_setup = False
    if isinstance(node, ast.Expr):
        operation_type = "expr"
        assign_target = None
        call = node.value
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
            if isinstance(call.func.value, ast.Name):
               if call.func.value.id in ["context", "browser"]:
                    is_setup = True

    elif isinstance(node, ast.Assign):
        operation_type = "assign"
        assign_target = node.targets[0].id
        call = node.value
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
            if isinstance(call.func.value, ast.Name):
                if call.func.value.id in ["context", "browser"]:
                    is_setup = True
            elif isinstance(call.func.value.value, ast.Name):
                if call.func.value.value.id == "playwright":
                    is_setup = True

    else:
        return None

    if not isinstance(call, ast.Call):
        return None
    if not isinstance(call.func, ast.Attribute):
        return None

    action = call.func.attr
    action_arguments = extract_arguments(call)
    action_keywords = extract_keywords(call)

    operation = call.func.value
    is_negated = False

    if isinstance(operation, ast.Attribute) and operation.attr == 'not_':
        is_negated = True
        operation = operation.value

    is_assertion = False
    if isinstance(operation, ast.Call):
        if isinstance(operation.func, ast.Name) and operation.func.id == 'expect':
            is_assertion = True
            if operation.args is None:
                return None
            operation = operation.args[0]

            if isinstance(operation, ast.Name):
                return NormalizedInstruction(
                    root=operation.id,
                    locator_method=None,
                    locator_arguments=[],
                    locator_keywords={},
                    modifiers=[],
                    action=action,
                    action_arguments=action_arguments,
                    action_keywords=action_keywords,
                    is_assertion=is_assertion,
                    is_negated=is_negated,
                    operation_type=operation_type,
                    assign_target=assign_target,
                    is_setup=is_setup
                )
    modifiers = []
    while True:
        if isinstance(operation, ast.Attribute):
            if operation.attr in ('first', 'last'):
                modifiers.append((operation.attr, [], {}))
                operation = operation.value
            else:
                break
        elif isinstance(operation, ast.Call) and isinstance(operation.func, ast.Attribute):
            if operation.func.attr in ('nth', 'filter'):
                mod_arguments = extract_arguments(operation)
                mod_keywords = extract_keywords(operation)
                modifiers.append((operation.func.attr, mod_arguments, mod_keywords))
                operation = operation.func.value
            else:
                break
        else:
            break

    if len(modifiers) > 0:
        modifiers.reverse()

    root = None
    if isinstance(operation, ast.Name):
        root = operation.id
    elif isinstance(operation, ast.Call) and isinstance(operation.func, ast.Attribute):
        root_node = operation.func.value
        if isinstance(root_node, ast.Name):
            root = root_node.id
        else:
            root = ast.unparse(root_node)

    locator_method = None
    locator_arguments = None
    locator_keywords = None
    if isinstance(operation, ast.Call) and isinstance(operation.func, ast.Attribute):
        locator_method = operation.func.attr
        locator_arguments = extract_arguments(operation)
        locator_keywords = extract_keywords(operation)

    return NormalizedInstruction(
        root=root,
        locator_method=locator_method,
        locator_arguments=locator_arguments,
        locator_keywords=locator_keywords,
        modifiers=modifiers,
        action=action,
        action_arguments=action_arguments,
        action_keywords=action_keywords,
        is_assertion=is_assertion,
        is_negated=is_negated,
        operation_type=operation_type,
        assign_target=assign_target,
        is_setup=is_setup
    )


def extract_arguments(call):
    action_arguments = []
    if call.args is not None:
        for arg in call.args:
            try:
                action_arguments.append(ast.literal_eval(arg))
            except Exception:
                action_arguments.append(ast.unparse(arg))
    return action_arguments


def extract_keywords(call):
    action_keywords = {}
    if call.keywords is not None:
        for keyword in call.keywords:
            try:
                action_keywords[keyword.arg] = ast.literal_eval(keyword.value)
            except Exception:
                action_keywords[keyword.arg] = ast.unparse(keyword.value)
    return action_keywords