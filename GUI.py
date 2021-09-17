# GUI command for CoolLED pE-300
# using PyQt5 and Pyserial

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
pg.setConfigOption('background','w') # set background default to white
pg.setConfigOption('antialias',True)

import time, serial, atexit
import traceback, sys


### Configure serial communication 
PORTNAME = 'COM3' # set port name here
#ser = serial.Serial() 
#ser.baudrate = 9600
#ser.port = PORTNAME
#ser.bytesize = 8 
#ser.parity = 'N'
#ser.stopbits = 1
#ser.timeout = 0 # second



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
    
    def __init__(self, serial, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.ser = serial
    #    print(ser.name)

        self.setWindowTitle("CoolLED pE-300 controller")
        self.setFixedSize(800,600)

        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self._createStateButton()
        self._createInputField()


        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.getButtonsState()

    # Auxilary functions

    def _createStateButton(self):
        self.l = QPushButton("Set state")
        self.l.setCheckable(True)
        self.l.pressed.connect(self.getButtonsState) # when button pressed, set state
        self.generalLayout.addWidget(self.l)   

    def _createInputField(self):
        self.horizonLayout = QHBoxLayout()
        self.label = QLabel("Input:")
        self.label.setFixedWidth(120)        
        self.k = QLineEdit()
        self.horizonLayout.addWidget(self.label)
        self.horizonLayout.addWidget(self.k)
        self.generalLayout.addLayout(self.horizonLayout)


    # slots


    def getButtonsState(self):
        # read state of buttons 
        state = int(self.l.isChecked())
        self.k.setText(str(state))
        self.k.setFocus()

#        CMD = 'relay writeall '+hexstring+'\r' # hex numbers lower case
#        ser.write(CMD.encode()) # convert to byte array
#        time.sleep(0.05)
 #       ser.flushInput()



def handle_exit():
#    ser.close()
    print('Port closed')

def main(ser):

    # Open port
#    ser.open()
    print('Port open')
    # Make sure to close port on exit
    atexit.register(handle_exit)

    # here is the app running
    app = QApplication(sys.argv)

    window = MainWindow(ser)
    window.show()

    sys.exit(app.exec_())

    

if __name__=='__main__':
    ser = 0
    main(ser)

