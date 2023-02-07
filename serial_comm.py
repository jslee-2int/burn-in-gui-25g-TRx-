import serial
import time, re
import threading


class Serial_comm:
    def __init__(self, port, baud):
        # init. setting
        self.port = port
        self.baud = baud

        # self.ser = serial.Serial(self.port, self.baud, timeout=0.5, rtscts=1)
        self.ser = serial.Serial(self.port, self.baud, timeout=2)

        if self.ser.isOpen():
            print(self.ser.name + ' is open ...')

        print('init.')
        self.df = []

    def wh_data(self, cmd):
        t = threading.Thread(target=self.making_df, args=(cmd,))
        t.daemon = True
        t.start()

    def making_df(self, cmd):
        result_df = []
        for i in range(1, 9):
            self.ser.write(bytes('*pin set selch {}\n'.format(i), encoding='ascii'))
            self.ser.write(bytes('*i2c r a0 ff 2a 2 2\n', encoding='ascii'))
            while True:
                if self.ser.readable():
                    tx_bias = self.ser.readline().decode("utf-8").strip().replace(">R>OK;", "").replace(";", "").replace(" ", "")
                    if tx_bias != '':
                        break
            self.ser.write(bytes('*imon;\n', encoding='ascii'))
            while True:
                if self.ser.readable():
                    meas_curr = self.ser.readline().decode("utf-8").strip().replace("Imon ", "")
                    meas_curr = re.findall(r"[-+]?\d*\.\d+|\d+", meas_curr)[0]
                    if float(meas_curr) > 60:
                        meas_curr = '0.000'
                    if meas_curr != '':
                        break
            self.ser.write(bytes('*i2c r a4 ff 6c 2 2\n', encoding='ascii'))
            while True:
                if self.ser.readable():
                    meas_temp = self.ser.readline().decode("utf-8").strip().replace(">R>OK;", "").replace(";", "").replace(" ", "")
                    if meas_temp != '':
                        break
            self.ser.write(bytes('*i2c r a0 ff f0 2 2\n', encoding='ascii'))
            while True:
                if self.ser.readable():
                    meas_mpd = self.ser.readline().decode("utf-8").strip().replace(">R>OK;", "").replace(";", "").replace(" ", "")
                    if meas_mpd != '':
                        break
            self.ser.write(bytes('*i2c r a0 ff f8 2 2\n', encoding='ascii'))
            while True:
                if self.ser.readable():
                    meas_rssi = self.ser.readline().decode("utf-8").strip().replace(">R>OK;", "").replace(";", "").replace(" ", "")
                    if meas_rssi != '':
                        break
            self.ser.write(bytes('*i2c r a4 ff 70 2 2\n', encoding='ascii')) # TEC_Temp.
            while True:
                if self.ser.readable():
                    meas_vapd = self.ser.readline().decode("utf-8").strip().replace(">R>OK;", "").replace(";", "").replace(" ", "")
                    if meas_vapd != '':
                        break
            result_df.append([meas_curr, meas_temp, meas_mpd, meas_rssi, meas_vapd])
        self.df = result_df
        # print(self.df)
        return result_df

    def serial_close(self):
        print(self.ser.name + ' is close ...')
        self.ser.close()


if __name__ == "__main__":
    sc = Serial_comm('COM12', 38400)
    # while True:
    #     cmd = input('Command : ')
    #     if cmd != []:
    #         getVal = sc.making_df(cmd)
    #         print(getVal)
    #     elif cmd == 'exit':
    #         break
    sc.making_df('1')
    time.sleep(1)
    sc.serial_close()