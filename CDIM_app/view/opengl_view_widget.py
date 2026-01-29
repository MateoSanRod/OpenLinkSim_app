import time

import numpy as np
from OpenGL.GL import *
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QFontMetrics
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QVBoxLayout
from ..UI.UI_utils.display_buttontree import VectorTree
from .view_camera import Camera


class ViewWidgetPlot(QOpenGLWidget):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.input = self.app.input
        self.camera = Camera(self)
        self.color_palette = self.app.theme_manager.view_plot_palette

        self.is_first_plot = True
        self.display_simulation = False
        self.current_frame = 0
        self.last_time = time.time()
        self.skip_time = 0

        self.frame_count = 0
        self.fps = 0
        self.t0 = 0

        self.simulation_data = None
        self.overlay_angles = []
        self.overlay_labels = {"nodes": {}, "links": {}}
        self._link_label_centers = {}
        self._link_base_lengths = {}
        self._overlay_arc_cache = []
        self.vec_tree = None
        self.simu_range = 360

        # setup buffers

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.one_over_sqrt_2 = np.float64(1 / np.sqrt(2))


    def reset_widget_buffers(self):

        # Nodes
        self.links_vao = None
        self.links_vbo = None
        self.num_node_vertices = 0

        # Links
        self.nodes_vbo = None
        self.nodes_vao = None
        self.num_link_vertices = 0

        # Filled links
        self.link_fill_vao = None
        self.link_fill_vbo = None
        self.num_link_fill_vertices = 0

        # CG
        self.cg_vao = None
        self.cg_vbo = None
        self.num_cg = 0

        # link poitns
        self.link_points_vao = None
        self.link_points_vbo = None
        self.num_link_points = 0

        # Paths
        self.path_vaos = {}
        self.path_vbos = {}
        self.path_counts = {}

        # Paint visivlity layer
        self.draw_cg_cross = False
        self.draw_link_points = False

        self.node_on = {}
        self.cg_on = {}
        self.pt_on = {}
        self.path_firsts = {}


    def initializeGL(self):
        glClearColor(*self.color_palette["background-color"], 1.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
        glEnable(GL_SAMPLE_SHADING)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

    def resizeGL(self, w, h):
        self.camera.set_aspect_ratio(w / h)
        glViewport(0, 0, w, h)
        self.camera.apply_view()

    def paintGL(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.frame_count += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if not self.is_first_plot:
            self.makeCurrent()

            
            if self.draw_cg_cross:
                self._draw_cg_crosses()
            self._draw_nodes()
            self._draw_link_points()
            if self.display_simulation:
                if "node_coordinates_dt" in self.simulation_data[0]:
                    # --- Velocity
                    orig = self._filter_nodes("Velocity",
                                              self.simulation_data[self.current_frame]['node_coordinates'])
                    vecs = self._filter_nodes("Velocity",
                                              self.simulation_data[self.current_frame]['node_coordinates_dt'])
                    self._draw_vector(self.color_palette["vel-color"], orig, vecs,
                                      self.simulation_data[0]['_dt_max_95%'])

                    # --- Acceleration
                    orig = self._filter_nodes("Acceleration",
                                              self.simulation_data[self.current_frame]['node_coordinates'])
                    vecs = self._filter_nodes("Acceleration",
                                              self.simulation_data[self.current_frame]['node_coordinates_ddt'])
                    self._draw_vector(self.color_palette["acc-color"], orig, vecs,
                                      self.simulation_data[0]['_ddt_max_95%'])
                    if self.draw_cg_cross:
                        # --- Velocity (CG)
                        orig = self._filter_cg("Velocity",
                                               self.simulation_data[self.current_frame]['cg_global_cord'])
                        vecs = self._filter_cg("Velocity",
                                               self.simulation_data[self.current_frame]['cg_global_cord_dt'])
                        self._draw_vector(self.color_palette["vel-color"], orig, vecs,
                                          self.simulation_data[0]['_dt_max_95%'])

                        # --- Acceleration (CG)
                        orig = self._filter_cg("Acceleration",
                                               self.simulation_data[self.current_frame]['cg_global_cord'])
                        vecs = self._filter_cg("Acceleration",
                                               self.simulation_data[self.current_frame]['cg_global_cord_ddt'])
                        self._draw_vector(self.color_palette["acc-color"], orig, vecs,
                                          self.simulation_data[0]['_ddt_max_95%'])

                    # --- Velocity (link points)
                    if self.draw_link_points:
                        orig = self._filter_pt("Velocity",
                                               self.simulation_data[self.current_frame]['link_extra_points'])
                        vecs = self._filter_pt("Velocity",
                                               self.simulation_data[self.current_frame]['link_extra_points_dt'])
                        self._draw_vector(self.color_palette["vel-color"], orig, vecs,
                                          self.simulation_data[0]['_dt_max_95%'])

                        # --- Acceleration (link points)
                        orig = self._filter_pt("Acceleration",
                                               self.simulation_data[self.current_frame]['link_extra_points'])
                        vecs = self._filter_pt("Acceleration",
                                               self.simulation_data[self.current_frame]['link_extra_points_ddt'])
                        self._draw_vector(self.color_palette["acc-color"], orig, vecs,
                                          self.simulation_data[0]['_ddt_max_95%'])
                # --- Node reaction forces
                if "link_joint_forces" in self.simulation_data[0]:
                    orig = self._filter_nodes("Forces",
                                              self.simulation_data[self.current_frame]['node_coordinates'])
                    vecs = self._filter_nodes("Forces",
                                              self.simulation_data[self.current_frame]['node_reactions'])
                    self._draw_vector(self.color_palette["force-color"], orig, vecs,
                                      [self.simulation_data[0]['node_reactions_max'] * .95, self.simulation_data[0]['node_reactions_max']])

                    # col_link = self.color_palette["force-color"]
                    # col_ground = (220, 50, 50)  # any colour you like
                    #
                    # for n, owners in enumerate(fr["node_force_vectors"]):
                    #     P = fr["node_coordinates"][n]
                    #     for lid, F in zip(self._joint_links[n], owners):
                    #         color = col_ground if lid < 0 else col_link
                    #         self._draw_vector(color, np.array([P]), np.array([F]),
                    #                           scale, dot_on_origin_points=False)

                if "Paths" in self.node_on or "Paths" in self.cg_on or "Paths" in self.pt_on:
                    self._draw_static_paths()

            if self.simulation_data[self.current_frame]["external_forces_coord"].any():
                self._draw_vector([220, 0, 0],
                                  self.simulation_data[self.current_frame]['external_forces_coord'],
                                  self.simulation_data[self.current_frame]['external_forces_vectors'],
                                  [self.simulation_space_range * .95, self.simulation_space_range],
                                  dot_on_origin_points=True)

            # self._draw_overlay_labels()
            self._draw_link_fills()
            self._draw_links()
            self._draw_overlay_arcs()
        glFinish()
        if self.frame_count % 30 == 0:
            print("Framerate:", int((1 / (time.time() - self.t0)) * 30), "fps")
            self.t0 = time.time()

    def _node_internal_forces(self) -> tuple[np.ndarray, np.ndarray]:
        fr = self.simulation_data[self.current_frame]
        mask = self.node_on.get("Int.Forces")

        orig = []
        vecs = []
        for n, owners in enumerate(fr["node_force_vectors"]):
            if mask is not None and not mask[n]:
                continue
            P = fr["node_coordinates"][n]
            for F in owners:
                orig.append(P)
                vecs.append(F)
        if not orig:
            return np.empty((0, 2)), np.empty((0, 2))
        return np.asarray(orig, np.float32), np.asarray(vecs, np.float32)

    def _update_node_vbos(self):
        fr0 = self.simulation_data[0]
        frame = self.simulation_data[self.current_frame]

        coords = np.asarray(frame['node_coordinates'], dtype=np.float32)
        bc_state = fr0.get("node_bc_state",
                           np.zeros(len(coords), dtype=int))
        coords = np.asarray(frame["node_coordinates"], dtype=np.float32)
        bc_state = fr0.get("node_bc_state", np.zeros(len(coords), int))

        slider_axis = frame.get("slider_axis")
        if slider_axis is None:
            slider_axis = [None] * len(coords)

        base = self.camera.view_range[0] / max(1, self.width())
        half = base * 4.5
        tri_h = base * 6.5

        # FREE PINS
        free_mask = bc_state == 0
        free_pts = coords[free_mask]

        # SLIDERS
        sl_mask = bc_state == 1
        sl_pos = coords[sl_mask]

        sl_ax = np.array([ax if ax is not None else (1.0, 0.0)
                          for ax, m in zip(slider_axis, sl_mask) if m],
                         dtype=np.float32)
        if sl_ax.size != 0:
            ang = np.arctan2(sl_ax[:, 1], -sl_ax[:, 0])
            c, s = np.cos(ang), np.sin(ang)

            lc = np.array([[-half, -half],
                           [half, -half],
                           [half, half],
                           [-half, half]], dtype=np.float32)

            R = np.stack([np.stack([c, -s], axis=1),
                          np.stack([s, c], axis=1)], axis=1)
            sl_quads = (lc @ R) + sl_pos[:, None, :]
            sl_quads = sl_quads.reshape(-1, 2)
        else:
            sl_quads = np.empty((0, 2), dtype=np.float32)

        # GROUNDS
        gr_mask = bc_state == 2
        gr_pos = coords[gr_mask]
        gr_tris = np.empty((len(gr_pos) * 3, 2), dtype=np.float32)
        gr_tris[0::3] = gr_pos + (0.0, tri_h)
        gr_tris[1::3] = gr_pos + (-tri_h, -tri_h)
        gr_tris[2::3] = gr_pos + (tri_h, -tri_h)

        # upload to three dynamic VBOs
        spec = [('free', free_pts),
                ('slider', sl_quads),
                ('ground', gr_tris)]
        for name, verts in spec:
            self.node_counts[name] = verts.shape[0]
            glBindBuffer(GL_ARRAY_BUFFER, self.node_vbos[name])
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _update_cg_cross_vbo(self):
        pos = np.asarray(self.simulation_data[self.current_frame]
                         ['cg_global_cord'], dtype=np.float32)
        N = pos.shape[0]

        half_len = (self.camera.view_range[0] / self.width()) * 3.5
        half_width = (self.camera.view_range[0] / self.width()) * 0.75

        p1 = np.array([+self.one_over_sqrt_2, +self.one_over_sqrt_2], dtype=np.float32) * half_width
        p2 = np.array([-self.one_over_sqrt_2, +self.one_over_sqrt_2], dtype=np.float32) * half_width

        # vec endpoints
        a0 = pos + [-half_len, +half_len]  # start
        a1 = pos + [+half_len, -half_len]  # end
        b0 = pos + [+half_len, +half_len]  # start
        b1 = pos + [-half_len, -half_len]  # end

        verts = np.empty((N * 12, 2), dtype=np.float32)

        verts[0::12] = a0 + p1
        verts[1::12] = a1 + p1
        verts[2::12] = a0 - p1
        verts[3::12] = a0 - p1
        verts[4::12] = a1 + p1
        verts[5::12] = a1 - p1

        verts[6::12] = b0 + p2
        verts[7::12] = b1 + p2
        verts[8::12] = b0 - p2
        verts[9::12] = b0 - p2
        verts[10::12] = b1 + p2
        verts[11::12] = b1 - p2

        glBindBuffer(GL_ARRAY_BUFFER, self.cg_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _update_link_vbos(self):
        links = self._link_segments(
            self.simulation_data[self.current_frame]['link_line_list'])
        new_size = links.nbytes
        self.num_link_vertices = links.shape[0]

        glBindBuffer(GL_ARRAY_BUFFER, self.links_vbo)

        cur_size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
        if new_size == cur_size:
            glBufferSubData(GL_ARRAY_BUFFER, 0, new_size, links)
        else:
            glBufferData(GL_ARRAY_BUFFER, new_size, links, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _update_link_fill_vbo(self):
        tris = self._link_triangles(
            self.simulation_data[self.current_frame]['link_line_list'])
        self.num_link_fill_vertices = tris.shape[0]

        glBindBuffer(GL_ARRAY_BUFFER, self.link_fill_vbo)
        cur_size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
        new_size = tris.nbytes
        if new_size == cur_size:
            glBufferSubData(GL_ARRAY_BUFFER, 0, new_size, tris)
        else:
            glBufferData(GL_ARRAY_BUFFER, new_size, tris, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _update_link_points_vbo(self):
        link_points = self._flat_pts(self.simulation_data[self.current_frame]
                                                ['link_extra_points'])
        glBindBuffer(GL_ARRAY_BUFFER, self.link_points_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, link_points.nbytes, link_points)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _setup_link_buffers(self):
        links = self._link_segments(self.simulation_data[0]['link_line_list'])
        self.num_link_vertices = links.shape[0]

        self.links_vao = glGenVertexArrays(1)
        self.links_vbo = glGenBuffers(1)

        glBindVertexArray(self.links_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.links_vbo)
        glBufferData(GL_ARRAY_BUFFER, links.nbytes, links, GL_STATIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def _setup_link_fill_buffers(self):
        tris = self._link_triangles(self.simulation_data[0]['link_line_list'])
        self.num_link_fill_vertices = tris.shape[0]

        self.link_fill_vao = glGenVertexArrays(1)
        self.link_fill_vbo = glGenBuffers(1)

        glBindVertexArray(self.link_fill_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.link_fill_vbo)
        glBufferData(GL_ARRAY_BUFFER, tris.nbytes, tris, GL_STATIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def _setup_node_buffers(self):
        """
           free pin    point 1 vertex
           slider     square 4 vertices
           ground      triangle 3 vertices
        """
        self.node_vaos = {}
        self.node_vbos = {}
        self.node_counts = {}

        def _alloc(name, max_vert):
            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)
            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER,
                         max_vert * 2 * 4,
                         None,
                         GL_DYNAMIC_DRAW)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
            glBindVertexArray(0)
            self.node_vaos[name] = vao
            self.node_vbos[name] = vbo
            self.node_counts[name] = 0

        n_total = len(self.simulation_data[0]['node_coordinates'])
        _alloc('free', n_total * 1)
        _alloc('slider', n_total * 4)
        _alloc('ground', n_total * 3)

    def _setup_link_points_buffer(self):
        link_points = self._flat_pts(self.simulation_data[0]['link_extra_points'])
        self.num_link_points = link_points.shape[0]
        self.link_points_vao = glGenVertexArrays(1)
        self.link_points_vbo = glGenBuffers(1)

        glBindVertexArray(self.link_points_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.link_points_vbo)
        glBufferData(GL_ARRAY_BUFFER, link_points.nbytes, link_points, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def _setup_cg_cross_buffer(self):
        self.num_cg = len(self.simulation_data[0]['cg_global_cord'])
        max_bytes = self.num_cg * 12 * 2 * 4

        self.cg_vao = glGenVertexArrays(1)
        self.cg_vbo = glGenBuffers(1)

        glBindVertexArray(self.cg_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.cg_vbo)
        glBufferData(GL_ARRAY_BUFFER, max_bytes, None, GL_DYNAMIC_DRAW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def _setup_path_buffers(self):
        def _build(name, list_of_list_of_xy):
            strips = [np.asarray(s, np.float32).reshape(-1, 2)
                      for s in list_of_list_of_xy if len(s)]
            if not strips:
                return
            verts = np.concatenate(strips, axis=0)
            counts = np.array([len(s) for s in strips], dtype=np.int32)

            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)

            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
            glBindVertexArray(0)

            first = np.concatenate(([0], np.cumsum(counts[:-1]))).astype(np.int32)
            self.path_vaos[name] = vao
            self.path_vbos[name] = vbo
            self.path_firsts[name] = first
            self.path_counts[name] = counts

        frames = self.simulation_data
        _build("node_all",
               [[f['node_coordinates'][i] for f in frames]
                for i in range(len(frames[0]['node_coordinates']))])

        if 'cg_global_cord' in frames[0]:
            _build("cg_all",
                   [[f['cg_global_cord'][i] for f in frames]
                    for i in range(len(frames[0]['cg_global_cord']))])

        if 'link_extra_points' in frames[0]:
            _build("extra_all",
                   [[pt for f in frames
                     for pt in f['link_extra_points'][i]]
                    for i in range(len(frames[0]['link_extra_points']))])

        prog_vao = glGenVertexArrays(1)
        prog_vbo = glGenBuffers(1)
        glBindVertexArray(prog_vao)
        glBindBuffer(GL_ARRAY_BUFFER, prog_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4, None, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, ctypes.c_void_p(0))
        glBindVertexArray(0)

        self.path_vaos["node_prog"] = prog_vao
        self.path_vbos["node_prog"] = prog_vbo
        self.path_counts["node_prog"] = np.array([], dtype=np.int32)

    def _visible_strips(self, name: str):
        counts = self.path_counts.get(name)
        first = self.path_firsts.get(name)
        if counts is None or counts.size == 0:
            return None, None

        if name == "node_all" or name == "node_prog":
            mask = self.node_on["Paths"]
        elif name == "cg_all":
            mask = self.cg_on["Paths"]
        elif name == "extra_all":
            link_pts = self.simulation_data[0]["link_extra_points_per_link"]
            n_links = len(link_pts)

            mask_pt = self.pt_on["Paths"]
            mask = np.zeros(n_links, dtype=bool)

            off = np.concatenate(([0],
                                  np.cumsum([len(l) for l in link_pts])))

            for lid in range(n_links):
                lo, hi = off[lid], off[lid + 1]
                mask[lid] = mask_pt[lo:hi].any()

            if mask.size < counts.size:
                counts = counts[:mask.size]
                first = first[:mask.size]
            elif mask.size > counts.size:
                mask = mask[:counts.size]

        else:
            return None, None

        if not mask.any():
            return None, None
        return first[mask], counts[mask]


    def _update_prog_path(self):
        strips = [[self.simulation_data[f]['node_coordinates'][i]
                   for f in range(self.current_frame + 1)]
                  for i in range(len(self.simulation_data[0]['node_coordinates']))]

        verts = np.concatenate([np.asarray(s, np.float32) for s in strips], axis=0)
        counts = np.array([len(s) for s in strips], dtype=np.int32)

        glBindBuffer(GL_ARRAY_BUFFER, self.path_vbos["node_prog"])
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.path_counts["node_prog"] = counts

    def _draw_static_paths(self):
        glLineWidth(2)
        glColor3ub(*self.color_palette["pos-color"])

        for name in ("node_all", "cg_all", "extra_all", "node_prog"):
            vao = self.path_vaos.get(name)
            if vao is None:
                continue

            first, counts = self._visible_strips(name)
            if first is None:
                continue

            glBindVertexArray(vao)
            glMultiDrawArrays(GL_LINE_STRIP,
                              first.ctypes.data_as(ctypes.POINTER(GLint)),
                              counts.ctypes.data_as(ctypes.POINTER(GLsizei)),
                              len(counts))
            glBindVertexArray(0)

    def _filter_nodes(self, layer: str, arr: np.ndarray) -> np.ndarray:
        mask = self.node_on.get(layer)
        if mask is None or len(mask) != len(arr):
            return arr
        return arr[mask]

    def _filter_cg(self, layer: str, arr: np.ndarray) -> np.ndarray:
        mask = self.cg_on.get(layer)
        if mask is None or len(mask) != len(arr):
            return arr
        return arr[mask]

    def _filter_pt(self, layer: str, flat_arr: np.ndarray) -> np.ndarray:
        mask = self.pt_on.get(layer)
        if mask is None or len(mask) != len(flat_arr):
            return flat_arr
        return flat_arr[mask]

    def _draw_aa_line(self, x1, y1, x2, y2, half_width):
        dx = x2 - x1
        dy = y2 - y1
        length = np.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        px, py = -uy * half_width, ux * half_width

        glBegin(GL_TRIANGLE_STRIP)
        glVertex2f(x1 + px, y1 + py)
        glVertex2f(x2 + px, y2 + py)
        glVertex2f(x1 - px, y1 - py)
        glVertex2f(x2 - px, y2 - py)
        glEnd()

    def _draw_nodes(self):
        self._update_node_vbos()

        glColor3ub(*self.color_palette["node-color"])

        #  free & revolute pins
        glPointSize(12.0)
        if self.node_counts['free']:
            glBindVertexArray(self.node_vaos['free'])
            glDrawArrays(GL_POINTS, 0, self.node_counts['free'])
            glBindVertexArray(0)

        # sliders
        if self.node_counts['slider']:
            glBindVertexArray(self.node_vaos['slider'])
            glDrawArrays(GL_QUADS, 0, self.node_counts['slider'])
            glBindVertexArray(0)

        # ground nodes
        if self.node_counts['ground']:
            glBindVertexArray(self.node_vaos['ground'])
            glDrawArrays(GL_TRIANGLES, 0, self.node_counts['ground'])
            glBindVertexArray(0)

    def _draw_cg_crosses(self):
        if self.draw_cg_cross:
            self._update_cg_cross_vbo()
            glLineWidth(2.5)
            glColor3ub(*self.color_palette["cg-color"])
            glBindVertexArray(self.cg_vao)
            glDrawArrays(GL_TRIANGLES, 0, self.num_cg * 12)
            glBindVertexArray(0)

    def _draw_link_points(self):
        if self.draw_link_points:
            self._update_link_points_vbo()
            glPointSize(12.0)
            glColor3ub(*self.color_palette["link-color"])
            glBindVertexArray(self.link_points_vao)
            glDrawArrays(GL_POINTS, 0, self.num_link_points)
            glBindVertexArray(0)

    def _draw_link_fills(self):
        self._update_link_fill_vbo()

        glColor4ub(*self.color_palette["link-color"], 180)
        glBindVertexArray(self.link_fill_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.num_link_fill_vertices)
        glBindVertexArray(0)

    def _draw_links(self):
        self._update_link_vbos()
        glLineWidth(8.0)
        glColor3ub(*self.color_palette["link-color"])
        glBindVertexArray(self.links_vao)
        glDrawArrays(GL_LINES, 0, self.num_link_vertices)
        glBindVertexArray(0)

    def _draw_overlay_arcs(self):
        """Draw angle overlays as small arcs at specified nodes."""
        if not self._overlay_arc_cache or self.simulation_data is None:
            return
        fr = self.simulation_data[self.current_frame]
        nodes = fr.get("node_coordinates")
        link_angles = fr.get("link_angle")
        if nodes is None or link_angles is None:
            return

        glLineWidth(3.0)
        glColor3ub(6, 123, 194)
        glDisable(GL_LINE_SMOOTH)
        arc_labels = []
        for ov in self._overlay_arc_cache:
            node_idx = ov["node_idx"]
            link_idx = ov["link_idx"]
            if node_idx >= len(nodes) or link_idx >= len(link_angles):
                continue
            center = np.asarray(nodes[node_idx], dtype=float)
            angle = float(link_angles[link_idx])
            radius = ov["radius"]
            px_per_world = self.width() / max(self.camera.view_range[0], 1e-6)
            radius_px = max(1.0, radius * px_per_world)
            steps = int(np.clip(radius_px * 0.25, 12, 60))
            theta = np.linspace(0.0, angle, steps)
            half_w_world = (2.0 / max(px_per_world, 1e-6))  # ~2 px thickness
            r_outer = radius + half_w_world * 0.5
            r_inner = max(0.0, radius - half_w_world * 0.5)
            x_outer = center[0] + r_outer * np.cos(theta)
            y_outer = center[1] + r_outer * np.sin(theta)
            x_inner = center[0] + r_inner * np.cos(theta)
            y_inner = center[1] + r_inner * np.sin(theta)
            glBegin(GL_TRIANGLE_STRIP)
            for xo, yo, xi, yi in zip(x_outer, y_outer, x_inner, y_inner):
                glVertex2f(xo, yo)
                glVertex2f(xi, yi)
            glEnd()
            glBegin(GL_LINES)
            glVertex2f(center[0], center[1])
            glVertex2f(center[0] + r_outer*1.2, center[1])
            glEnd()
            name = ov.get("name", "")
            if name:
                arc_labels.append((np.array([center[0] + r_outer*1.5, center[1]]), name))

        if arc_labels:
            painter = QPainter(self)
            # painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.beginNativePainting()
            font = self.app.ui.plainTextEdit.font()
            painter.setFont(font)
            painter.setPen(QColor(6, 123, 194))
            for widget_pos, text in arc_labels:
                pt = self._world_to_screen(widget_pos)
                if pt is None:
                    continue
                painter.drawText(pt.x(), pt.y(), text)
            painter.end()

    def draw_aa_arrow(self, x_tail, y_tail, x_tip, y_tip,
                      shaft_half_px=1.25,
                      head_len_px=7,
                      head_width_mult=3):
        dx, dy = x_tip - x_tail, y_tip - y_tail
        length = np.hypot(dx, dy)
        if length < 1e-6:
            return
        ux, uy = dx / length, dy / length
        px, py = -uy, ux

        wx = self.camera.view_range[0] / self.width()
        wy = self.camera.view_range[1] / self.height()

        shaft_hwx = shaft_half_px * wx
        shaft_hwy = shaft_half_px * wy

        head_len_w = head_len_px * np.hypot(wx, wy)
        head_hwx = head_width_mult * shaft_half_px * wx
        head_hwy = head_width_mult * shaft_half_px * wy

        sx, sy = px * shaft_hwx, py * shaft_hwy
        hx, hy = px * head_hwx, py * head_hwy

        bx, by = x_tip, y_tip
        tx, ty = x_tip + ux * head_len_w, y_tip + uy * head_len_w

        glBegin(GL_TRIANGLE_STRIP)
        glVertex2f(x_tail + sx, y_tail + sy)
        glVertex2f(x_tail - sx, y_tail - sy)
        glVertex2f(bx + sx, by + sy)
        glVertex2f(bx - sx, by - sy)
        glVertex2f(tx, ty)
        glVertex2f(bx + hx, by + hy)
        glVertex2f(bx - hx, by - hy)
        glEnd()

    @staticmethod
    def _link_segments(line_list: list[np.ndarray]) -> np.ndarray:
        segments = []
        for pts in line_list:
            if len(pts) < 2:
                continue
            seg = np.empty(((len(pts) - 1) * 2, 2), dtype=np.float32)
            seg[0::2] = pts[:-1]
            seg[1::2] = pts[1:]
            segments.append(seg)
        if not segments:
            return np.empty((0, 2), dtype=np.float32)
        return np.concatenate(segments, axis=0)

    @staticmethod
    def _link_triangles(line_list: list[np.ndarray]) -> np.ndarray:
        tris = []
        for pts in line_list:
            m = len(pts)
            if m < 3:
                continue
            base = pts[0]
            tri = np.empty(((m - 2) * 3, 2), dtype=np.float32)
            tri[0::3] = base
            tri[1::3] = pts[1:-1]
            tri[2::3] = pts[2:]
            tris.append(tri)
        if not tris:
            return np.empty((0, 2), dtype=np.float32)
        return np.concatenate(tris, axis=0)

    def _prepare_overlays(self):
        """Cache overlay data from the input for rendering."""
        self.overlay_angles = getattr(self.app.input, "overlay_angles", []) or []
        self.overlay_labels = getattr(self.app.input, "overlay_labels", {"nodes": {}, "links": {}}) or {"nodes": {}, "links": {}}
        self._link_label_centers = {}
        self._link_base_lengths = {}
        self._overlay_arc_cache = []

        if self.simulation_data is None:
            return
        fr0 = self.simulation_data[0]
        link_lines = fr0.get("link_line_list") or []

        for lid_str, label in self.overlay_labels.get("links", {}).items():
            try:
                lid = int(lid_str)
            except Exception:
                lid = lid_str if isinstance(lid_str, int) else None
            if lid is None:
                continue
            idx = lid - 1
            if idx < 0 or idx >= len(link_lines):
                continue
            pts = np.asarray(link_lines[idx], dtype=float)
            if len(pts) == 0:
                continue
            center = pts.mean(axis=0)
            if len(pts) >= 2:
                base_len = np.linalg.norm(pts[1] - pts[0])
            else:
                base_len = max(self.camera.view_range) * 0.05
            self._link_label_centers[idx] = center
            self._link_base_lengths[idx] = base_len

        # Precompute arc helpers (radius etc., samples chosen per frame based on zoom)
        if self.overlay_angles:
            default_radius = max(self.camera.view_range) * 0.02
            for ov in self.overlay_angles:
                node_idx = int(ov.get("node", 0)) - 1
                link_idx = int(ov.get("link", 0)) - 1
                if node_idx < 0 or link_idx < 0 or link_idx >= len(link_lines):
                    continue
                line = np.asarray(link_lines[link_idx], dtype=float)
                if line.shape[0] >= 2:
                    seg_len = np.linalg.norm(line[1] - line[0])
                else:
                    seg_len = default_radius * 5
                radius = max(seg_len * 0.25, default_radius)
                self._overlay_arc_cache.append(
                    {
                        "node_idx": node_idx,
                        "link_idx": link_idx,
                        "radius": radius,
                        "name": ov.get("name", ""),
                    }
                )

    def _world_to_screen(self, pos: np.ndarray) -> QPointF | None:
        """Convert world (model) coordinates to widget pixel coordinates."""
        if pos is None or self.width() <= 0 or self.height() <= 0:
            return None
        cx, cy = self.camera.view_center
        rx, ry = self.camera.view_range / 2
        left, right = cx - rx, cx + rx
        bottom, top = cy - ry, cy + ry
        x = (pos[0] - left) / (right - left) * self.width()
        y = (top - pos[1]) / (top - bottom) * self.height()
        return QPointF(x, y)

    def _draw_overlay_labels(self):
        """Draw node/link labels using QPainter, rotating link labels with the link."""
        if not self.overlay_labels or self.simulation_data is None:
            return
        fr = self.simulation_data[self.current_frame]
        nodes = fr.get("node_coordinates")
        link_angles = fr.get("link_angle")
        if nodes is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        fm = QFontMetrics(font)

        node_color = QColor(*self.color_palette["node-color"])
        link_color = QColor(*self.color_palette["link-color"])

        # Node labels follow the node position each frame
        for nid_str, label in self.overlay_labels.get("nodes", {}).items():
            try:
                nid = int(nid_str) - 1
            except Exception:
                continue
            if nid < 0 or nid >= len(nodes):
                continue
            pos = self._world_to_screen(nodes[nid])
            if pos is None:
                continue
            w = fm.horizontalAdvance(label) + 6
            h = fm.height() + 4
            painter.setPen(node_color)
            painter.drawText(pos.x() - w / 2, pos.y() - h / 2, w, h, Qt.AlignCenter, label)

        # Link labels stay at precomputed centers, rotate with link angle
        for lid, label in self.overlay_labels.get("links", {}).items():
            try:
                idx = int(lid) - 1
            except Exception:
                continue
            center = self._link_label_centers.get(idx)
            if center is None:
                continue
            pos = self._world_to_screen(center)
            if pos is None:
                continue
            angle_deg = 0.0
            if link_angles is not None and 0 <= idx < len(link_angles):
                angle_deg = np.degrees(link_angles[idx])
            w = fm.horizontalAdvance(label) + 6
            h = fm.height() + 4
            painter.save()
            painter.translate(pos)
            painter.rotate(-angle_deg)
            painter.setPen(link_color)
            painter.drawText(-w / 2, -h / 2, w, h, Qt.AlignCenter, label)
            painter.restore()

        painter.end()

    def _draw_vector(self, color, origin_points, vectors, scale_vector, dot_on_origin_points=False):
        glColor3ub(*color)
        cross_size = 8
        width = 1.1
        half_width = (width / 3) * (self.camera.view_range[0] / self.width())
        glLineWidth(width)

        for idx, (origin_point, vector) in enumerate(zip(origin_points, vectors)):

            x, y = origin_point[0], origin_point[1]
            vec_x, vec_y = vector[0], vector[1]
            magnitude = np.sqrt(vec_x ** 2 + vec_y ** 2)
            if magnitude.all() < 1e-7:
                continue
            unit_vec = vector / magnitude

            if magnitude <= scale_vector[0]:
                scale = magnitude / scale_vector[0]
            elif magnitude < scale_vector[1] and scale_vector[0] * 3 < scale_vector[1]:
                normalized_magnitude = (magnitude - scale_vector[0]) / (scale_vector[1] - scale_vector[0])
                linear_component = normalized_magnitude * 0.9
                logarithmic_component = np.log(1 + 9 * normalized_magnitude) / np.log(10)
                scale = 1 + linear_component * 0.5 + logarithmic_component * 0.5
            else:
                scale = 1 + 0.02 * ((magnitude / scale_vector[1]) - 1)

            scale *= self.simulation_space_range / 4

            normalized_vec_x = (vec_x / magnitude) * scale
            normalized_vec_y = (vec_y / magnitude) * scale

            glBegin(GL_LINES)
            glVertex2f(x, y)
            glVertex2f(x + normalized_vec_x, y + normalized_vec_y)
            glEnd()

            self.draw_aa_arrow(x, y,
                               x + normalized_vec_x,
                               y + normalized_vec_y,
                               shaft_half_px=width)

            if dot_on_origin_points:
                glPointSize(10.0)
                glBegin(GL_POINTS)
                glVertex2f(x, y)
                glEnd()

    def update_simulation(self):
        self.current_frame = int(
            ((time.time() - self.initial_time) / (self.ani_run_time)) * self.len_data)
        if abs(self.current_frame) >= abs(self.len_data):
            self.initial_time = time.time()
            self.current_frame %= self.len_data
        # print(self.current_frame)
        data = self.simulation_data[self.current_frame]
        self.update()

    def stop_simulation(self):
        self.killTimer(0)
        self.elapsed_time = time.time()

    def kill_simulation(self):
        if hasattr(self, 'timer') and self.timer:
            self.killTimer(self.timer)
            self.timer = None

        self.current_frame = 0
        self.display_simulation = True
        self.simulation_data = None
        self.skip_time = 0
        self.app.view_controller._is_simulation_running = False
        self.update()

    def play_simulation(self):
        self.update_projection()

        self.elapsed_time = time.time() - self.elapsed_time
        self.initial_time += self.elapsed_time - self.skip_time
        self.skip_time = 0
        if abs(int(((time.time() - self.initial_time) / (self.ani_run_time)) * self.len_data)) >= self.len_data:
            self.initial_time = time.time() - ((self.current_frame / self.len_data) * self.ani_run_time)
        self.timer = self.startTimer(0)

    def step_simulation(self, step):
        frames_per_step = int((self.len_data / self.simu_range) * step * np.sign(self.input.delta_time))
        self.current_frame = (self.current_frame + frames_per_step) % self.len_data
        self.skip_time += (self.ani_run_time / self.simu_range) * step
        self.update()

    def playback_speed_simulation(self, factor):
        ani_run_time_old = self.ani_run_time
        self.ani_run_time = (self.len_data * self.input.delta_time) / factor
        self.initial_time += (ani_run_time_old - self.ani_run_time) * (
                time.time() - self.initial_time) / ani_run_time_old

    def plot_simu(self, data):
        self.kill_simulation()
        self.reset_widget_buffers()
        self.len_data = len(data)
        self.v_ang = self.input.speed_indep_var
        self.ani_run_time = self.len_data * self.input.delta_time

        self.display_simulation = True
        self.app.view_controller._is_simulation_running = True
        self.simulation_data = data
        self._prepare_overlays()
        self.current_frame = 0
        self.timer = self.startTimer(0)
        self.initial_time = time.time()
        self._setup_link_buffers()
        self._setup_link_fill_buffers()
        self._setup_node_buffers()
        self._setup_path_buffers()
        if self.simulation_data[0]["cg_global_cord"].any():
            self._setup_cg_cross_buffer()
            self.draw_cg_cross = True
        if "link_extra_points" in self.simulation_data[0]:
            self.draw_link_points = True
            self._setup_link_points_buffer()
        self.display_button_tree()
        self.update_projection()

    def plot_image(self, data):
        self.reset_widget_buffers()
        self.display_simulation = False
        self.simulation_data = data
        self._prepare_overlays()
        self.current_frame = 0
        data = self.simulation_data[self.current_frame]
        self._setup_link_buffers()
        self._setup_link_fill_buffers()
        self._setup_node_buffers()
        self._setup_path_buffers()
        if self.simulation_data[0]["cg_global_cord"].any():
            self._setup_cg_cross_buffer()
            self.draw_cg_cross = True
        if "link_extra_points" in self.simulation_data[0]:
            self.draw_link_points = True
            self._setup_link_points_buffer()
        self.update_projection()

    def timerEvent(self, event):
        if self.app.view_controller._is_simulation_running:
            self.update_simulation()
        else:
            pass

    def update_theme_colors(self, colors):
        self.color_palette = colors
        glClearColor(*self.color_palette["background-color"], 1)
        self.update()

    def wheelEvent(self, event):
        self.app.view_controller.wheelEvent(event)

    def mousePressEvent(self, event):
        self.app.view_controller.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.app.view_controller.mouseMoveEvent(event)

    def update_projection(self):
        self.makeCurrent()
        self.camera.apply_view()
        self.update()

    def _set_first_plot_limits(self, data):

        if self.is_first_plot:
            if len(data) > 1:
                factor = 1.25
                x_max = np.max([i['node_coordinates'][:, 0].max() for i in data])
                y_max = np.max([i['node_coordinates'][:, 1].max() for i in data])
                x_min = np.min([i['node_coordinates'][:, 0].min() for i in data])
                y_min = np.min([i['node_coordinates'][:, 1].min() for i in data])
            else:
                factor = 1.75
                x_max = data[self.current_frame]['node_coordinates'][:, 0].max()
                y_max = data[self.current_frame]['node_coordinates'][:, 1].max()
                x_min = data[self.current_frame]['node_coordinates'][:, 0].min()
                y_min = data[self.current_frame]['node_coordinates'][:, 1].min()

            center_x = (x_max + x_min) / 2
            center_y = (y_max + y_min) / 2

            width = x_max - x_min
            height = y_max - y_min
            self.simulation_space_range = max(width, height)
            if self.camera.aspect_ratio >= 1:
                max_range = max(width, height / self.camera.aspect_ratio)
                width = max_range
                height = max_range * self.camera.aspect_ratio
            else:
                max_range = max(width, height / self.camera.aspect_ratio)
                width = max_range
                height = max_range / self.camera.aspect_ratio

            # self.resizeGL(self.width(), self.height())
            self.camera.view_center = np.array([center_x, center_y])
            self.camera.view_range = np.array([width * factor, height * factor])
            self.is_first_plot = False
            self.resizeGL(self.width(), self.height())
            self.update_projection()
        else:
            self.resizeGL(self.width(), self.height())
            self.update_projection()

    def display_button_tree(self) -> None:
        if self.vec_tree is not None:
            self.vec_tree.setParent(None)
            self.vec_tree.deleteLater()


        n_nodes = len(self.simulation_data[0]["node_coordinates"])
        n_cg = []
        link_pts = []


        if "cg_global_cord" in self.simulation_data[0]:
            n_cg = len(self.simulation_data[0]["cg_global_cord"])

        self._pt_offset = []
        flat_pt_count = 0
        if "link_extra_points_per_link" in self.simulation_data[0]:
            link_pts = self.simulation_data[0]["link_extra_points_per_link"]
            self._pt_offset = np.cumsum([0] + [len(l) for l in link_pts[:-1]])

            for lnk_id, pts in enumerate(link_pts):
                for pt_id in range(len(pts)):
                    flat_pt_count += 1

        self.vec_tree = VectorTree(n_nodes, n_cg, link_pts)
        self.vec_tree.setParent(self, Qt.FramelessWindowHint)
        self.vec_tree.setAttribute(Qt.WA_TranslucentBackground)

        def _reposition():
            m = 10
            siz = self.vec_tree.sizeHint()
            self.vec_tree.setGeometry(self.width() - siz.width() - m,
                                      m, siz.width(), siz.height())

        _reposition()
        def _resize_evt(evt):
            super(ViewWidgetPlot, self).resizeEvent(evt)
            _reposition()

        if not hasattr(self, "_patched_resize_evt"):
            self._patched_resize_evt = True
            self.resizeEvent = _resize_evt

        self.vec_tree.show()

        self.vec_tree.layerToggled.connect(self._on_layer_toggle)
        self.vec_tree.nodeShown   .connect(self._on_node_toggle)
        self.vec_tree.cgShown     .connect(self._on_cg_toggle)
        self.vec_tree.ptShown     .connect(self._on_pt_toggle)

        for layer in ("Paths", "Velocity", "Acceleration", "Forces"):
            self.node_on[layer]  = np.zeros(n_nodes,          dtype=bool)
            self.cg_on[layer]    = np.zeros(n_cg,             dtype=bool)
            self.pt_on[layer]    = np.zeros(flat_pt_count,    dtype=bool)

    @staticmethod
    def _flat_pts(nested) -> np.ndarray:
        if isinstance(nested, np.ndarray) and nested.ndim == 2:
            return nested.astype(np.float32, copy=False)
        return np.asarray([pt for link in nested for pt in link],
                          dtype=np.float32)

    def _on_layer_toggle(self, layer: str, on: bool) -> None:
        self.node_on[layer][:] = on
        self.cg_on[layer][:] = on
        self.pt_on[layer][:] = on
        self.update()
    def _on_node_toggle(self, layer: str, idx: int, on: bool) -> None:
        self.node_on[layer][idx] = on
        self.update()

    def _on_cg_toggle(self, layer: str, idx: int, on: bool) -> None:
        self.cg_on[layer][idx] = on
        self.update()

    def _on_pt_toggle(self, layer: str, link_id: int, pt_id: int, on: bool) -> None:
        flat_idx = int(self._pt_offset[link_id] + pt_id)
        self.pt_on[layer][flat_idx] = on
        self.update()
