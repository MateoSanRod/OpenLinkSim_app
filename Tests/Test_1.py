from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

        self.vbox = QVBoxLayout()
        self.setupUi()

    def setupUi(self):
        self.hbox = QHBoxLayout()

        self.lineEdit = self.lab()
        self.hbox.addWidget(self.lineEdit)

        self.hbox.addStretch()

        self.pushButton = self.butt()
        self.hbox.addWidget(self.pushButton)

        self.vbox.addLayout(self.hbox)


        self.pushButton.clicked.connect(self.klik)

    def klik(self):
        s = self.lineEdit.text()
        if (len(s.strip()) != 0):
            self.pushButton.setEnabled(False)
            self.setupUi()
        pass

    def f(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        return font

    def i(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../Users/Downloads/Hopstarter-Button-Button-Add.ico"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        return icon

    def butt(self):
        pushButton = QtWidgets.QPushButton()
        ff = self.f()
        pushButton.setFont(ff)
        pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        pushButton.setText("")

        ii = self.i()
        pushButton.setIcon(ii)
        pushButton.setIconSize(QtCore.QSize(21, 21))
        pushButton.setAutoDefault(True)
        pushButton.setDefault(True)
        pushButton.setFlat(True)
        pushButton.setObjectName("pushButton")
        return pushButton

    def lab(self):
        lineEdit = QtWidgets.QLineEdit()
        ff = self.f()
        lineEdit.setFont(ff)

        lineEdit.setObjectName("lineEdit")
        return lineEdit


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
