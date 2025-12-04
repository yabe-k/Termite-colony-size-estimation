#This is a library to utilize mh-z14a.
#Ver. 2.10
#Written by YABE, on Jan. 17, 2022.

import time
import datetime
import serial
def read_co2():
    s = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.1)
    # Send command to MH-Z14A
    s.write(bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]))
    # Read response
    data = s.read(9)

    # Is response length correct?
    if len(data) != 9:
        print("Response length is not correct.")
        s.reset_input_buffer()
        return None

    # Is this a valid command response?
    if data[0] != 0xFF or data[1] != 0x86:
        print("Not a valid response")
        s.reset_input_buffer()
        return None

    # Checksum
    checksum = 0xFF - (sum(data[1:7]) & 0xFF) + 1
    if checksum != data[8]:
        print("Checksum error!")
        s.reset_input_buffer()
        return None

    # Return CO2 level [ppm]
    return data[2] * 256 + data[3]

def calibrate():## ゼロ点(400 ppm)を補正
    s = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.1)
    # Send command to MH-Z14A
    s.write(bytes([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78]))

def disableAutoCalibration():# 自動キャリブレーションをOFFに
    s = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.1)
    # Send command to MH-Z14A
    s.write(bytes([0xFF, 0x01, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86]))

def calibrate_span(conc):# 上側を補正
    s = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.1)
    first = int(conc / 256)
    last = int(conc % 256)
    byte_list = [0xFF, 0x01, 0x88, first, last, 0x00, 0x00, 0x00]
    checksum = 0xFF - (sum(byte_list[1:7]) & 0xFF) + 1
    byte_list.append(checksum)
    s.write(bytes(byte_list))

def monitor_co2():
    while True:
        try:
            print(read_co2())
            time.sleep(1)
        except KeyboardInterrupt:
            return None

def record_co2(filename=None):
    now = datetime.datetime.now()
    if filename is None:
        filename = "recorded_" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second) + ".csv"
    f = open(filename, "w")
    while True:
        try:
            now = datetime.datetime.now()
            co2 = None
            while co2 == None:
                co2 = read_co2()
            co2 = str(co2)
            print(co2, now.year, now.month, now.day, now.hour, now.minute, now.second)
            f.write(co2 + "," + str(now.year) + "," + str(now.month) + "," + str(now.day) + "," + str(now.hour) + "," + str(now.minute) + "," + str(now.second) + "\n")
            time.sleep(5)
        except KeyboardInterrupt:
            f.close()
            print("Data was saved to " + filename + ".")
            return None
