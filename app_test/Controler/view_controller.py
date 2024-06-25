import numpy as np
from app_test.Controler.run_model import run_image

class ViewPlotController():
    def __init__(self, plot_widget, app):
        self.plot_widget = plot_widget
        self.app = app
        self.ui = app.ui
        self.last_press = None
        self._is_panning = False
        self._x0 = 0
        self._y0 = 0

        # Connect mouse events
        self.plot_widget.canvas.mpl_connect('button_press_event', self._on_press)
        self.plot_widget.canvas.mpl_connect('button_release_event', self._on_release)
        self.plot_widget.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.plot_widget.canvas.mpl_connect('scroll_event', self._on_scroll)

        self._connect_buttons()

    def _connect_buttons(self):
        self.ui.playstop_button.clicked.connect(self._handle_playstop_button)
        self.ui.forwards_button.clicked.connect(self._handle_forwards_button)
        self.ui.backwards_button.clicked.connect(self._handle_backwards_button)

    def _on_press(self, event):
        if event.button == 1:  # Left mouse button
            self._is_panning = True
            self._x0 = event.x
            self._y0 = event.y

    def _on_release(self, event):
        if event.button == 1:  # Left mouse button
            self._is_panning = False

    def _on_motion(self, event):
        if self._is_panning:
            dx = event.x - self._x0
            dy = event.y - self._y0
            ax = self.plot_widget.figure.gca()
            view_xrange = np.array(ax.get_xlim()) - dx * 0.001 * np.ptp(ax.get_xlim())
            view_yrange = np.array(ax.get_ylim()) - dy * 0.001 * np.ptp(ax.get_ylim())
            ax.set_xlim(view_xrange)
            ax.set_ylim(view_yrange)
            self._x0 = event.x
            self._y0 = event.y
            self.plot_widget.view_center = np.array([view_xrange.mean(), view_yrange.mean()])

            self.plot_widget.canvas.draw()

    def _on_scroll(self, event):
        ax = self.plot_widget.figure.gca()
        mouse_x = event.xdata
        mouse_y = event.ydata

        if mouse_x is None or mouse_y is None:
            return

        if event.button == 'up':
            ax.set_xlim([mouse_x - (mouse_x - ax.get_xlim()[0]) * 0.9,
                         mouse_x + (ax.get_xlim()[1] - mouse_x) * 0.9])
            ax.set_ylim([mouse_y - (mouse_y - ax.get_ylim()[0]) * 0.9,
                         mouse_y + (ax.get_ylim()[1] - mouse_y) * 0.9])
        elif event.button == 'down':
            ax.set_xlim([mouse_x - (mouse_x - ax.get_xlim()[0]) * 1.1,
                         mouse_x + (ax.get_xlim()[1] - mouse_x) * 1.1])
            ax.set_ylim([mouse_y - (mouse_y - ax.get_ylim()[0]) * 1.1,
                         mouse_y + (ax.get_ylim()[1] - mouse_y) * 1.1])

        view_xrange = (ax.get_xlim()[1] - ax.get_xlim()[0]) / 2
        view_yrange = (ax.get_ylim()[1] - ax.get_ylim()[0]) / 2
        view_xcenter = np.array(ax.get_xlim()).mean()
        view_ycenter = np.array(ax.get_ylim()).mean()
        self.plot_widget.view_center = np.array([view_xcenter, view_ycenter])
        self.plot_widget.view_range = np.array([view_xrange, view_yrange])

        self.plot_widget.canvas.draw()

    def _handle_playstop_button(self):
        if hasattr(self.plot_widget, 'ani'):
            if self.plot_widget.ani.running:
                self.plot_widget.ani.running = False
                self.plot_widget.play_one_frame = True
                self.app.theme_manager.activate_ani_controlls()
                self.plot_widget.ani.event_source.stop()
            else:
                self.plot_widget.ani.event_source.start()
                self.plot_widget.ani.running = True
                self.plot_widget.play_one_frame = False
                self.app.theme_manager.activate_ani_controlls()

    def _handle_forwards_button(self):
        if hasattr(self.plot_widget, 'ani'):
            if self.plot_widget.ani.running:
                self.plot_widget.speed_up_animation()
            else:
                self.plot_widget.steep_forward_animation()
            self.ui.ani_speed_label.setText(f"{self.app.plot_widget.ani.speed}x")

        if self.plot_widget.is_first_plot == False:
            print('hola')
            self.app.input.compile()
            self.app.input.init_indep_var =+ 0.25
            run_image(self.app, self.app.plot_widget, self.app.input)

    def _handle_backwards_button(self):
        if hasattr(self.plot_widget, 'ani'):
            if self.plot_widget.ani.running:
                self.plot_widget.slow_down_animation()
            else:
                self.plot_widget.steep_backward_animation()
            self.ui.ani_speed_label.setText(f"{self.app.plot_widget.ani.speed}x")
