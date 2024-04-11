import numpy as np


class Node:
    def __init__(self, node_xfunction, node_yfunction, node_name=None):
        self.node_xfunction = node_xfunction
        self.node_yfunction = node_yfunction
        self.node_name = node_name
        self.node_position = None

    def compute_position(self, variables):
        [x_cord, y_cord] = eval(self.node_xfunction, {**variables})
        self.node_position = [x_cord, y_cord]
        return self.node_position

    def get_node_position(self, variables):
        if self.node_position is None:
            self.compute_position(variables)
        return self.node_position

    def reset_node_position(self):
        self.node_position = None

    def __str__(self):
        return f'Hello, I\'m {self.node_name}'

    def __del__(self):
        return f'{self.node_name} has been destroyed'
