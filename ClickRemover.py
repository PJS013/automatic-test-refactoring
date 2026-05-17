import ast


class ClickRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        i = 0
        while i < len(node.body):
            if (i + 1 < len(node.body) and
                    isinstance(node.body[i], ast.Expr) and
                    isinstance(node.body[i + 1], ast.Expr) and
                    isinstance(node.body[i].value, ast.Call) and
                    isinstance(node.body[i + 1].value, ast.Call) and
                    isinstance(node.body[i].value.func, ast.Attribute) and
                    isinstance(node.body[i+1].value.func, ast.Attribute) and
                    (node.body[i].value.func.attr == 'click' or node.body[i].value.func.attr == 'press') and
                    node.body[i + 1].value.func.attr == 'fill'):
                try:
                    current = node.body[i].value
                    next_node = node.body[i + 1].value

                    click_locator = current.func.value.args[0].value
                    fill_locator = next_node.func.value.args[0].value

                    if click_locator == fill_locator:
                        del node.body[i]
                        continue
                except (AttributeError, IndexError):
                    pass
            elif (i > 0 and
                    isinstance(node.body[i], ast.Expr) and
                    isinstance(node.body[i - 1], ast.Expr) and
                    node.body[i].value.func.attr == 'fill' and
                    node.body[i+1].value.func.attr == 'press'):
                try:
                    current = node.body[i].value
                    next_node = node.body[i+1].value

                    click_locator = current.func.value.args[0].value
                    fill_locator = next_node.func.value.args[0].value

                    if click_locator == fill_locator:
                        del node.body[i+1]
                        continue
                except (AttributeError, IndexError):
                    pass
            i += 1
        return node