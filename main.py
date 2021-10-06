# Serial command using pyserial
# for CoolLED pE-300
# GUI control
# N Laohakunakorn, University of Edinburgh, 2021

import serial, atexit

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
pg.setConfigOption('background','w') # set background default to white
pg.setConfigOption('antialias',True)
import traceback, sys

### Configure serial communication 
PORTNAME = 'COM3' # set port name here
ser = serial.Serial() 
ser.baudrate = 9600
ser.port = PORTNAME
ser.bytesize = 8 
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 0 # second

# GUI
class WorkerSignals(QObject):
    '''defines signals from running worker thread
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    '''worker thread
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs['results'] = self.signals.result

    @pyqtSlot()
    def run(self):
        '''initialise runner function with passed args, kwargs
        '''
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        self.setWindowTitle("MCL Microstage Controller")
        self.setFixedSize(300,300)

        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        buttons = {'LED ON': (0, 0)
                  }
        self._createButtons(buttons)


        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.resetButtonsState()

    # Auxilary functions

    def _createButtons(self,buttons):
        self.buttons = {}
        buttonsLayout = QGridLayout()

        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            self.buttons[btnText].setFixedSize(100,60)
            self.buttons[btnText].setCheckable(True)
            self.buttons[btnText].clicked.connect(self.getButtonsState) # when button clicked, get state
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
        self.generalLayout.addLayout(buttonsLayout)

    # slots

    def getButtonsState(self):
        # read state of buttons and trigger actions
        state = []
        for btnText, pos in self.buttons.items():
            state.append(int(self.buttons[btnText].isChecked()))
        binstring = ''.join(['1' if x else '0' for x in state])

        # Write command
        INPUT = binstring 
        if bool(int(INPUT)):
            print('LED on')
            CMD = 'CSN\n'
            ser.write(CMD.encode())
        else:
            print('LED off')
            CMD = 'CSF\n'
            ser.write(CMD.encode())
     
    def resetButtonsState(self):
        for btnText, pos in self.buttons.items():
                self.buttons[btnText].setChecked(False)


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
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__=='__main__':
    main(ser)