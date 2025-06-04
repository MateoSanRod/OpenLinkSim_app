import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    def __init__(self, widget):
        self.widget = widget
        self.view_center = np.array([0.0, 0.0])
        self.view_range = np.array([1.0, 1.0])
        self.aspect_ratio = self.widget.width() / self.widget.height()
        self.update_aspect_ratio()

    def update_aspect_ratio(self):
        if self.aspect_ratio > 1:
            self.view_range[1] = self.view_range[0] / self.aspect_ratio
        else:
            self.view_range[0] = self.view_range[1] * self.aspect_ratio

    def set_aspect_ratio(self, aspect_ratio):
        self.aspect_ratio = aspect_ratio
        self.update_aspect_ratio()

    def zoom(self, factor):
        self.view_range *= factor
        self.widget.update_projection()

    def pan(self, dx, dy):
        self.view_center += np.array([-dx, +dy]) * self.view_range
        self.widget.update_projection()

    def apply_view(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        left = self.view_center[0] - self.view_range[0] / 2
        right = self.view_center[0] + self.view_range[0] / 2
        bottom = self.view_center[1] - self.view_range[1] / 2
        top = self.view_center[1] + self.view_range[1] / 2

        gluOrtho2D(left, right, bottom, top)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
