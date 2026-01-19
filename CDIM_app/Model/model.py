import copy
import logging
import types

import numpy as np
import scipy.optimize as sp_optimize

from .link import Link
from test_utils.timer import get_time


class Simulation:
    def __init__(self, compiled_input, delta_time_factor=0.006, simu_time=None):
        self.input = compiled_input
        self.simu_time = simu_time
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
        self.independent_variables_ddt = np.array(
            [0] * (self.input.independent_variables.count(
                ",") + 1)) if self.input.accel_indep_var is None else np.array(
            self.input.accel_indep_var) if isinstance(self.input.accel_indep_var,
                                                      (np.ndarray, list)) else np.array([
            self.input.accel_indep_var])
        print("::::::::::::ind::::::::::", self.input.speed_indep_var, "::::::::ind::::::::::")

        self.initial_guess = np.array(np.random.default_rng().uniform(0, 0,
                                                                      size=self.input.dependent_variables.count(
                                                                          ",") + 1)) if self.input.init_dep_var is None else np.array(
            self.input.init_dep_var) if isinstance(self.input.init_dep_var, (np.ndarray, list)) else np.array([
            self.input.init_dep_var])
        print(self.input.dependent_variables, "dependent_variables", self.input.dependent_variables.count(",") + 1)
        self.dep_var_guess = self.initial_guess
        self.rev_to_sim = 1
        self.delta_time = np.min(delta_time_factor * 1 / (self.independent_variables_dt))

        self.input.delta_time = self.delta_time
        self.numpy = {'numpy': np}
        self.numpy.update({name: getattr(np, name)
                           for name in dir(np) if self._is_public_math(name, getattr(np, name))})
        exec_globals = dict(self.numpy)
        exec_globals.update(globals())
        exec_globals['np'] = np
        self.functions = {}
        exec(self.input.eq_code, exec_globals, self.functions)
        self.geometric_func = self.functions.get('eqs')
        self.node_dict = {f'Node{index + 1}': node for index, node in enumerate(self.input.nodes_code)}
        _allowed = {
            "connections", "length", "cg",
            "mass", "inertia", "driven_by",
            "external_forces", "points"
        }

        self.link_dict = {
            f'Link{idx + 1}':
                Link(**{k: v for k, v in data.items() if k in _allowed})

            for idx, data in enumerate(self.input.link_dict.values())

        }
        self._explicit_revolute = set()
        for key, ln in self.link_dict.items():
            cfg = self.input.link_dict[key]
            if cfg.get("is_revolute"):
                for local in cfg["rev_nodes"]:
                    g = ln.connections[local]
                    self._explicit_revolute.add(g)
        self._explicit_slider = {}

        self.links = list(self.link_dict.values())
        self.n_links = len(self.link_dict)
        self.n_nodes = len(self.node_dict)

        self.is_link_dict = len(self.link_dict) > 0
        self._prev_dep = None
        self.geometry_checker = True
        self.geometry_checker_flag = False

        self.output_simulation_data = None

        self._prev_xy = None
        self._prev_slider_axis = {}

    @staticmethod
    def _is_public_math(name, obj):
        if name.startswith('_'):
            return False
        if isinstance(obj, (np.ufunc, types.BuiltinFunctionType, types.FunctionType)):
            return True
        if isinstance(obj, (float, int, np.ndarray)):
            return True
        return False

    # Per frame slider axis computation
    def _update_link_dict(self, fr) -> None:
        TOL = 1.0e-9
        xy  = fr["node_coordinates"]

        axes = [None]*self.n_nodes

        for key, ln in self.link_dict.items():
            cfg = self.input.link_dict[key]
            if not cfg["is_prismatic"]:
                continue

            for local, ang, is_abs in zip(cfg["pris_nodes"],
                                          cfg["pris_axis"],
                                          cfg["pris_abs"]):
                g_n = ln.connections[local]
                ang = np.deg2rad(ang)

                if is_abs:  # absolute axis
                    ax = np.array([np.cos(ang), np.sin(ang)])
                else:
                    other = ln.connections[1 - local]
                    v = xy[g_n] - xy[other]
                    if np.linalg.norm(v) < TOL:
                        v = self._prev_slider_axis.get(g_n, np.array([1.0, 0.0]))
                    v /= np.linalg.norm(v)
                    if abs(ang) > 1e-12:
                        c, s = np.cos(ang), np.sin(ang)
                        v = np.array([c * v[0] - s * v[1],
                                      s * v[0] + c * v[1]])
                    ax = v

                ax /= np.linalg.norm(ax) + 1e-12
                axes[g_n] = ax
                self._prev_slider_axis[g_n] = ax
                self._explicit_slider[g_n] = ax

        if self._prev_xy is not None:
            disp = xy-self._prev_xy
            for n in range(self.n_nodes):
                if axes[n] is not None:
                    continue
                d = disp[n]
                if np.linalg.norm(d) > TOL:
                    ax = d/np.linalg.norm(d)
                    axes[n] = ax
                    self._prev_slider_axis[n] = ax
                elif n in self._prev_slider_axis:
                    axes[n] = self._prev_slider_axis[n]

        self._prev_xy = xy.copy()
        fr["slider_axis"] = axes

    def compute_image(self, position=None, is_first_frame=False):
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
        link_points_global = []
        self.numpy[self.input.independent_variables] = position
        self.geometric_eq_solver = sp_optimize.root(self.geometric_func, self.dep_var_guess, args=(position,))

        dependent_var_value = self.geometric_eq_solver.x.tolist()
        if self._prev_dep is None:
            self.dep_var_guess = dependent_var_value.copy()
        else:
            dep_var_guess_gradient = np.array(dependent_var_value) - np.array(self._prev_dep)
            self.dep_var_guess = dependent_var_value + dep_var_guess_gradient

        self._prev_dep = dependent_var_value.copy()
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
                nodes_glob = node_coordinates[link.connections]
                link.j1, link.j2 = nodes_glob[0], nodes_glob[1]
                link_line_list.append(nodes_glob)
                if link.cg.any() is not None:
                    link.update()
                    cg_global_cord.append(link.local_to_global_coord(link.cg))
                    if link.points_global:
                        link_points_global.append(link.points_global)
                if link.external_forces_positions:
                    for external_forces_position, external_forces_vector in zip(link.external_forces_positions,
                                                                                link.external_forces_vectors):
                        external_forces_positions.append(link.local_to_global_coord(external_forces_position))
                        external_forces_vectors.append(external_forces_vector)
                link_global_cord_angle.append(link.global_coord_angle)
        frame_data = {
            'independent_variable': np.round(position, 10),
            'dependent_variable': np.round(dependent_var_value, 10),
            'node_coordinates': np.round(node_coordinates, 10),
            'cg_global_cord': np.round(np.array(cg_global_cord), 10),
            'link_angle': np.round(np.array(link_global_cord_angle), 10),
            'link_line_list': link_line_list,
            'external_forces_coord': np.round(np.array(external_forces_positions), 10),
            'external_forces_vectors': np.round(np.array(external_forces_vectors), 10)
        }
        self._update_link_dict(frame_data)
        if link_points_global:
            frame_data['link_extra_points'] = np.round(np.array(np.concatenate(link_points_global)), 10)
        if is_first_frame:
            if link_points_global:
                frame_data['link_extra_points_per_link'] = \
                    [np.round(np.asarray(lst), 10) for lst in link_points_global]
        return frame_data

    def _eval_expression(self, expression, point_list):
        local_vars = self.numpy.copy()
        local_vars['point_list'] = point_list
        try:
            return eval(expression, None, local_vars)
        except Exception as e:
            logging.error(f"Error evaluating expression: {expression}")
            logging.exception(e)
            raise EvaluationError(f"Error evaluating expression: {expression}")

    def compute_simulation(self):
        output_simulation_data = []
        limiting_input = np.argmin(self.independent_variables_dt)

        pos = self.initial_position.copy()
        vel = self.independent_variables_dt.copy()
        acc = self.independent_variables_ddt.copy()
        if pos.shape == (1,):
            pos = np.float64(pos[0])
            vel = np.float64(vel[0])
            acc = np.float64(acc[0])
        else:
            pos = np.array(pos, dtype=float)
            vel = np.array(vel, dtype=float)
            acc = np.array(acc, dtype=float)

        initial_pos = pos.copy()
        initial_vel = vel.copy()
        if self.simu_time is not None:
            big_time = self.simu_time
            max_cycles_angle = None

        elif self.input.type_indep_var and any(t.strip() == "P" for t in self.input.type_indep_var):
            max_cycles_angle = None
            big_time = 1e6 * self.delta_time
        else:
            if isinstance(pos, np.ndarray):
                angle_0 = pos[limiting_input]
            else:
                angle_0 = pos

            final_angle = angle_0 + (2 * np.pi * self.rev_to_sim)
            max_cycles_angle = final_angle
            big_time = None



        frame_data = self.compute_image(pos)
        while not self.geometry_checker:
            pos += vel * self.delta_time + 0.5 * acc * (self.delta_time ** 2)
            vel += acc * self.delta_time
            frame_data = self.compute_image(pos)
            if self.geometry_checker:
                break
        self.initial_guess = self.dep_var_guess

        self.geometry_checker = True
        is_first_frame = True
        while self.geometry_checker:
            frame_data = self.compute_image(pos, is_first_frame)
            if is_first_frame:
                is_first_frame = False

            output_simulation_data.append(frame_data)
            pos += vel * self.delta_time + 0.5 * acc * (self.delta_time ** 2)
            vel += acc * self.delta_time

            if max_cycles_angle is not None:
                current_angle = pos[limiting_input] if isinstance(pos, np.ndarray) else pos

                if isinstance(initial_pos, np.ndarray):
                    init_angle = initial_pos[limiting_input]
                    curr_angle = pos[limiting_input]
                else:
                    init_angle = initial_pos
                    curr_angle = pos

                if (init_angle < max_cycles_angle and curr_angle >= max_cycles_angle):
                    break
                elif (init_angle > max_cycles_angle and curr_angle <= max_cycles_angle):
                    break
            else:
                if (len(output_simulation_data) * self.delta_time) >= big_time:
                    break

        if not self.geometry_checker:
            self.geometry_checker = True
            self.geometry_checker_flag = True
            self.dep_var_guess = self.initial_guess
            pos = initial_pos
            vel = initial_vel

            neg_delta_time = -self.delta_time

            while self.geometry_checker:

                pos += vel * neg_delta_time + 0.5 * acc * (neg_delta_time ** 2)
                vel += acc * neg_delta_time

                frame_data = self.compute_image(pos)
                output_simulation_data.insert(0, frame_data)

                if max_cycles_angle is not None:
                    current_angle = pos[limiting_input] if isinstance(pos, np.ndarray) else pos
                else:
                    if (len(output_simulation_data) * self.delta_time) >= big_time:
                        break
            frame_data = self.compute_image(pos, is_first_frame=True)
            output_simulation_data[1] = frame_data

            output_simulation_data = (
                    output_simulation_data[1:-1] +
                    [copy.deepcopy(d) for d in output_simulation_data[::-1][2:-1]]
            )

        self.output_simulation_data = output_simulation_data

    @get_time
    def derivate_output_simulation_data_component(self, component_name):
        num_frames = len(self.output_simulation_data)
        if self.geometry_checker_flag:
            num_frames = (len(self.output_simulation_data) + 1) // 2

        first_frame = self.output_simulation_data[0][component_name]
        is_2d = (first_frame.ndim == 2) if hasattr(first_frame, "ndim") else False
        num_values = first_frame.shape[0] if is_2d else len(first_frame)

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

        _dt_x_matrix = np.gradient(_x_matrix, self.delta_time, axis=0, edge_order=2)
        _dt_x_matrix = self.discontinuity_filter(_dt_x_matrix)
        _ddt_x_matrix = np.gradient(_dt_x_matrix, self.delta_time, axis=0)
        _ddt_x_matrix = self.discontinuity_filter(_ddt_x_matrix)

        if is_2d:
            _dt_y_matrix = np.gradient(_y_matrix, self.delta_time, axis=0, edge_order=2)
            _dt_y_matrix = self.discontinuity_filter(_dt_y_matrix)
            _ddt_y_matrix = np.gradient(_dt_y_matrix, self.delta_time, axis=0)
            _ddt_y_matrix = self.discontinuity_filter(_ddt_y_matrix)

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

        if is_2d:
            _dt_vec_mod_matrix = np.sqrt(_dt_x_matrix ** 2 + _dt_y_matrix ** 2)
            _ddt_vec_mod_matrix = np.sqrt(_ddt_x_matrix ** 2 + _ddt_y_matrix ** 2)
            _dt_mod_max_vec = [np.percentile(_dt_vec_mod_matrix, 95), np.max(_dt_vec_mod_matrix)]
            _ddt_mod_max_vec = [np.percentile(_ddt_vec_mod_matrix, 95), np.max(_ddt_vec_mod_matrix)]
            self.output_simulation_data[0].setdefault("_dt_max_95%", _dt_mod_max_vec)
            self.output_simulation_data[0].setdefault("_ddt_max_95%", _ddt_mod_max_vec)

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

    def discontinuity_filter(self, matrix, trigger_threshold=0.01, window_size=5):
        filtered_matrix = matrix.copy()

        for j in range(matrix.shape[1]):
            col = np.asarray(matrix[:, j], float).ravel()
            n = col.size

            window_size = max(3, min(window_size, n - 1))
            half = window_size // 2

            med = np.array([np.median(col[max(0, i - half):min(n, i + half + 1)])
                            for i in range(n)])
            std = np.array([np.std(col[max(0, i - half):min(n, i + half + 1)])
                            for i in range(n)])
            std[std < 1e-12] = 1e-12

            mask = np.abs(col - med) > trigger_threshold * std

            mask[:window_size] = False
            mask[-window_size:] = False

            bad = np.where(mask)[0]
            good = np.where(~mask)[0]

            if good.size > 1 and bad.size > 0:
                col[bad] = np.interp(bad, good, col[good])

            filtered_matrix[:, j] = col

        return filtered_matrix

    def _compute_boundary_conditions(self, tol: float = 1e-8) -> None:
        """
            0 → free
            1 → slider
            2 → ground-pin
        """

        self.node_bc_state = np.zeros(self.n_nodes, dtype=int)

        if len(self.output_simulation_data) >= 2:
            coords = np.array([fr["node_coordinates"][:, :2]
                               for fr in self.output_simulation_data])

            disp = coords - coords[0]
            max_disp = np.max(np.abs(disp), axis=0)

            rigid = (max_disp[:, 0] < tol) & (max_disp[:, 1] < tol)
            self.node_bc_state[rigid] = 2
        else:
            pass

        for n in self._explicit_slider:
            self.node_bc_state[n] = 1
        for n in self._explicit_revolute:
            self.node_bc_state[n] = 0
        self.output_simulation_data[0]["node_bc_state"] = self.node_bc_state.copy()

    def _prepare_joint_tables(self) -> None:
        """
        0 → free
        1 → slider
        2 → ground-pin

        sets up:
            self._joints[node]      → SimpleNamespace(index, ncol, axis)
            self._joint_links[node] → [link_id, …]
            self._ncols_basic       → Columns before DOFs are added
            self._total_cols        → n of unknowns
        """

        self._compute_boundary_conditions()

        Joint = types.SimpleNamespace
        self._joints: dict[int, Joint] = {}
        self._joint_links: dict[int, list[int]] = {}

        # build the owner map
        for lid, ln in enumerate(self.link_dict.values()):
            for n in ln.connections:
                self._joint_links.setdefault(n, []).append(lid)

        col = 0
        MAX_DEV = 1e-4
        GROUND = -1

        # walk every node and sets DOF
        for node, owners in self._joint_links.items():

            if node in self._explicit_revolute:
                axis = None
                ncol = 2

            elif node in self._explicit_slider:
                axis = self._explicit_slider[node]
                ncol = 1
                self.node_bc_state[node] = 1

            elif self.node_bc_state[node] == 2:
                axis = None
                ncol = 2
                self._joint_links[node].append(-1)


            else:
                XY = np.array([fr["node_coordinates"][node, :2]
                               for fr in self.output_simulation_data])
                cov = np.cov((XY - XY.mean(0)).T)
                evals, evecs = np.linalg.eigh(cov)

                if evals[0] < MAX_DEV * evals[1]:  # moves on a straight line
                    axis = evecs[:, np.argmax(evals)]
                    axis /= np.linalg.norm(axis)
                    ncol = 1
                    self.node_bc_state[node] = 1  # slider (auto)
                    self._joint_links.setdefault(node, []).append(-1)  # ⇦ imaginary owner
                else:
                    axis = None
                    ncol = 2

            # decide whether this node should get reaction unknowns

            if (
                    len(owners) == 1
                    and (
                    self.node_bc_state[node] == 0  # free
                    or node in self._explicit_slider  # user slider
            )
            ):
                continue
            self._joints[node] = types.SimpleNamespace(index=col, ncol=ncol, axis=axis)
            col += ncol

        self._auto_slider_nodes = {
            n for n in range(self.n_nodes)
            if self.node_bc_state[n] == 1 and n not in self._explicit_slider
        }

        # independent variables column --------------------------
        self._ncols_basic = col
        drv_names = [s.strip() for s in self.input.independent_variables.split(",")]
        self._drv_cols = {name: self._ncols_basic + i
                          for i, name in enumerate(drv_names)}
        self._total_cols = self._ncols_basic + len(self._drv_cols)

        self.output_simulation_data[0]["node_bc_state"] = self.node_bc_state.copy()

        self.output_simulation_data[0]["slider_axis"] = [
            self._explicit_slider.get(i)
            if i not in self._explicit_slider and
               i in self._joints and
               self._joints[i].ncol == 1
            else self._explicit_slider[i]
            if i in self._explicit_slider or
               (i in self._joints and self._joints[i].ncol == 1)
            else None
            for i in range(self.n_nodes)
        ]
        for n in range(self.n_nodes):
            if n in self._auto_slider_nodes:
                self._joint_links[n].append(-1)

    @get_time
    def compute_forces_and_moments(self, g: float = 0.0):
        # build the joint tables
        self._prepare_joint_tables()

        # per‐link parameters
        m = np.asarray([ln.mass for ln in self.links])
        I = np.asarray([ln.inertia for ln in self.links])

        # pick onlylinks with ≥1 connection
        active_links = [
            lid for lid, ln in enumerate(self.links)
            if len(ln.connections) > 0 or ln.driven_by
        ]
        eq_count = 3 * len(active_links)

        # matrix system G · R = D
        G = np.zeros((eq_count, self._total_cols))
        D = np.zeros(eq_count)

        eq_map = {lid: i for i, lid in enumerate(active_links)}

        per_link_F = [
            np.zeros((ln.n_joints, 2))
            for ln in self.links
        ]
        Fx_node = np.zeros(self.n_nodes)
        Fy_node = np.zeros(self.n_nodes)

        # loop over every saved frame
        for fr in self.output_simulation_data:
            node_actions = {n: [] for n in range(self.n_nodes)}

            # inertial & gravitational terms
            aG = np.asarray(fr["cg_global_cord_ddt"])
            if g != 0:
                aG[:, 1] += g
            alpha = np.asarray(fr["link_angle_ddt"])

            D.fill(0.0)
            for lid in active_links:
                block = 3 * eq_map[lid]
                D[block + 0] = m[lid] * aG[lid, 0]
                D[block + 1] = m[lid] * aG[lid, 1]
                D[block + 2] = I[lid] * alpha[lid]

            # add external forces
            for pos, F in zip(fr["external_forces_coord"],
                              fr["external_forces_vectors"]):
                pos = np.asarray(pos).ravel()
                F = np.asarray(F).ravel()
                k = np.argmin(np.linalg.norm(
                    pos - fr["cg_global_cord"], axis=1
                ))
                if k not in eq_map:
                    continue
                blk = 3 * eq_map[k]
                D[blk + 0] += F[0]
                D[blk + 1] += F[1]
                r = pos - fr["cg_global_cord"][k]
                D[blk + 2] += r[0] * F[1] - r[1] * F[0]

            # geometryc matrix construction
            G.fill(0.0)
            node_xy = np.asarray(fr["node_coordinates"])
            cg_xy = np.asarray(fr["cg_global_cord"])

            for lid in active_links:
                ln = self.links[lid]
                base = 3 * eq_map[lid]

                for node in ln.connections:
                    J = self._joints.get(node)
                    if J is None:
                        continue
                    if lid < 0:
                        continue

                    r = cg_xy[lid] - node_xy[node]
                    if J.ncol == 2:
                        c = J.index
                        G[base + 0, c + 0] += 1
                        G[base + 1, c + 1] += 1
                        G[base + 2, c + 0] += r[1]
                        G[base + 2, c + 1] += -r[0]
                    else:
                        nx, ny = -J.axis[1], J.axis[0]
                        c = J.index
                        G[base + 0, c] += nx
                        G[base + 1, c] += ny
                        G[base + 2, c] += -r[0] * ny + r[1] * nx

                if ln.driven_by:
                    G[base + 2, self._drv_cols[ln.driven_by.strip()]] = 1.0


            for node, owners in self._joint_links.items():
                J = self._joints.get(node)
                if node in self._auto_slider_nodes:
                    continue
                for lid in owners[1:]:
                    if lid not in eq_map:
                        continue
                    rs = slice(3 * eq_map[lid], 3 * eq_map[lid] + 3)
                    G[rs, J.index:J.index + J.ncol] *= -1.0

            # solve
            R, *_ = np.linalg.lstsq(G, D, rcond=None)

            # output handeling to obtain nodal forces
            for node, owners in self._joint_links.items():
                J = self._joints.get(node)
                if J is None:
                    continue

                if J.ncol == 2:
                    Fxy = R[J.index:J.index + 2]
                else:
                    q = R[J.index]
                    nx, ny = -J.axis[1], J.axis[0]
                    Fxy = np.array([q * nx, q * ny])

                for j, lid in enumerate(owners):
                    if lid not in eq_map:
                        node_actions[node].append(Fxy)
                        continue


                    local_j = np.where(self.links[lid].connections == node)[0][0]
                    node_actions[node].append(Fxy)

                    Fx_node.fill(0.0)
                    Fy_node.fill(0.0)

                    for n, lst in node_actions.items():
                        if not lst:
                            continue
                        is_ground_pin = (self.node_bc_state[n] == 2)
                        is_auto_slider = (n in self._auto_slider_nodes)

                        if not (is_ground_pin or is_auto_slider):
                            continue
                        if node in self._auto_slider_nodes:
                            sign = - 1
                        elif j == 0:
                            sign = -1
                        else:
                            sign = +1

                        Fsum = np.sum(lst, axis=0)
                        Fx_node[n] = -Fsum[0]*sign
                        Fy_node[n] = -Fsum[1]*sign

            for n in self._explicit_slider:
                Fx_node[n] = Fy_node[n] = 0.0
            fr["link_joint_forces"] = per_link_F
            fr["node_reactions"] = np.column_stack((
                Fx_node,
                Fy_node,
                np.hypot(Fx_node, Fy_node)
            ))
            fr["driver_loads"] = R[self._ncols_basic:]

        self.output_simulation_data[0]["is_grounded_slider"] = [
            n in self._auto_slider_nodes for n in range(self.n_nodes)
        ]

        print(
            f"Solved {len(self.output_simulation_data)} frames  "
            f"({self._total_cols} unknowns, "
            f"{len(active_links)} active links)"
        )
        self.output_simulation_data[0]["node_reactions_max"] = max(
            np.linalg.norm(f["node_reactions"][:, :2], axis=1).max()
            for f in self.output_simulation_data
        ) or 1.0

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from pathlib import Path
    from ..Controler.input_compiler import Input
    import pandas as pd
    from scipy.ndimage import gaussian_filter

    # np.set_printoptions(precision=3, suppress=True, threshold=np.inf, linewidth=200)

    txt_list = [
        Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_base.txt').read_text(),
        # Path(
        #     'C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links_v2.txt').read_text(),
        # Path(
        #     'C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_articulated_quafrilaters_2input_test.txt').read_text(),
        # Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_triangle_articulated.txt').read_text(),
        #
        # Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_p4_7.txt').read_text()
    ]
    for txt in txt_list:
        input = Input(app=None, txt=txt)
        compiled_input = input.compile()
        simulation_time = None
        timestep = 0.0035
        gravity = 0
        simulation = Simulation(input, delta_time_factor=timestep, simu_time=simulation_time)
        simulation.compute_simulation()
        simulation._prepare_joint_tables()
        simulation.derivate_output_simulation_data_component("node_coordinates")
        simulation.derivate_output_simulation_data_component("link_angle")
        simulation.derivate_output_simulation_data_component("cg_global_cord")
        simulation.compute_forces_and_moments(g=gravity)
        result = simulation.output_simulation_data
        # # simulation.derivate_output_simulation_data_component("node_coordinates", "dt_node_coordinates",grade=1)
        col_index = 2
        val = 0
        #
        #
        # node_idx = 2  # “node 4” in 0-based indexing
        # print("-------------------------")
        # print(result[0]["driver_loads"])
        # print("-------------------------")
        # # extract raw data
        # x = np.array([f["cg_global_cord"][col_index, :][0] for f in result])
        # dx = np.array([f["cg_global_cord_dt"][col_index, :][0] for f in result])
        # ddx = np.array([f["cg_global_cord_ddt"][col_index, :][0] for f in result])
        # n = len(result)
        # half = n // 3
        #
        # # first segment: from 3.45 down to (but not including) 1
        # linsp = np.linspace(4, .8, n, endpoint=False)
        # #
        # # # second segment: from 1 up to 2, with exactly the remaining points
        # # linsp2 = np.linspace(1, 2.8, n - half)
        #
        # # linsp = np.concatenate([linsp1, linsp2])
        # dl = np.array([-f["driver_loads"] * lin * 1.2 for f, lin in zip(result, linsp)])
        # # x = np.array([f['node_reactions'][node_idx][0] for f in result])
        # # y = np.array([f['node_reactions'][node_idx][1] for f in result])
        # ivar = np.array([f['independent_variable'] for f in result])
        # t = np.arange(0, simulation.delta_time * len(x), simulation.delta_time)
        #
        # print(ivar[0])
        # print(ivar[0])
        # print(ivar[0])
        # print(ivar[-1])
        # print(ivar[-1])
        #
        # plt.rcParams['mathtext.fontset'] = 'custom'
        # plt.rcParams['font.family'], plt.rcParams['mathtext.rm'], plt.rcParams['mathtext.it'], \
        #     plt.rcParams['mathtext.bf'], plt.rcParams['mathtext.sf'] = 5 * ['Times New Roman']
        # #
        # fig, ax1 = plt.subplots(figsize=(10, 5))
        # plt.rcParams['hatch.linewidth'] = 3
        #
        # # Plot for df['column1'] on the left y-axis
        # ax1.plot(t, x,
        #          color='tab:blue',
        #          linestyle='--',
        #          label=r"$x_{cg_x}(t)$", linewidth=1)
        # ax1.set_ylabel(r'Displacement [$m$]', color='tab:blue')
        # ax1.tick_params(axis='y', labelcolor='tab:blue')
        #
        # # Create a second y-axis for velocity
        # ax2 = ax1.twinx()
        # ax2.plot(t, dx,
        #          color='tab:red',
        #          linestyle='--',
        #          label=r"$V_{cg_x}(t)$", linewidth=1)
        # ax2.set_ylabel('Velocity [$m/s$]', color='tab:red')
        # ax2.tick_params(axis='y', labelcolor='tab:red')
        #
        # # Create a third y-axis for acceleration
        # ax3 = ax1.twinx()
        # ax3.spines['right'].set_position(('outward', 60))  # Offset the third axis
        # ax3.plot(t, ddx,
        #          color='tab:green',
        #          linestyle='--',
        #          label=r"$a_{cg_x}(t)$", linewidth=1)
        # ax3.set_ylabel('Acceleration [$m/s^2$]', color='tab:green')
        # ax3.tick_params(axis='y', labelcolor='tab:green')
        #
        # ax1.set_xticks(np.arange(0, t[-1] + .2, 0.2))
        # ax1.set_xticks(np.arange(0, t[-1] + .2, 0.1), minor=True)
        # ax1.set_xlim(0, t[-1])
        #
        # # Additional settings for the x-axis
        # ax1.set_xlabel('Time (s)')
        # ax1.grid(True, linestyle='-.', linewidth=0.5, alpha=0.25)
        #
        # # Show the legend for all axes
        # fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=7)


        # # Save or display the plot
        # # Adjust layout to prevent clipping when saving
        # fig.tight_layout(rect=[0, 0, 1, 0.95])
        #
        # # Save or display the plot
        # fig.savefig("test.png", dpi=700)
        # plt.show()

        # — style to match your numer‐deriv example —

        # df = pd.read_csv("C:/Users/teoto/OneDrive/Escritorio/RotaryMotor223.csv",
        #                  skiprows=1, header=0,  # treat the next line as the header
        #                  index_col=False,  # do not interpret any column as the index
        #                  quotechar='"')
        # df
        # t = np.array(df["Time (sec)"])
        # torque_1 = np.array(df.iloc[:, 1])  # the second column, “Motor Torque12 (newton‑meter)”
        # torque = gaussian_filter(torque_1, sigma=2.0)
        #
        # fig, ax = plt.subplots(figsize=(10, 5))
        # ax.plot(t, torque, linestyle='--', lw=1, color="tab:blue")
        #
        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel(r"Torque ($N/m$)")
        # # ax.legend(loc="lower left")
        # ax.grid(True, linestyle='-.', linewidth=0.5, alpha=0.25)
        # ax.set_xlim(0, 2)
        # fig.tight_layout()
        # fig.savefig("test.png", dpi=700)
        # plt.show()

        plt.style.use('dark_background')
        plt.figure(figsize=(7, 10))
        for col_index in range(3):
            if col_index == 0:
                continue
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
            plt.plot(np.linspace(0, 100, len(dx_values_f)), x_values, label=f'lin_pos rad (col {col_index})',
                     linewidth=1,  # marker='.',
                     alpha=1)

            plt.plot(np.linspace(0, 100, len(dx_values_f)), dx_values_f, label=f'lin_vel rad/s (col {col_index})',
                     linewidth=1, linestyle='--',  # marker='.',
                     alpha=1)
            plt.plot(np.linspace(0, 100, len(dx_values_f)), dx_values_ff, label=f'lin_acc rad/s^2 (col {col_index})',
                     linewidth=1, linestyle=':',
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
            plt.legend(loc="lower center", bbox_to_anchor=(0.5, 1.025), ncol=2,
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
