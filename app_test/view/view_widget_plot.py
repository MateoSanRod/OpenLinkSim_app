import math
import time

import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from view.animation import FuncAnimation

from app_test.Controler.view_controller import ViewPlotController


class ViewWidgetPlot(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.input = self.app.input
        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.aspect_ratio = self.size().width() / self.size().height()
        self.view_center = np.array([0, 0])
        self.view_range = np.array([1, 1 / self.aspect_ratio])
        self.color_palette = self.app.theme_manager.view_plot_colors
        self.is_first_plot = True
        self.current_frame = 0

        self.controller = ViewPlotController(self, app)
        self.ax = self.figure.gca()
        self._blanck_plot()

    def _blanck_plot(self):
        self.figure.clear()
        self.ax = self.figure.gca()
        x_limits = self.ax.get_xlim()
        y_limits = self.ax.get_ylim()
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.grid(True, linestyle=(0, (5, 10)), linewidth=.5)
        self.ax.set_aspect('equal')
        self.ax.set_position([0, 0, 1, 1])
        self._update_limits()

        self.nodes = self.ax.scatter([], [], s=16, color=self.color_palette['node-color'], zorder=4)
        self.links_cg = self.ax.scatter([], [], s=25, marker='x', color='#F92672', zorder=5)
        self.links, = self.ax.plot([], [], color='darkgray', linestyle='-', linewidth=2.5, zorder=3)

    def plot_image(self, data):
        self._blanck_plot()
        self._destroy_previous_animation()
        self.simulation_data = data
        self._set_first_plot_limits(data)
        self._destroy_previous_animation()
        self.link_triger = True if len(self.simulation_data['link_line_list']) > 0 else False
        self.links_cg_triger = True if len(self.simulation_data['cg_global_cord']) > 0 else False

        self.nodes.set_offsets(np.column_stack([data['node_coordinates'][:, 0], data['node_coordinates'][:, 1]]))
        if self.link_triger:
            self.links.set_data(data['link_line_list'][:, :, 0], data['link_line_list'][:, :, 1])
            if self.links_cg_triger:
                self.links_cg.set_offsets(np.column_stack([data['cg_global_cord'][:, 0], data['cg_global_cord'][:, 1]]))
        self.canvas.draw_idle()

    def _animation_init(self):
        self.links.set_data([], [])
        self.nodes.set_offsets(np.empty((0, 2)))
        self.links_cg.set_offsets(np.empty((0, 2)))
        return self.links, self.nodes, self.links_cg

    def update(self, frame):
        data = self.simulation_data[self.current_frame]
        self.nodes.set_offsets(np.column_stack([data['node_coordinates'][:, 0], data['node_coordinates'][:, 1]]))

        if self.link_triger:
            self.links.set_data(data['link_line_list'][:, :, 0], data['link_line_list'][:, :, 1])
            if self.links_cg_triger:
                self.links_cg.set_offsets(np.column_stack([data['cg_global_cord'][:, 0], data['cg_global_cord'][:, 1]]))

        update_list = [self.nodes, self.links, self.links_cg]

        if not self.play_one_frame:
            self.current_frame += self.frame_jump
        if self.current_frame >= len(self.simulation_data) - 1:
            self.current_frame = 0
            print(f'loop time -> {time.time() - self.base_time:.2f})', f'target ->{self.ani_run_time:.2f}',
                  f'\n!!error!!{((time.time() - self.base_time) / (self.ani_run_time) - 1) * 100: .2f}%',
                  '\n' + '-' * 20)

            self.base_time = time.time()
        return update_list

    def plot_simu(self, data):
        self.simulation_data = data
        self._set_first_plot_limits(data)
        self._destroy_previous_animation()
        self._animation_init()

        self.link_triger = True if len(self.simulation_data[0]['link_line_list']) > 0 else False
        self.links_cg_triger = True if len(self.simulation_data[0]['cg_global_cord']) > 0 else False

        indep_vars = np.array([frame_data['independent_variable'] for frame_data in self.simulation_data])
        indices = np.where(indep_vars == self.input.init_indep_var)[0]
        self.current_frame = indices[0] if indices.size > 0 else 0

        self.len_data = len(indep_vars)
        self.target_fps = 150
        v_ang = 1
        resolution = 10
        self.ani_run_time = self.len_data * (((2 * np.pi) / v_ang) / (360 * resolution))

        frame_jump = self.len_data / (self.ani_run_time * self.target_fps)
        self.frame_jump = math.ceil(frame_jump) if frame_jump > 1 else 1

        self.interval_corrector = (frame_jump / self.frame_jump)
        self.interval = (1000 / self.target_fps) / self.interval_corrector

        print('-' * 20)
        print(f'{self.ani_run_time:.3f}', 'animation runtime')
        print(f'{frame_jump:.2f}', self.frame_jump, 'frame jump')
        print(f'{self.len_data / self.frame_jump:.2f}', 'frames to plot')
        print(f'{self.interval_corrector:.3f}', '<-- corrector | interval -->', f'{self.interval:.3f}')
        print('-' * 20)

        self.play_one_frame = False
        self.elapsed_time = time.time()
        self.base_time = time.time()
        self.ani = FuncAnimation(self.figure, self.update, frames=range(0, len(self.simulation_data)),
                                 blit=True, interval=self.interval,
                                 cache_frame_data=False)
        self.ani.running = True
        self.ani.speed = 1.0

    def steep_forward_animation(self):
        frame_steep = 10 * self.frame_jump
        if self.current_frame < self.len_data - frame_steep:
            self.current_frame += frame_steep
            self.ani.running = False
            self.play_one_frame = True
            self.ani.event_source.start()
            self.update(self.current_frame)
        else:
            self.current_frame = self.current_frame - self.len_data + frame_steep
            self.ani.running = False
            self.play_one_frame = True
            self.ani.event_source.start()
            self.update(self.current_frame)

    def steep_backward_animation(self):
        frame_steep = 10 * self.frame_jump
        if self.current_frame > self.frame_jump:
            self.current_frame -= frame_steep
            self.ani.running = False
            self.play_one_frame = True
            self.ani.event_source.start()
            self.update(self.current_frame)
        else:
            self.current_frame = self.len_data - 1 - self.current_frame
            self.current_frame -= frame_steep
            self.ani.running = False
            self.play_one_frame = True
            self.ani.event_source.start()
            self.update(self.current_frame)

    def speed_up_animation(self):
        if self.ani.speed > 10000:
            return
        self.ani.speed /= 0.5
        self.ani_run_time *= 0.5
        frame_jump = self.len_data / (self.ani_run_time * self.target_fps)
        self.frame_jump = math.ceil(frame_jump) if frame_jump > 1 else 1

        self.interval_corrector = (frame_jump / self.frame_jump)
        self.ani._interval = (1000 / self.target_fps) / self.interval_corrector

    def slow_down_animation(self):
        if self.ani.speed < 0.001:
            return
        self.ani.speed /= 2
        self.ani_run_time *= 2
        frame_jump = self.len_data / (self.ani_run_time * self.target_fps)
        self.frame_jump = math.ceil(frame_jump) if frame_jump > 1 else 1

        self.interval_corrector = (frame_jump / self.frame_jump)
        self.ani._interval = (1000 / self.target_fps) / self.interval_corrector

    def _destroy_previous_animation(self):
        if hasattr(self, 'ani'):
            self.current_frame = 0
            self.ani._stop()
            del self.ani
            self._blanck_plot()

    def _update_limits(self):
        self.ax.set_xlim((self.view_center[0] - self.view_range[0]),
                         (self.view_center[0] + self.view_range[0]))
        self.ax.set_ylim((self.view_center[1] - self.view_range[1]),
                         (self.view_center[1] + self.view_range[1]))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.aspect_ratio = self.size().width() / self.size().height()
        self.view_range[1] = self.view_range[0] / self.aspect_ratio
        self._update_limits()

    def _set_first_plot_limits(self, data):
        if self.is_first_plot:
            if type(data) is list:
                factor = 1.75
                x_max = np.array([i['node_coordinates'][:, 0].max() for i in data]).max()
                y_max = np.array([i['node_coordinates'][:, 1].max() for i in data]).max()
                x_min = np.array([i['node_coordinates'][:, 0].min() for i in data]).min()
                y_min = np.array([i['node_coordinates'][:, 1].min() for i in data]).min()
            else:
                factor = 2.5
                x_max = data['node_coordinates'][:, 0].max()
                y_max = data['node_coordinates'][:, 1].max()
                x_min = data['node_coordinates'][:, 0].min()
                y_min = data['node_coordinates'][:, 1].min()

            object_range = np.array([[x_max, x_min],
                                     [y_max, y_min]])
            self.view_center = np.array([np.mean(object_range[0]), np.mean(object_range[1])])
            view_range = (np.max(
                [np.ptp(object_range[0]), np.ptp(object_range[1])]) / 2) * factor
            self.view_range = [view_range, view_range / self.aspect_ratio]
            self._update_limits()
            self.is_first_plot = False
        else:
            self._update_limits()
