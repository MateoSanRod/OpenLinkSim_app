import sys
from pathlib import Path

from PySide6 import QtWidgets as qtw
from PySide6.QtWidgets import QMainWindow

from Controler.app_controller import AppController
from Controler.input_compiler import Input
from UI.UI_utils.Test_splitter import SplitterWithButton
from UI.UI_utils.theme_manager import ThemeManager
from app_test.UI.test_ui import Ui_MainWindow
from view.view_widget_plot import ViewWidgetPlot

txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_base.txt').read_text()
# txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links.txt').read_text()


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Theme manager [light, dark]
        self.theme = 'light'
        self.theme_manager = ThemeManager(self, self.ui, self.theme)

        # Default window parameters
        self.ui.splitter.setSizes([650, 1000, 0])
        self.left_splitter_button = SplitterWithButton(self.ui, self.ui.left_splitter_button, [0, 1, 1])
        self.right_splitter_button = SplitterWithButton(self.ui, self.ui.right_splitter_button, [1, 1, 0])

        # Input text editor
        self.ui.plainTextEdit.setPlainText(txt)
        self.input = Input(self)

        # Plot widget
        self.plot_widget = ViewWidgetPlot(self)
        self.ui.view_widget.layout().addWidget(self.plot_widget)

        # Event controller
        self.app_controller = AppController(self)
        self.installEventFilter(self.app_controller)
        self.ui.plainTextEdit.installEventFilter(self.app_controller)


def main() -> None:
    app = qtw.QApplication(sys.argv)
    form = MainApp()
    form.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
