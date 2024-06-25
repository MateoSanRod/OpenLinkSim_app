import types

import numpy as np


def points_distance(point1, point2):
    return np.sqrt(np.sum(np.square(np.array(point1) - np.array(point2))))


def points_to_vector(point1, point2):
    return np.array(point2 - point1)


def vector_module(vector):
    return np.sqrt(np.sum(np.square(vector)))


def create_function_from_string(func_str):
    module = types.ModuleType('dynamic_module')
    exec(func_str, module.__dict__)
    if 'dynamic_function' in module.__dict__:
        return module.dynamic_function
    else:
        raise ValueError("Function 'dynamic_function' not found in the provided code string.")
