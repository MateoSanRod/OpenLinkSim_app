import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    def __init__(self, widget):
        self.widget = widget
        self.view_center = np.array([0.0, 0.0])  # Center of the camera
        self.view_range = np.array([1.0, 1.0])  # Width and height of the view
        self.aspect_ratio = self.widget.width() / self.widget.height()
        self.update_aspect_ratio()

    def update_aspect_ratio(self):
        """Update the view range based on the current aspect ratio."""
        if self.aspect_ratio > 1:
            self.view_range[1] = self.view_range[0] / self.aspect_ratio
        else:
            self.view_range[0] = self.view_range[1] * self.aspect_ratio

    def set_aspect_ratio(self, aspect_ratio):
        """Set the aspect ratio and update the view range accordingly."""
        self.aspect_ratio = aspect_ratio
        self.update_aspect_ratio()

    def zoom(self, factor):
        """Zoom the camera by scaling the view range."""
        self.view_range *= factor
        self.widget.update_projection()  # Ensure projection is updated after zoom

    def pan(self, dx, dy):
        """Pan the camera by adjusting the view center."""
        # Normalize panning by scaling it with the current view range
        self.view_center += np.array([-dx, +dy]) * self.view_range
        self.widget.update_projection()  # Ensure projection is updated after pan

    def apply_view(self):
        """Apply the camera's view (projection matrix) to OpenGL."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Calculate the boundaries of the view
        left = self.view_center[0] - self.view_range[0] / 2
        right = self.view_center[0] + self.view_range[0] / 2
        bottom = self.view_center[1] - self.view_range[1] / 2
        top = self.view_center[1] + self.view_range[1] / 2

        # Set the projection matrix using gluOrtho2D
        gluOrtho2D(left, right, bottom, top)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()  # Ensure the model view matrix is reset
