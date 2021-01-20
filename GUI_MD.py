
# GUI for multimode detection
# author: Mehrdad Zarei
# e-mail: mehr.zarei1@gmail.com
# date: 25.11.2020

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, time
import pyqtgraph as pg
import numpy as np
from scipy.signal import find_peaks
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MyAlarm(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.default_color = self.getColor()

    def getColor(self):
        return self.palette().color(QPalette.Button)

    def setColor(self, value):
        if value == self.getColor():
            return
        palette = self.palette()
        palette.setColor(self.backgroundRole(), value)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def reset_color(self):
        self.setColor(self.default_color)

    color = pyqtProperty(QColor, getColor, setColor)

class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Multimode Detection')
        # self.resize(500,400)
        self.setGeometry(100, 100, 1150, 600)
        # self.showMaximized()
        QApplication.setStyle('Fusion')
        # background-color: black; color: white; 
        self.setStyleSheet('font-size: 11pt;')
        icon = QIcon()
        icon.addPixmap(QPixmap("icons\multimode.jpg"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.centralWidget = QWidget()
        mainLayout = QVBoxLayout()

        self.dataPoints=2000
        self.x_range = np.linspace(0, 20, self.dataPoints)
        self.a = 1
        self.mu1 = 7
        self.sig = 0.3
        self.mu2 = 14
        self.notification = 1
        self.contentMess = '''Hi,

your device is unstable.
don't worry, this is a notification from a bot by Mehrdad.

Best,
KL FAMO.'''

        #The mail addresses and password
        self.sender_address = 'zareimehrdad72@gmail.com'
        self.sender_pass = 'password'
        self.receiver_address = ['mzarei@umk.pl', 'mehr.zarey@yahoo.com']#, 'pmorzynski@fizyka.umk.pl', 'zawada@fizyka.umk.pl']

        #Setup the MIME
        self.message = MIMEMultipart()
        self.message['From'] = self.sender_address
        self.message['To'] = ','.join(self.receiver_address)
        self.message['Subject'] = 'An Alarm from KL FAMO Lab'   #The subject line
        #The body and the attachments for the mail
        self.message.attach(MIMEText(self.contentMess, 'plain'))

        self.createElementsOfSetting()
        self.createElementsOfGraph()

        self.singMulti.activated[str].connect(self.changeMode)
        self.shift.valueChanged.connect(self.changeShift)
        self.corr.clicked.connect(self.correction)

        self.plotRef()
        self.changeMode()

        # mainLayout.addStretch()
        mainLayout.addWidget(self.settingGroupBox)
        mainLayout.addWidget(self.dataGroupBox)
        mainLayout.addWidget(self.plotPattern)
        mainLayout.addWidget(self.plotStd)
        # mainLayout.addStretch()
        # mainLayout.setStretch(0, 1)
        # mainLayout.setStretch(1, 1)
        # mainLayout.setAlignment(Qt.AlignTop)
        
        self.centralWidget.setLayout(mainLayout)
        self.setCentralWidget(self.centralWidget)

    def createElementsOfSetting(self):

        self.settingGroupBox=QGroupBox("Setting")
        # self.settingGroupBox.setGeometry(QRect(10, 10, 450, 130))
        # self.settingGroupBox.adjustSize()
        self.settingGroupBox.setFixedHeight(110)
        # self.settingGroupBox.setFixedWidth(500)
        self.settingGroupBox.setMinimumWidth(1150)

        modeL = QLabel("Choose Mode", self.settingGroupBox)
        modeL.move(40, 35)
        self.singMulti = QComboBox(self.settingGroupBox)
        items = ['Single Mode', 'Multi Mode']
        self.singMulti.addItems(items)
        self.singMulti.move(35, 60)
        self.singMulti.resize(120, 30)
        # self.singMulti.setEditable(True)        
        modeL.setBuddy(self.singMulti)

        shiftL = QLabel("Shift", self.settingGroupBox)
        shiftL.move(280, 35)
        self.shift = QSpinBox(self.settingGroupBox)
        self.shift.setMaximum(int(self.dataPoints/2))
        self.shift.setMinimum(-int(self.dataPoints/2))
        self.shift.setValue(0)
        self.shift.setGeometry(275, 60, 150, 30)
        shiftL.setBuddy(self.shift)

        self.corr = QPushButton("Correction", self.settingGroupBox)
        self.corr.setDefault(True)
        self.corr.setEnabled(True)
        self.corr.move(585, 61)
        self.corr.resize(100, 27)
        
    def createElementsOfGraph(self):

        self.dataGroupBox = QGroupBox()
        self.dataGroupBox.setFixedHeight(60)
        # self.dataGroupBox.setFixedSize(500, 150)

        correlL = QLabel("Correlation:", self.dataGroupBox)
        correlL.move(20, 20)
        self.correl = QTextEdit(self.dataGroupBox)
        self.correl.setReadOnly(True)
        self.correl.move(98, 16)
        self.correl.resize(80, 30)
        # self.correl.adjustSize()
        # correlL.setBuddy(self.correl)

        noPeaksL = QLabel("No. Peaks:", self.dataGroupBox)
        noPeaksL.move(270, 20)
        self.noPeaks = QTextEdit(self.dataGroupBox)
        self.noPeaks.setReadOnly(True)
        self.noPeaks.move(347, 16)
        self.noPeaks.resize(80, 30)
        # self.noPeaks.adjustSize()

        stdL = QLabel("Standard Deviation:", self.dataGroupBox)
        stdL.move(535, 20)
        self.std = QTextEdit(self.dataGroupBox)
        self.std.setReadOnly(True)
        self.std.move(667, 16)
        self.std.resize(80, 30)
        # self.std.adjustSize()

        self.alarm = MyAlarm("Alarm", self.dataGroupBox)
        # self.alarm.setDefault(False)
        self.alarm.setEnabled(False)
        self.alarm.move(1000, 16)
        self.alarm.resize(100, 30)
        self.alarm.width()
        # self.alarm.adjustSize()
        # self.alarm.setText("Single Mode")

        self.animation = QPropertyAnimation(self.alarm, b"color", self.dataGroupBox)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(100)
        self.animation.setStartValue(self.alarm.default_color)
        self.animation.setEndValue(self.alarm.default_color)
        self.animation.setKeyValueAt(0.1, QColor(255, 0, 0))

        self.plotPattern = pg.PlotWidget(title="Pattern")
        self.plotPattern.setLabels(left = ('Amplitude'), bottom = ('data points'))
        self.plotPattern.addLegend(offset = (0, -60))
        self.plotPattern.clear()
        self.refP = self.plotPattern.plot(pen = (250, 0, 0), name = 'Reference Pattern')
        self.curP = self.plotPattern.plot(pen = (0, 0, 250), name = 'Current Pattern')
        self.peakP = self.plotPattern.plot(pen = None, name = 'Peaks', symbol = 'o', symbolPen = (0, 250, 0), symbolBrush = (0, 250, 0))
        
        self.plotStd = pg.PlotWidget(title = "Residual")
        self.plotStd.setLabels(left = ('Amplitude'), bottom = ('data points'))
        # self.plotStd.addLegend()
        self.plotStd.clear()
        self.res = self.plotStd.plot(pen = (0, 250, 0))
        
    def changeShift(self):

        self.changeMode()

    def changeMode(self):

        mode = self.singMulti.currentText()
        d = self.shift.value()
        profile = np.zeros(self.dataPoints)
        shift = np.zeros(self.dataPoints)
        noise = np.random.normal(0, 0.04, self.dataPoints)
        if mode == 'Single Mode':
            
            profile = self.gaussian(self.x_range, self.a, self.mu1, self.sig) + self.gaussian(self.x_range, self.a, self.mu2, self.sig)
        else:

            amp = [0.3, 0.4, 0.5, 0.4, 0.3]
            indx = [-2, -1, 0, 1, 2]
            for i in range(5):
            
                a = amp[i]
                mu1p = self.mu1 + indx[i]
                mu2p = self.mu2 + indx[i]
                profile += self.gaussian(self.x_range, a, mu1p, self.sig) + self.gaussian(self.x_range, a, mu2p, self.sig)
        if d>=0:

            shift[d:] = profile[:len(profile)-d]
        else:

            shift[:len(profile) - abs(d)] = profile[abs(d):]
        self.y_range_prof = shift + noise
        self.curP.setData(self.y_range_prof)
        self.analyse()

    def correction(self):

        d = self.shift.value()
        shift = np.zeros(self.dataPoints)
        if d>=0:

            shift[:len(self.y_range_prof) - abs(d)] = self.y_range_prof[abs(d):]
        else:

            shift[abs(d):] = self.y_range_prof[:len(self.y_range_prof)-abs(d)]
        self.y_range_prof = shift
        self.curP.setData(self.y_range_prof)
        self.analyse()

    def analyse(self):

        res = self.y_range_ref - self.y_range_prof
        std_signal = np.std(res)
        cor_signal = np.corrcoef(self.y_range_ref, self.y_range_prof)
        peaksInd, peaksH = find_peaks(self.y_range_prof, height = 0.2, distance = 100)
        noPeaks = len(peaksInd)

        self.correl.setText("%.4f"%cor_signal[0,1])
        self.noPeaks.setText(str(noPeaks))
        self.std.setText("%.4f"%std_signal)

        self.peakP.setData(peaksInd, self.y_range_prof[peaksInd])
        self.res.setData(res)

        if cor_signal[0,1]<0.85 or std_signal>0.1 or noPeaks>2:

            self.animation.start()
            self.alarm.setText("Multi Mode")
            if self.notification:

                self.notification = 0
                # self.sendNotificaion()
        else:

            self.notification = 1
            self.animation.stop()
            self.alarm.setText("Single Mode")

    def sendNotificaion(self):

        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(self.sender_address, self.sender_pass) #login with mail_id and password
        text = self.message.as_string()
        session.sendmail(self.sender_address, self.receiver_address, text)
        session.quit()
        print('sent email')

    def plotRef(self):

        noise = np.random.normal(0, 0.04, self.dataPoints)
        ref_profile = self.gaussian(self.x_range, self.a, self.mu1, self.sig) + self.gaussian(self.x_range, self.a, self.mu2, self.sig)
        self.y_range_ref = ref_profile + noise

        self.refP.setData(self.y_range_ref)

    def gaussian(self, x, a, mu, sig):

        return a*np.exp(-np.power(x-mu, 2)/(2*np.power(sig, 2)))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())

