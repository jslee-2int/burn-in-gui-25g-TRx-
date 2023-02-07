import math
import sys, os
from ui_main import Ui_MainWindow
import sys, rss.rss
import threading
import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui
import configparser
from serial_comm import Serial_comm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from matplotlib.ticker import FuncFormatter
from matplotlib import cm


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    send_instance_singal = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Effect shadow
        frames = [self.frame, self.frame_2, self.frame_3, self.frame_4, self.frame_5, self.frame_7, self.frame_24,
                  self.frame_setting, self.frame_18, self.frame_17, self.frame_20, self.frame_temp, self.frame_21,
                  self.frame_mpd, self.frame_22, self.frame_rssi, self.frame_19]

        for frame in frames:
            frame.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=50.0, xOffset=0.0, yOffset=0.0,
                                                                        color=QtGui.QColor(0, 0, 0, 20)))

        self.model = QtGui.QStandardItemModel()

        self.init_state_btn()

        # Configuration
        self.onlyInt = QtGui.QIntValidator()
        self.lineEdit_st.setValidator(self.onlyInt)
        self.lineEdit_st_7.setValidator(self.onlyInt)

        self.config = configparser.ConfigParser()
        self.config.read('setting.ini', "utf8")
        self.lineEdit_st.setText(self.config['Setting']['durating_time'])
        self.lineEdit_st_2.setText(self.config['Setting']['file_name'])
        self.lineEdit_st_3.setText(self.config['Setting']['operator'])
        self.lineEdit_st_4.setText(self.config['Setting']['template_file_open'])
        self.lineEdit_st_5.setText(self.config['Setting']['save_folder_path'])
        self.lineEdit_st_7.setText(self.config['Setting']['time_interval'])

        self.serial_connect_list = self.config['instrument']['arduino_port_list'].split(',')

        self.pushButton_st.clicked.connect(self.file_dialog_tfo)
        self.pushButton_st_2.clicked.connect(self.file_dialog_sf)
        self.pushButton_st_3.clicked.connect(self.save_setting)
        self.pushButton_st_4.clicked.connect(self.restore_setting)

        # Multi Threading define
        self.pushButton_start.clicked.connect(lambda: self.time_start(self.serial_connect_list[0], 38400))
        self.pushButton_start_2.clicked.connect(lambda: self.time_start_2(self.serial_connect_list[1], 38400))
        self.pushButton_start_3.clicked.connect(lambda: self.time_start_3(self.serial_connect_list[2], 38400))
        self.pushButton_stop.clicked.connect(
            lambda: self.time_stop(self.port_ch, self.th, self.pushButton_start, self.pushButton_stop,
                                   [self.label_c1_1, self.label_c1_2, self.label_c1_3]))
        self.pushButton_stop_2.clicked.connect(
            lambda: self.time_stop(self.port_ch2, self.th_2, self.pushButton_start_2, self.pushButton_stop_2,
                                   [self.label_c2, self.label_c2_2, self.label_c2_3]))
        self.pushButton_stop_3.clicked.connect(
            lambda: self.time_stop(self.port_ch3, self.th_3, self.pushButton_start_3, self.pushButton_stop_3,
                                   [self.label_c3, self.label_c3_2, self.label_c3_3]))

        # Menu Btn.
        self.btn_home.clicked.connect(lambda: self.btn_menu(0))
        self.btn_monitor.clicked.connect(lambda: self.btn_menu(1))
        self.btn_curr.clicked.connect(lambda: self.btn_menu(2))
        self.btn_temp.clicked.connect(lambda: self.btn_menu(3))
        self.btn_mpd.clicked.connect(lambda: self.btn_menu(4))
        self.btn_rssi.clicked.connect(lambda: self.btn_menu(5))
        self.btn_vapd.clicked.connect(lambda: self.btn_menu(6))
        self.btn_setting.clicked.connect(lambda: self.btn_menu(7))
        self.pushButton_set.clicked.connect(lambda: self.btn_menu(7))

        # Ch. Btn connect
        self.btn_curr_1.clicked.connect(lambda: self.btn_plot_test('curr_ch1'))
        self.btn_curr_2.clicked.connect(lambda: self.btn_plot_test('curr_ch2'))
        self.btn_curr_3.clicked.connect(lambda: self.btn_plot_test('curr_ch3'))
        self.btn_temp_1.clicked.connect(lambda: self.btn_plot_test('temp_ch1'))
        self.btn_temp_2.clicked.connect(lambda: self.btn_plot_test('temp_ch2'))
        self.btn_temp_3.clicked.connect(lambda: self.btn_plot_test('temp_ch3'))
        self.btn_mpd_1.clicked.connect(lambda: self.btn_plot_test('mpd_ch1'))
        self.btn_mpd_2.clicked.connect(lambda: self.btn_plot_test('mpd_ch2'))
        self.btn_mpd_3.clicked.connect(lambda: self.btn_plot_test('mpd_ch3'))
        self.btn_rssi_1.clicked.connect(lambda: self.btn_plot_test('rssi_ch1'))
        self.btn_rssi_2.clicked.connect(lambda: self.btn_plot_test('rssi_ch2'))
        self.btn_rssi_3.clicked.connect(lambda: self.btn_plot_test('rssi_ch3'))
        self.btn_vapd_1.clicked.connect(lambda: self.btn_plot_test('vapd_ch1'))
        self.btn_vapd_2.clicked.connect(lambda: self.btn_plot_test('vapd_ch2'))
        self.btn_vapd_3.clicked.connect(lambda: self.btn_plot_test('vapd_ch3'))

        self.btn_mon1_0.clicked.connect(lambda: self.mon_action(0))
        self.btn_mon1_1.clicked.connect(lambda: self.mon_action(1))
        self.btn_mon1_2.clicked.connect(lambda: self.mon_action(2))
        self.btn_mon2_0.clicked.connect(lambda: self.mon_action_2(0))
        self.btn_mon2_1.clicked.connect(lambda: self.mon_action_2(1))
        self.btn_mon2_2.clicked.connect(lambda: self.mon_action_2(2))

        self.btn_table_11.clicked.connect(lambda: self.btn_table(0, 0))
        self.btn_table_12.clicked.connect(lambda: self.btn_table(0, 1))
        self.btn_table_13.clicked.connect(lambda: self.btn_table(0, 2))
        self.btn_table_14.clicked.connect(lambda: self.btn_table(0, 3))
        self.btn_table_15.clicked.connect(lambda: self.btn_table(0, 4))
        self.btn_table_16.clicked.connect(lambda: self.btn_table(0, 5))
        self.btn_table_17.clicked.connect(lambda: self.btn_table(0, 6))
        self.btn_table_18.clicked.connect(lambda: self.btn_table(0, 7))
        self.btn_table_21.clicked.connect(lambda: self.btn_table(1, 0))
        self.btn_table_22.clicked.connect(lambda: self.btn_table(1, 1))
        self.btn_table_23.clicked.connect(lambda: self.btn_table(1, 2))
        self.btn_table_24.clicked.connect(lambda: self.btn_table(1, 3))
        self.btn_table_25.clicked.connect(lambda: self.btn_table(1, 4))
        self.btn_table_26.clicked.connect(lambda: self.btn_table(1, 5))
        self.btn_table_27.clicked.connect(lambda: self.btn_table(1, 6))
        self.btn_table_28.clicked.connect(lambda: self.btn_table(1, 7))
        self.btn_table_31.clicked.connect(lambda: self.btn_table(2, 0))
        self.btn_table_32.clicked.connect(lambda: self.btn_table(2, 1))
        self.btn_table_33.clicked.connect(lambda: self.btn_table(2, 2))
        self.btn_table_34.clicked.connect(lambda: self.btn_table(2, 3))
        self.btn_table_35.clicked.connect(lambda: self.btn_table(2, 4))
        self.btn_table_36.clicked.connect(lambda: self.btn_table(2, 5))
        self.btn_table_37.clicked.connect(lambda: self.btn_table(2, 6))
        self.btn_table_38.clicked.connect(lambda: self.btn_table(2, 7))

        # Configuration plot :: init. values
        self.curr_plot = 'ch1'
        self.temp_plot = 'ch1'
        self.mpd_plot = 'ch1'
        self.rssi_plot = 'ch1'
        self.vapd_plot = 'ch1'

        self.pmu_2 = 0
        self.pmu = 0

        self.table_m = 0
        self.table_k = 0

        # Data list & dict & frame
        # Ch1 col : [ Data , Current, Temperature, MPD, RSSI, TEC_Temp.]

        self.df_ch1, self.df_ch2, self.df_ch3, self.df_ch4, self.df_ch5, self.df_ch6, self.df_ch7, self.df_ch8, \
            = [], [], [], [], [], [], [], []

        self.df_bundle = [self.df_ch1, self.df_ch2, self.df_ch3]

        for i in range(3):
            for j in range(8):
                self.df_bundle[i].append(pd.DataFrame({'Duration_Time': [], 'Current': [], 'Temperature': [], 'MPD': [],
                                                       'RSSI': [], 'TEC_Temp.': []}))

    def btn_more_info(self, layer_no):
        msg = QtWidgets.QMessageBox()
        msg.setText("More Information : {} \nCould not open port : ".format(layer_no))
        msg.setWindowTitle("More Information")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setStyleSheet("")
        msg.exec()

    def btn_table(self, layer_no, ch_no):
        self.table_m = layer_no
        self.table_k = ch_no
        self.table_update()

    def hex_to_dec(self, hex_df):
        msg_dex = []
        for i in range(8):
            list_b = []
            for j in range(5):
                if j == 0: # Current value is dec
                    list_b.append(round(float(hex_df[i][j]),3))
                else:
                    list_b.append(int(hex_df[i][j], 16))
            msg_dex.append(list_b)
        return msg_dex

    def clear_plot(self, index=0):
        for i in range(5):
            self.widget_mon.axes[i].cla()
            self.widget_mon_2.axes[i].cla()
        self.widget_curr.axes.cla()
        self.widget_temp.axes.cla()
        self.widget_mpd.axes.cla()
        self.widget_rssi.axes.cla()
        self.widget_vapd.axes.cla()
        self.df_bundle[index] = []
        for j in range(8):
            self.df_bundle[index].append(pd.DataFrame({'Duration_Time': [], 'Current': [], 'Temperature': [], 'MPD': [],
                                                   'RSSI': [], 'TEC_Temp.': []}))

    def _update_buttons(self, bol_1, bol_2, index=0):
        btns = [[self.pushButton_start, self.pushButton_stop],
                [self.pushButton_start_2, self.pushButton_stop_2],
                [self.pushButton_start_3, self.pushButton_stop_3]]
        btns[index][0].setEnabled(bol_1)
        btns[index][1].setEnabled(bol_2)

    def _update_labels(self, start_time, end_time, index=0):
        labels = [[self.label_c1_2, self.label_c1_3],
                  [self.label_c2_2, self.label_c2_3],
                  [self.label_c3_2, self.label_c3_3]]
        labels[index][0].setText(start_time)
        labels[index][0].setStyleSheet("color:rgba(255, 70, 70, 210);")
        labels[index][1].setText(end_time)
        labels[index][1].setStyleSheet("color:rgba(255, 70, 70, 210);")

    # Multi Threading
    @QtCore.pyqtSlot()
    def time_start(self, port, baud):
        self.clear_plot(0)
        try:
            self.port_ch = Serial_comm(port=port, baud=baud)

            self.th = Worker(self.port_ch, parent=self)
            self.th.sec_changed.connect(self.time_update)

            self._update_buttons(False, True, index=0)
            # Cal. Time & delta
            self.start_time = datetime.now()
            self.end_time = self.start_time + relativedelta(hours=int(self.config['Setting']['durating_time']))
            self.start_time_str = self.start_time.isoformat(timespec='seconds').replace("T", ' ')
            self.end_time_str = self.end_time.isoformat(timespec='seconds').replace("T", ' ')
            self._update_labels(self.start_time_str, self.end_time_str, index=0)
            self.th.start()
            self.th.working = True
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Serial Connect Error\nCould not open port : {}".format(port))
            msg.setWindowTitle("Serial Connect Error")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setStyleSheet("")
            msg.exec()
            pass

    @QtCore.pyqtSlot()
    def time_start_2(self, port, baud):
        self.clear_plot(1)
        try:
            self.port_ch2 = Serial_comm(port=port, baud=baud)

            self.th_2 = Worker(self.port_ch2, parent=self)
            self.th_2.sec_changed.connect(self.time_update_2)

            self._update_buttons(False, True, index=1)
            # Cal. Time & delta
            self.start_time_2 = datetime.now()
            self.end_time_2 = self.start_time_2 + relativedelta(hours=int(self.config['Setting']['durating_time']))
            self.start_time_2_str = self.start_time_2.isoformat(timespec='seconds')
            self.end_time_2_str = self.end_time_2.isoformat(timespec='seconds')
            self.start_time_2_str, self.end_time_2_str = self.start_time_2_str.replace("T",
                                                                                       ' '), self.end_time_2_str.replace(
                "T", ' ')
            self._update_labels(self.start_time_2_str, self.end_time_2_str, index=1)
            self.th_2.start()
            self.th_2.working = True
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Serial Connect Error\nCould not open port : {}".format(port))
            msg.setWindowTitle("Serial Connect Error")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setStyleSheet("")
            msg.exec()
            pass

    @QtCore.pyqtSlot()
    def time_start_3(self, port, baud):
        self.clear_plot(2)
        try:
            self.port_ch3 = Serial_comm(port=port, baud=baud)
            self.th_3 = Worker(self.port_ch3, parent=self)
            self.th_3.sec_changed.connect(self.time_update_3)

            self._update_buttons(False, True, index=2)
            # Cal. Time & delta
            self.start_time_3 = datetime.now()
            self.end_time_3 = self.start_time_3 + relativedelta(hours=int(self.config['Setting']['durating_time']))
            self.start_time_3_str = self.start_time_3.isoformat(timespec='seconds').replace("T", ' ')
            self.end_time_3_str = self.end_time_3.isoformat(timespec='seconds').replace("T", ' ')
            self._update_labels(self.start_time_3_str, self.end_time_3_str, index=2)
            self.th_3.start()
            self.th_3.working = True

        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Serial Connect Error\nCould not open port : {}".format(port))
            msg.setWindowTitle("Serial Connect Error")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setStyleSheet("")
            msg.exec()
            pass

    @QtCore.pyqtSlot(list)
    def time_update(self, msg):
        now_time = datetime.now()
        delta_day = relativedelta(self.end_time, now_time)
        duration_time = relativedelta(now_time, self.start_time)
        remaining_seconds = (self.end_time - datetime.now()).total_seconds()
        total_time = int(self.config['Setting']['durating_time']) * 60 * 60
        prog_val = int((1 - float(remaining_seconds)/total_time)*100)
        self.progressBar.setValue(prog_val)
        duration_time_sec = duration_time.days * 60 * 60 * 24 \
                            + duration_time.hours * 60 * 60 \
                            + duration_time.minutes * 60 \
                            + duration_time.seconds + 1
        # Data read & draw plot
        time_interval = int(self.config['Setting']['time_interval'])
        if (int(delta_day.minutes) % time_interval == 0) and (int(delta_day.seconds) == 0):
            list_msg = self.hex_to_dec(msg)
            for i in range(8):
                df = self.df_update(duration_time_sec, index_no=i, list_msg=list_msg)
                self.df_bundle[0][i] = pd.concat([self.df_bundle[0][i],df])
                self.df_bundle[0][i] = self.df_bundle[0][i].reset_index(drop=True)
            t = threading.Thread(target=self.plot_update, args=())
            t.daemon = True
            t.start()
            self.table_update()
            if self.pmu == 0:
                self.pmu_mon()
            if self.pmu_2 == 0:
                self.pmu_3d_mon2()
            path = self.config['Setting']['save_folder_path']
            file_name = self.config['Setting']['file_name']
            mkdir_path = '{}/{}'.format(path, self.start_time_str.split(' ')[0])
            os.makedirs(mkdir_path, exist_ok=True)
            mkdir_path = f"{mkdir_path}/Ch1"
            os.makedirs(mkdir_path, exist_ok=True)
            for i in range(8):
                self.df_bundle[0][i].to_csv(
                    f"{mkdir_path}/{file_name}_no{i + 1}_{self.start_time_str.replace(' ', '').replace(':', '').replace('-', '')[8:]}.csv",
                    index=False)

        if int(delta_day.seconds) < 0:
            self.time_stop(self.port_ch, self.th, self.pushButton_start, self.pushButton_stop,
                                       [self.label_c1_1, self.label_c1_2, self.label_c1_3])
        else:
            delta_day_str = "{}d {}h {}m {}s".format(delta_day.days, delta_day.hours, delta_day.minutes,
                                                     delta_day.seconds)
            self.label_c1_1.setText(delta_day_str)
            self.label_c1_1.setStyleSheet("color:rgba(255, 70, 70, 210);")



    @QtCore.pyqtSlot(list)
    def time_update_2(self, msg):
        now_time = datetime.now()
        delta_day = relativedelta(self.end_time_2, now_time)
        duration_time = relativedelta(now_time, self.start_time_2)
        remaining_seconds = (self.end_time_2 - datetime.now()).total_seconds()
        total_time = int(self.config['Setting']['durating_time']) * 60 * 60
        prog_val = int((1 - float(remaining_seconds) / total_time) * 100)
        self.progressBar_2.setValue(prog_val)
        duration_time_sec = duration_time.days * 60 * 60 * 24 \
                            + duration_time.hours * 60 * 60 \
                            + duration_time.minutes * 60 \
                            + duration_time.seconds + 1
        # Data read & draw plot
        time_interval = int(self.config['Setting']['time_interval'])
        if (int(delta_day.minutes) % time_interval == 0) and (int(delta_day.seconds) == 0):
            list_msg = self.hex_to_dec(msg)
            print(self.hex_to_dec(msg))
            for i in range(8):
                df = self.df_update(duration_time_sec, index_no=i, list_msg=list_msg)
                self.df_bundle[1][i] = pd.concat([self.df_bundle[1][i],df])
                self.df_bundle[1][i] = self.df_bundle[1][i].reset_index(drop=True)
            t = threading.Thread(target=self.plot_update, args=())
            t.daemon = True
            t.start()
            self.table_update()
            if self.pmu == 1:
                self.pmu_mon()
            if self.pmu_2 == 1:
                self.pmu_3d_mon2()
            path = self.config['Setting']['save_folder_path']
            file_name = self.config['Setting']['file_name']
            mkdir_path = '{}/{}'.format(path, self.start_time_str.split(' ')[0])
            os.makedirs(mkdir_path, exist_ok=True)
            mkdir_path = f"{mkdir_path}/Ch2"
            os.makedirs(mkdir_path, exist_ok=True)
            for i in range(8):
                self.df_bundle[1][i].to_csv(
                    '{}/{}_no{}_{}.csv'.format(mkdir_path, file_name, (i + 1),
                                               self.start_time_str.replace(' ', '').replace(':', '').replace('-', '')[
                                               8:]),
                    index=False)
        if int(delta_day.seconds) < 0:
            self.time_stop(self.port_ch2, self.th_2, self.pushButton_start_2, self.pushButton_stop_2,
                                   [self.label_c2, self.label_c2_2, self.label_c2_3])
        else:
            delta_day_str = "{}d {}h {}m {}s".format(delta_day.days, delta_day.hours, delta_day.minutes,
                                                     delta_day.seconds)
            self.label_c2.setText(delta_day_str)
            self.label_c2.setStyleSheet("color:rgba(255, 70, 70, 210);")

    @QtCore.pyqtSlot(list)
    def time_update_3(self, msg):
        now_time = datetime.now()
        delta_day = relativedelta(self.end_time_3, now_time)
        duration_time = relativedelta(now_time, self.start_time_3)
        remaining_seconds = (self.end_time_3 - datetime.now()).total_seconds()
        total_time = int(self.config['Setting']['durating_time']) * 60 * 60
        prog_val = int((1 - float(remaining_seconds) / total_time) * 100)
        self.progressBar_3.setValue(prog_val)
        duration_time_sec = duration_time.days * 60 * 60 * 24 \
                            + duration_time.hours * 60 * 60 \
                            + duration_time.minutes * 60 \
                            + duration_time.seconds + 1
        # Data read & draw plot
        time_interval = int(self.config['Setting']['time_interval'])
        if (int(delta_day.minutes) % time_interval == 0) and (int(delta_day.seconds) == 0):
            list_msg = self.hex_to_dec(msg)
            print(self.hex_to_dec(msg))
            for i in range(8):
                df = self.df_update(duration_time_sec, index_no=i, list_msg=list_msg)
                self.df_bundle[2][i] = pd.concat([self.df_bundle[2][i],df])
                self.df_bundle[2][i] = self.df_bundle[2][i].reset_index(drop=True)
            t = threading.Thread(target=self.plot_update, args=())
            t.daemon = True
            t.start()
            self.table_update()
            if self.pmu == 2:
                self.pmu_mon()
            if self.pmu_2 == 2:
                self.pmu_3d_mon2()
            path = self.config['Setting']['save_folder_path']
            file_name = self.config['Setting']['file_name']
            mkdir_path = '{}/{}'.format(path, self.start_time_str.split(' ')[0])
            os.makedirs(mkdir_path, exist_ok=True)
            mkdir_path = f"{mkdir_path}/Ch3"
            os.makedirs(mkdir_path, exist_ok=True)
            for i in range(8):
                self.df_bundle[2][i].to_csv(
                    '{}/{}_no{}_{}.csv'.format(mkdir_path, file_name, (i + 1),
                                               self.start_time_str.replace(' ', '').replace(':', '').replace('-', '')[
                                               8:]),
                    index=False)
        if int(delta_day.seconds) < 0:
            self.time_stop(self.port_ch3, self.th_3, self.pushButton_start_3, self.pushButton_stop_3,
                                   [self.label_c3, self.label_c3_2, self.label_c3_3])
        else:
            delta_day_str = "{}d {}h {}m {}s".format(delta_day.days, delta_day.hours, delta_day.minutes,
                                                     delta_day.seconds)
            self.label_c3.setText(delta_day_str)
            self.label_c3.setStyleSheet("color:rgba(255, 70, 70, 210);")

    @QtCore.pyqtSlot()
    def time_stop(self, port, th, start_button, stop_button, labels):
        port.serial_close()
        th.working = False

        start_button.setEnabled(True)
        stop_button.setEnabled(False)
        for label in labels:
            label.setStyleSheet("")

    def table_update(self):
        self.label_mon_state.setText("Layer : {} / Ch. No. :{}".format(self.table_m + 1, self.table_k + 1))
        # create a standard model
        self.model = QtGui.QStandardItemModel()
        self.table_view.setModel(self.model)
        # Set headers
        self.model.setHorizontalHeaderLabels(self.df_bundle[self.table_m][self.table_k].columns)
        for i in range(self.model.columnCount()):
            self.table_view.setColumnWidth(i, 120)
        # populate the model
        for i, item in enumerate(self.df_bundle[self.table_m][self.table_k].values):
            for j, value in enumerate(item):
                standard_item = QtGui.QStandardItem(str(value))
                standard_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.model.setItem(i, j, standard_item)
                # self.model.setItem(i, j, QtGui.QStandardItem(str(value)))

    def mon_action(self, layer_no):
        self.pmu = layer_no
        self.pmu_mon()

    def mon_action_2(self, layer_no):
        self.pmu_2 = layer_no
        self.pmu_3d_mon2()

    def plot_update(self):
        date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        index_no = int(self.mpd_plot.replace('ch', '')) - 1
        for i in range(8):
            date_list.append(np.array(self.df_bundle[index_no][i]['Duration_Time']).tolist())
            mpd_list.append(np.array(self.df_bundle[index_no][i]['Current']).tolist())
        self.plot_curr(title='Current Chart :: Layer {}'.format(index_no+1), x_data=date_list, y_data=mpd_list)
        date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        index_no = int(self.curr_plot.replace('ch', '')) - 1
        for i in range(8):
            date_list.append(np.array(self.df_bundle[index_no][i]['Duration_Time']).tolist())
            ther_list.append(np.array(self.df_bundle[index_no][i]['Temperature']).tolist())
        self.plot_temp(title='Temperature Chart :: Layer {}'.format(index_no+1), x_data=date_list, y_data=ther_list)
        date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        index_no = int(self.temp_plot.replace('ch', '')) - 1
        for i in range(8):
            date_list.append(np.array(self.df_bundle[index_no][i]['Duration_Time']).tolist())
            ther_list.append(np.array(self.df_bundle[index_no][i]['MPD']).tolist())
        self.plot_mpd(title='MPD Chart :: Layer {}'.format(index_no+1), x_data=date_list, y_data=ther_list)
        date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        index_no = int(self.mpd_plot.replace('ch', '')) - 1
        for i in range(8):
            date_list.append(np.array(self.df_bundle[index_no][i]['Duration_Time']).tolist())
            ther_list.append(np.array(self.df_bundle[index_no][i]['RSSI']).tolist())
        self.plot_rssi(title='RSSI Chart :: Layer {}'.format(index_no+1), x_data=date_list, y_data=ther_list)
        date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        index_no = int(self.rssi_plot.replace('ch', '')) - 1
        for i in range(8):
            date_list.append(np.array(self.df_bundle[index_no][i]['Duration_Time']).tolist())
            ther_list.append(np.array(self.df_bundle[index_no][i]['TEC_Temp.']).tolist())
        self.plot_vapd(title='TEC_Temp. Chart :: Layer {}'.format(index_no+1), x_data=date_list, y_data=ther_list)
        # date_list, mpd_list, ther_list, tec_volt_list, tec_curr_list, ld_volt_list, ld_curr_list = [], [], [], [], [], [], []
        # index_no = int(self.vapd_plot.replace('ch', '')) - 1

    def read_tec(self, value):
        data = value
        s_val = int(data)
        calc_val = s_val * 2400 / 65536
        r_val = int(round(calc_val, 0))
        r_val = hex(r_val)
        try:
            f_v_thm = int(r_val, 16) / 1000
            f_r_thm = 1/ ((2.4 / f_v_thm) - 1)
            f_t_k = (298 * 3930) / ((298 * math.log(f_r_thm)) + 3930)
            f_t_c = f_t_k - 273
            f_t_c = round(f_t_c, 2)
        except ZeroDivisionError:
            f_t_c = 0
        except ValueError:
            f_t_c = 0

        return f_t_c

    def df_update(self, duration_time_sec, index_no, list_msg):
        date_val = round((duration_time_sec / 3600), 2)
        curr_val = list_msg[index_no][0]
        temp_val = self.read_tec(list_msg[index_no][1])
        mpd_val = list_msg[index_no][2]
        rssi_val = list_msg[index_no][3]
        vapd_val = self.read_tec(list_msg[index_no][4]) #TEC Temp.

        df = pd.DataFrame(
            {'Duration_Time': [date_val], 'Current': [curr_val], 'Temperature': [temp_val], 'MPD': [mpd_val],
             'RSSI': [rssi_val], 'TEC_Temp.': [vapd_val]})
        return df

    def file_dialog_tfo(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', './', 'Excel File (*.xlsx)')
        if not fname:
            self.lineEdit_st_4.setText(self.config['Setting']['template_file_open'])
        else:
            self.lineEdit_st_4.setText(fname)

    def file_dialog_sf(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open File', './')
        if not fname:
            self.lineEdit_st_5.setText(self.config['Setting']['save_folder_path'])
        else:
            self.lineEdit_st_5.setText(fname)

    def save_setting(self):
        self.config['Setting']['durating_time'] = self.lineEdit_st.text()
        self.config['Setting']['file_name'] = self.lineEdit_st_2.text()
        self.config['Setting']['operator'] = self.lineEdit_st_3.text()
        self.config['Setting']['template_file_open'] = self.lineEdit_st_4.text()
        self.config['Setting']['save_folder_path'] = self.lineEdit_st_5.text()
        self.config['Setting']['time_interval'] = self.lineEdit_st_7.text()

        with open('setting.ini', 'w', encoding='UTF-8') as configfile:
            self.config.write(configfile)

    def restore_setting(self):
        self.config.read('setting.ini', "utf8")
        self.lineEdit_st.setText(self.config['Setting']['durating_time'])
        self.lineEdit_st_2.setText(self.config['Setting']['file_name'])
        self.lineEdit_st_3.setText(self.config['Setting']['operator'])
        self.lineEdit_st_4.setText(self.config['Setting']['template_file_open'])
        self.lineEdit_st_5.setText(self.config['Setting']['save_folder_path'])

    # plot draw
    def plot(self, title, x_data, y_data, widget, y_label, linestyle_start):
        widget.axes.cla()
        widget.axes.set_title(title)
        widget.axes.set_xlabel(r"Duration Time (hr)")
        widget.axes.set_ylabel(y_label)
        widget.axes.tick_params(axis="y", direction="in", pad=10)
        widget.axes.tick_params(axis="x", direction="in", pad=10)
        if x_data:
            linestyles = ['-', '--', '-.', ':']
            for i in range(8):
                widget.axes.plot(x_data[i], y_data[i], ms=100, lw=1, linestyle=linestyles[int(i / 4) + linestyle_start],
                                 label='No. {}'.format((i + 1)))
            widget.axes.legend(loc='upper center', bbox_to_anchor=(1.1, 1), ncol=1)
        else:
            pass
        widget.draw()

    def plot_curr(self, title, x_data, y_data):
        self.plot(title, x_data, y_data, self.widget_curr, r"Current (mA)", 0)

    def plot_temp(self, title, x_data, y_data):
        self.plot(title, x_data, y_data, self.widget_temp, r"Temperature (deg.)", 0)

    def plot_mpd(self, title, x_data, y_data):
        self.plot(title, x_data, y_data, self.widget_mpd, r"Mpd (Voltage)", 0)

    def plot_rssi(self, title, x_data, y_data):
        self.plot(title, x_data, y_data, self.widget_rssi, r"RSSI (a.u.)", 0)

    def plot_vapd(self, title, x_data, y_data):
        self.plot(title, x_data, y_data, self.widget_vapd, r"TEC_Temp. (a.u.)", 0)

    def format_y_tick(self, value, tick_number):
        return '{:.0f}k'.format(value / 1000)

    def pmu_mon(self):
        for i in range(5):
            self.widget_mon.axes[i].cla()
        res_0, res_1, res_2, res_3, res_4 = [], [], [], [], []
        try:
            for i in range(8):
                res_0.append(self.df_bundle[self.pmu][i].iloc[-1]['Current'])
                res_1.append(self.df_bundle[self.pmu][i].iloc[-1]['Temperature'])
                res_2.append(self.df_bundle[self.pmu][i].iloc[-1]['MPD'])
                res_3.append(self.df_bundle[self.pmu][i].iloc[-1]['RSSI'])
                res_4.append(self.df_bundle[self.pmu][i].iloc[-1]['TEC_Temp.'])
            x_label = np.array(['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8'])
            res_0 = np.array([round(float(i), 3) for i in res_0])
            res_1 = np.array([round(float(i), 3) for i in res_1])
            res_2 = np.array([round(float(i), 3) for i in res_2])
            res_3 = np.array([round(float(i), 3) for i in res_3])
            res_4 = np.array([round(float(i), 3) for i in res_4])

            for i in range(5):
                self.widget_mon.axes[i].tick_params(axis="y", direction="in", pad=3)
                self.widget_mon.axes[i].tick_params(axis="x", direction="in", pad=3)

            formatter = FuncFormatter(self.format_y_tick)

            self.widget_mon.axes[2].yaxis.set_major_formatter(formatter)
            self.widget_mon.axes[3].yaxis.set_major_formatter(formatter)

            self.widget_mon.axes[0].grid(visible=False, which='both')
            self.widget_mon.axes[1].grid(visible=False, which='both')
            self.widget_mon.axes[2].grid(visible=False, which='both')
            self.widget_mon.axes[3].grid(visible=False, which='both')
            self.widget_mon.axes[4].grid(visible=False, which='both')

            self.widget_mon.axes[0].bar(x_label, res_0, color='#FF003C', alpha=0.3)
            self.widget_mon.axes[1].bar(x_label, res_1, color='#FF8A00', alpha=0.3)
            self.widget_mon.axes[2].bar(x_label, res_2, color='#FABE28', alpha=0.3)
            self.widget_mon.axes[3].bar(x_label, res_3, color='#88C100', alpha=0.3)
            self.widget_mon.axes[4].bar(x_label, res_4, color='#00C176', alpha=0.3)

            self.widget_mon.axes[0].set_ylabel("Curr.")
            self.widget_mon.axes[1].set_ylabel("Temp.")
            self.widget_mon.axes[2].set_ylabel("MPD")
            self.widget_mon.axes[3].set_ylabel("RSSI")
            self.widget_mon.axes[4].set_ylabel("TEC")

            # self.widget_mon.axes.set_title("Monitor Current Values - Layer #1")
            self.widget_mon.draw()
        except Exception as e:
            for i in range(5):
                self.widget_mon.axes[i].tick_params(axis="y", direction="in", pad=3)
                self.widget_mon.axes[i].tick_params(axis="x", direction="in", pad=3)
            self.widget_mon.axes[0].grid(visible=False, which='both')
            self.widget_mon.axes[1].grid(visible=False, which='both')
            self.widget_mon.axes[2].grid(visible=False, which='both')
            self.widget_mon.axes[3].grid(visible=False, which='both')
            self.widget_mon.axes[4].grid(visible=False, which='both')
            self.widget_mon.axes[0].set_ylabel("Curr.")
            self.widget_mon.axes[1].set_ylabel("Temp.")
            self.widget_mon.axes[2].set_ylabel("MPD")
            self.widget_mon.axes[3].set_ylabel("RSSI")
            self.widget_mon.axes[4].set_ylabel("TEC")
            print('There are no datas.', e)
            pass
        res_0, res_1, res_2, res_3, res_4 = [], [], [], [], []

    def pmu_3d_mon2(self):
        # for i in range(5):
        #     self.widget_mon_2.axes[i].cla()
        res_0, res_1, res_2, res_3, res_4 = [], [], [], [], []
        try:
            for i in range(8):
                res_0.append(
                    self.df_bundle[self.pmu][i].iloc[-1]['Current'])
                res_1.append(self.df_bundle[self.pmu][i].iloc[-1]['Temperature'])
                res_2.append(self.df_bundle[self.pmu][i].iloc[-1]['MPD'])
                res_3.append(self.df_bundle[self.pmu][i].iloc[-1]['RSSI'])
                res_4.append(self.df_bundle[self.pmu][i].iloc[-1]['TEC_Temp.'])
            x_label = ['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7', 'No8']
            res_0 = np.array([round(float(i), 3) for i in res_0])
            res_1 = np.array([round(float(i), 3) for i in res_1])
            res_2 = np.array([round(float(i), 3) for i in res_2])
            res_3 = np.array([round(float(i), 3) for i in res_3])
            res_4 = np.array([round(float(i), 3) for i in res_4])

            for i in range(5):
                self.widget_mon_2.axes[i].tick_params(axis="y", direction="in", pad=3)
                self.widget_mon_2.axes[i].tick_params(axis="x", direction="in", pad=3)

            self.widget_mon_2.axes[0].scatter(x_label, res_0, color='#FF003C', alpha=0.2)
            self.widget_mon_2.axes[1].scatter(x_label, res_1, color='#FF8A00', alpha=0.2)
            self.widget_mon_2.axes[2].scatter(x_label, res_2, color='#FABE28', alpha=0.2)
            self.widget_mon_2.axes[3].scatter(x_label, res_3, color='#88C100', alpha=0.2)
            self.widget_mon_2.axes[4].scatter(x_label, res_4, color='#00C176', alpha=0.2)

            self.widget_mon_2.axes[0].set_ylabel("Curr.")
            self.widget_mon_2.axes[1].set_ylabel("Temp.")
            self.widget_mon_2.axes[2].set_ylabel("MPD")
            self.widget_mon_2.axes[3].set_ylabel("RSSI")
            self.widget_mon_2.axes[4].set_ylabel("TEC")

            self.widget_mon_2.draw()
        except Exception as e:
            for i in range(5):
                self.widget_mon_2.axes[i].tick_params(axis="y", direction="in", pad=3)
                self.widget_mon_2.axes[i].tick_params(axis="x", direction="in", pad=3)
            self.widget_mon_2.axes[0].grid(visible=False, which='both')
            self.widget_mon_2.axes[1].grid(visible=False, which='both')
            self.widget_mon_2.axes[2].grid(visible=False, which='both')
            self.widget_mon_2.axes[3].grid(visible=False, which='both')
            self.widget_mon_2.axes[4].grid(visible=False, which='both')
            self.widget_mon_2.axes[0].set_ylabel("Curr.")
            self.widget_mon_2.axes[1].set_ylabel("Temp.")
            self.widget_mon_2.axes[2].set_ylabel("MPD")
            self.widget_mon_2.axes[3].set_ylabel("RSSI")
            self.widget_mon_2.axes[4].set_ylabel("TEC")
            print('There are no datas.', e)
            pass
        res_0, res_1, res_2, res_3, res_4 = [], [], [], [], []

    def btn_plot_test(self, name):
        if 'curr_' in name:
            self.curr_plot = name.replace('curr_', '')
            index_no = int(name.replace('curr_ch', '')) - 1
            date_list, x_data = [], []
            for j in range(8):
                date_list.append(np.array(self.df_bundle[index_no][j]['Duration_Time']).tolist())
                x_data.append(np.array(self.df_bundle[index_no][j]['Current']).tolist())
            self.plot_curr(title='Current Chart :: Layer {}'.format(index_no + 1), x_data=date_list, y_data=x_data)
        if 'temp_' in name:
            self.temp_plot = name.replace('temp_', '')
            index_no = int(name.replace('temp_ch', '')) - 1
            date_list, x_data = [], []
            for j in range(8):
                date_list.append(np.array(self.df_bundle[index_no][j]['Duration_Time']).tolist())
                x_data.append(np.array(self.df_bundle[index_no][j]['Temperature']).tolist())
            self.plot_temp(title='Temperature Chart :: Layer {}'.format(index_no + 1), x_data=date_list, y_data=x_data)
        if 'mpd_' in name:
            self.mpd_plot = name.replace('mpd_', '')
            index_no = int(name.replace('mpd_ch', '')) - 1
            date_list, x_data = [], []
            for j in range(8):
                date_list.append(np.array(self.df_bundle[index_no][j]['Duration_Time']).tolist())
                x_data.append(np.array(self.df_bundle[index_no][j]['MPD']).tolist())
            self.plot_mpd(title='MPD Chart :: Layer {}'.format(index_no + 1), x_data=date_list, y_data=x_data)
        if 'rssi_' in name:
            self.rssi_plot = name.replace('rssi_', '')
            index_no = int(name.replace('rssi_ch', '')) - 1
            date_list, x_data = [], []
            for j in range(8):
                date_list.append(np.array(self.df_bundle[index_no][j]['Duration_Time']).tolist())
                x_data.append(np.array(self.df_bundle[index_no][j]['RSSI']).tolist())
            self.plot_rssi(title='RSSI Chart :: Layer {}'.format(index_no + 1), x_data=date_list, y_data=x_data)
        if 'vapd_' in name:
            self.vapd_plot = name.replace('vapd_', '')
            index_no = int(name.replace('vapd_ch', '')) - 1
            date_list, x_data = [], []
            for j in range(8):
                date_list.append(np.array(self.df_bundle[index_no][j]['Duration_Time']).tolist())
                x_data.append(np.array(self.df_bundle[index_no][j]['TEC_Temp.']).tolist())
            self.plot_vapd(title='TEC_Temp. Chart :: Layer {}'.format(index_no + 1), x_data=date_list, y_data=x_data)

    # Page move func.
    def btn_menu(self, index):
        menu_text = ['Main', 'Main >> Monitor', 'Main >> Current', 'Main >> Temperature', 'Main >> MPD', 'Main >> RSSI',
                     'Main >> TEC_Temp.', 'Main >> Setting']
        self.label_nav.setText(menu_text[index])
        self.btn_select_style(index)
        self.stackedWidget.setCurrentIndex(index)

    def btn_select_style(self, index_no):
        buttons = [self.btn_home, self.btn_monitor, self.btn_curr, self.btn_temp, self.btn_mpd, self.btn_rssi,
                   self.btn_vapd, self.btn_setting]
        for btn in buttons:
            btn.setStyleSheet("")
            btn.setGraphicsEffect(None)

        selected_style = "border-radius: 5px; font-weight: 600;padding: 7px;background-color: #FFF;color:rgba(0, 0, 255, 210);"
        selected_effect = QtWidgets.QGraphicsDropShadowEffect(blurRadius=50.0, xOffset=0.0, yOffset=0.0,
                                                              color=QtGui.QColor(0, 0, 0, 20))

        if 0 <= index_no < len(buttons):
            buttons[index_no].setStyleSheet(selected_style)
            buttons[index_no].setGraphicsEffect(selected_effect)

    def init_state_btn(self):
        self.pushButton_stop.setEnabled(False)
        self.pushButton_stop_2.setEnabled(False)
        self.pushButton_stop_3.setEnabled(False)


class Worker(QtCore.QThread):
    sec_changed = QtCore.pyqtSignal(list)

    def __init__(self, port_ch, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.working = True
        self.sec = sec

        # Serial Port connect
        self.port_ch = port_ch
        # self.port_ch = Serial_comm(port, baud)
        # self.port_ch1 = Serial_comm('COM4', 38400)

        self.config = configparser.ConfigParser()
        self.config.read('setting.ini', "utf8")
        self.time_interval = int(self.config['Setting']['time_interval'])

    ''' Runtime error !!
    def __del__(self):
        print(".... end thread.....")
        self.wait()
    '''

    def run(self):
        # self.port_ch.wh_data('1')
        while self.working:
            if self.port_ch != '':
                if self.sec % (self.time_interval * 60) - (self.time_interval * 60 - 60) == 0:
                    self.port_ch.wh_data('1')
                getVal = self.port_ch.df
            else:
                getVal = list(self.sec)
            # print(getVal)
            self.sec_changed.emit(getVal)
            self.sleep(1)
            self.sec += 1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    # plot update
    form.btn_plot_test('curr_ch1')
    form.btn_plot_test('temp_ch1')
    form.btn_plot_test('mpd_ch1')
    form.btn_plot_test('rssi_ch1')
    form.btn_plot_test('vapd_ch1')
    form.pmu_mon()
    form.pmu_3d_mon2()

    app.exec()
