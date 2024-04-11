import numpy as np

from app_test.Model.utils import *

class Link:
    def __init__(self, node_1, node_2, connections, length=None, cg=None, mass=None, inertia=None):
        self.node_1 = node_1
        self.node_2 = node_2
        self.connections = eval(connections) - np.ones(2, dtype=int)
        self.mass = eval(mass) if mass is not None else None
        self.inertia = eval(inertia) if inertia is not None else None
        self.cg = np.vstack(eval(cg)) if cg is not None else np.array([None, None])
        self.length = eval(length) if length is not None else vector_module(points_to_vector(self.node_1, self.node_2))

    def update(self):
        self.vector = points_to_vector(self.node_1, self.node_2)
        self.global_cord_angle = np.arccos(self.vector[0] / self.length)
        if self.node_1[1] > self.node_2[1]:
            self.global_cord_angle = 2 * np.pi - self.global_cord_angle

    def get_cg_global_cord(self):
        if self.cg is not None:
            rotation_matrix = np.array([[np.cos(self.global_cord_angle), -np.sin(self.global_cord_angle)],
                                    [np.sin(self.global_cord_angle), np.cos(self.global_cord_angle)]])
            return np.append(np.hstack(np.vstack(self.node_1) + rotation_matrix.dot(self.cg)),
                             self.global_cord_angle)
        else:
            return None