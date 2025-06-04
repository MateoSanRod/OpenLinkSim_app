import numpy as np
from CDIM_app.Model.utils import *


class Link:
    def __init__(self,
                 connections,
                 length=None,
                 cg=None,
                 mass=None,
                 inertia=None,
                 driven_by=None,
                 external_forces=None,
                 points=None):
        self.connections = eval(connections) - np.ones(len(eval(connections)), dtype=int)
        self.n_joints = len(self.connections)
        self.j1, self.j2 = np.zeros(2),np.ones(2)
        self.driven_by = driven_by if driven_by is not None else None
        self.mass = eval(mass) if mass is not None else 1
        self.inertia = eval(inertia) if inertia is not None else 0.1
        self.length = eval(length) if length is not None else vector_module(points_to_vector(self.j1, self.j2))
        if cg is not None:
            cg_list = eval(cg)
            if isinstance(cg_list, list) and len(cg_list) >= 3 and isinstance(cg_list[2], str) and cg_list[2].lower() == "polar":
                r = cg_list[0]
                angle_deg = cg_list[1]
                angle_rad = np.deg2rad(angle_deg)
                x = r * np.cos(angle_rad)
                y = r * np.sin(angle_rad)
                self.cg = np.array([[x], [y]])
            else:
                self.cg = np.array(cg_list).reshape(2, 1)
        else:
            self.cg = np.array([None, None])
        self.points_local = []
        self.points_global = []
        if points is not None:
            print(points)
            print(type(points))
            for p in points:
                self.points_local.append(self._parse_coord(p))

        self.external_forces_positions = []
        self.external_forces_vectors = []

        self._local_force_entries = []
        self.update()
        if external_forces is not None:
            self.load_external_forces(external_forces)

    def update(self):
        self.vector = points_to_vector(self.j1, self.j2)
        self.global_coord_angle = np.arctan2(*self.vector[::-1])

        self.external_forces_vectors = []
        for entry in self._local_force_entries:
            f_vector = self._transform_force_vector(*entry)
            self.external_forces_vectors.append(f_vector)
        self.points_global = [self.local_to_global_coord(pt) for pt in self.points_local]

    @staticmethod
    def _parse_coord(spec):
        lst = spec if isinstance(spec, list) else eval(spec)
        if isinstance(lst, list) and len(lst) >= 3 and str(lst[2]).lower() == "polar":
            r, ang = lst[0], np.deg2rad(lst[1])
            return np.array([[r*np.cos(ang)], [r*np.sin(ang)]])
        else:                               # cartesian local
            return np.array(lst).reshape(2,1)
    def local_to_global_coord(self, coord):
        rotation_matrix = np.array([[np.cos(self.global_coord_angle), -np.sin(self.global_coord_angle)],
                                    [np.sin(self.global_coord_angle), np.cos(self.global_coord_angle)]])
        return np.hstack(np.vstack(self.j1) + rotation_matrix.dot(coord))

    def _transform_force_vector(self, force_value, coord_type, frame_type):
        if coord_type.lower() == "cartesian":
            f_vector = np.array(force_value).reshape(2,)
        elif coord_type.lower() == "polar":
            mag, angle_deg = force_value
            angle_rad = np.deg2rad(angle_deg)
            f_vector = np.array([mag * np.cos(angle_rad), mag * np.sin(angle_rad)])
        else:
            raise ValueError("Unknown coordinate type for force: " + str(coord_type))

        if frame_type.lower() == "local":
            rotation_matrix = np.array([
                [np.cos(self.global_coord_angle), -np.sin(self.global_coord_angle)],
                [np.sin(self.global_coord_angle),  np.cos(self.global_coord_angle)]
            ])
            f_vector = rotation_matrix.dot(f_vector)

        return f_vector

    def add_external_force(self, application_point, force_value, coord_type="cartesian", frame_type="global"):
        app_point = np.array(application_point).reshape(2, 1)
        self.external_forces_positions.append(app_point)

        self._local_force_entries.append((force_value, coord_type, frame_type))
        f_vector = self._transform_force_vector(force_value, coord_type, frame_type)
        self.external_forces_vectors.append(f_vector)

    def load_external_forces(self, external_forces):
        external_forces = eval(external_forces)
        if isinstance(external_forces[-1], str):
            external_forces = [external_forces]

        for force_def in external_forces:
            if len(force_def) == 3:
                application_point, force_value, coord_type = force_def
                frame_type = "global"
            elif len(force_def) == 4:
                application_point, force_value, coord_type, frame_type = force_def
            else:
                raise ValueError("Invalid external force format: " + str(force_def))

            self.add_external_force(application_point, force_value, coord_type, frame_type)
