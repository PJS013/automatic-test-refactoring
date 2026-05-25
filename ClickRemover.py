import ast

from Normalize import normalize_instruction

class ClickRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        i = 0
        while i < len(node.body):
            if i + 1 < len(node.body):
                normalized = normalize_instruction(node.body[i])
                next_normalized = normalize_instruction(node.body[i + 1])

                if normalized is not None and next_normalized is not None:
                    if ((normalized.action == 'click' or normalized.action == 'press')
                            and next_normalized.action == 'fill'):
                        if normalized.locator_arguments is not None and len(normalized.locator_arguments) > 0:
                            if next_normalized.locator_arguments is not None and len(next_normalized.locator_arguments) > 0:
                                for n_argument, next_n_argument in zip(normalized.locator_arguments, next_normalized.locator_arguments):
                                    if n_argument == next_n_argument:
                                        del node.body[i]
                                        continue

                            elif next_normalized.locator_keywords is not None and len(next_normalized.locator_keywords) > 0:
                                for n_argument, next_n_keyword in zip(normalized.locator_arguments, next_normalized.locator_keywords):
                                    if n_argument == next_normalized.locator_keywords[next_n_keyword]:
                                        del node.body[i]
                                        continue

                        if normalized.locator_keywords is not None and len(normalized.locator_keywords) > 0:
                            if next_normalized.locator_arguments is not None and len(next_normalized.locator_arguments) > 0:
                                for n_keyword, next_n_argument in zip(normalized.locator_keywords, next_normalized.locator_arguments):
                                    if normalized.locator_keywords[n_keyword] == next_n_argument:
                                        del node.body[i]
                                        continue

                            elif next_normalized.locator_keywords is not None and len(next_normalized.locator_keywords) > 0:
                                for key, n_value in normalized.locator_keywords.items():
                                    if n_value == next_normalized.locator_keywords[key]:
                                        del node.body[i]
                                        continue

            i += 1
        return node