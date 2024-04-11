import re

def substitute_values(lst):
    substituted_list = []
    for sublist in lst:
        substituted_sublist = []
        for item in sublist:
            substituted_item = re.sub(r'\b(x(\d+))\b', r'Node\2.node_position[0]', item)
            substituted_item = re.sub(r'\b(y(\d+))\b', r'Node\2.node_position[1]', substituted_item)
            substituted_sublist.append(substituted_item)
        substituted_list.append(substituted_sublist)
    return substituted_list

# Original list
original_list = [['0', '0+x1'],
                 ['np.cos(phi) * l1', 'np.sin(phi) * l1'],
                 ['dv[0] - l3 * np.cos(phi_3)', 'dv[1] + l3 * np.sin(phi_3)'],
                 ['dv[0]', 'dv[1]'],
                 ['dv[0] + l4 * np.cos(-phi_3)', 'dv[1] + l4 * np.sin(-phi_3)'],
                 ['fxv', 'y5 - l5 * np.sqrt(1 - (l5 ** -2) * (-l4 * np.cos(phi_3) - dv[0] + fxv) ** 2)'],
                 ['x6', 'y6 - l6']]

substituted_list = substitute_values(original_list)

print(substituted_list)
