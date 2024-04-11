import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle


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
                                                "		groove: rgb(96, 33, 255)\n"
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
            self.ui.preveiew_button.setStyleSheet(u"QPushButton {\n"
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
            self.view_plot_colors = {
                "background-color": "#ffffff",
                "grid-color": "#DCDCDC",
                # "grid-color": "red", # For testing purposes
                "node-color": "#000000",
            }
            plt.rcParams.update({
                "lines.color": "w",
                "patch.edgecolor": "w",
                "text.color": "w",
                "axes.facecolor": self.view_plot_colors["background-color"],
                "axes.edgecolor": "w",
                "axes.labelcolor": "w",
                "xtick.color": "w",
                "ytick.color": "w",
                "grid.color": self.view_plot_colors["grid-color"],
                "figure.facecolor": self.view_plot_colors["background-color"],
                "figure.edgecolor": self.view_plot_colors["background-color"],
                "savefig.facecolor": self.view_plot_colors["background-color"],
                "savefig.edgecolor": self.view_plot_colors["background-color"]})

            # Set stylesheet for the menu bar
            self.ui.menubar.setStyleSheet("QMenuBar { color: rgb(0,0,0); }")

        if theme == 'dark':
            plt.style.use('dark_background')
            mplstyle.use('fast')
            matplotlib.rcParams['toolbar'] = 'None'

            self.ui.menubar.setStyleSheet("QMenuBar { color: rgb(255,255,255); }")
            self.view_plot_colors = {
                "background-color": "#000000",
                "grid-color": "#1E1E1E",
                "node-color": "#ffffff",
            }
            plt.rcParams.update({
                "lines.color": "k",
                "patch.edgecolor": "k",
                "text.color": "k",
                "axes.facecolor": self.view_plot_colors["background-color"],
                "axes.edgecolor": "k",
                "axes.labelcolor": "k",
                "xtick.color": "k",
                "ytick.color": "k",
                "grid.color": self.view_plot_colors["grid-color"],
                "figure.facecolor": self.view_plot_colors["background-color"],
                "figure.edgecolor": self.view_plot_colors["background-color"],
                "savefig.facecolor": self.view_plot_colors["background-color"],
                "savefig.edgecolor": self.view_plot_colors["background-color"]})
            pass
