import time
import numpy as np
import scipy.optimize as sp_optimize

from app_test.Controler.input import Input
from app_test.Model.link import Link

class Simulation:
    def __init__(self, input_multiline_string, initial_position, v_angular, resolution):
        self.input = Input(input_multiline_string)
        self.input.compile()
        self.initial_position = initial_position
        self.resolution = resolution
        self.v_angular = v_angular
        self.seconds_per_revolution = (2 * np.pi) / v_angular
        self.initial_guess = np.array([1, 0])
        self.resolution = 10

        # self.variables = {variable: eval(value) for variable, value in self.input.cosntant_list}
        self.variables = {'np': np}

        self.functions = {}
        exec(self.input.eq_geometricas, globals(), self.functions)
        self.geometric_func = self.functions.get('eqs')

        self.node_dict = {f'Node{index + 1}': node for index, node in enumerate(self.input.manipulated_node_equations)}

        self.link_dict = {
            f'Link{index + 1}': Link(np.zeros(2, dtype=int), np.ones(2, dtype=int), **link_data)
            for index, (key, link_data) in enumerate(self.input.link_dict.items())
        }
        self.is_link_dict = len(self.link_dict) > 0
        self.frame_data = {
            'node_coordinates': np.empty((0, 2)),
            'link_line_list': [],
            'cg_global_cord': []
        }

    def compute_image(self):
        self.frame_data['node_coordinates'] = np.empty((0, 2))
        self.frame_data['link_line_list'] = []
        self.frame_data['cg_global_cord'] = []

        self.variables[self.input.independent_variables] = self.initial_position
        dependent_var_value = sp_optimize.root(self.geometric_func, self.initial_guess, args=(self.initial_position,)).x.tolist()
        exec(f'{self.input.dependent_variables} = {dependent_var_value}', globals(), self.variables)

        for node_xfunction in self.node_dict.values():
            a = np.array(eval(node_xfunction, self.variables, {'point_list': self.frame_data['node_coordinates']}))
            self.frame_data['node_coordinates'] = np.vstack((self.frame_data['node_coordinates'], a))

        if self.is_link_dict:
            for link in self.link_dict.values():
                link.node_1 = self.frame_data['node_coordinates'][link.connections[0]]
                link.node_2 = self.frame_data['node_coordinates'][link.connections[1]]
                link_line = [link.node_1, link.node_2]
                self.frame_data['link_line_list'].append(link_line)
                if link.cg.any() is not None:
                    link.update()
                    self.frame_data['cg_global_cord'].append(link.get_cg_global_cord())

        self.frame_data['link_line_list'] = np.array(self.frame_data['link_line_list'])
        self.frame_data['cg_global_cord'] = np.array(self.frame_data['cg_global_cord'])

        return self.frame_data

    def compute_simulation(self):
        start_time_2 = time.time()
        simulation_data = []

        for i in np.linspace(0, 2 * np.pi, int(360 * self.resolution)):
            self.initial_position = i
            self.frame_data = self.compute_image()
            simulation_data.append(self.frame_data)

        self.simulation_data = simulation_data
        print("Simulation --- %s seconds ---" % (time.time() - start_time_2))
        return self.simulation_data
