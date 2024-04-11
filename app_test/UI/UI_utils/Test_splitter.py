
import numpy as np
from PySide6.QtWidgets import QPushButton
from app_test.UI.UI_utils.utils import check_zeros

class SplitterWithButton(QPushButton):
    def __init__(self, ui, button, splitter_expansion_factor):
        super().__init__()
        self.ui = ui
        self.button = button
        self.splitter_expansion_factor = splitter_expansion_factor
        self.button.clicked.connect(self.on_clicked)
        self.splitter_size_snapshot = np.array(self.ui.splitter.sizes())

    def on_clicked(self):
        if not check_zeros(self.ui.splitter.sizes(), self.splitter_expansion_factor):
            self.splitter_size_snapshot = np.array(self.ui.splitter.sizes())
            self.ui.splitter.setSizes(self.splitter_size_snapshot * self.splitter_expansion_factor)
        else:
            self.ui.splitter.setSizes(self.splitter_size_snapshot)