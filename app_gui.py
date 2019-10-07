#https://www.learnpyqt.com/apps/simple-sales-tax-calculator/

import sys, requests, json, time
from PyQt5 import uic, QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import VTiger_API

class MyEmitter(QObject):
    '''
    Creates the custom signal for the Worker class.
    '''
    done = pyqtSignal(list)

class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    This Worker class is used by self.threading_function to initiate self.gather_vtiger_data
    and then returns the data gathered as a list. 
    That list of data is then sent to self.manual_refresh_data to populate the GUI.
    '''
    done = pyqtSignal(list)
    def __init__(self, fn,):
        super(Worker, self).__init__()
        self.fn = fn
        self.emitter = MyEmitter()

    @pyqtSlot(list)
    def run(self):
        '''
        Initialise the runner function with passed function.
        '''
        mylist = self.fn()
        self.emitter.done.emit(mylist)


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

        self.manual_refresh_pushButton.clicked.connect(self.threading_function)
        self.auto_refresh_checkBox.clicked.connect(self.auto_refresh)
        self.quit_pushButton.clicked.connect(self.close_the_program)
        self.plus_push_button.clicked.connect(self.increase_size)
        self.minus_push_button.clicked.connect(self.decrease_size)

        self.week_table.setRowCount(1)
        self.week_table.setCurrentCell(0,0)
        self.week_row = self.week_table.currentRow()

        self.today_table.setRowCount(1)
        self.today_table.setCurrentCell(0,0)
        self.today_row = self.today_table.currentRow()   

        self.threadpool = QThreadPool()

        #Print Silent Errors
        sys._excepthook = sys.excepthook 
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback) 
            sys.exit(1) 
        sys.excepthook = exception_hook


    def threading_function(self):
        '''
        Uses the Worker class to push gathering the VTiger data into another thread.
        The data returned from that function is sent to manual_refresh_data where
        it auto populates the GUI.
        '''
        worker = Worker(self.gather_vtiger_data)
        worker.emitter.done.connect(self.manual_refresh_data)
        self.threadpool.start(worker)


    def gather_vtiger_data(self):
        '''
        Gathers data from the VTiger API Class. 
        Returns it all as a list which gets sent to self.manual_refresh_data.
        '''
        case_count = self.vtigerapi.case_count()
        week_open_cases, week_closed_cases, week_kill_ratio = self.vtigerapi.get_weeks_case_data()
        today_open_cases, today_closed_cases, today_kill_ratio = self.vtigerapi.get_today_case_data()
        week_user_list = self.vtigerapi.week_user_stats()
        today_user_list = self.vtigerapi.today_user_stats()

        return [case_count, week_open_cases, week_closed_cases, week_kill_ratio, today_open_cases, today_closed_cases, today_kill_ratio, week_user_list, today_user_list]


    def manual_refresh_data(self, data_list):
        '''
        This function uses all the data supplied from gather_vtiger_data and fills out
        the respective fields. This is all done in a separate thread so as to not freeze the GUI.
        '''
        case_count = data_list[0]
        week_open_cases = data_list[1]
        week_closed_cases = data_list[2]
        week_kill_ratio = data_list[3]
        today_open_cases = data_list[4]
        today_closed_cases = data_list[5]
        today_kill_ratio = data_list[6]
        week_user_list = data_list[7]
        today_user_list = data_list[8]

        self.total_open_cases_plainTextEdit.setPlainText(case_count)
        
        self.week_open_cases_plainTextEdit.setPlainText(str(week_open_cases))
        self.week_closed_cases_plainTextEdit.setPlainText(str(week_closed_cases))
        self.week_kill_ratio_plainTextEdit.setPlainText(str(week_kill_ratio))

        self.today_open_cases_plainTextEdit.setPlainText(str(today_open_cases))
        self.today_closed_cases_plainTextEdit.setPlainText(str(today_closed_cases))
        self.today_kill_ratio_plainTextEdit.setPlainText(str(today_kill_ratio))

        #Fill out the Week's User Table
        #Clear the table contents first
        self.week_table.clearContents()
        self.week_table.setRowCount(1)
        self.week_table.setCurrentCell(0,0)
        self.week_row = 0
        

        for item in range(len(week_user_list)):
            if week_user_list[item][1] > 0:
                self.week_table.setItem(self.week_row, 0, QtWidgets.QTableWidgetItem((f"{self.vtigerapi.full_user_dict[week_user_list[item][0]][0]} {self.vtigerapi.full_user_dict[week_user_list[item][0]][1]}")))
                self.week_table.setItem(self.week_row, 1, QtWidgets.QTableWidgetItem((f"{week_user_list[item][1]}")))
                        
                row_amount = self.week_table.rowCount()
                if self.week_row + 1 == row_amount:
                    self.week_table.setRowCount(row_amount + 1) 
                    self.week_row += 1
        self.week_table.setRowCount(self.week_table.rowCount() - 1)
        
        #Fill out the Daily User Table
        #Clear the table contents first
        self.today_table.clearContents()
        self.today_table.setRowCount(1)
        self.today_table.setCurrentCell(0,0)
        self.today_row = 0


        for item in range(len(today_user_list)):
            if today_user_list[item][1] > 0:
                self.today_table.setItem(self.today_row, 0, QtWidgets.QTableWidgetItem((f"{self.vtigerapi.full_user_dict[today_user_list[item][0]][0]} {self.vtigerapi.full_user_dict[today_user_list[item][0]][1]}")))
                self.today_table.setItem(self.today_row, 1, QtWidgets.QTableWidgetItem((f"{today_user_list[item][1]}")))
                
                row_amount = self.today_table.rowCount()
                if self.today_row + 1 == row_amount:
                    self.today_table.setRowCount(row_amount + 1) 
                    self.today_row += 1
        self.today_table.setRowCount(self.today_table.rowCount() - 1)


    def auto_refresh(self):
        '''
        #This function causes the manual_refresh_data() function to happen at regular intervals.
        '''
        if self.refresh_time_lineEdit.text() == '':
            msg = QtWidgets.QMessageBox()
            msg.setText("Auto refresh time is empty.\nSelect a refresh time in minutes.")
            msg.setWindowTitle("Warning!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.auto_refresh_checkBox.setChecked(False)
        elif not self.refresh_time_lineEdit.text().isdigit():
            msg = QtWidgets.QMessageBox()
            msg.setText("Auto refresh time must be a whole number.\nSelect a refresh time in minutes.")
            msg.setWindowTitle("Warning!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.auto_refresh_checkBox.setChecked(False)
        elif int(self.refresh_time_lineEdit.text()) < 1: 
            msg = QtWidgets.QMessageBox()
            msg.setText("Auto refresh time may not be less than 1.\nSelect a refresh time in minutes.")
            msg.setWindowTitle("Warning!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.auto_refresh_checkBox.setChecked(False)
        
        else:
            self.threading_function()
            self.interval = int(self.refresh_time_lineEdit.text()) * 60 * 1000
            self.auto_refresh_progressBar.setMaximum(self.interval)


            self.progressbar_timer = QTimer()
            self.progressbar_timer.setInterval(1000)
            self.progressbar_timer.timeout.connect(self.progress_bar)
            self.progressbar_timer.start()

            self.timer = QTimer()
            self.timer.setInterval(self.interval)
            self.timer.timeout.connect(self.threading_function)
            self.timer.start()
        if self.auto_refresh_checkBox.isChecked() == False:
            try:
                self.timer.stop()
                self.progressbar_timer.stop()
            except AttributeError:
                pass
            self.auto_refresh_progressBar.setValue(0)

    def progress_bar(self):
        time_left = self.interval - self.timer.remainingTime()
        self.auto_refresh_progressBar.setValue(time_left)
       
    def increase_size(self):
        '''
        Increase the font sizes of the plain text edit widgets.
        '''
        self.total_open_cases_plainTextEdit.zoomIn(2)
        self.week_open_cases_plainTextEdit.zoomIn(2)
        self.week_closed_cases_plainTextEdit.zoomIn(2)
        self.week_kill_ratio_plainTextEdit.zoomIn(2)
        self.today_open_cases_plainTextEdit.zoomIn(2)
        self.today_closed_cases_plainTextEdit.zoomIn(2)
        self.today_kill_ratio_plainTextEdit.zoomIn(2)

    def decrease_size(self):
        '''
        Decrease the font sizes of the plain text edit widgets.
        '''
        self.total_open_cases_plainTextEdit.zoomOut(2)
        self.week_open_cases_plainTextEdit.zoomOut(2)
        self.week_closed_cases_plainTextEdit.zoomOut(2)
        self.week_kill_ratio_plainTextEdit.zoomOut(2)
        self.today_open_cases_plainTextEdit.zoomOut(2)
        self.today_closed_cases_plainTextEdit.zoomOut(2)
        self.today_kill_ratio_plainTextEdit.zoomOut(2)

    def close_the_program(self):
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = vtiger_api_gui()
    window.show()
    sys.exit(app.exec_())