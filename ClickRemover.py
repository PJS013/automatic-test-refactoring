import ast

from Normalize import normalize_instruction

class ClickRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        i = 0
        while i < len(node.body):
            if i + 1 < len(node.body):
                normalized = normalize_instruction(node.body[i])
                next_normalized = normalize_instruction(node.body[i + 1])

                if normalized is None and next_normalized is None:
                    i += 1
                    continue


                if (normalized.action in ('click', 'press')
                    and next_normalized.action == 'fill'
                    and self._is_same_locator(normalized, next_normalized)):
                    del node.body[i]
                    continue

                if (normalized.action == 'fill'
                    and next_normalized.action in ('click', 'press')
                    and self._is_same_locator(normalized, next_normalized)):
                    del node.body[i+1]
                    continue
            i += 1
        return node

    def _is_same_locator(self, a, b):
        if a.locator_arguments is not None and len(a.locator_arguments) > 0:
            if b.locator_arguments is not None and len(b.locator_arguments) > 0:
                for n_argument, next_n_argument in zip(a.locator_arguments, b.locator_arguments):
                    if n_argument == next_n_argument:
                        return True

            elif b.locator_keywords is not None and len(b.locator_keywords) > 0:
                for n_argument, next_n_keyword in zip(a.locator_arguments, b.locator_keywords):
                    if n_argument == b.locator_keywords[next_n_keyword]:
                        return True

        if a.locator_keywords is not None and len(a.locator_keywords) > 0:
            if b.locator_arguments is not None and len(b.locator_arguments) > 0:
                for n_keyword, next_n_argument in zip(a.locator_keywords, b.locator_arguments):
                    if a.locator_keywords[n_keyword] == next_n_argument:
                        return True

            elif b.locator_keywords is not None and len(b.locator_keywords) > 0:
                for key, n_value in a.locator_keywords.items():
                    if n_value == b.locator_keywords[key]:
                        return True
        return False