import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QPalette)


class ThemeManager:
    def __init__(self, app, ui, theme):
        self.app = app
        self.ui = ui
        self.theme = theme
        self.set_theme(self.theme)

    def set_theme(self, theme):
        if theme == 'light':
            self.ui.mainwindow.setStyleSheet(u"QWidget {\n"
                                             "    background-color: rgb(220, 220, 220);\n"
                                             "}\n"
                                             "\n"
                                             "QMenuBar::item {\n"
                                             "    background-color: transparent;\n"
                                             "}\n"
                                             "\n"
                                             "QMenuBar::item:selected {\n"
                                             "    background-color: rgb(255, 255, 255);\n"
                                             "}\n"
                                             "")
            self.ui.splitter.setStyleSheet(u"QSplitter::handle {\n"
                                           "    background-color: rgb(220, 220, 220);\n"
                                           "}\n"
                                           "\n"
                                           "QSplitter::handle:pressed {\n"
                                           "    background-color: rgb(110, 110, 110);\n"
                                           "}\n"
                                           "")
            self.ui.left_widget.setStyleSheet(u"background-color: rgb(243, 243, 243);")
            self.ui.plainTextEdit.setStyleSheet(u"QPlainTextEdit {\n"
                                                "    background-color: rgb(243, 243, 243);\n"
                                                "    color: #000000;\n"
                                                "    border: none rgb(243, 243, 243); \n"
                                                "    padding: 0px; /* Remove default padding */\n"
                                                "    font-size: 12px; /* Font size */\n"
                                                "    groove: none; /* Remove the groove */\n"
                                                "    font-family: Consolas, monospace; /* Font family */\n"
                                                "}\n"
                                                "\n"
                                                "QPlainTextEdit QScrollBar {\n"
                                                "		background: rgb(243, 243, 243);\n"
                                                "		border: none;\n"
                                                "		margin: 0;\n"
                                                "		padding: 0;\n"
                                                "		width: 10px;\n"
                                                "	}\n"
                                                "	\n"
                                                "QPlainTextEdit QScrollBar:handle {\n"
                                                "		border: none;\n"
                                                "		background:  rgb(189, 189, 189);\n"
                                                "}\n"
                                                "\n"
                                                "QPlainTextEdit QScrollBar::add-line:vertical, QPlainTextEdit QScrollBar::sub-line:vertical {\n"
                                                "    background: none; /* No background for scrollbar buttons */\n"
                                                "}\n"
                                                "QPlainTextEdit QScrollBar::up-arrow:vertical, QPlainTextEdit QScrollBar::down-arrow:vertical{\n"
                                                "	background: none;\n"
                                                "}\n"
                                                "QPlainTextEdit QScrollBar::add-page:vertical, QPlainTextEdit QScro"
                                                "llBar::sub-page:vertical{\n"
                                                "	background: none;\n"
                                                "}\n"
                                                "\n"
                                                "QPlainTextEdit {\n"
                                                "    selection-color: #000000; /* Change selection text color */\n"
                                                "    selection-background-color: #A4CDFF; /* Change selection background color */\n"
                                                "}")
            self.ui.left_splitter_widget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
            self.ui.left_splitter_button.setStyleSheet(u"QPushButton {\n"
                                                       "    background-color: rgb(220, 220, 220); \n"
                                                       "    color: white; /* White text color */\n"
                                                       "	border: 4px solid rgb(255, 255, 255)\n"
                                                       "}\n"
                                                       "\n"
                                                       "QPushButton:hover {\n"
                                                       "    background-color: rgb(190, 190, 190); \n"
                                                       "}\n"
                                                       "\n"
                                                       "QPushButton:pressed {\n"
                                                       "    background-color: rgb(110, 110, 110);  \n"
                                                       "}\n"
                                                       "\n"
                                                       "")
            self.ui.view_widget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
            self.ui.right_splitter_widget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
            self.ui.right_splitter_button.setStyleSheet(self.ui.left_splitter_button.styleSheet())
            self.ui.right_widget.setStyleSheet(self.ui.left_widget.styleSheet())
            mplstyle.use('fast')
            self.ui.preview_button.setStyleSheet(u"QPushButton {\n"
                                                 "        background-color: transparent;\n"
                                                 "        border: none;\n"
                                                 "        padding: 4px; \n"
                                                 "        color: rgb(220, 220, 220);\n"
                                                 "    }\n"
                                                 "    QPushButton:hover {\n"
                                                 "        color: rgb(190, 190, 190); /* Change text color on hover */\n"
                                                 "    }\n"
                                                 "    QPushButton:pressed {\n"
                                                 "        color: rgb(110, 110, 110); /* Change text color when pressed */\n"
                                                 "    }\n"
                                                 "")
            self.view_plot_palette = {
                "background-color": [255, 255, 255],
                "grid-color": [220, 220, 220],
                "node-color": [0, 0, 0],
                "link-color": [169, 169, 169],
                "cg-color": [249, 38, 114],
                "vel-color": [166, 226, 46],
                "acc-color": [253, 151, 31],
                "force-color": [102, 217, 239],
            }

            # Set stylesheet for the menu bar
            height = 9
            self.ui.menubar.setStyleSheet("QMenuBar {\n"
                                          "    color: black;\n"
                                          "}\n"
                                          "\n"
                                          "QMenuBar::item {\n"
                                          f"    padding: {height}px 10px; /* Padding for each menu item */\n"
                                          "    background-color: transparent; /* Background color of each menu item */\n"
                                          "}\n"
                                          "\n"
                                          "QMenuBar::item:selected {\n"
                                          "    background-color: rgb(190, 190, 190); /* Background color when menu item is hover */\n"
                                          "    padding: 0px; /* Remove padding */\n"
                                          "}\n"
                                          "\n"
                                          "QMenuBar::item:pressed {\n"
                                          "    background-color: #A4CDFF; /* Background color when menu item is pressed */\n"
                                          "}\n"
                                          "\n"
                                          "QMenu {\n"
                                          "    background-color: red; /* Background color of drop-down menus */\n"
                                          "    color: blue; /* Text color of drop-down menus */\n"
                                          "    border: 0px solid #333; /* Border of drop-down menus */\n"
                                          "}\n"
                                          "\n"
                                          "QMenu::item {\n"
                                          "    background-color: transparent; /* Background color of each item in drop-down menus */\n"
                                          "}\n"
                                          "\n"
                                          "QMenu::item:selected {\n"
                                          "    background-color: #555; /* Background color when item in drop-down menu is selected */\n"
                                          "}\n"
                                          "\n"
                                          "QMenu::separator {\n"
                                          "    background-color: #666; /* Color of separator lines in drop-down menus */\n"
                                          "    height: 1px; /* Height of separator lines */\n"
                                          "}\n"
                                          )
            self.ui.render_button.setStyleSheet(u"QPushButton {\n"
                                                "        background-color: transparent;\n"
                                                "        border: none;\n"
                                                "		 color: rgb(110, 110, 110);\n"
                                                "    }\n"
                                                "    QPushButton:hover {\n"
                                                "        color: black; /* Change text color on hover */\n"
                                                "    }\n"
                                                "    QPushButton:pressed {\n"
                                                "        background-color: #727272;\n"
                                                "        color: rgb(220, 220, 220); /* Change text color when pressed */\n"
                                                "    }\n"
                                                "")
            self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                "        background-color: transparent;\n"
                                                "        border: none;\n"
                                                "		 color: rgb(110, 110, 110);\n"
                                                "    }\n"
                                                "")
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(190, 190, 190);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.forwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())
            self.ui.backwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())

        if theme == 'dark':
            plt.style.use('dark_background')
            mplstyle.use('fast')
            matplotlib.rcParams['toolbar'] = 'None'

            self.view_plot_palette = {
                "background-color": [0, 0, 0],
                "grid-color": [30, 30, 30],
                "node-color": [255, 255, 255],
                "link-color": [169, 11699, 169],
                "cg-color": [249, 38, 114],
                "vel-color": [166, 226, 46],
                "acc-color": [253, 151, 31],
                "force-color": [102, 217, 239],
            }
            pass

    def activate_ani_controlls(self):
        if self.app.view_controller._is_simulation_running:
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: #E67E7E;\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: #C94F4F; /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            font = QFont()
            font.setPointSize(13)
            self.ui.playstop_button.setFont(font)
            self.ui.playstop_button.setText("\u25A0")
            self.ui.forwards_button.setText(">>")
            self.ui.backwards_button.setText("<<")
            if self.theme == 'dark':
                self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "")
                self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "        padding: none; \n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "    QPushButton:pressed {\n"
                                                      "        color: rgb(190, 190, 190); /* Change text color when pressed */\n"
                                                      "    }\n"
                                                      "")
                self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())
            if self.theme == 'light':
                self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "")
                self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "        padding: none; \n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "    QPushButton:pressed {\n"
                                                      "        color: rgb(48, 48, 48); /* Change text color when pressed */\n"
                                                      "    }\n"
                                                      "")
                self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())
        else:

            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: #7BBB80;\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: #4F9E54; /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            font = QFont()

            font.setPointSize(20)
            self.ui.playstop_button.setFont(font)
            self.ui.playstop_button.setText("\u25BA")
            self.ui.forwards_button.setText(">|")
            self.ui.backwards_button.setText("|<")
            if self.theme == 'dark':
                self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "        padding: none; \n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "    QPushButton:pressed {\n"
                                                      "        color: rgb(190, 190, 190); /* Change text color when pressed */\n"
                                                      "    }\n"
                                                      "")
                self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())
            if self.theme == 'light':
                self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                      "        background-color: transparent;\n"
                                                      "        border: none;\n"
                                                      "        padding: none; \n"
                                                      "		 color: rgb(114, 114, 114);\n"
                                                      "    }\n"
                                                      "    QPushButton:pressed {\n"
                                                      "        color: rgb(48, 48, 48); /* Change text color when pressed */\n"
                                                      "    }\n"
                                                      "")
                self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())

        pass

    def deactivate_ani_controlls(self):
        if self.theme == 'dark':
            self.ui.ani_speed_label.setText("")
            self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "		 color: rgb(114, 114, 114);\n"
                                                  "    }\n"
                                                  "")
            self.ui.playstop_button.setText("\u25BA")
            self.ui.forwards_button.setText(">>")
            self.ui.backwards_button.setText("<<")
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(114, 114, 114);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(190, 190, 190); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.forwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())
            self.ui.backwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())
        if self.theme == 'light':
            self.ui.ani_speed_label.setText("")
            self.ui.playstop_button.setText("\u25BA")
            self.ui.forwards_button.setText(">>")
            self.ui.backwards_button.setText("<<")
            self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "		 color: rgb(114, 114, 114);\n"
                                                  "    }\n"
                                                  "")
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(190, 190, 190);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.forwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())
            self.ui.backwards_button.setStyleSheet(self.ui.playstop_button.styleSheet())
        pass

    def activate_preview_controlls(self):
        font = QFont()
        font.setPointSize(13)
        self.ui.playstop_button.setFont(font)
        self.ui.playstop_button.setText("\u25A0")
        self.ui.forwards_button.setText(">|")
        self.ui.backwards_button.setText("|<")
        if self.theme == 'dark':
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(48, 48, 48);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(48, 48, 48);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())
        if self.theme == 'light':
            self.ui.playstop_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		 color: rgb(190, 190, 190);\n"

                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.forwards_button.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        padding: none; \n"
                                                  "		   color: rgb(190, 190, 190);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                                  "    }\n"
                                                  "")
            self.ui.backwards_button.setStyleSheet(self.ui.forwards_button.styleSheet())
        pass
