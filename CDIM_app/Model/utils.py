import types

import numpy as np

def points_to_vector(point1, point2):
    return np.array(point2 - point1)

def vector_module(vector):
    return np.sqrt(np.sum(np.square(vector)))