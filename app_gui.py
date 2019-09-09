#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTableWidget.html#
#https://www.pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/

import sys, requests, json, time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import VTiger_API

#This .ui file is created by QTDesigner and then imported here.
#Add new widgets via QTDesigner, save the ui file and then reference them here.
qtCreatorFile = "app_gui.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class vtiger_api_gui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.username ='(USERNAME)'
        self.access_key = '(ACCESS KEY)'
        self.host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'

        self.vtigerapi = VTiger_API.Vtiger_api(self.username, self.access_key, self.host)

        self.week_table.setRowCount(1)
        self.week_table.setCurrentCell(0,0)
        self.week_row = self.week_table.currentRow()

        self.today_table.setRowCount(1)
        self.today_table.setCurrentCell(0,0)
        self.today_row = self.today_table.currentRow()
        

        #Print Silent Errors
        sys._excepthook = sys.excepthook 
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback) 
            sys.exit(1) 
        sys.excepthook = exception_hook

        self.manual_refresh_pushButton.clicked.connect(self.manual_refresh_data)

    def manual_refresh_data(self):
        #Total Amount of Open Cases
        case_count = self.vtigerapi.case_count()
        self.total_open_cases_plainTextEdit.setPlainText(case_count)
        
        #Weeks open, closed and kill ratio
        week_open_cases, week_closed_cases, week_kill_ratio = self.vtigerapi.get_weeks_case_data()
        self.week_open_cases_plainTextEdit.setPlainText(str(week_open_cases))
        self.week_closed_cases_plainTextEdit.setPlainText(str(week_closed_cases))
        self.week_kill_ratio_plainTextEdit.setPlainText(str(week_kill_ratio))

        #Todays open, closed and kill ratio
        today_open_cases, today_closed_cases, today_kill_ratio = self.vtigerapi.get_today_case_data()
        self.today_open_cases_plainTextEdit.setPlainText(str(today_open_cases))
        self.today_closed_cases_plainTextEdit.setPlainText(str(today_closed_cases))
        self.today_kill_ratio_plainTextEdit.setPlainText(str(today_kill_ratio))

        #Fill out the Week's User Table
        user_list = self.vtigerapi.week_user_stats()
        for item in range(len(user_list)):
            if user_list[item][1] > 0:
                self.week_table.setItem(self.week_row, 0, QtWidgets.QTableWidgetItem((f"{self.vtigerapi.full_user_dict[user_list[item][0]][0]} {self.vtigerapi.full_user_dict[user_list[item][0]][1]}")))
                self.week_table.setItem(self.week_row, 1, QtWidgets.QTableWidgetItem((f"{user_list[item][1]}")))

                row_amount = self.week_table.rowCount()
                if self.week_row + 1 == row_amount:
                    self.week_table.setRowCount(row_amount + 1) 
                    self.week_row += 1
        self.week_table.setRowCount(row_amount)
        
        #Fill out the Daily User Table
        user_list = self.vtigerapi.today_user_stats()
        for item in range(len(user_list)):
            if user_list[item][1] > 0:
                self.today_table.setItem(self.today_row, 0, QtWidgets.QTableWidgetItem((f"{self.vtigerapi.full_user_dict[user_list[item][0]][0]} {self.vtigerapi.full_user_dict[user_list[item][0]][1]}")))
                self.today_table.setItem(self.today_row, 1, QtWidgets.QTableWidgetItem((f"{user_list[item][1]}")))

                row_amount = self.today_table.rowCount()
                if self.today_row + 1 == row_amount:
                    self.today_table.setRowCount(row_amount + 1) 
                    self.today_row += 1
        self.today_table.setRowCount(row_amount)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = vtiger_api_gui()
    window.show()
    sys.exit(app.exec_())

