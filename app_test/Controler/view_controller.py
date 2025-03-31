import math

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QMouseEvent


class ViewPlotController(QObject):
    def __init__(self, opengl_widget, app):
        super().__init__()
        self.app = app
        self.ui = app.ui
        self.opengl_widget = opengl_widget
        self.camera = opengl_widget.camera
        self.last_press = None
        self._is_simulation_running = False  # Track simulation state

        self.playback_speed_factor = 1
        self.step_factor_decimals = 0
        self.step_factor = 1
        self.current_fib_index = 1

        self._connect_buttons()

    def _connect_buttons(self):
        self.ui.playstop_button.clicked.connect(self._handle_playstop_button)
        self.ui.forwards_button.clicked.connect(self._handle_forwards_button)
        self.ui.backwards_button.clicked.connect(self._handle_backwards_button)
        self.ui.ani_speed_label.mousePressEvent = self._handle_step_label

    def wheelEvent(self, event):
        zoom_factor = 0.9 if event.angleDelta().y() > 0 else 1.1
        self.camera.zoom(zoom_factor)
        self.opengl_widget.update()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        dx = (event.position().x() - self.last_mouse_pos.x()) / self.opengl_widget.width()
        dy = (event.position().y() - self.last_mouse_pos.y()) / self.opengl_widget.height()
        self.camera.pan(dx, dy)
        self.last_mouse_pos = event.position()

    def _handle_playstop_button(self):
        if self.opengl_widget.display_simulation:
            if self._is_simulation_running:
                self._is_simulation_running = not self._is_simulation_running
                self.opengl_widget.stop_simulation()
                self.app.theme_manager.activate_ani_controlls()
                if self.step_factor >= 1:
                    self.ui.ani_speed_label.setText(f"{self.step_factor:.0f}")
                else:
                    self.ui.ani_speed_label.setText(f"{self.step_factor:.{self.step_factor_decimals}f}")
            else:
                self._is_simulation_running = not self._is_simulation_running
                self.opengl_widget.play_simulation()
                self.app.theme_manager.activate_ani_controlls()
                if self.step_factor > 1:
                    self.ui.ani_speed_label.setText(f"{self.playback_speed_factor:.0f} x")
                else:
                    self.ui.ani_speed_label.setText(f"1/{(self._fib(self.current_fib_index)):.0f} x")

    def _handle_forwards_button(self):
        if self.opengl_widget.display_simulation:
            if self._is_simulation_running:
                if self.playback_speed_factor >= 1:
                    self.current_fib_index += 1
                    self.playback_speed_factor = self._fib(self.current_fib_index)
                    self.ui.ani_speed_label.setText(f"{self.playback_speed_factor:.0f} x")
                else:
                    self.current_fib_index -= 1
                    self.playback_speed_factor = 1 / (self._fib(self.current_fib_index))
                    self.ui.ani_speed_label.setText(f"1/{(self._fib(self.current_fib_index)):.0f} x")

                if self.playback_speed_factor == 1:
                    self.ui.ani_speed_label.setText("")
                self.opengl_widget.playback_speed_simulation(self.playback_speed_factor)
            else:
                self.opengl_widget.step_simulation(+self.step_factor)

    def _handle_backwards_button(self):
        if self.opengl_widget.display_simulation:
            if self._is_simulation_running:
                if self.playback_speed_factor > 1:
                    self.current_fib_index -= 1
                    self.playback_speed_factor = self._fib(self.current_fib_index)
                    self.ui.ani_speed_label.setText(f"{self.playback_speed_factor:.0f} x")
                else:
                    self.current_fib_index += 1
                    self.playback_speed_factor = 1 / (self._fib(self.current_fib_index))
                    self.ui.ani_speed_label.setText(f"1/{(self._fib(self.current_fib_index)):.0f} x")
                if self.playback_speed_factor == 1:
                    self.ui.ani_speed_label.setText("")
                self.opengl_widget.playback_speed_simulation(self.playback_speed_factor)
            else:
                self.opengl_widget.step_simulation(-self.step_factor)

    def _handle_step_label(self, event: QMouseEvent):
        if self.opengl_widget.display_simulation:
            if not self._is_simulation_running:
                if event.button() == Qt.LeftButton:
                    # Increase step factor
                    self.step_factor = self.next_step(self.step_factor, 1)

                elif event.button() == Qt.RightButton:
                    # Decrease step factor
                    self.step_factor = self.next_step(self.step_factor, -1)
                else:
                    return

                # Determine the number of significant decimal places dynamically
                if self.step_factor < 1:
                    decimal_places = abs(int(math.floor(math.log10(self.step_factor)))) + 1
                elif self.step_factor < 10:
                    decimal_places = 1
                else:
                    decimal_places = 0

                # Format the label with the appropriate number of significant figures
                self.ui.ani_speed_label.setText(f"{self.step_factor:.{decimal_places}f}")
    def next_step(self, value, direction):

        if value <= 0:
            raise ValueError("Step factor must be positive.")

        base = 10 ** math.floor(math.log10(value))
        approx_multiplier = value / base

        multipliers = [1, 2.5, 5, 7.5]

        closest_idx = min(range(len(multipliers)), key=lambda i: abs(multipliers[i] - approx_multiplier))

        multiplier_idx = closest_idx + direction
        if multiplier_idx < 0:
            base /= 10
            multiplier_idx = len(multipliers) - 1
        elif multiplier_idx >= len(multipliers):
            base *= 10
            multiplier_idx = 0

        return base * multipliers[multiplier_idx]

    def _fib(self, n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return b
