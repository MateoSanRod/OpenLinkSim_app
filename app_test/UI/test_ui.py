# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QPalette)
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout,
                               QLayout, QMenu, QMenuBar,
                               QPlainTextEdit, QPushButton, QSplitter,
                               QStatusBar, QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(921, 636)
        self.mainwindow = MainWindow
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
                                 "\n"
                                 "QMenuBar::item {\n"
                                 "    background-color: transparent;\n"
                                 "}\n"
                                 "\n"
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

        self.preveiew_button = QPushButton(self.left_widget)
        self.preveiew_button.setObjectName(u"preveiew_button")
        self.preveiew_button.setGeometry(QRect(290, 520, 40, 40))
        font = QFont()
        font.setPointSize(24)
        self.preveiew_button.setFont(font)
        self.preveiew_button.setStyleSheet(u"QPushButton {\n"
                                           "        background-color: transparent;\n"
                                           "        border: none;\n"
                                           "        padding: 4px; \n"
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
        self.splitter.addWidget(self.right_widget)

        self.horizontalLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 921, 22))
        palette1 = QPalette()
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush)
        brush2 = QBrush(QColor(255, 255, 255, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Active, QPalette.Midlight, brush2)
        brush3 = QBrush(QColor(127, 127, 127, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Dark, brush3)
        brush4 = QBrush(QColor(170, 170, 170, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Mid, brush4)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush1)
        palette1.setBrush(QPalette.Active, QPalette.BrightText, brush2)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush)
        palette1.setBrush(QPalette.Active, QPalette.Shadow, brush1)
        palette1.setBrush(QPalette.Active, QPalette.AlternateBase, brush2)
        brush5 = QBrush(QColor(255, 255, 220, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipBase, brush5)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipText, brush1)
        brush6 = QBrush(QColor(0, 0, 0, 127))
        brush6.setStyle(Qt.SolidPattern)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush6)
        # endif
        palette1.setBrush(QPalette.Active, QPalette.Accent, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.Midlight, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.Dark, brush3)
        palette1.setBrush(QPalette.Inactive, QPalette.Mid, brush4)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.BrightText, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Shadow, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush5)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush1)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush6)
        # endif
        palette1.setBrush(QPalette.Inactive, QPalette.Accent, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.Midlight, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.Dark, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Mid, brush4)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.BrightText, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Shadow, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush5)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush1)
        brush7 = QBrush(QColor(127, 127, 127, 127))
        brush7.setStyle(Qt.SolidPattern)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush7)
        # endif
        palette1.setBrush(QPalette.Disabled, QPalette.Accent, brush2)
        self.menubar.setPalette(palette1)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        palette2 = QPalette()
        brush8 = QBrush(QColor(135, 135, 135, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette2.setBrush(QPalette.Active, QPalette.WindowText, brush8)
        palette2.setBrush(QPalette.Active, QPalette.Button, brush)
        palette2.setBrush(QPalette.Active, QPalette.Text, brush2)
        palette2.setBrush(QPalette.Active, QPalette.ButtonText, brush2)
        palette2.setBrush(QPalette.Active, QPalette.Base, brush)
        palette2.setBrush(QPalette.Active, QPalette.Window, brush)
        palette2.setBrush(QPalette.Active, QPalette.ToolTipText, brush8)
        palette2.setBrush(QPalette.Inactive, QPalette.WindowText, brush8)
        palette2.setBrush(QPalette.Inactive, QPalette.Button, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.Text, brush2)
        palette2.setBrush(QPalette.Inactive, QPalette.ButtonText, brush2)
        palette2.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.HighlightedText, brush2)
        palette2.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush8)
        palette2.setBrush(QPalette.Disabled, QPalette.Button, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush8)
        self.statusbar.setPalette(palette2)
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
        self.preveiew_button.setText(QCoreApplication.translate("MainWindow", u"\U0001F733", None))
        self.left_splitter_button.setText("")
        self.right_splitter_button.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))

    # retranslateUi
    def adjustFrameSize(self, event):
        self.frame.setGeometry(QRect(0, 0, self.left_widget.width(), self.left_widget.height()))
        self.preveiew_button.setGeometry(QRect(self.left_widget.width() - self.preveiew_button.width() - 13
                                               , self.left_widget.height() - self.preveiew_button.height() - 5
                                               , self.preveiew_button.width(), self.preveiew_button.height()))
