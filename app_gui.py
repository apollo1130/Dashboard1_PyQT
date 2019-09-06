#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTableWidget.html#
#https://www.pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/

import sys, requests, json, time
from PyQt5 import QtCore, QtGui, QtWidgets, uic

#This .ui file is created by QTDesigner and then imported here.
#Add new widgets via QTDesigner, save the ui file and then simply reference them here.
qtCreatorFile = "app_gui.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class vtiger_api_gui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        #Print Silent Errors
        sys._excepthook = sys.excepthook 
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback) 
            sys.exit(1) 
        sys.excepthook = exception_hook

        self.open_cases_plainTextEdit.setPlainText('135')
        self.refresh_pushButton.clicked.connect(self.refresh_data)

    def refresh_data(self):
        num = int(self.open_cases_plainTextEdit.toPlainText())
        num += 1
        self.open_cases_plainTextEdit.setPlainText(str(num))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = vtiger_api_gui()
    window.show()
    sys.exit(app.exec_())

