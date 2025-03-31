import sys
from pathlib import Path

from PySide6 import QtWidgets as qtw
from PySide6.QtWidgets import QMainWindow

from Controler.app_controller import AppController
from Controler.input_compiler import Input
from UI.UI_utils.Test_splitter import SplitterWithButton
from UI.UI_utils.theme_manager import ThemeManager
from app_test.Controler.view_controller import ViewPlotController
from app_test.UI.test_ui import Ui_MainWindow
from view.opengl_view_widget import ViewWidgetPlot

# txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_base.txt').read_text()
txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_input_links_v2.txt').read_text()
# txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_articulated_quafrilaters_2input_test.txt').read_text()
# txt = Path('C:/Users/teoto/PycharmProjects/CDIM_app/Tests/test_triangle_articulated.txt').read_text()
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Theme manager [light, dark]
        self.theme = 'light'
        # self.theme = 'dark'
        self.theme_manager = ThemeManager(self, self.ui, self.theme)

        # Input text editor
        self.ui.plainTextEdit.setPlainText(txt)
        self.input = Input(self)

        # Plot widget

        self.opengl_widget = ViewWidgetPlot(self)
        self.ui.view_widget.layout().addWidget(self.opengl_widget)


        # Event controller
        self.app_controller = AppController(self)
        self.installEventFilter(self.app_controller)
        self.ui.plainTextEdit.installEventFilter(self.app_controller)

        self.view_controller = ViewPlotController(self.opengl_widget,self)
        self.ui.view_widget.installEventFilter(self.view_controller)

        # self.move_to_second_screen()

        #  Later fix:

        # Connect the plot widget's mouse events to the controller
        # self.plot_widget.setMouseTracking(True)
        # self.plot_widget.mousePressEvent = self.app_controller.mousePressEvent
        # self.plot_widget.mouseReleaseEvent = self.app_controller.mouseReleaseEvent
        # self.plot_widget.mouseMoveEvent = self.app_controller.mouseMoveEvent
        # self.plot_widget.wheelEvent = self.app_controller.wheelEvent

        # Default window parameters
        self.ui.splitter.setSizes([650, 1000, 0])
        self.left_splitter_button = SplitterWithButton(self, self.ui.left_splitter_button, "left")
        self.right_splitter_button = SplitterWithButton(self, self.ui.right_splitter_button, "right")

    def move_to_second_screen(self):
        app = qtw.QApplication.instance()
        screens = app.screens()
        if len(screens) > 1:
            center_x = screens[1].geometry().center().x() - self.frameGeometry().width() // 2
            center_y = screens[1].geometry().center().y() - self.frameGeometry().height() // 2
            self.move(center_x, center_y)
        # self.showMaximized()

def main() -> None:
    app = qtw.QApplication(sys.argv)
    form = MainApp()
    form.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
