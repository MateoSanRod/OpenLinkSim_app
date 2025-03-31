import numpy as np
from PySide6.QtWidgets import QPushButton
import numpy as np
from PySide6.QtWidgets import QPushButton


import numpy as np
from PySide6.QtWidgets import QPushButton

class SplitterWithButton(QPushButton):
    def __init__(self, app, button, splitter_side):
        super().__init__()
        self.ui = app.ui
        self.button = button
        self.splitter_side = 0 if splitter_side == "left" else -1
        self.button.clicked.connect(self.on_clicked)
        self.first_resize = True
    def on_clicked(self):
        current_sizes = np.array(self.ui.splitter.sizes(), dtype=np.float64)
        total_size = np.sum(current_sizes)
        new_sizes = np.array(current_sizes)
        ratios = np.array([i / (total_size - new_sizes[self.splitter_side]) for idx, i in enumerate(new_sizes)])

        if self.first_resize:
            self.splitter_size_snapshot = current_sizes
            self.first_resize = False


        if current_sizes[self.splitter_side] != 0:
            self.splitter_size_snapshot[self.splitter_side] = current_sizes[self.splitter_side]
            new_sizes = new_sizes + (ratios * new_sizes[self.splitter_side])
            new_sizes[self.splitter_side] = 0
            self.ui.splitter.setSizes(new_sizes)
            print("Collapsed:", new_sizes)
        else:
            if self.splitter_size_snapshot[self.splitter_side] == 0:
                snaphot_ratios = np.array([i / (sum(self.splitter_size_snapshot)) for i in self.splitter_size_snapshot])
                self.splitter_size_snapshot[self.splitter_side] = int(sum(self.splitter_size_snapshot) * 0.15)
                self.splitter_size_snapshot = self.splitter_size_snapshot + (snaphot_ratios * self.splitter_size_snapshot[self.splitter_side])

                self.splitter_size_snapshot[1] -= new_sizes[self.splitter_side]

            new_sizes = self.splitter_size_snapshot * ratios
            new_sizes[self.splitter_side] = self.splitter_size_snapshot[self.splitter_side]
            self.ui.splitter.setSizes(new_sizes)
            # self.ui.splitter.setSizes(self.splitter_size_snapshot)
            print("Restored:", self.splitter_size_snapshot)

        print("End sizes:", self.ui.splitter.sizes())
