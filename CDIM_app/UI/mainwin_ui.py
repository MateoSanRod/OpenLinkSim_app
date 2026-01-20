# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwin_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt,QTimer)
from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QPalette,QActionGroup)
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout,
                               QLayout, QMenu, QMenuBar,
                               QPlainTextEdit, QPushButton, QSplitter,
                               QStatusBar, QVBoxLayout, QWidget, QLabel,QToolButton,
                               QWidgetAction, QLineEdit)
from .UI_utils.display_buttontree import VectorTree


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(921, 636)
        self.mainwindow = MainWindow
        self.mainwindow.resizeEvent = self.adjustWindowSize
        palette = QPalette()
        brush = QBrush(QColor(35, 35, 35, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        MainWindow.setPalette(palette)
        MainWindow.setStyleSheet(u"QWidget {\n"
                                 "    background-color: rgb(35, 35, 35);\n"
                                 "}\n"
                                 "QMenuBar::item {\n"
                                 "    background-color: transparent;\n"
                                 "}\n"
                                 "QMenuBar::item:selected {\n"
                                 "    background-color: #303030;\n"
                                 "}\n"
                                 "")
        self.action1 = QAction(MainWindow)
        self.action1.setObjectName(u"action1")
        self.action2 = QAction(MainWindow)
        self.action2.setObjectName(u"action2")
        self.action3 = QAction(MainWindow)
        self.action3.setObjectName(u"action3")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle {\n"
                                    "    background-color: rgb(35, 35, 35);\n"
                                    "}\n"
                                    "\n"
                                    "QSplitter::handle:pressed {\n"
                                    "    background-color: #E5E5E5;\n"
                                    "}\n"
                                    "")
        self.splitter.setFrameShape(QFrame.NoFrame)
        self.splitter.setFrameShadow(QFrame.Plain)
        self.splitter.setLineWidth(0)
        self.splitter.setMidLineWidth(0)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(2)
        self.left_widget = QWidget(self.splitter)
        self.left_widget.setObjectName(u"left_widget")
        self.left_widget.setStyleSheet(u"background-color: rgb(48, 48, 48);")
        self.frame = QFrame(self.left_widget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(9, 9, 601, 210))
        self.frame.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit = QPlainTextEdit(self.frame)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setBaseSize(QSize(0, 0))
        self.plainTextEdit.setStyleSheet(u"QPlainTextEdit {\n"
                                         "    background-color: #303030; /* Dark background */\n"
                                         "    color: #ffffff; /* White text color */\n"
                                         "    border: 1px solid #303030; /* Dark border */\n"
                                         "    padding: 0px; /* Remove default padding */\n"
                                         "    font-size: 12px; /* Font size */\n"
                                         "    groove: none; /* Remove the groove */\n"
                                         "    font-family: Consolas, monospace; /* Font family */\n"
                                         "}\n"
                                         "\n"
                                         "QPlainTextEdit QScrollBar {\n"
                                         "		background: #303030;\n"
                                         "		border: none;\n"
                                         "		margin: 0;\n"
                                         "		padding: 0;\n"
                                         "		width: 10px;\n"
                                         "		groove: rgb(96, 33, 255)\n"
                                         "	}\n"
                                         "	\n"
                                         "QPlainTextEdit QScrollBar:handle {\n"
                                         "		border: none;\n"
                                         "		background: #414141;\n"
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
                                         "    selection-color: #ffffff; /* Change selection text color */\n"
                                         "    selection-background-color: rgb(153, 153, 153); /* Change selection background color */\n"
                                         "}")
        self.plainTextEdit.setTabStopDistance(20.000000000000000)
        self.left_widget.resizeEvent = self.adjustFrameSize

        self.horizontalLayout_3.addWidget(self.plainTextEdit)

        self.preview_button = QPushButton(self.left_widget)
        self.preview_button.setObjectName(u"preveiew_button")
        self.preview_button.setGeometry(QRect(290, 520, 40, 40))
        font = QFont()
        font.setPointSize(22)
        self.preview_button.setFont(font)
        self.preview_button.setStyleSheet(u"QPushButton {\n"
                                           "        background-color: transparent;\n"
                                           "        border: none;\n"
                                           "        padding: 4px; \n"
                                           "		 color: rgb(35, 35, 35);\n"
                                           "    }\n"
                                           "    QPushButton:hover {\n"
                                           "        color: #727272; /* Change text color on hover */\n"
                                           "    }\n"
                                           "    QPushButton:pressed {\n"
                                           "        color: #E5E5E5; /* Change text color when pressed */\n"
                                           "    }\n"
                                           "")
        self.splitter.addWidget(self.left_widget)
        self.main_main_widget = QWidget(self.splitter)
        self.main_main_widget.setObjectName(u"main_main_widget")
        self.main_main_widget.setMinimumSize(QSize(50, 20))
        self.main_main_widget.setBaseSize(QSize(0, 0))
        self.horizontalLayout_2 = QHBoxLayout(self.main_main_widget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.left_splitter_widget = QWidget(self.main_main_widget)
        self.left_splitter_widget.setObjectName(u"left_splitter_widget")
        self.left_splitter_widget.setMinimumSize(QSize(8, 0))
        self.left_splitter_widget.setMaximumSize(QSize(8, 16777215))
        self.left_splitter_widget.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.verticalLayout_2 = QVBoxLayout(self.left_splitter_widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.left_splitter_button = QPushButton(self.left_splitter_widget)
        self.left_splitter_button.setObjectName(u"left_splitter_button")
        self.left_splitter_button.setMinimumSize(QSize(10, 33))
        self.left_splitter_button.setMaximumSize(QSize(10, 33))
        self.left_splitter_button.setStyleSheet(u"QPushButton {\n"
                                                "    background-color: rgb(48, 48, 48); \n"
                                                "    color: white; /* White text color */\n"
                                                "	border: 4px solid black\n"
                                                "}\n"
                                                "\n"
                                                "QPushButton:hover {\n"
                                                "    background-color: rgb(114, 114, 114); \n"
                                                "}\n"
                                                "\n"
                                                "QPushButton:pressed {\n"
                                                "    background-color: #E5E5E5;  \n"
                                                "}\n"
                                                "\n"
                                                "")

        self.verticalLayout_2.addWidget(self.left_splitter_button, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.left_splitter_widget)

        self.view_widget = QWidget(self.main_main_widget)
        self.view_widget.setObjectName(u"view_widget")
        self.view_widget.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.gridLayout = QGridLayout(self.view_widget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_2.addWidget(self.view_widget)

        self.right_splitter_widget = QWidget(self.main_main_widget)
        self.right_splitter_widget.setObjectName(u"right_splitter_widget")
        self.right_splitter_widget.setMinimumSize(QSize(8, 0))
        self.right_splitter_widget.setMaximumSize(QSize(8, 16777215))
        self.right_splitter_widget.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.verticalLayout = QVBoxLayout(self.right_splitter_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.right_splitter_button = QPushButton(self.right_splitter_widget)
        self.right_splitter_button.setObjectName(u"right_splitter_button")
        self.right_splitter_button.setMinimumSize(QSize(10, 33))
        self.right_splitter_button.setMaximumSize(QSize(10, 33))
        self.right_splitter_button.setStyleSheet(u"QPushButton {\n"
                                                 "    background-color: rgb(48, 48, 48); \n"
                                                 "    color: white; /* White text color */\n"
                                                 "	border: 4px solid black\n"
                                                 "}\n"
                                                 "\n"
                                                 "QPushButton:hover {\n"
                                                 "    background-color: rgb(114, 114, 114); \n"
                                                 "}\n"
                                                 "\n"
                                                 "QPushButton:pressed {\n"
                                                 "    background-color: #E5E5E5;  \n"
                                                 "}\n"
                                                 "\n"
                                                 "\n"
                                                 "")

        self.verticalLayout.addWidget(self.right_splitter_button, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.right_splitter_widget)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 100000)
        self.horizontalLayout_2.setStretch(2, 1)
        self.splitter.addWidget(self.main_main_widget)
        self.right_widget = QWidget(self.splitter)
        self.right_widget.setObjectName(u"right_widget")
        self.right_widget.setStyleSheet(u"Background-color:rgb(48, 48, 48);")
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(6, 6, 6, 6)
        self.right_layout.setSpacing(6)
        self.splitter.addWidget(self.right_widget)

        self.horizontalLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        height = 9
        self.menubar.setStyleSheet("QMenuBar {\n"
                                   "    color: white;\n"
                                   "}\n"
                                   "\n"
                                   "QMenuBar::item {\n"
                                   f"    padding: {height}px 10px; /* Padding for each menu item */\n"
                                   "    background-color: transparent; /* Background color of each menu item */\n"
                                   "}\n"
                                   "\n"
                                   "QMenuBar::item:selected {\n"
                                   "    background-color: rgb(48, 48, 48); /* Background color when menu item is hover */\n"
                                   "    padding: 0px; /* Remove padding */\n"
                                   "}\n"
                                   "\n"
                                   "QMenuBar::item:pressed {\n"
                                   "    background-color: rgb(114, 114, 114); /* Background color when menu item is pressed */\n"
                                   "}\n"
                                   "\n"
                                   "QMenu {\n"
                                   "    background-color: rgb(190, 190, 190); /* Background color of drop-down menus */\n"
                                   "    color: rgb(11, 11, 11); /* Text color of drop-down menus */\n"
                                   "    border: 0px solid #333; /* Border of drop-down menus */\n"
                                   "}\n"
                                   "\n"
                                   "QMenu::item {\n"
                                   "    background-color: transparent; /* Background color of each item in drop-down menus */\n"
                                   "}\n"
                                   "\n"
                                   "QMenu::item:selected {\n"
                                   "    background-color: rgb(190, 190, 190); /* Background color when item in drop-down menu is selected */\n"
                                   "}\n"
                                   "\n"
                                   "QMenu::separator {\n"
                                   "    background-color: rgb(190, 190, 190); /* Color of separator lines in drop-down menus */\n"
                                   "    height: 1px; /* Height of separator lines */\n"
                                   "}\n"
                                   )
        self.menubar_height = self.menubar.height() + height - 3
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        font = self.menuFile.font()
        font.setPointSize(8)
        self.menuFile.setFont(font)

        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")

        self.render_button = QPushButton(self.menubar)
        self.render_button.setObjectName(u"render_button")
        self.render_button.setText("\u2637")
        self.render_button.setGeometry(QRect(80, 0, self.menubar_height-9, self.menubar_height))
        self.render_button.setStyleSheet(u"QPushButton {\n"
                                         "        background-color: transparent;\n"
                                         "        border: none;\n"
                                         "		 color: #727272;\n"
                                         "    }\n"
                                         "    QPushButton:hover {\n"
                                         "        color: white; /* Change text color on hover */\n"
                                         "    }\n"
                                         "    QPushButton:pressed {\n"
                                         "        background-color: rgb(190, 190, 190);\n"
                                         "        color: rgb(35, 35, 35); /* Change text color when pressed */\n"
                                         "    }\n"
                                         "")
        
        self.ani_speed_label = QPushButton(self.menubar)
        self.ani_speed_label.setGeometry(QRect(500, 0, self.menubar_height * 2.8, self.menubar_height))
        font = QFont()
        font.setPointSize(10)
        self.ani_speed_label.setFont(font)
        self.ani_speed_label.setText("")
        # self.ani_speed_label.setAlignment(Qt.AlignCenter)
        self.ani_speed_label.setStyleSheet(u"QPushButton {\n"
                                         "        background-color: transparent;\n"
                                         "        border: none;\n"
                                         "		 color: #727272;\n"
                                         "    }\n"
                                         "    QPushButton:hover {\n"
                                         "        color: white; /* Change text color on hover */\n"
                                         "    }\n"
                                         "    QPushButton:pressed {\n"
                                         "        background-color: rgb(190, 190, 190);\n"
                                         "        color: rgb(35, 35, 35); /* Change text color when pressed */\n"
                                         "    }\n"
                                         "")
            # 1) Create the little down-arrow toolbutton
        self.simOptionsButton = QToolButton(self.menubar)
        self.simOptionsButton.setObjectName("simOptionsButton")
        font = QFont()
        font.setPointSize(5)
        self.simOptionsButton.setFont(font)
        # Show popup menu instantly when clicked
        self.simOptionsButton.setPopupMode(QToolButton.InstantPopup)

        # Position it immediately to the right of the render_button
        rb = self.render_button.geometry()
        self.simOptionsButton.setGeometry(
            QRect(
                rb.x() + rb.width(),  # no extra gap
                0,
                10,
                self.menubar_height
            )
        )

        self.simOptionsMenu = QMenu(self.simOptionsButton)
        self.simOptionsButton.setMenu(self.simOptionsMenu)
        self.simOptionsButton.setStyleSheet("""
            QToolButton {
                background-color: rgb(205, 205, 205);
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
        self.simOptionsMenu.setStyleSheet("""
            QMenu {
                background-color: #E0E0E0;    /* light gray */
                color:          #333333;     /* dark gray text */
                border:         1px solid #AAAAAA;
            }
            QMenu::item:selected {
                background-color: #CCCCCC;   /* slightly darker on hover */
            }
        """)

        # — 1) Kinematic & Dynamic analysis — both checkable, not exclusive —
        self.kin_action = QAction("Kinematic analysis", self.simOptionsMenu)
        self.kin_action.setCheckable(True)
        self.dyn_action = QAction("Dynamic analysis", self.simOptionsMenu)
        self.dyn_action.setCheckable(True)

        self.simOptionsMenu.addAction(self.kin_action)
        self.simOptionsMenu.addAction(self.dyn_action)
        self.simOptionsMenu.addSeparator()


        timestep_widget_action = QWidgetAction(self.simOptionsMenu)
        sw = QWidget();
        sw.setLayout(QHBoxLayout())
        sw.layout().setContentsMargins(8, 4, 8, 4)
        sw.layout().addWidget(QLabel("Time step:"))
        self.timestepLineEdit = QLineEdit("")
        self.timestepLineEdit.setMaximumWidth(60)
        sw.layout().addWidget(self.timestepLineEdit)
        timestep_widget_action.setDefaultWidget(sw)
        self.simOptionsMenu.addAction(timestep_widget_action)

        # — 2) Duration (s) entry —
        time_widget_action = QWidgetAction(self.simOptionsMenu)
        tw = QWidget();
        tw.setLayout(QHBoxLayout())
        tw.layout().setContentsMargins(8, 4, 8, 4)
        tw.layout().addWidget(QLabel("Duration:"))
        self.simTimeLineEdit = QLineEdit("")
        self.simTimeLineEdit.setMaximumWidth(60)
        tw.layout().addWidget(self.simTimeLineEdit)
        time_widget_action.setDefaultWidget(tw)
        self.simOptionsMenu.addAction(time_widget_action)

        # — 3) Gravity (m/s²) entry —
        grav_widget_action = QWidgetAction(self.simOptionsMenu)
        gw = QWidget();
        gw.setLayout(QHBoxLayout())
        gw.layout().setContentsMargins(8, 4, 8, 4)
        gw.layout().addWidget(QLabel("Gravity:"))
        self.gravityLineEdit = QLineEdit("0")
        self.gravityLineEdit.setMaximumWidth(60)
        gw.layout().addWidget(self.gravityLineEdit)
        grav_widget_action.setDefaultWidget(gw)
        self.simOptionsMenu.addAction(grav_widget_action)



        # Attach menu to button
        # self.ani_speed_label = QLabel(self.menubar)
        # self.ani_speed_label.setGeometry(QRect(500, 0, self.menubar_height * 2.8, self.menubar_height))
        # font = QFont()
        # font.setPointSize(10)
        # self.ani_speed_label.setFont(font)
        # self.ani_speed_label.setText("")
        # self.ani_speed_label.setAlignment(Qt.AlignCenter)
        # self.ani_speed_label.setStyleSheet(u"QLabel {\n"
        #                                    "        color: rgb(48, 48, 48);\n"
        #                                    "}\n"
        #                                    "")
        self.playstop_button = QPushButton(self.menubar)
        self.playstop_button.setObjectName(u"PlayStop_button")
        font = QFont()
        font.setPointSize(20)
        self.control_buttons_width = self.menubar.height() * 1.25
        self.playstop_button.setFont(font)
        self.playstop_button.setText("\u25BA")
        self.playstop_button.setGeometry(QRect(0, 0, self.control_buttons_width, self.menubar_height))
        self.forwards_button = QPushButton(self.menubar)
        self.forwards_button.setObjectName(u"play_button")
        font = QFont()
        font.setPointSize(14)
        self.forwards_button.setFont(font)
        self.forwards_button.setText(">>")
        self.forwards_button.setGeometry(QRect(0, 0, self.control_buttons_width, self.menubar_height))
        self.backwards_button = QPushButton(self.menubar)
        self.backwards_button.setObjectName(u"play_button")
        self.backwards_button.setFont(font)
        self.backwards_button.setText("<<")
        self.backwards_button.setGeometry(QRect(0, 0, self.control_buttons_width, self.menubar_height))
        self.playstop_button.setStyleSheet(u"QPushButton {\n"
                                           "        background-color: transparent;\n"
                                           "        border: none;\n"
                                           "        padding: none; \n"
                                           "		 color: rgb(48, 48, 48);\n"
                                           "    }\n"
                                           "    QPushButton:pressed {\n"
                                           "        color: rgb(114, 114, 114); /* Change text color when pressed */\n"
                                           "    }\n"
                                           "")
        self.forwards_button.setStyleSheet(self.playstop_button.styleSheet())
        self.backwards_button.setStyleSheet(self.playstop_button.styleSheet())

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuFile.addAction(self.action1)
        self.menuFile.addAction(self.action2)
        self.menuFile.addAction(self.action3)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
        # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.action2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.action3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.preview_button.setText(QCoreApplication.translate("MainWindow", u"\U0001F733", None))
        self.left_splitter_button.setText("")
        self.right_splitter_button.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))

    def adjustFrameSize(self, event):
        self.frame.setGeometry(QRect(0, 0, self.left_widget.width(), self.left_widget.height()))
        self.preview_button.setGeometry(QRect(self.left_widget.width() - self.preview_button.width() - 13
                                              , self.left_widget.height() - self.preview_button.height() - 5
                                              , self.preview_button.width(), self.preview_button.height()))

    def adjustWindowSize(self, event):
        # Place playback controls using size hints to avoid collapsing to zero width
        btn_w = max(int(self.menubar_height * 1.25), self.playstop_button.sizeHint().width() + 8)
        speed_w = max(int(self.menubar_height * 1.8), self.ani_speed_label.sizeHint().width() + 10)
        self.control_buttons_width = btn_w

        x = self.menubar.width()
        h = self.menubar_height

        x -= speed_w
        self.ani_speed_label.setGeometry(QRect(x, 0, speed_w, h))

        x -= btn_w
        self.forwards_button.setGeometry(QRect(x, 0, btn_w, h))

        x -= btn_w
        self.playstop_button.setGeometry(QRect(x, 0, btn_w, h))

        x -= btn_w
        self.backwards_button.setGeometry(QRect(x, 0, btn_w, h))

        rb = self.render_button.geometry()
        self.simOptionsButton.setGeometry(
            QRect(
                rb.x() + rb.width(),
                0,
                10,
                h
            )
        )
