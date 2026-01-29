import re
import textwrap
from pathlib import Path

import numpy as np


class Input(object):
    def __init__(self, app, txt=None):
        self.app = app
        self.txt = txt
        self.delta_time = None

    def compile(self):
        if self.txt == None:
            self.input_multiline_string = self.app.ui.plainTextEdit.toPlainText()
        else:
            self.input_multiline_string = self.txt
        self.compile_constants()
        self.substitute_constants()
        self.compile_geometric_eqs()
        self.initial_conditions()
        self.compile_view_overlays()
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

        self.eq_code = (eq_geometricas_header +
                               eq_geometricas_body + eq_geometricas_footer)

    def initial_conditions(self):
        init_cond_flags = re.compile(r'\$ INITIAL CONDITIONS \$([\s\S]*?)(?:\$.*?|$)')
        init_cond_match = init_cond_flags.search(self.input_multiline_string)
        init_cond_input = init_cond_match.group(1).strip() if init_cond_match else ""

        position_flags = re.compile(r'Position:\s*([\s\S]*?)(?=:|\Z)')
        position_match = position_flags.search(init_cond_input)
        position_cond_input = position_match.group(1).strip() if position_match else ""
        position_indep_var_str = ''.join(re.findall(rf'{self.independent_variables}\s*=\s*(.*)', position_cond_input))
        position_dep_var_str = ''.join(re.findall(rf'{self.dependent_variables}\s*=\s*(.*)', position_cond_input))
        self.init_indep_var = None if position_indep_var_str == '' else np.deg2rad(eval(position_indep_var_str))
        self.init_dep_var = None if position_dep_var_str == '' else np.deg2rad(eval(position_dep_var_str))
        print(self.independent_variables, "indep_var")
        print(self.dependent_variables, "dep_var")

        speed_flags = re.compile(r'Input speed:\s*([\s\S]*?)(?=:|\Z)')
        speed_match = speed_flags.search(init_cond_input)
        speed_cond_input = speed_match.group(1).strip() if speed_match else ""
        speed_indep_var_str = ''.join(re.findall(rf'{self.independent_variables}\s*=\s*(.*)', speed_cond_input))
        self.speed_indep_var = None if speed_indep_var_str == '' else eval(speed_indep_var_str)
        print(speed_cond_input)
        print(speed_indep_var_str)

        acceleration_flags = re.compile(r'Input acceleration:\s*([\s\S]*?)(?=:|\Z)')
        acceleration_match = acceleration_flags.search(init_cond_input)
        acceleration_cond_input = acceleration_match.group(1).strip() if acceleration_match else ""
        acceleration_indep_var_str = ''.join(
            re.findall(rf'{self.independent_variables}\s*=\s*(.*)', acceleration_cond_input))
        self.accel_indep_var = None if acceleration_indep_var_str == '' else eval(acceleration_indep_var_str)
        print(acceleration_cond_input)
        print(acceleration_indep_var_str)

        type_flags = re.compile(r'Input type:\s*([\s\S]*?)(?=:|\Z)')
        type_match = type_flags.search(init_cond_input)
        type_cond_input = type_match.group(1).strip() if type_match else ""
        type_indep_var_str = ''.join(re.findall(rf'{self.independent_variables}\s*=\s*(.*)', type_cond_input))
        self.type_indep_var = None if type_indep_var_str == '' else type_indep_var_str
        print(type_indep_var_str)

    def compile_view_overlays(self):
        self.overlay_angles = []
        self.overlay_labels = {"nodes": {}, "links": {}}

        view_flags = re.compile(r'\$ VIEW OPTIONS \$([\s\S]*?)(?:\$.*?|$)', re.IGNORECASE)
        view_match = view_flags.search(self.input_multiline_string)
        view_body = view_match.group(1).strip() if view_match else ""
        if not view_body:
            return

        angles_match = re.search(r'Angles:\s*([\s\S]*?)(?=Labels:|$)', view_body, re.IGNORECASE)
        if angles_match:
            angle_lines = [ln.strip() for ln in angles_match.group(1).splitlines() if ln.strip()]
            for ln in angle_lines:
                # Allow comma or space separated key=val specs
                parts = dict()
                for chunk in re.split(r'[,\s]+', ln.split(':', 1)[-1]):
                    if "=" in chunk:
                        k, v = chunk.split("=", 1)
                        parts[k.strip().lower()] = v.strip()
                try:
                    node_id = int(parts.get("node"))
                    link_id = int(parts.get("link"))
                    name = parts.get("name", f"angle_{node_id}_{link_id}")
                except (TypeError, ValueError):
                    continue
                self.overlay_angles.append(
                    {"node": node_id, "link": link_id, "name": name}
                )

        labels_match = re.search(r'Labels:\s*([\s\S]*?)$', view_body, re.IGNORECASE)
        if labels_match:
            label_lines = [ln.strip() for ln in labels_match.group(1).splitlines() if ln.strip()]
            for ln in label_lines:
                mm_node = re.match(r'node\s+(\d+)\s*=\s*(.+)', ln, re.IGNORECASE)
                mm_link = re.match(r'link\s+(\d+)\s*=\s*(.+)', ln, re.IGNORECASE)
                if mm_node:
                    self.overlay_labels["nodes"][int(mm_node.group(1))] = mm_node.group(2).strip()
                elif mm_link:
                    self.overlay_labels["links"][int(mm_link.group(1))] = mm_link.group(2).strip()

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
        self.nodes_code = [str.join(', ', eq) for eq in substituted_list]

    def compile_links(self):
        """Populate self.link_dict – one entry per ‘Link…’ block."""
        txt = self.input_multiline_string
        m = re.search(r"\$ LINKS \$([\s\S]*?)(?:\$\s*[A-Z_ ]+\$|$)", txt)
        raw = m.group(1).strip() if m else ""

        blocks = re.findall(r"Link\d+\s*:\s*([\s\S]*?)(?=Link\d+:|\Z)", raw)
        POINT_RX = re.compile(r"point_\d+\s*=", re.I)
        PRIS_RX = re.compile(r"""
            ^\s*(\d+)\s*,\s*([+-]?\d+(?:\.\d+)?)   # ‹node› , ‹angle›
            (?:\s*,\s*(abs))?\s*$                  # optional ‘abs’
            """, re.X | re.I)

        REV_RX = re.compile(r"^\s*(\d+)\s*$")  # revolute = ‹node›

        self.link_dict = {}

        for idx, blk in enumerate(blocks, start=1):

            pris_nodes, pris_axis, pris_abs = [], [], []
            revolute_nodes = []

            keyvals = {}

            for line in blk.strip().splitlines():
                if "=" not in line:
                    continue
                k, v = (s.strip() for s in line.split("=", 1))

                if k.lower() == "prismatic":
                    mm = PRIS_RX.match(v)
                    if not mm:
                        raise ValueError(f"Bad prismatic spec in Link{idx}: {v}")
                    pris_nodes.append(int(mm.group(1)) - 1)  # global id
                    pris_axis.append(float(mm.group(2)))
                    pris_abs.append(bool(mm.group(3)))

                elif k.lower() == "revolute":
                    mm = REV_RX.match(v)
                    if not mm:
                        raise ValueError(f"Bad revolute spec in Link{idx}: {v}")
                    revolute_nodes.append(int(mm.group(1)) - 1)  # global id

                else:  # keep the *first* occurrence
                    keyvals.setdefault(k, v)

            # connections *must* exist – we need them now
            conn = eval(keyvals.get("connections", "[]"))

            # ------------ collect extra ‘point_n = …’ keys -------------------
            points = [keyvals.pop(k) for k in sorted(keyvals, key=str.lower)
                      if POINT_RX.match(f"{k}=")]
            if points:
                keyvals["points"] = points

            # map all global ids → local (0 / 1)
            pris_local = [conn.index(g + 1) for g in pris_nodes]
            rev_local = [conn.index(g + 1) for g in revolute_nodes]

            keyvals.update({
                "is_prismatic": bool(pris_nodes),
                "pris_nodes": pris_local,
                "pris_axis": pris_axis,
                "pris_abs": pris_abs,
                "is_revolute": bool(rev_local),
                "rev_nodes": rev_local
            })
            self.link_dict[f"Link{idx}"] = keyvals

    def __add__(self, other) -> None:
        self.input_multiline_string += self.other.input_multiline_string
