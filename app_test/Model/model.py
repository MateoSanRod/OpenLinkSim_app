import numpy as np
import scipy.optimize as sp_optimize

from app_test.Model.link import Link
from test_utils.timer import get_time


class Simulation:
    def __init__(self, compiled_input, v_angular=0.5, resolution=30):
        self.input = compiled_input
        self.resolution = resolution
        self.v_angular = v_angular
        self.initial_position = 0 if self.input.init_indep_var is None else self.input.init_indep_var
        self.initial_guess = np.array([1, 0]) if self.input.init_dep_var is None else np.array(self.input.init_dep_var)
        self.dep_var_guess = self.initial_guess
        self.rev_to_sim = 1
        self.seconds_per_revolution = (2 * np.pi) / v_angular
        self.numpy = {'numpy': np}
        self.functions = {}
        exec(self.input.eq_geometricas, globals(), self.functions)
        self.geometric_func = self.functions.get('eqs')
        self.node_dict = {f'Node{index + 1}': node for index, node in enumerate(self.input.manipulated_node_equations)}
        self.link_dict = {
            f'Link{index + 1}': Link(np.zeros(2, dtype=int), np.ones(2, dtype=int), **link_data)
            for index, (key, link_data) in enumerate(self.input.link_dict.items())
        }
        self.is_link_dict = len(self.link_dict) > 0
        self.geometry_checker = True

    def compute_image(self, position=None):
        if position is None:
            position = self.initial_position
        node_coordinates = np.empty((0, 2))
        link_line_list = []
        cg_global_cord = []

        self.numpy[self.input.independent_variables] = position
        self.geometric_eq_solver = sp_optimize.root(self.geometric_func, self.dep_var_guess, args=(position,))

        dependent_var_value = self.geometric_eq_solver.x.tolist()
        self.dep_var_guess = dependent_var_value
        self.geometry_checker = self.geometric_eq_solver.success

        for key, value in zip(self.input.dependent_variables.split(','), dependent_var_value):
            self.numpy[key.strip()] = value

        for node_function in self.node_dict.values():
            node_coordinate = self._eval_expression(node_function, node_coordinates)
            node_coordinates = np.vstack((node_coordinates, node_coordinate))

        if self.is_link_dict:
            for link in self.link_dict.values():
                link.node_1 = node_coordinates[link.connections[0]]
                link.node_2 = node_coordinates[link.connections[1]]
                link_line_list.append([link.node_1, link.node_2])
                if link.cg.any() is not None:
                    link.update()
                    cg_global_cord.append(link.get_cg_global_cord())

        return {
            'independent_variable': position,
            'dependent_variable': dependent_var_value,
            'node_coordinates': node_coordinates,
            'link_line_list': np.array(link_line_list),
            'cg_global_cord': np.array(cg_global_cord)
        }

    def _eval_expression(self, expression, point_list):
        local_vars = self.numpy.copy()
        local_vars['point_list'] = point_list
        try:
            return eval(expression, None, local_vars)
        except Exception as e:
            logging.error(f"Error evaluating expression: {expression}")
            logging.exception(e)
            raise EvaluationError(f"Error evaluating expression: {expression}")

    @get_time
    def compute_simulation(self):
        simulation_data = []

        i = self.initial_position
        breakpoint = self.initial_position + (2 * np.pi) * self.rev_to_sim

        while self.geometry_checker:
            i += (2 * np.pi / (360 * self.resolution))
            frame_data = self.compute_image(i)
            simulation_data.append(frame_data)
            if i >= breakpoint:
                break

        if not self.geometry_checker:
            self.geometry_checker = True
            i = self.initial_position + (2 * np.pi / (360 * self.resolution))
            self.dep_var_guess = self.initial_guess
            breakpoint = self.initial_position - (2 * np.pi) * self.rev_to_sim

            while self.geometry_checker:
                i -= (2 * np.pi / (360 * self.resolution))
                frame_data = self.compute_image(i)
                simulation_data.insert(0, frame_data)
                if i <= breakpoint:
                    break
            simulation_data += simulation_data[::-1]

        return simulation_data
if __name__ == '__main__':
    from pathlib import Path

    txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_base.txt').read_text()
    # txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links.txt').read_text()

    simulation = Simulation(txt, 0, 5, None)
    data = simulation.compute_simulation()
    print(np.shape(data))
    print(data[0]['node_coordinates'])

    # iterator
    iterator = False
    if iterator:
        time_lis = []
        for i in range(40):
            simulation = Simulation(txt, 0, 5, None)
            data = simulation.compute_simulation()
            time_lis.append(data)
        print(np.mean(time_lis))
