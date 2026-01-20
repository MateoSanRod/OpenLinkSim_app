import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QPalette)


class ThemeManager:
    def __init__(self, app, ui, theme):
        self.app = app
        self.ui = ui
        self.theme = theme
        self.graph_palette = {}
        self.graph_series_colors = {}
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
                "pos-color": [188, 173, 217],
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
                                                "        background-color: rgb(205, 205, 205);\n"
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
                                                "		 color: rgba(0, 0, 0, 0);\n"
                                                "    }\n"
                                                "")
            btn_light_hidden = (
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 0;"
                "  color: rgba(0, 0, 0, 0);"
                "}"
                "QPushButton:pressed {"
                "  color: rgba(0, 0, 0, 0);"
                "}"
            )
            self.ui.playstop_button.setStyleSheet(btn_light_hidden)
            self.ui.forwards_button.setStyleSheet(btn_light_hidden)
            self.ui.backwards_button.setStyleSheet(btn_light_hidden)

            self.graph_palette = {
                "face": "#f4f4f4",
                "spine": "#606060",
                "ticks": "#202020",
                "grid": "#cfcfcf",
                "text": "#202020",
                "line": "#1f77b4",
            }
            self.graph_series_colors = self._series_colors_from_palette()

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
                "pos-color": [158, 134, 200],
                "vel-color": [166, 226, 46],
                "acc-color": [253, 151, 31],
                "force-color": [102, 217, 239],
            }

            self.ui.render_button.setStyleSheet(u"QPushButton {\n"
                                             "        background-color: rgb(40, 40, 40);\n"
                                             "        border: none;\n"
                                             "		  color: #727272;\n"
                                             "    }\n"
                                             "    QPushButton:hover {\n"
                                             "        color: white; /* Change text color on hover */\n"
                                             "    }\n"
                                             "    QPushButton:pressed {\n"
                                             "        background-color: rgb(190, 190, 190);\n"
                                             "        color: rgb(35, 35, 35); /* Change text color when pressed */\n"
                                             "    }\n"
                                             "")

            # Make playback controls clearly visible on dark menu bar
            btn_dark_hidden = (
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 0;"
                "  color: rgba(0, 0, 0, 0);"
                "}"
                "QPushButton:pressed {"
                "  color: rgba(0, 0, 0, 0);"
                "}"
            )
            self.ui.playstop_button.setStyleSheet(btn_dark_hidden)
            self.ui.forwards_button.setStyleSheet(btn_dark_hidden)
            self.ui.backwards_button.setStyleSheet(btn_dark_hidden)
            self.ui.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                                  "        background-color: transparent;\n"
                                                  "        border: none;\n"
                                                  "        color: rgba(0, 0, 0, 0);\n"
                                                  "    }\n"
                                                  "    QPushButton:pressed {\n"
                                                  "        color: rgb(255, 255, 255);\n"
                                                  "    }\n"
                                                  "")

            self.ui.simOptionsButton.setStyleSheet("""
                        QToolButton {
                            background-color: rgb(40, 40, 40);
                            border: none;
                            color: #727272;
                            padding: 0px;    
                            margin: 0px;     
                            font-size: 8px; 
                        }
                        QToolButton:hover {
                            color: white;
                        }
                        QToolButton:pressed {
                            background-color: rgb(190, 190, 190);
                            color: rgb(35, 35, 35);
                        }
                        QToolButton::menu-indicator {
                            subcontrol-origin: padding;
                            subcontrol-position: center center;
                            width: 8px; 
                            height: 8px;
                        }
                    """)
            self.ui.simOptionsMenu.setStyleSheet("""
                        QMenu {
                            background-color: rgb(35, 35, 35);    /* light gray */
                            color:          rgb(190, 190, 190);     /* dark gray text */
                            border:         1px solid rgb(35, 35, 35);
                        }
                        QMenu::item:selected {
                            background-color: rgb(110, 110, 110);   /* slightly darker on hover */
                        }
                    """)
            self.graph_palette = {
                "face": "#1f1f1f",
                "spine": "#808080",
                "ticks": "#dcdcdc",
                "grid": "#444444",
                "text": "#e6e6e6",
                "line": "#59b8ff",
            }
            self.graph_series_colors = self._series_colors_from_palette()

        self.apply_graph_theme()

    def activate_ani_controlls(self):
        def flat(color: str, pressed: str):
            return (
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 0;"
                f"  color: {color};"
                "}"
                "QPushButton:pressed {"
                f"  color: {pressed};"
                "}"
            )

        if self.app.view_controller._is_simulation_running:
            self.ui.playstop_button.setStyleSheet(flat("#E67E7E", "#C94F4F"))
            font = QFont()
            font.setPointSize(13)
            self.ui.playstop_button.setFont(font)
            self.ui.playstop_button.setText("\u25A0")
            self.ui.forwards_button.setText(">>")
            self.ui.backwards_button.setText("<<")
            if self.theme == 'dark':
                btn = flat("rgb(230, 230, 230)", "rgb(255, 255, 255)")
                self.ui.ani_speed_label.setStyleSheet(
                    "QPushButton { background-color: transparent; border: none; color: rgb(230, 230, 230);} "
                    "QPushButton:pressed { color: rgb(255, 255, 255);} ")
            else:
                btn = flat("rgb(50, 50, 50)", "rgb(20, 20, 20)")
                self.ui.ani_speed_label.setStyleSheet(
                    "QPushButton { background-color: transparent; border: none; color: rgb(70, 70, 70);} "
                    "QPushButton:pressed { color: rgb(30, 30, 30);} ")
            self.ui.forwards_button.setStyleSheet(btn)
            self.ui.backwards_button.setStyleSheet(btn)
        else:
            self.ui.playstop_button.setStyleSheet(flat("#7BBB80", "#4F9E54"))
            font = QFont()
            font.setPointSize(20)
            self.ui.playstop_button.setFont(font)
            self.ui.playstop_button.setText("\u25BA")
            self.ui.forwards_button.setText(">|")
            self.ui.backwards_button.setText("|<")
            if self.theme == 'dark':
                btn = flat("rgb(230, 230, 230)", "rgb(255, 255, 255)")
            else:
                btn = flat("rgb(50, 50, 50)", "rgb(20, 20, 20)")
            self.ui.forwards_button.setStyleSheet(btn)
            self.ui.backwards_button.setStyleSheet(btn)

        pass

    def apply_graph_theme(self):
        if hasattr(self.app, "graph_widget") and self.app.graph_widget is not None and hasattr(self, "graph_palette"):
            self.app.graph_widget.apply_palette(self.graph_palette)
            self.app.graph_widget.set_series_colors(getattr(self, "graph_series_colors", {}))

    def _series_colors_from_palette(self):
        def to_hex(color_triplet, default):
            try:
                r, g, b = color_triplet
                r = max(0, min(int(r), 255))
                g = max(0, min(int(g), 255))
                b = max(0, min(int(b), 255))
                return f"#{r:02x}{g:02x}{b:02x}"
            except Exception:
                return default

        vp = getattr(self, "view_plot_palette", {})
        return {
            "Paths": to_hex(vp.get("pos-color", (156, 125, 217)), "#9c7dd9"),
            "Velocity": to_hex(vp.get("vel-color", (166, 226, 46)), "#a6e22e"),
            "Acceleration": to_hex(vp.get("acc-color", (253, 151, 31)), "#fd971f"),
            "Forces": to_hex(vp.get("force-color", (102, 217, 239)), "#66d9ef"),
            "Input": "#888888",
            "Time": "#888888",
        }

    def deactivate_ani_controlls(self):
        def flat(color: str, pressed: str):
            return (
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 0;"
                f"  color: {color};"
                "}"
                "QPushButton:pressed {"
                f"  color: {pressed};"
                "}"
            )

        self.ui.ani_speed_label.setText("")
        self.ui.playstop_button.setText("\u25BA")
        self.ui.forwards_button.setText(">>")
        self.ui.backwards_button.setText("<<")

        if self.theme == 'dark':
            btn = flat("rgb(230, 230, 230)", "rgb(255, 255, 255)")
            self.ui.ani_speed_label.setStyleSheet(
                "QPushButton { background-color: transparent; border: none; color: rgb(230, 230, 230);} "
                "QPushButton:pressed { color: rgb(255, 255, 255);} ")
        else:
            btn = flat("rgb(50, 50, 50)", "rgb(20, 20, 20)")
            self.ui.ani_speed_label.setStyleSheet(
                "QPushButton { background-color: transparent; border: none; color: rgb(70, 70, 70);} "
                "QPushButton:pressed { color: rgb(30, 30, 30);} ")

        self.ui.playstop_button.setStyleSheet(btn)
        self.ui.forwards_button.setStyleSheet(btn)
        self.ui.backwards_button.setStyleSheet(btn)
        pass

    def activate_preview_controlls(self):
        font = QFont()
        font.setPointSize(13)
        self.ui.playstop_button.setFont(font)
        self.ui.playstop_button.setText("\u25A0")
        self.ui.forwards_button.setText(">|")
        self.ui.backwards_button.setText("|<")

        def flat(color: str, pressed: str):
            return (
                "QPushButton {"
                "  background-color: transparent;"
                "  border: none;"
                "  padding: 0;"
                f"  color: {color};"
                "}"
                "QPushButton:pressed {"
                f"  color: {pressed};"
                "}"
            )

        if self.theme == 'dark':
            btn = flat("rgb(230, 230, 230)", "rgb(255, 255, 255)")
        else:
            btn = flat("rgb(50, 50, 50)", "rgb(20, 20, 20)")

        self.ui.playstop_button.setStyleSheet(btn)
        self.ui.forwards_button.setStyleSheet(btn)
        self.ui.backwards_button.setStyleSheet(btn)
        pass
