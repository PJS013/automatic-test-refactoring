import ast
import copy

from Normalize import normalize_instruction
from TransformToPageObject import normalize_node
from gst import match

MIN_LENGTH = 3


def gst_similarity(nodes_a, nodes_b, min_match_length=3):
    str_a = "\n".join(ast.unparse(n) for n in nodes_a)
    str_b = "\n".join(ast.unparse(n) for n in nodes_b)

    if not str_a or not str_b:
        return 0.0

    matches = match(str_a, '', str_b, '', min_match_length)
    covered = sum(el[2] for el in matches)
    return (2 * covered) / (len(str_a) + len(str_b))

class InstructionSequence:
    def __init__(self, nodes):
        self.nodes = nodes
        self.shape = self.compute_shape()
        self.occurrence_number = 1
        self.length = len(nodes)

    def compute_shape(self):
        # try:
        return tuple(normalize_node(n) for n in self.nodes)
        # except Exception as e:
        #     print(f"Error computing shape: {type(e).__name__}: {e}")
        #     print(f"  Nodes: {[ast.dump(n) for n in self.nodes]}")
        #     return ()

    def __eq__(self, other):
        return self.shape == other.shape

    def increase_occurrence_number(self):
        self.occurrence_number += 1


def embed_new_method_in_class(method, module_node, used_names):
    for node in module_node.body:
        if isinstance(node, ast.ClassDef) and node.name == "MiscClass":
            init_method = None

            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    init_method = child
                    break

            if init_method is not None:
                existing_arguments = set(arg.arg for arg in init_method.args.args)
                print(existing_arguments)

                for name in used_names:
                    if name not in existing_arguments and name != "miscclass":
                        print("Name " + name)
                        init_method.args.args.append(ast.arg(arg=name))
                        init_method.body.append(ast.Assign(targets=[
                            ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr=name,
                                ctx=ast.Store())],
                        value=ast.Name(id=name, ctx=ast.Load())))
            node.body.append(method)
            return module_node

    arg_list = ([ast.arg(arg='self'), ast.arg(arg='page')]
                + [ast.arg(arg=name) for name in used_names if used_names is not None and name != "miscclass"])

    new_class = ast.ClassDef(
        name="MiscClass",
        decorator_list=[],
        bases=[],
        keywords=[],
        body=[
            ast.FunctionDef(
                name="__init__",
                args=ast.arguments(
                    posonlyargs=[],
                    args=arg_list,
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[]
                ),
                body=[
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr='page',
                                ctx=ast.Store())],
                        value=ast.Name(id='page', ctx=ast.Load())),
                ] + [
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr=name,
                                ctx=ast.Store())],
                        value=ast.Name(id=name, ctx=ast.Load()))
                    for name in used_names if used_names is not None and name != "miscclass"],
                decorator_list=[],
            ),
            method
        ]
    )
    ast.fix_missing_locations(new_class)

    module_node.body.append(new_class)
    return module_node


def find_used_names(nodes, instance_maps):
    found_classes = set()
    class UsedNameFinder(ast.NodeVisitor):
        def visit_Name(self, node):
            if node.id in instance_maps.keys():
                found_classes.add(node.id)
    finder = UsedNameFinder()
    for node in nodes:
        finder.visit(node)
    return found_classes


