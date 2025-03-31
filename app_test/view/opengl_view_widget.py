import time

import numpy as np
from OpenGL.GL import *
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QVBoxLayout
from view.view_camera import Camera


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

        self.simulation_data = None
        self.simu_range = 360

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def initializeGL(self):
        glClearColor(*self.color_palette["background-color"], 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

    def resizeGL(self, w, h):
        self.camera.set_aspect_ratio(w / h)
        glViewport(0, 0, w, h)
        self.camera.apply_view()

    def paintGL(self):
        # fps
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.frame_count += 1

        # if delta_time > 0.25:  # Update FPS every second
        #     self.fps = self.frame_count / delta_time
        #     self.frame_count = 0
        #     self.last_time = current_time
        #     print(self.fps)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if not self.is_first_plot:
            self._draw_links_cg(color=self.color_palette["cg-color"],
                                links_cg=self.simulation_data[self.current_frame]['cg_global_cord'])

            self._draw_nodes(color=self.color_palette["node-color"],
                             nodes=self.simulation_data[self.current_frame]['node_coordinates'])

            if self.display_simulation:

                self._draw_vector(color=self.color_palette["vel-color"],
                                  origin_points=self.simulation_data[self.current_frame]['node_coordinates'],
                                  vectors=self.simulation_data[self.current_frame]['node_coordinates_dt'],
                                  scale_vector=self.simulation_data[0]['_dt_max_95%'])

                self._draw_vector(color=self.color_palette["acc-color"],
                                  origin_points=self.simulation_data[self.current_frame]['node_coordinates'],
                                  vectors=self.simulation_data[self.current_frame]['node_coordinates_ddt'],
                                  scale_vector=self.simulation_data[0]['_ddt_max_95%'])

                self._draw_vector(color=self.color_palette["vel-color"],
                                  origin_points=self.simulation_data[self.current_frame]['cg_global_cord'],
                                  vectors=self.simulation_data[self.current_frame]['cg_global_cord_dt'],
                                  scale_vector=self.simulation_data[0]['_dt_max_95%'])

                self._draw_vector(color=self.color_palette["acc-color"],
                                  origin_points=self.simulation_data[self.current_frame]['cg_global_cord'],
                                  vectors=self.simulation_data[self.current_frame]['cg_global_cord_ddt'],
                                  scale_vector=self.simulation_data[0]['_ddt_max_95%'])

                self._draw_vector(color=self.color_palette["force-color"],
                                  origin_points=self.simulation_data[self.current_frame]['node_coordinates'],
                                  vectors=self.simulation_data[self.current_frame]['node_reactions'],
                                  scale_vector=[self.simulation_space_range*.95,self.simulation_space_range])

                self._draw_vector(color=[220, 0, 0],
                                  origin_points=self.simulation_data[self.current_frame]['external_forces_coord'],
                                  vectors=self.simulation_data[self.current_frame]['external_forces_vectors'],
                                  scale_vector=[self.simulation_space_range * .95, self.simulation_space_range],
                                  dot_on_origin_points=True)

            self._draw_links(color=self.color_palette["link-color"],
                             links=self.simulation_data[self.current_frame]['link_line_list'])



    def _draw_nodes(self, color, nodes):
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        glColor3ub(*color)
        glPointSize(10.0)
        glBegin(GL_POINTS)
        for node in nodes:
            glVertex2f(node[0], node[1])
        glEnd()

    def _draw_links(self, color, links):
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(6.0)
        glColor3ub(*color)
        glBegin(GL_LINES)
        for link in links:
            glVertex2f(link[0][0], link[0][1])
            glVertex2f(link[1][0], link[1][1])
        glEnd()

    def _draw_links_cg(self, color, links_cg):
        glEnable(GL_LINE_SMOOTH)

        glColor3ub(*color)
        cross_size = 3.5
        x_cross_size = (self.camera.view_range[0] / self.width()) * cross_size
        y_cross_size = (self.camera.view_range[1] / self.height()) * cross_size
        glLineWidth(2.25)
        for cg in links_cg:
            x, y = cg[0], cg[1]
            glBegin(GL_LINES)
            glVertex2f(x - x_cross_size, y + y_cross_size)
            glVertex2f(x + x_cross_size, y - y_cross_size)
            glEnd()
            glBegin(GL_LINES)
            glVertex2f(x + x_cross_size, y + y_cross_size)
            glVertex2f(x - x_cross_size, y - y_cross_size)
            glEnd()

    def _draw_vector(self, color, origin_points, vectors, scale_vector, dot_on_origin_points=False):
        glEnable(GL_LINE_SMOOTH)
        glColor3ub(*color)
        cross_size = 8
        width = 2.5
        x_cross_size = (self.camera.view_range[0] / self.width()) * cross_size
        y_cross_size = (self.camera.view_range[1] / self.height()) * cross_size
        glLineWidth(width)

        sin_cos_45 = 0.7071067811865476
        width_length_ratio = (width / cross_size) / 2

        for origin_point, vector in zip(origin_points, vectors):
            x, y = origin_point[0], origin_point[1]
            vec_x, vec_y = vector[0], vector[1]

            magnitude = np.sqrt(vec_x ** 2 + vec_y ** 2)

            if magnitude == 0:
                continue
            if magnitude <= scale_vector[0]:
                scale = magnitude / scale_vector[0]
            elif magnitude < scale_vector[1] and scale_vector[0]*3 < scale_vector[1]:
                normalized_magnitude = (magnitude - scale_vector[0]) / (scale_vector[1] - scale_vector[0])
                linear_component = normalized_magnitude * 0.9
                logarithmic_component = np.log(1 + 9 * normalized_magnitude) / np.log(10)
                scale = 1 + linear_component * 0.5 + logarithmic_component * 0.5
            else:
                scale = 1 + 0.02 * ((magnitude / scale_vector[1]) - 1)

            scale *= self.simulation_space_range/4

            normalized_vec_x = (vec_x / magnitude) * scale
            normalized_vec_y = (vec_y / magnitude) * scale

            # Draw the main vector line
            glBegin(GL_LINES)
            glVertex2f(x, y)
            glVertex2f(x + normalized_vec_x, y + normalized_vec_y)
            glEnd()

            # Calculate perpendicular vectors for arrow heads
            perpendicular_x = -vec_y
            perpendicular_y = vec_x

            perpendicular_x /= magnitude
            perpendicular_y /= magnitude

            perpendicular_x *= x_cross_size
            perpendicular_y *= y_cross_size

            # Rotate the perpendicular vectors for arrow heads
            rotated_x_45_1 = perpendicular_x * sin_cos_45 - perpendicular_y * sin_cos_45
            rotated_x_45_2 = perpendicular_x * sin_cos_45 + perpendicular_y * sin_cos_45
            rotated_y_45_3 = -perpendicular_x * sin_cos_45 + perpendicular_y * sin_cos_45

            # Draw the arrow heads
            glBegin(GL_LINES)
            glVertex2f((x + normalized_vec_x) - rotated_x_45_1 * width_length_ratio,
                       (y + normalized_vec_y) - rotated_x_45_2 * width_length_ratio)
            glVertex2f((x + normalized_vec_x) + rotated_x_45_1, (y + normalized_vec_y) + rotated_x_45_2)
            glEnd()

            glBegin(GL_LINES)
            glVertex2f((x + normalized_vec_x) + rotated_x_45_2 * width_length_ratio,
                       (y + normalized_vec_y) + rotated_y_45_3 * width_length_ratio)
            glVertex2f((x + normalized_vec_x) - rotated_x_45_2, (y + normalized_vec_y) - rotated_y_45_3)
            glEnd()

            if dot_on_origin_points:
                glPointSize(10.0)
                glBegin(GL_POINTS)
                glVertex2f(x, y)
                glEnd()

    def update_simulation(self):
        self.current_frame = int(
            ((time.time() - self.initial_time) / (self.ani_run_time)) * self.len_data)
        if self.current_frame >= self.len_data:
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
        frames_per_step = int((self.len_data / self.simu_range) * step)
        self.current_frame = (self.current_frame + frames_per_step) % self.len_data
        self.skip_time += (self.ani_run_time / self.simu_range) * step
        self.update()

    def playback_speed_simulation(self, factor):
        ani_run_time_old = self.ani_run_time
        self.ani_run_time = (self.len_data * self.input.delta_time) / factor
        self.initial_time += (ani_run_time_old - self.ani_run_time) * (
                time.time() - self.initial_time) / ani_run_time_old

    def plot_simu(self, data):
        self.len_data = len(data)
        self.v_ang = self.input.speed_indep_var
        self.ani_run_time = self.len_data * self.input.delta_time

        self.display_simulation = True
        self.app.view_controller._is_simulation_running = True
        self.simulation_data = data
        self.current_frame = 0
        self.timer = self.startTimer(0)
        self.initial_time = time.time()

    def plot_image(self, data):
        self.display_simulation = False
        self.simulation_data = data
        self.current_frame = 0
        data = self.simulation_data[self.current_frame]
        self.update_projection()
        self.update()

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
                max_range =  max(width, height / self.camera.aspect_ratio)
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
