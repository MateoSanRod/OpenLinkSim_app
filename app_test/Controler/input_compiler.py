import re
import textwrap
from pathlib import Path
import numpy as np

class Input(object):
    def __init__(self, app):
        self.app = app

    def compile(self):
        self.input_multiline_string = self.app.ui.plainTextEdit.toPlainText()
        self.compile_constants()
        self.substitute_constants()
        self.compile_geometric_eqs()
        self.initial_conditions()
        self.compile_nodes()
        self.compile_links()
        # print('Compiled')

    def compile_constants(self):
        constants_flags = re.compile(r'\$ VARIABLES \$([\s\S]*?)(?:\$.*?|$)')
        constant_match = constants_flags.search(self.input_multiline_string)
        variables = constant_match.group(1).strip() if constant_match else ""
        self.cosntant_list = re.findall(r'([a-zA-Z_]\w*)\s*=\s*(\[.*?\]|[\w\.\[\],]+)', variables)
        global_header = 'global ' + ', '.join(variable for variable, _ in self.cosntant_list) + '\n'
        self.constants = global_header + variables

    def substitute_constants(self):
        for constant, value in self.cosntant_list:
            self.input_multiline_string = self.input_multiline_string.replace(constant, value)

    def compile_geometric_eqs(self):
        geometric_eq_flags = re.compile(r'\$ GEOMETRIC EQ \$([\s\S]*?)(?:\$.*?|$)')
        geometric_eq_match = geometric_eq_flags.search(self.input_multiline_string)
        eq_geometricas_body = geometric_eq_match.group(1).strip() if geometric_eq_match else ""
        self.independent_variables = ''.join(re.findall(r'([\w_, ]+) = indep_var', eq_geometricas_body))
        self.dependent_variables = ''.join(re.findall(r'([\w_, ]+) = dep_var', eq_geometricas_body))
        eq_geometricas_body = textwrap.indent(eq_geometricas_body, '\t')
        num_eqs = eq_geometricas_body.count("eq")
        eq_geometricas_header = u"def eqs(dep_var, indep_var):\n"

        eq_geometricas_footer = (
            f"\nnon_linear_matrix = np.array([{', '.join(f'eq{i + 1}' for i in range(num_eqs))}])\n"
            u"return non_linear_matrix")
        eq_geometricas_footer = textwrap.indent(eq_geometricas_footer, '\t')

        self.eq_geometricas = (eq_geometricas_header +
                               eq_geometricas_body + eq_geometricas_footer)

    def initial_conditions(self):
        init_cond_flags = re.compile(r'\$ INITIAL CONDITIONS \$([\s\S]*?)(?:\$.*?|$)')
        init_cond_match = init_cond_flags.search(self.input_multiline_string)
        init_cond_input = init_cond_match.group(1).strip() if init_cond_match else ""

        indep_var_str = ''.join(re.findall(rf'{self.independent_variables}\s*=\s*(.*)', init_cond_input))
        dep_var_str = ''.join(re.findall(rf'{self.dependent_variables}\s*=\s*(.*)', init_cond_input))
        self.init_indep_var = None if indep_var_str == '' else np.deg2rad(eval(indep_var_str))
        self.init_dep_var = None if dep_var_str == '' else np.deg2rad(eval(dep_var_str))


    def compile_nodes(self):
        node_flags = re.compile(r'\$ NODES \$([\s\S]*?)(?:\$.*?|$)')
        node_match = node_flags.search(self.input_multiline_string)
        node_raw_input = node_match.group(1).strip() if node_match else ""
        node_equations = re.findall(r'Node\d+:([\s\S]*?)(?=Node\d+|\Z)', node_raw_input)

        # Extract the node equations
        nodes = []
        for node_def in node_equations:
            lines = node_def.strip().split('\n')
            node_equations = []
            for line in lines:
                variable, expression = line.split('=')[0].strip(), line.split('=')[1].strip()
                node_equations.append((variable, expression))
            nodes.extend([f"{variable} = {expression}" for variable, expression in node_equations])
        nodes_string = '\n'.join(nodes)
        nodes_string = textwrap.indent(nodes_string, '\t')
        nodes_list = [[f"x{i + 1}", f"y{i + 1}"] for i in range(int(len(nodes) / 2))]
        nodes_list_string = ', '.join([f"[{', '.join(node)}]" for node in nodes_list])
        result = (f"def nodes(dep_var, indep_var):\n\t{self.dependent_variables} = dep_var"
                  f"\n\t{self.independent_variables} = indep_var\n{nodes_string}\n\treturn [{nodes_list_string}]")
        self.node_general_equations = result

        # List of executeable node equations
        node_raw_input = node_match.group(1).strip() if node_match else ""
        node_equations = re.findall(r'Node\d+:([\s\S]*?)(?=Node\d+|\Z)', node_raw_input)
        self.raw_node_equations = []
        self.manipulated_node_equations = []
        for node_def in node_equations:
            lines = node_def.strip().split('\n')
            self.raw_node_equations.append(lines)
            node_eq = [pos_eq.split('=')[1].strip() for pos_eq in lines]
            self.manipulated_node_equations = []
            for node_def in node_equations:
                lines = node_def.strip().split('\n')
                node_eq = [pos_eq.split('=')[1].strip() for pos_eq in lines]

                self.manipulated_node_equations.append(node_eq)
        self.raw_node_equations = [eq for node_equations in self.raw_node_equations for eq in node_equations]

        substituted_list = []
        for sublist in self.manipulated_node_equations:
            substituted_sublist = []
            for item in sublist:
                substituted_item = re.sub(r'\b(x)(\d+)\b', lambda i: f'point_list[{int(i.group(2)) - 1}][0]', item)
                substituted_item = re.sub(r'\b(y)(\d+)\b', lambda i: f'point_list[{int(i.group(2)) - 1}][1]',
                                          substituted_item)
                substituted_sublist.append(substituted_item)
            substituted_list.append(substituted_sublist)
        self.manipulated_node_equations = [str.join(', ', eq) for eq in substituted_list]

    def compile_links(self):
        link_flags = re.compile(r'\$ LINKS \$([\s\S]*?)(?:\$.*?|$)')
        link_match = link_flags.search(self.input_multiline_string)
        link_raw_input = link_match.group(1).strip() if link_match else ""

        self.link_dict = {}
        matches = re.findall(r'Link\d+:([\s\S]*?)(?=Link\d+|\Z)', link_raw_input)
        for index, node_def in enumerate(matches):
            lines = node_def.strip().split('\n')
            link_keys = [pos_eq.split('=')[0].strip() for pos_eq in lines]
            link_values = [pos_eq.split('=')[1].strip() for pos_eq in lines]
            self.link_dict.update({f'Link{index + 1}': {key: value for key, value in zip(link_keys, link_values)}})


    def __add__(self, other) -> None:
        self.input_multiline_string += self.other.input_multiline_string


if __name__ == '__main__':

    app = MagicMock()
    input_obj = Input(app)
    input_obj.input_multiline_string = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links.txt').read_text()
    input_obj.compile_constants()
    input_obj.substitute_constants()
    input_obj.compile_geometric_eqs()
    input_obj.initial_conditions()
    input_obj.compile_nodes()
    input_obj.compile_links()

    # Tests
    print(input_obj.init_indep_var)
    print(input_obj.init_dep_var)


