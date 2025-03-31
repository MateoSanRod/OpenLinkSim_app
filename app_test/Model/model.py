import copy
import logging
import math

import numpy as np
import scipy.optimize as sp_optimize
from scipy.interpolate import interp1d

from app_test.Model.link import Link
from test_utils.timer import get_time
from scipy.ndimage import median_filter, generic_filter



class Simulation:
    def __init__(self, compiled_input, delta_time_factor=0.005):
        self.input = compiled_input
        print(self.input.independent_variables, "independent_variables")
        self.initial_position = np.array(
            [0] * (self.input.independent_variables.count(",") + 1)) if self.input.init_indep_var is None else np.array(
            self.input.init_indep_var) if isinstance(self.input.init_indep_var, (np.ndarray, list)) else np.array([
            self.input.init_indep_var])
        self.independent_variables_dt = np.array(
            [1] * (self.input.independent_variables.count(
                ",") + 1)) if self.input.speed_indep_var is None else np.array(
            self.input.speed_indep_var) if isinstance(self.input.speed_indep_var, (np.ndarray, list)) else np.array([
            self.input.speed_indep_var])
        print("::::::::::::ind::::::::::", self.input.speed_indep_var, "::::::::ind::::::::::")
        self.initial_guess = np.array(
            [0] * (self.input.dependent_variables.count(",") + 1)) if self.input.init_dep_var is None else np.array(
            self.input.init_dep_var) if isinstance(self.input.init_dep_var, (np.ndarray, list)) else np.array([
            self.input.init_dep_var])
        print(self.input.dependent_variables, "dependent_variables", self.input.dependent_variables.count(",") + 1)
        print(self.initial_guess)
        self.dep_var_guess = self.initial_guess
        self.rev_to_sim = 1
        self.delta_time = np.min(delta_time_factor * 1 / (self.independent_variables_dt))

        self.input.delta_time = self.delta_time
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
        self.geometry_checker_flag = False

        self.output_simulation_data = None

    def _update_numpy_variables(var_str, values):
        var_list = [v.strip() for v in var_str.split(',')]
        if len(var_list) == len(values):
            for name, val in zip(var_list, values):
                self.numpy[name] = val
        else:
            if len(var_list) == 1 and len(values) == 1:
                self.numpy[var_list[0]] = values[0]

    def compute_image(self, position=None):
        if position is None:
            position = self.initial_position.copy()
            if position.shape == (1,):
                position = np.float64(position[0])
                self.independent_variables_dt = np.float64(self.independent_variables_dt[0])

        node_coordinates = np.empty((0, 2))
        link_line_list = []
        cg_global_cord = []
        external_forces_positions = []
        external_forces_vectors = []
        link_global_cord_angle = []
        self.numpy[self.input.independent_variables] = position
        self.geometric_eq_solver = sp_optimize.root(self.geometric_func, self.dep_var_guess, args=(position,))

        dependent_var_value = self.geometric_eq_solver.x.tolist()
        self.dep_var_guess = dependent_var_value
        self.geometry_checker = self.geometric_eq_solver.success

        if ',' in self.input.dependent_variables:
            for key, value in zip(self.input.dependent_variables.split(','), dependent_var_value):
                self.numpy[key.strip()] = value

        if ',' in self.input.independent_variables:
            for key, value in zip(self.input.independent_variables.split(','), position):
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
                    cg_global_cord.append(link.local_to_global_coord(link.cg))
                if link.external_forces_positions:
                    for external_forces_position,external_forces_vector in zip(link.external_forces_positions,link.external_forces_vectors):
                        external_forces_positions.append(link.local_to_global_coord(external_forces_position))
                        external_forces_vectors.append(external_forces_vector)
                link_global_cord_angle.append(link.global_coord_angle)

        return {
            'independent_variable': position,
            'dependent_variable': np.round(dependent_var_value,10),
            'node_coordinates': np.round(node_coordinates,10),
            'cg_global_cord': np.round(np.array(cg_global_cord),10),
            'link_angle': np.round(np.array(link_global_cord_angle),10),
            'link_line_list': np.round(np.array(link_line_list),10),
            'external_forces_coord': np.round(np.array(external_forces_positions),10),
            'external_forces_vectors': np.round(np.array(external_forces_vectors),10)
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
        output_simulation_data = []

        i = self.initial_position.copy()

        if i.shape == (1,):
            i = np.float64(i[0])
            self.independent_variables_dt = np.float64(self.independent_variables_dt[0])
        initial_indep_var = i
        if self.input.type_indep_var:
            if not any(type == "P" for type in self.input.type_indep_var):
                breakpoint = np.max((((2 * np.pi) * self.rev_to_sim) / self.independent_variables_dt))
            else:
                breakpoint = 1e6 * self.delta_time
        else:
            breakpoint = np.max((((2 * np.pi) * self.rev_to_sim) / self.independent_variables_dt))
        frame_data = self.compute_image(i)
        while not self.geometry_checker:
            i += (self.independent_variables_dt * self.delta_time)
            frame_data = self.compute_image(i)
            if self.geometry_checker:
                break
        self.geometry_checker = True
        initial_dep_var = self.dep_var_guess
        while self.geometry_checker:
            frame_data = self.compute_image(i)
            output_simulation_data.append(frame_data)
            i += (self.independent_variables_dt * self.delta_time)
            if len(output_simulation_data) * self.delta_time >= breakpoint:
                break

        if not self.geometry_checker:
            self.geometry_checker = True
            self.geometry_checker_flag = True
            i = initial_indep_var
            self.dep_var_guess = initial_dep_var
            while self.geometry_checker:
                i -= (self.independent_variables_dt * self.delta_time)
                frame_data = self.compute_image(i)
                output_simulation_data.insert(0, frame_data)
                if len(output_simulation_data) * self.delta_time >= breakpoint:
                    break

            output_simulation_data = output_simulation_data[1:-1] + [copy.deepcopy(d) for d in
                                                                     output_simulation_data[::-1][2:-1]]
        self.output_simulation_data = output_simulation_data

    @get_time
    def derivate_output_simulation_data_component(self, component_name):
        # Determine how many frames to process
        num_frames = len(self.output_simulation_data)
        if self.geometry_checker_flag:
            num_frames = (len(self.output_simulation_data) + 1) // 2

        # Determine if the component data is 2D (each frame a matrix) or 1D (a vector)
        first_frame = self.output_simulation_data[0][component_name]
        is_2d = (first_frame.ndim == 2) if hasattr(first_frame, "ndim") else False
        num_values = first_frame.shape[0] if is_2d else len(first_frame)

        # Build matrices for the component values
        _x_matrix = np.empty((num_frames, num_values), dtype=float)
        if is_2d:
            _y_matrix = np.empty((num_frames, num_values), dtype=float)
        else:
            _y_matrix = None

        for i in range(num_frames):
            data = self.output_simulation_data[i][component_name]
            if is_2d:
                _x_matrix[i, :] = data[:, 0]
                _y_matrix[i, :] = data[:, 1]
            else:
                _x_matrix[i, :] = data

        # Compute time derivatives for _x_matrix (and _y_matrix if needed)
        _dt_x_matrix = np.gradient(_x_matrix, self.delta_time, axis=0, edge_order=2)
        _dt_x_matrix = self.discontinuity_filter(_dt_x_matrix)
        _ddt_x_matrix = np.gradient(_dt_x_matrix, self.delta_time, axis=0)
        _ddt_x_matrix = self.discontinuity_filter(_ddt_x_matrix)

        if is_2d:
            _dt_y_matrix = np.gradient(_y_matrix, self.delta_time, axis=0, edge_order=2)
            _dt_y_matrix = self.discontinuity_filter(_dt_y_matrix)
            _ddt_y_matrix = np.gradient(_dt_y_matrix, self.delta_time, axis=0)
            _ddt_y_matrix = self.discontinuity_filter(_ddt_y_matrix)

        # If geometry_checker_flag is True, compute reversed gradients and combine them
        if self.geometry_checker_flag:
            if is_2d:
                _x_matrix_rev = _x_matrix[::-1]
                _y_matrix_rev = _y_matrix[::-1]
                _dt_x_matrix_rev = np.gradient(_x_matrix_rev, self.delta_time, axis=0, edge_order=2)
                _dt_x_matrix_rev = self.discontinuity_filter(_dt_x_matrix_rev)
                _dt_y_matrix_rev = np.gradient(_y_matrix_rev, self.delta_time, axis=0, edge_order=2)
                _dt_y_matrix_rev = self.discontinuity_filter(_dt_y_matrix_rev)
                _ddt_x_matrix_rev = np.gradient(_dt_x_matrix_rev, self.delta_time, axis=0)
                _ddt_x_matrix_rev = self.discontinuity_filter(_ddt_x_matrix_rev)
                _ddt_y_matrix_rev = np.gradient(_dt_y_matrix_rev, self.delta_time, axis=0)
                _ddt_y_matrix_rev = self.discontinuity_filter(_ddt_y_matrix_rev)
                # Combine by vertically stacking all rows except the last from the forward matrices
                _dt_x_matrix = np.vstack((_dt_x_matrix[:-1], _dt_x_matrix_rev))
                _dt_y_matrix = np.vstack((_dt_y_matrix[:-1], _dt_y_matrix_rev))
                _ddt_x_matrix = np.vstack((_ddt_x_matrix[:-1], _ddt_x_matrix_rev))
                _ddt_y_matrix = np.vstack((_ddt_y_matrix[:-1], _ddt_y_matrix_rev))
            else:
                _x_matrix_rev = _x_matrix[::-1]
                _dt_x_matrix_rev = np.gradient(_x_matrix_rev, self.delta_time, axis=0, edge_order=2)
                _dt_x_matrix_rev = self.discontinuity_filter(_dt_x_matrix_rev)
                _ddt_x_matrix_rev = np.gradient(_dt_x_matrix_rev, self.delta_time, axis=0)
                _ddt_x_matrix_rev = self.discontinuity_filter(_ddt_x_matrix_rev)
                _dt_x_matrix = np.vstack((_dt_x_matrix[:-1], _dt_x_matrix_rev))
                _ddt_x_matrix = np.vstack((_ddt_x_matrix[:-1], _ddt_x_matrix_rev))

        # For 2D data, compute the modulus (vector magnitude) and update the max values in the first frame
        if is_2d:
            _dt_vec_mod_matrix = np.sqrt(_dt_x_matrix ** 2 + _dt_y_matrix ** 2)
            _ddt_vec_mod_matrix = np.sqrt(_ddt_x_matrix ** 2 + _ddt_y_matrix ** 2)
            _dt_mod_max_vec = [np.percentile(_dt_vec_mod_matrix, 95), np.max(_dt_vec_mod_matrix)]
            _ddt_mod_max_vec = [np.percentile(_ddt_vec_mod_matrix, 95), np.max(_ddt_vec_mod_matrix)]
            self.output_simulation_data[0].setdefault("_dt_max_95%", _dt_mod_max_vec)
            self.output_simulation_data[0].setdefault("_ddt_max_95%", _ddt_mod_max_vec)

        # Update each frame with the computed derivatives
        for idx, frame in enumerate(self.output_simulation_data):
            if is_2d:
                dt_coords = np.column_stack((
                    _dt_x_matrix[idx, :],
                    _dt_y_matrix[idx, :],
                    np.sqrt(_dt_x_matrix[idx, :] ** 2 + _dt_y_matrix[idx, :] ** 2)
                ))
                ddt_coords = np.column_stack((
                    _ddt_x_matrix[idx, :],
                    _ddt_y_matrix[idx, :],
                    np.sqrt(_ddt_x_matrix[idx, :] ** 2 + _ddt_y_matrix[idx, :] ** 2)
                ))
                frame[f"{component_name}_dt"] = np.round(dt_coords, 10)
                frame[f"{component_name}_ddt"] = np.round(ddt_coords, 10)
            else:
                frame[f"{component_name}_dt"] = np.round(_dt_x_matrix[idx, :], 10)
                frame[f"{component_name}_ddt"] = np.round(_ddt_x_matrix[idx, :], 10)
    def discontinuity_filter(self, matrix, trigger_threshold=0.01, window_size=4):
        filtered_matrix = matrix.copy()
        for j in range(matrix.shape[1]):
            col = matrix[:, j]
            col = np.asarray(col, dtype=float).flatten()
            filtered_col = col.copy()

            window_size = max(3, min(window_size, len(col) - 1))
            half_window = window_size // 2

            rolling_median = np.array(
                [np.median(col[max(0, i - half_window):min(len(col), i + half_window + 1)]) for i in range(len(col))])
            rolling_std = np.array(
                [np.std(col[max(0, i - half_window):min(len(col), i + half_window + 1)]) for i in range(len(col))])

            mask = np.abs(col - rolling_median) > (trigger_threshold * rolling_std)

            valid_indices = np.where(~mask)[0]
            if len(valid_indices) > 1:
                interp_func = interp1d(valid_indices, col[valid_indices], kind="linear", fill_value="extrapolate")
                filtered_col[mask] = interp_func(np.where(mask)[0])

            filtered_matrix[:, j][mask] = filtered_col[mask]
        return filtered_matrix

    @get_time
    def compute_forces_and_moments(self):
        if not self.is_link_dict:
            return

        n_nodes = len(self.node_dict)
        n_drv = self.input.independent_variables.count(",") + 1
        total_variables = n_nodes * 2 + n_drv

        drv_list = [var.strip() for var in self.input.independent_variables.split(",")]

        links = list(self.link_dict.values())
        n_links = len(links)
        total_equations = n_links * 3

        node_i_arr = np.array([link.connections[0] for link in links])
        node_j_arr = np.array([link.connections[1] for link in links])
        mass_arr = np.array([link.mass for link in links])
        inertia_arr = np.array([link.inertia for link in links])

        rows = np.arange(n_links)
        rows_fx = 3 * rows
        rows_fy = 3 * rows + 1
        rows_mom = 3 * rows + 2

        for frame_data in self.output_simulation_data:
            node_coords = np.array(frame_data['node_coordinates'])
            cg_arr = np.array(frame_data['cg_global_cord'])
            cg_acc_arr = np.array(frame_data['cg_global_cord_ddt'])
            link_alpha_arr = np.array(frame_data['link_angle_ddt'])

            dynamic_matrix = np.zeros((total_equations, 1))
            dynamic_matrix[rows_fx, 0] = mass_arr * cg_acc_arr[:, 0]
            dynamic_matrix[rows_fy, 0] = mass_arr * (cg_acc_arr[:, 1] - 9.80665)
            dynamic_matrix[rows_mom, 0] = inertia_arr * link_alpha_arr

            for idx, link in enumerate(links):
                F_ext_total = np.zeros(2)
                M_ext_total = 0
                if link.external_forces_positions:
                    for pos, F in zip(link.external_forces_positions, link.external_forces_vectors):
                        r = pos - link.cg
                        F_ext_total += F
                        M_ext_total += r[0] * F[1] - r[1] * F[0]

                dynamic_matrix[3 * idx, 0] += F_ext_total[0]
                dynamic_matrix[3 * idx + 1, 0] += F_ext_total[1]
                dynamic_matrix[3 * idx + 2, 0] += M_ext_total

            geometric_matrix = np.zeros((total_equations, total_variables))
            geometric_matrix[rows_fx, node_i_arr * 2] = 1
            geometric_matrix[rows_fx, node_j_arr * 2] = -1
            geometric_matrix[rows_fy, node_i_arr * 2 + 1] = 1
            geometric_matrix[rows_fy, node_j_arr * 2 + 1] = -1

            node_i_coords = node_coords[node_i_arr]
            node_j_coords = node_coords[node_j_arr]
            r_i = cg_arr - node_i_coords
            r_j = cg_arr - node_j_coords
            geometric_matrix[rows_mom, node_i_arr * 2] = -r_i[:, 1]
            geometric_matrix[rows_mom, node_i_arr * 2 + 1] = r_i[:, 0]
            geometric_matrix[rows_mom, node_j_arr * 2] = r_j[:, 1]
            geometric_matrix[rows_mom, node_j_arr * 2 + 1] = -r_j[:, 0]
            external_forces_vectors = []
            for idx, link in enumerate(links):
                if link.driven_by:
                    try:
                        drv_index = drv_list.index(link.driven_by.strip())
                    except ValueError:
                        drv_index = 0
                    col_idx = n_nodes * 2 + drv_index
                    geometric_matrix[3 * idx + 2, col_idx] = 1
            try:
                if geometric_matrix.shape[0] != geometric_matrix.shape[1]:
                    reaction = np.dot(np.linalg.pinv(geometric_matrix), dynamic_matrix)
                else:
                    reaction = np.linalg.solve(geometric_matrix, dynamic_matrix)
                frame_data['reactions'] = np.round(reaction, 10)
            except np.linalg.LinAlgError:
                logging.error("Geometric matrix is singular; unable to solve for reactions.")
                frame_data['reactions'] = None

            if frame_data['reactions'] is not None:
                reaction_vector = frame_data['reactions'].ravel()
                Fx = reaction_vector[:2 * n_nodes:2]
                Fy = reaction_vector[1:2 * n_nodes:2]
                modulus = np.sqrt(Fx ** 2 + Fy ** 2)
                frame_data['node_reactions'] = np.column_stack((Fx, Fy, modulus))
            else:
                frame_data['node_reactions'] = None
        print("results____________________________________________")
        print(self.output_simulation_data[0])
        print("results____________________________________________")


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from pathlib import Path
    from app_test.Controler.input_compiler import Input

    np.set_printoptions(precision=3, suppress=True, threshold=np.inf, linewidth=200)

    txt_list = [Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_base.txt').read_text(),
                Path(
                    'C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links_v2.txt').read_text(),
                Path(
                    'C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_articulated_quafrilaters_2input_test.txt').read_text(),
                Path(
                    'C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_triangle_articulated.txt').read_text()]
    for txt in txt_list:
        input = Input(app=None, txt=txt)
        compiled_input = input.compile()
        simulation = Simulation(input)
        simulation.compute_simulation()
        simulation.derivate_output_simulation_data_component("node_coordinates")
        simulation.derivate_output_simulation_data_component("link_angle")
        simulation.derivate_output_simulation_data_component("cg_global_cord")
        simulation.compute_forces_and_moments()
        result = simulation.output_simulation_data
        print("_____________")
        print(result[0])
        print("_____________")
        # # simulation.derivate_output_simulation_data_component("node_coordinates", "dt_node_coordinates",grade=1)
        col_index = 0
        val = 0
        #
        # # dx_values_ff =[result[i]["dt_node_coordinates_ddt"] for i in range(len(result))]
        # # print(dx_values_ff)
        # # print(dx_values_ff[-1])
        # # print(len(dx_values_ff))
        # # dx_values_f = [
        # #     result[i]["dt_node_coordinates_dt"][col_index, :][0]
        # #     if "dt_node_coordinates_dt" in result[i]
        # #     else print(i)
        # #     for i in range(len(result))
        # # ]
        # # dx_values_ff =  [
        # #     result[i]["dt_node_coordinates_ddt"][col_index, :][0]
        # #     if "dt_node_coordinates_ddt" in result[i]
        # #     else print(i)
        # #     for i in range(len(result))
        # # ]
        plt.style.use('dark_background')
        plt.figure(figsize=(7, 10))
        for col_index in range(3):
            try:
                x_values = [result[i]["node_coordinates"][col_index][val] for i in range(len(result))]
                dx_values_f = [result[i]["node_coordinates_dt"][col_index][val] for i in range(len(result))]
                dx_values_ff = [result[i]["node_coordinates_ddt"][col_index][val] for i in range(len(result))]

                link_angles = [result[i]["link_angle"][col_index] for i in range(len(result))]
                dt_link_angles = [result[i]["link_angle_dt"][col_index] for i in range(len(result))]
                ddt_link_angles = [result[i]["link_angle_ddt"][col_index] for i in range(len(result))]
            except:
                pass
            # plt.plot(np.rad2deg([result[i]['independent_variable'] for i in range(len(result))]), x_values,label='pos_   (col 2)', linewidth=1.5)
            # plt.plot(np.linspace(0, 100, len(x_values)), x_values, label='pos_   (col 2)', linewidth=1.5)

            # plt.plot(np.linspace(0, 100, len(x_values)), x_values, label='vel_ (col 2)', color="b", linewidth=1,
            #          alpha=1)
            # plt.plot(np.linspace(0, 100, len(dx_values_ff)), dx_values_f, label='vel_ (col 2)', color="g", linewidth=1,
            #          alpha=1)

            # if col_index not in [0,3]:
            # plt.plot(np.linspace(0, 100, len(x_values)), x_values, label=f'pos_ (col {col_index})', linewidth=1,
            #          alpha=1)
            # plt.plot(np.linspace(0, 100, len(dx_values_f)), dx_values_f, label=f'vel_ (col {col_index})', linewidth=1,
            #          alpha=1)
            plt.plot(np.linspace(0, 100, len(dx_values_f)), link_angles, label=f'ang_pos rad (col {col_index})',
                     linewidth=1,  # marker='.',
                     alpha=1)

            plt.plot(np.linspace(0, 100, len(dx_values_f)), dt_link_angles, label=f'ang_vel rad/s (col {col_index})',
                     linewidth=1, linestyle='--',  # marker='.',
                     alpha=1)
            plt.plot(np.linspace(0, 100, len(dx_values_f)), ddt_link_angles, label=f'ang_acc rad/s^2 (col {col_index})',
                     linewidth=1, linestyle=':', marker='.',
                     alpha=1)
            # plt.plot(np.linspace(0, 100, len(dx_values_ff)), dx_values_ff, label=f'acc_ (col {col_index})', linewidth=1,
            #          alpha=1)
            # except:
            #     pass
            print(":::::::::::::::::")
            print(len(dx_values_ff))
            print(":::::::::::::::::")
            # sdyval = []
            # xvaasdf = np.linspace(0, 2, 100)  # Generate 100 points between 0 and 2
            # exp = 2  # Exponential value to adjust decreasing gradient
            # threshgold = 1  # Threshold where behavior changes
            # x_end = xvaasdf[-1]  # Last value of the linspace
            #
            # # Loop to generate y values based on condition
            # for x in xvaasdf:
            #     if x <= threshgold:
            #         # Linear part (initial part of the function)
            #         y = x
            #     else:
            #         # Non-linear part (after the threshold)
            #         falloff_factor = exp
            #         t = (x_end - (x - threshgold) - threshgold) / (x_end - threshgold)
            #         y = threshgold + (x_end - threshgold) * (
            #                 1 - (x_end - (x - threshgold) - threshgold) / (x_end - threshgold) ** falloff_factor)
            #     sdyval.append(y)
            # plt.plot(xvaasdf, sdyval, label='acc_ (col 2)', color="r", linewidth=1,
            #          alpha=1)
            #
            # plt.plot(xvaasdf, np.gradient(sdyval), label='acc_ (col 2)', color="b", linewidth=1,
            #          alpha=1)

            # plt.plot(np.linspace(0,100,len(ddx_values_f)),ddx_values_f, label='acc_ (col 2)',color ="r",linewidth=.75,alpha=0.5 )
            # plt.plot(np.linspace(0, 100, len(dx_values_b)), dx_values_b, label='vel_ (col 2)', color="orange", linewidth=.75,
            #          alpha=0.5)
            # plt.plot(np.linspace(0,100,len(ddx_values_b)),ddx_values_b, label='acc_ (col 2)',color ="r",linewidth=.75,alpha=0.5 )
            plt.ylabel('Values')
            # plt.ylim(-max(np.abs(x_values)) * 5, max(np.abs(x_values)) * 5)
            plt.legend(loc="lower center", bbox_to_anchor=(0.5, 1.025), ncol=3,
                       labelspacing=0.25, fontsize=8, frameon=False)

            # plt.xticks(np.arange(-95,95,45))
            # plt.xticks(np.arange(-95,95,1/simulation.resolution),minor=True)

            # plt.xticks(np.arange(-0,361,45))
            plt.grid(color='dimgray', linestyle='--', linewidth=.5)

            # plt.xticks(np.arange(-0,361,1/simulation.resolution),minor=True)
            # plt.grid(which='both', visible=True,linestyle=(0,(1,10)), linewidth=.25)

            # plt.savefig("C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test.png", dpi=300)

            # print(result[0]['node_coordinates'])

            # iterator = False
            # if iterator:
            #     time_lis = []
            #     for i in range(40):
            #         simulation = Simulation(txt, 0, 5, None)
            #         data = simulation.compute_simulation()
            #         time_lis.append(data)
            #     print(np.mean(time_lis))

        plt.show()
