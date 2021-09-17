# Serial command using pyserial
# for CoolLED pE-300

import serial, atexit

### Configure serial communication 
PORTNAME = 'COM3' # set port name here
ser = serial.Serial() 
ser.baudrate = 9600
ser.port = PORTNAME
ser.bytesize = 8 
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 0 # second


def handle_exit():
    ser.close()
    print('Port closed')

def main(ser):

    # Open port
    ser.open()
    print('Port open')
    # Make sure to close port on exit
    atexit.register(handle_exit)

    # here is the app running

    CMD = 'CSF\n' # CSN turns on, CSF turns off 
    ser.write(CMD.encode())
    print("Write")

if __name__=='__main__':
    main(ser)