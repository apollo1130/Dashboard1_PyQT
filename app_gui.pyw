#https://www.learnpyqt.com/apps/simple-sales-tax-calculator/

import sys, requests, json, time, datetime, os
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

        #Set the day, week and month labels with the current information.
        self.set_week_date()

        #Connect widgets to their respective functions.
        self.manual_refresh_pushButton.clicked.connect(self.threading_function)
        self.auto_refresh_checkBox.clicked.connect(self.auto_refresh)
        self.quit_pushButton.clicked.connect(self.close_the_program)
        self.plus_push_button.clicked.connect(self.increase_size)
        self.minus_push_button.clicked.connect(self.decrease_size)
        self.group_listWidget.itemClicked.connect(self.set_primary_group)
        self.import_credentials_pushbutton.clicked.connect(self.import_credentials)
        self.username_lineEdit.textChanged.connect(self.enable_export)
        self.accesskey_lineEdit.textChanged.connect(self.enable_export)
        self.host_lineEdit.textChanged.connect(self.enable_export)
        self.export_credentials_pushbutton.clicked.connect(self.export_credentials)
        self.test_connection_pushButton.clicked.connect(self.test_connection)
        self.today_checkBox.stateChanged.connect(self.display_stats)
        self.week_checkBox.stateChanged.connect(self.display_stats)
        self.month_checkBox.stateChanged.connect(self.display_stats)


        #Initialize the tables so they start from the correct locations.
        self.week_table.setRowCount(1)
        self.week_table.setCurrentCell(0,0)
        self.week_row = self.week_table.currentRow()

        self.today_table.setRowCount(1)
        self.today_table.setCurrentCell(0,0)
        self.today_row = self.today_table.currentRow()   

        self.month_table.setRowCount(1)
        self.month_table.setCurrentCell(0,0)
        self.month_row = self.month_table.currentRow()

        #Set the font size of all the tables
        self.table_font_size = 12   

        self.threadpool = QThreadPool()


        #Print Silent Errors
        sys._excepthook = sys.excepthook 
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback) 
            sys.exit(1) 
        sys.excepthook = exception_hook

    def set_week_date(self):
        '''
        For whichever day of the week it is, this past Monday at 12:00am is returned.
        Today = datetime.datetime(2019, 9, 5, 15, 31, 13, 134153)
        Returns: 2019-09-02 00:00:00
        '''
        end_of_week = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        day = end_of_week.weekday()
        beginning_of_week = end_of_week + datetime.timedelta(days = -day) 
        week_begin = beginning_of_week.strftime("%m/%d")
        week_end = end_of_week.strftime("%m/%d")
        self.week_label.setText(f"WEEK:\n{week_begin} - {week_end}")
        self.month_label.setText(f"Month:\n{datetime.datetime.now().strftime('%B')}")
        self.today_label.setText(f"Today:\n{datetime.datetime.now().strftime('%A')}")
        

    def import_credentials(self):
        '''
        Credentials are stored in a separate file with this format:
        {"username":"(USERNAME)",
        "access_key":"(ACCESS KEY)",
        "host":"https://(MYURL).vtiger.com/restapi/v1/vtiger/default"}
        '''
        with open('credentials.json') as f:
            data = f.read()
        credential_dict = json.loads(data)

        self.username_lineEdit.setText(credential_dict['username'])
        self.accesskey_lineEdit.setText(credential_dict['access_key'])
        self.host_lineEdit.setText(credential_dict['host'])
        self.username =credential_dict['username']
        self.access_key = credential_dict['access_key']
        self.host = credential_dict['host']


    def enable_export(self):
        '''
        Enables the export credentials button as long as all the fields aren't empty.
        '''
        if self.username_lineEdit.text() != '' and self.accesskey_lineEdit.text() != '' and self.host_lineEdit.text() != '':
            self.export_credentials_pushbutton.setEnabled(True)
        self.username = self.username_lineEdit.text()
        self.password = self.accesskey_lineEdit.text()
        self.host = self.host_lineEdit.text()

    def export_credentials(self):
        '''
        Exports current credentials to file
        '''
        username = self.username_lineEdit.text()
        password = self.accesskey_lineEdit.text()
        host = self.host_lineEdit.text()
        cred_dictionary = {'username': username, 'access_key':password, 'host':host}
        with open('credentials.json', 'w') as f:
            json.dump(cred_dictionary, f)


    def test_connection(self):
        '''
        Tests the credentials' ability to connect to VTiger
        '''
        try:
            self.vtigerapi = VTiger_API.Vtiger_api(self.username, self.access_key, self.host)
            msg = QtWidgets.QMessageBox()
            msg.setText(f"Hi {self.vtigerapi.first_name} {self.vtigerapi.last_name},\nConnection Successful!\nClick on a GROUP to get started.")
            msg.setWindowTitle("Success!")
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.exec_()
            self.choose_group()
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Connection was not successful.\nCheck your credentials and your internet connection and try again!")
            msg.setWindowTitle("Connection Failure!")
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.exec_()


    def choose_group(self):
        '''
        Populates the group list widget with all VTiger groups
        Disables Manual Refresh and Auto Refresh Buttons and
        removes the group name from the main Cases Label until an item
        is selected.
        '''
        group_list = []
        self.groups = self.vtigerapi.get_groups()
        for groupname in self.groups:
            group_list.append(groupname)
        self.group_listWidget.addItems(group_list)
        self.support_group_cases_label.setText(f'Cases')
        self.manual_refresh_pushButton.setEnabled(False)
        self.auto_refresh_checkBox.setEnabled(False)
        

    def set_primary_group(self):
        '''
        Sets the currently selected group from the listWidget as primary group
        Once an item is selected, Manual Refresh and Auto Refresh buttons become
        available and the main Cases Label is updated.
        '''
        self.primary_group = self.group_listWidget.currentItem().text()
        self.support_group_cases_label.setText(f'{self.primary_group} Cases')
        self.primary_group_id = self.groups[self.primary_group]
        self.manual_refresh_pushButton.setEnabled(True)
        self.auto_refresh_checkBox.setEnabled(True)
        
        #When a new group is selected, it auto-updates the data fields.
        self.threading_function()


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
        case_count = self.vtigerapi.case_count(self.primary_group_id)
        month_open_cases, month_closed_cases, month_kill_rate = self.vtigerapi.get_month_case_data(self.primary_group_id)
        week_open_cases, week_closed_cases, week_kill_rate = self.vtigerapi.get_weeks_case_data(self.primary_group_id)
        today_open_cases, today_closed_cases, today_kill_rate = self.vtigerapi.get_today_case_data(self.primary_group_id)
        month_user_list = self.vtigerapi.month_user_stats()
        week_user_list = self.vtigerapi.week_user_stats()
        today_user_list = self.vtigerapi.today_user_stats()

        vtiger_data_list = [
            case_count,
            week_open_cases, 
            week_closed_cases, 
            week_kill_rate, 
            today_open_cases, 
            today_closed_cases, 
            today_kill_rate, 
            week_user_list, 
            today_user_list, 
            month_open_cases, 
            month_closed_cases,
            month_kill_rate,
            month_user_list, ]

        return vtiger_data_list


    def manual_refresh_data(self, data_list):
        '''
        This function uses all the data supplied from gather_vtiger_data and fills out
        the respective fields. This is all done in a separate thread so as to not freeze the GUI.
        '''

        #set_week_date() is put here so that the Day, Week and Month labels auto
        #update every time the data is refreshed. Otherwise, if the software is running
        #for multiple days it would only change once when it was initially opened.
        self.set_week_date()

        case_count = data_list[0]
        week_open_cases = data_list[1]
        week_closed_cases = data_list[2]
        week_kill_rate = data_list[3]
        today_open_cases = data_list[4]
        today_closed_cases = data_list[5]
        today_kill_rate = data_list[6]
        week_user_list = data_list[7]
        today_user_list = data_list[8]
        month_open_cases = data_list[9] 
        month_closed_cases = data_list[10]
        month_kill_rate = data_list[11]
        month_user_list = data_list[12]         

        self.total_open_cases_plainTextEdit.setPlainText(case_count)
        
        self.week_open_cases_plainTextEdit.setPlainText(str(week_open_cases))
        self.week_closed_cases_plainTextEdit.setPlainText(str(week_closed_cases))
        self.week_kill_rate_plainTextEdit.setPlainText(str(week_kill_rate))

        self.today_open_cases_plainTextEdit.setPlainText(str(today_open_cases))
        self.today_closed_cases_plainTextEdit.setPlainText(str(today_closed_cases))
        self.today_kill_rate_plainTextEdit.setPlainText(str(today_kill_rate))

        self.month_open_cases_plainTextEdit.setPlainText(str(month_open_cases))
        self.month_closed_cases_plainTextEdit.setPlainText(str(month_closed_cases))
        self.month_kill_rate_plainTextEdit.setPlainText(str(month_kill_rate))

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
        
        #Fill out the Today User Table
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

        #Fill out the Month User Table
        #Clear the table contents first
        self.month_table.clearContents()
        self.month_table.setRowCount(1)
        self.month_table.setCurrentCell(0,0)
        self.month_row = 0


        for item in range(len(month_user_list)):
            if month_user_list[item][1] > 0:
                self.month_table.setItem(self.month_row, 0, QtWidgets.QTableWidgetItem((f"{self.vtigerapi.full_user_dict[month_user_list[item][0]][0]} {self.vtigerapi.full_user_dict[month_user_list[item][0]][1]}")))
                self.month_table.setItem(self.month_row, 1, QtWidgets.QTableWidgetItem((f"{month_user_list[item][1]}")))
                
                row_amount = self.month_table.rowCount()
                if self.month_row + 1 == row_amount:
                    self.month_table.setRowCount(row_amount + 1) 
                    self.month_row += 1
        self.month_table.setRowCount(self.month_table.rowCount() - 1)

        if self.auto_hide_show_checkBox.isChecked():
            #Hide week stats if today and week stats are the same. 
            #This occurs every Monday
            #Comparing Kill Rate would be redundant.
            if (    self.today_open_cases_plainTextEdit.toPlainText() == self.week_open_cases_plainTextEdit.toPlainText()
                and self.today_closed_cases_plainTextEdit.toPlainText() == self.week_closed_cases_plainTextEdit.toPlainText()
            ):
                self.week_checkBox.setChecked(False)
            else:
                self.week_checkBox.setChecked(True)

            #Hide month stats if week and month stats are the same.
            #This only occurs if the month begins at the same time as the week.
            if (    self.week_open_cases_plainTextEdit.toPlainText() == self.month_open_cases_plainTextEdit.toPlainText()
                and self.week_closed_cases_plainTextEdit.toPlainText() == self.month_closed_cases_plainTextEdit.toPlainText()
            ):
                self.month_checkBox.setChecked(False)     
            else:
                self.month_checkBox.setChecked(True)

            #Hide month stats if day and month stats are the same.
            #This only occurs on the day when a new month begins.
            if (    self.today_open_cases_plainTextEdit.toPlainText() == self.month_open_cases_plainTextEdit.toPlainText()
                and self.today_closed_cases_plainTextEdit.toPlainText() == self.month_closed_cases_plainTextEdit.toPlainText()
            ):
                self.month_checkBox.setChecked(False)     
            else:
                self.month_checkBox.setChecked(True)

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
        elif int(self.refresh_time_lineEdit.text()) <= 1: 
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
        '''
        Update the progress bar
        '''
        #VTiger only allows 60 api calls per minutes.
        #If there are no more allowed API requests, the program crashes. 
        #As a solution, the program is paused for however long remaining
        #until the 60 api call per minute is reset.
        time.sleep(self.vtigerapi.seconds_to_wait)

        time_left = self.interval - self.timer.remainingTime()
        self.auto_refresh_progressBar.setValue(time_left)
       
    def increase_size(self):
        '''
        Increase the font sizes of the plain text edit widgets.
        '''
        self.total_open_cases_plainTextEdit.zoomIn(2)
        self.week_open_cases_plainTextEdit.zoomIn(2)
        self.week_closed_cases_plainTextEdit.zoomIn(2)
        self.week_kill_rate_plainTextEdit.zoomIn(2)
        self.today_open_cases_plainTextEdit.zoomIn(2)
        self.today_closed_cases_plainTextEdit.zoomIn(2)
        self.today_kill_rate_plainTextEdit.zoomIn(2)
        self.month_open_cases_plainTextEdit.zoomIn(2)
        self.month_closed_cases_plainTextEdit.zoomIn(2)
        self.month_kill_rate_plainTextEdit.zoomIn(2)
        self.table_font_size += 1
        self.today_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")
        self.week_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")
        self.month_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")

    def decrease_size(self):
        '''
        Decrease the font sizes of the plain text edit widgets.
        '''
        self.total_open_cases_plainTextEdit.zoomOut(2)
        self.week_open_cases_plainTextEdit.zoomOut(2)
        self.week_closed_cases_plainTextEdit.zoomOut(2)
        self.week_kill_rate_plainTextEdit.zoomOut(2)
        self.today_open_cases_plainTextEdit.zoomOut(2)
        self.today_closed_cases_plainTextEdit.zoomOut(2)
        self.today_kill_rate_plainTextEdit.zoomOut(2)
        self.month_open_cases_plainTextEdit.zoomOut(2)
        self.month_closed_cases_plainTextEdit.zoomOut(2)
        self.month_kill_rate_plainTextEdit.zoomOut(2)
        self.table_font_size -= 1
        self.today_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")
        self.week_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")
        self.month_table.setStyleSheet(f"font: {self.table_font_size}pt Segoe UI")


        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function.
        python = sys.executable
        os.execl(python, python, * sys.argv)"""

    def display_stats(self):
        '''
        Shows/hides display stats based on the checkbox selection
        '''
        if self.today_checkBox.isChecked():
            self.today_open_cases_plainTextEdit.show()
            self.today_closed_cases_plainTextEdit.show()
            self.today_kill_rate_plainTextEdit.show()
            self.today_table.show()
            self.today_label.show()
            self.today_open_cases_label.show()
            self.today_closed_cases_label.show()
            self.daily_kill_rate_label.show()
            self.line_2.show()
        else:
            self.today_open_cases_plainTextEdit.hide()
            self.today_closed_cases_plainTextEdit.hide()
            self.today_kill_rate_plainTextEdit.hide()
            self.today_table.hide()
            self.today_label.hide()
            self.today_open_cases_label.hide()
            self.today_closed_cases_label.hide()
            self.daily_kill_rate_label.hide()
            self.line_2.hide()

        if self.week_checkBox.isChecked():
            self.week_open_cases_plainTextEdit.show()
            self.week_closed_cases_plainTextEdit.show()
            self.week_kill_rate_plainTextEdit.show()
            self.week_table.show()
            self.week_label.show()
            self.week_open_cases_label.show()
            self.week_closed_cases_label.show()
            self.week_kill_rate_label.show()
            self.line.show()
        else:
            self.week_open_cases_plainTextEdit.hide()
            self.week_closed_cases_plainTextEdit.hide()
            self.week_kill_rate_plainTextEdit.hide()
            self.week_table.hide()
            self.week_label.hide()
            self.week_open_cases_label.hide()
            self.week_closed_cases_label.hide()
            self.week_kill_rate_label.hide()
            self.line.hide()

        if self.month_checkBox.isChecked():
            self.month_open_cases_plainTextEdit.show()
            self.month_closed_cases_plainTextEdit.show()
            self.month_kill_rate_plainTextEdit.show()
            self.month_table.show()
            self.month_label.show()
            self.month_open_cases_label.show()
            self.month_closed_cases_label.show()
            self.month_kill_rate_label.show()
            self.line_3.show()
        else:
            self.month_open_cases_plainTextEdit.hide()
            self.month_closed_cases_plainTextEdit.hide()
            self.month_kill_rate_plainTextEdit.hide()
            self.month_table.hide()
            self.month_label.hide()
            self.month_open_cases_label.hide()
            self.month_closed_cases_label.hide()
            self.month_kill_rate_label.hide()
            self.line_3.hide()

    def close_the_program(self):
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = vtiger_api_gui()
    window.show()
    sys.exit(app.exec_())