class SequenceMatcher(ast.NodeTransformer):
    def __init__(self, miscMethods, instance_map, all_methods, match_threshold = 0.45):
        self.sequences = {}
        self.NEW_METHOD_COUNTER = 0
        self.all_methods = all_methods
        self.match_threshold = match_threshold
        misc = {}
        for method in miscMethods:
            sequence = InstructionSequence(method.body_nodes)
            misc[sequence.shape] = sequence
        self.MiscMethods = misc
        self.instance_map = instance_map

    def get_next_method_name(self, module_node, class_name):
        names = set()
        for node in module_node.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for method in node.body:
                    names.add(method.name)

        while True:
            if f'generated_{self.NEW_METHOD_COUNTER}' in names:
                self.NEW_METHOD_COUNTER += 1
            else:
                break

    def visit_FunctionDef(self, node):
        for i in range(MIN_LENGTH, len(node.body) + 1):
            for j in range(0, len(node.body) - i + 1):
                window = node.body[j : j + i]
                if any(isinstance(n, ast.Assign) for n in window):
                    continue
                seq = InstructionSequence(window)
                if seq.shape is None:
                    continue
                if any(inner[-1] for inner in seq.shape if inner is not None):
                    continue
                if seq.shape not in self.MiscMethods:
                    if seq.shape in self.sequences and self.sequences[seq.shape].length == seq.length:
                        self.sequences[seq.shape].increase_occurrence_number()
                    else:
                        self.sequences[seq.shape] = seq

        return node

    def print(self):
        for key, sequence in self.sequences:
            if sequence[key].occurrence_number != 1:
                print(sequence)

    def get_max_similarity(self, candidate):
        best = 0.0
        for method in self.all_methods:
            if method.class_name == "MiscClass":
                continue
            similarity = gst_similarity(candidate, method.body_nodes)
            if similarity > best:
                best = similarity
        return best

    def get_candidate(self):
        best_match = None
        best_score = 0
        for key, sequence in self.sequences.items():
            pom_similarity = self.get_max_similarity(sequence.nodes)

            if pom_similarity < self.match_threshold:
                continue
            score = (sequence.occurrence_number - 1) * sequence.length

            if score > best_score and sequence.occurrence_number > 1:
                best_score = score
                best_match = sequence
        return best_match

    def create_new_method(self, module_node):
        self.get_next_method_name(module_node, "MiscClass")
        locator_keyword_counter = 0
        locator_arg_counter = 0
        action_arg_counter = 0
        action_keyword_counter = 0
        action_modifier_counter = 0
        candidate_sequence = self.get_candidate()
        if candidate_sequence is None:
            # print("Create new method none")
            return None

        used_names = find_used_names(candidate_sequence.nodes, self.instance_map)

        print(used_names)

        bindings = {}
        for node in candidate_sequence.nodes:
            normalized_node = normalize_instruction(node)
            if normalized_node is None:
                continue
            if normalized_node.locator_arguments is not None:
                for arg in normalized_node.locator_arguments:
                    if arg not in bindings:
                        bindings[arg] = f"locator_arg_{locator_arg_counter}"
                        locator_arg_counter += 1

            if normalized_node.locator_keywords is not None:
                for key, arg in normalized_node.locator_keywords.items():
                    if arg not in bindings:
                        bindings[arg] = f"locator_keyword_{locator_keyword_counter}"
                        locator_keyword_counter += 1

            if normalized_node.modifiers is not None:
                for arg in normalized_node.modifiers:
                    if arg[0] == "filter" or arg[0] == "nth":
                        if len(arg[2]) > 0:
                            for key, dict_arg in arg[2].items():
                                if dict_arg not in bindings:
                                    bindings[dict_arg] = f"modifiers_{action_modifier_counter}"
                                    action_modifier_counter += 1
                        elif len(arg[1]) > 0:
                            for elem in arg[1]:
                                if elem not in bindings:
                                    bindings[elem] = f"modifiers_{action_modifier_counter}"
                                    action_modifier_counter += 1

            if normalized_node.action_arguments is not None:
                for arg in normalized_node.action_arguments:
                    if arg not in bindings:
                        bindings[arg] = f"action_arg_{action_arg_counter}"
                        action_arg_counter += 1

            if normalized_node.action_keywords is not None:
                for key, arg in normalized_node.action_keywords.items():
                    if arg not in bindings:
                        bindings[arg] = f"action_keyword_{action_keyword_counter}"
                        action_keyword_counter += 1
        print(bindings)
        transformed_nodes = []
        for node in candidate_sequence.nodes:
            copied_node = copy.deepcopy(node)
            transformed_node = self.transform_instance_references(copied_node, "page")
            for used_name in used_names:
                transformed_node = self.transform_instance_references(transformed_node, used_name)
            transformed_node = self.apply_substitution(transformed_node, bindings)
            transformed_nodes.append(transformed_node)

        param_arguments = [ast.arg(arg='self')] + [ast.arg(arg=arg) for arg in bindings.values()]

        new_method = ast.FunctionDef(
            name=f"generated_{self.NEW_METHOD_COUNTER}",
            body=transformed_nodes,
            args=ast.arguments(
                posonlyargs=[],
                args=param_arguments,
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]
            ),
            decorator_list=[],
            returns=None
        )
        ast.fix_missing_locations(new_method)
        self.NEW_METHOD_COUNTER += 1
        return new_method, used_names

    def transform_instance_references(self, node, instance_name):
        class InstanceReferenceTransformer(ast.NodeTransformer):
            def visit_Name(self, name_node):
                if instance_name == "miscclass":
                    if name_node.id == instance_name:
                        name_node.id = 'self'
                if name_node.id == instance_name:
                    return ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load()),
                            attr=instance_name,
                            ctx=ast.Store()
                        )
                return self.generic_visit(name_node)

        transformer = InstanceReferenceTransformer()
        return transformer.visit(node)

    def apply_substitution(self, node, bindings):
        class ConstantReplacer(ast.NodeTransformer):
            def __init__(self):
                self.bindings = bindings

            def visit_Constant(self, const_node):
                if const_node.value in self.bindings.keys():
                    param_name = self.bindings[const_node.value]
                    return ast.Name(id=param_name, ctx=ast.Load())
                return const_node

            def visit_Name(self, name_node):
                if name_node.id in self.bindings.keys():
                    param_name = self.bindings[name_node.id]
                    return ast.Name(id=param_name, ctx=ast.Load())
                return name_node

        return ConstantReplacer().visit(node)
