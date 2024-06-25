import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar
from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QPalette)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Blank Application")
        self.setGeometry(100, 100, 600, 400)

        menubar = self.menuBar()
        menubar.setStyleSheet("""
                                QMenuBar {
                                    background-color: #333; /* Background color */
                                    color: red; /* Text color */
                                }

                                QMenuBar::item {
                                    spacing: 6px; /* Spacing between menu items */
                                    padding: 40px 10px; /* Padding for each menu item */
                                    background-color: transparent; /* Background color of each menu item */
                                }

                                QMenuBar::item:selected {
                                    background-color: #555; /* Background color when menu item is selected */
                                }

                                QMenuBar::item:pressed {
                                    background-color: #777; /* Background color when menu item is pressed */
                                }

                                QMenu {
                                    background-color: #444; /* Background color of drop-down menus */
                                    color: white; /* Text color of drop-down menus */
                                    border: 1px solid #333; /* Border of drop-down menus */
                                }

                                QMenu::item {
                                    background-color: transparent; /* Background color of each item in drop-down menus */
                                }

                                QMenu::item:selected {
                                    background-color: #555; /* Background color when item in drop-down menu is selected */
                                }

                                QMenu::separator {
                                    background-color: #666; /* Color of separator lines in drop-down menus */
                                    height: 1px; /* Height of separator lines */
                                }
                                """
                              )

        fileMenu = menubar.addMenu('&File')

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(exitAction)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
