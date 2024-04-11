from PySide6.QtWidgets import QSplitter, QSlider


class SplitterButton(Qb):
    def __init__(self):
        super().__init__()
        self.slider = QSlider(Qt.Horizontal)