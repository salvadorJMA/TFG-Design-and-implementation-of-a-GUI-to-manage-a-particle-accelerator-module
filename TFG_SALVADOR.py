########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
#######################                                                #################################
####################### AUTHOR: SALVADOR JESÚS MEGÍAS ANDREU           #################################
####################### EMAIL: salvadorjmegias@gmail.com               #################################
####################### UNIVERSITY EMAIL: salvadorjesus@correo.ugr.es  #################################
#######################                                                #################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################


# We import all the libraries we need for our GUI
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5 import uic
from PyQt5.QtWidgets import QProgressBar
from analoggaugewidget import AnalogGaugeWidget
from analoggaugewidget2 import AnalogGaugeWidget2
import sys, time
from googletrans import Translator, constants
from AgilentN9020A import Agilent_MXA_N9020A
from AnritsuMS2830A import AnritsuMS2830A
from matplotlib import pyplot as plot
from matplotlib import pyplot as plot2
import requests
import numpy as np
import epics
from scipy.signal import argrelmax , find_peaks










########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
######################################                          ########################################
###################################### BEGINNING OF GUI's CLASS ########################################
######################################                          ########################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################


class MiTFG(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('Final.ui',self) # We import the GUI .ui file
        self.resize(888, 200)
        icon = QtGui.QIcon("./images/tfg.png") # We place the GUI icon (a graduation cap)
        self.setWindowIcon(icon)

        self.label.setPixmap(QtGui.QPixmap("./images/uk.png"))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("./images/switch-off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.checkBox.setIcon(icon2)

        # Here we initialize the images of the labels and checkBoxes that we want to be shown by default in the GUI
        icon3 = QtGui.QIcon("./images/power-off.png")
        self.checkBox_2.setIcon(icon3)

        self.checkBox_3.setIcon(QtGui.QIcon("./images/switch-off.png"))
        self.label_23.setPixmap(QtGui.QPixmap("./images/uk.png"))

        self.label_34.setPixmap(QtGui.QPixmap("./images/uk.png"))
        self.checkBox_4.setIcon(QtGui.QIcon("./images/switch-off.png"))

        # We must configure Anritsu's doubleSpinBox to allow negative numbers
        # and we also configure the jump that it will give each time its buttons are pressed
        self.doubleSpinBox.setSingleStep(0.1)
        self.doubleSpinBox.setRange(-4.0,1.0)


        # Here I give it the shape of a thermometer and assign colors to the BLAS progressBars related to temperature and flow
        # red for temperature and blue for water

        self.progressBar.setStyleSheet("QProgressBar"
                          "{"
                          "border : 1px solid black;"
                          "border-bottom-right-radius: 25px;"
                          "border-bottom-left-radius: 25px;"
                          "}"
                          "QProgressBar::chunk"
                          "{"                         
                            
                          "border-bottom-right-radius: 24px;"
                          "border-bottom-left-radius: 24px;"
                          "background : red"
                          "}"
                          )

        self.progressBar_2.setStyleSheet("QProgressBar"
                          "{"
                          "border : 1px solid black;"
                          "border-bottom-right-radius: 25px;"
                          "border-bottom-left-radius: 25px;"
                          "}"
                          "QProgressBar::chunk"
                          "{"                         
                            
                          "border-bottom-right-radius: 24px;"
                          "border-bottom-left-radius: 24px;"
                          "background : blue"
                          "}"
                          )
        #Here I determine the maximum value that the vertical progressBar can reach relative to the flow rate
        self.progressBar_2.setMaximum(7)


        # Lists where we will store the widgets and their respective ToolTips so that we can attribute them quickly and not one by one
        # This will allow the scalability of the GUI to be greater
        self.toolTipsObjects = [self.comboBox,self.comboBox_2,self.checkBox, self.radioButton, self.radioButton_2,self.pushButton,self.pushButton_2,self.pushButton_3,self.pushButton_4,self.checkBox_2,self.checkBox_3,self.comboBox_3,self.checkBox_4,self.radioButton_3,self.pushButton_5,self.pushButton_6,self.pushButton_7]
        self.toolTips = ["It changes the language of the GUI","It changes the language of the GUI","It connects and disconnect from the machine","It turns on generator mode","It turns on spectrum mode","It plots machine's data in an image","It sends Generator's data to the machine","It sends Spectrum's data to the machine","It plots machine's data between 100 MHz to 1.5 GHz in an image","turn on and off the Generator","It connects and disconnect from BLAS","It changes the language of the GUI","It connects and disconnect from the machine","It turns on spectrum mode","It sends Spectrum's data to the machine","It plots machine's data in an image","It plots machine's data between 100 MHz to 1.5 GHz in an image"]
        
        # We store the widgets (labels, buttons and radioButtons) from which we will take their text and thus be able to translate them quickly
        self.allLabels =[self.label_2,self.label_4,self.label_5,self.label_6,self.label_7,self.label_8,self.label_9,self.label_10,self.label_11,self.label_12,self.label_13,self.label_14,self.label_17,self.label_24,self.label_25,self.label_27,self.label_28,self.label_29,self.label_30,self.label_31,self.label_32,self.label_33,self.label_35]
        self.allPushButtons= [self.pushButton,self.pushButton_2,self.pushButton_3,self.pushButton_4,self.pushButton_5,self.pushButton_6,self.pushButton_7]
        self.allRadioButtons = [self.radioButton,self.radioButton_2,self.radioButton_3]
        
        # Here we will store the possible messages that will appear in the warning windows and their translations, so that this task is as fast as possible.
        # By doing it this way, expanding the translation to new GUI languages is an easier task (main language being English)

        self.messagesWindows=["Warning","You must connect to the machine first.","There is some problem with the machine's connection. Check the connection.","You must select the Generator mode first.","You must select the Spectrum mode first.","There was some problem with the BLAS connection","Fail in Patch Panel","Fail in water flow","Fail in RF","Temperature failure"]
        self.traducedMessagesWindows=[]

        # Variables we will use for Anritsu
        self.conectadoAnritsu = False
        self.maxPowerTimeAnritsu=[]
        self.maxFreqTimeAnritsu=[]
        self.numeroAnritsu = 0

        # Variables we will use for Agilent
        self.conectadoAgilent = False
        self.maxPowerTimeAgilent=[]
        self.maxFreqTimeAgilent=[]
        self.numeroAgilent = 0

        
        self.text= self.getCompleteText() # we initialize the text of the gui to be able to translate it
        self.setToolTips(self.toolTips) # we set the ToolTips text to the widgets "toolTipsObjects"


        # The signals to understand it are like Threads that are waiting for an event to occur to execute the function associated with that event
        # That is, it's like event-driven programming

        # Widget connections with functions for Anritsu using signals

        self.comboBox.currentIndexChanged.connect(lambda:self.idComboBox1())
        self.checkBox.clicked.connect(lambda:self.conectarAnritsu())
        self.radioButton.clicked.connect(lambda:self.setGenerator())
        self.radioButton_2.clicked.connect(lambda:self.setSpectrum())
        self.pushButton_2.clicked.connect(lambda:self.setParamsGenerator())
        self.pushButton_3.clicked.connect(lambda:self.setParamsSpectrumAnritsu())
        self.pushButton.clicked.connect(lambda:self.plotImageAnritsu())
        self.pushButton_4.clicked.connect(lambda:self.plotLargeSpectrumAnritsu())
        self.checkBox_2.clicked.connect(lambda:self.turnOnGenerator())
        self.doubleSpinBox.valueChanged.connect(lambda:self.moveDoubleSpinBox())
        self.spinBox.valueChanged.connect(lambda:self.moveSpinBox())

        # Widget connections with functions for BLAS using signals

        self.checkBox_3.clicked.connect(lambda:self.connectBlas())
        self.comboBox_2.currentIndexChanged.connect(lambda:self.idComboBox2())
        
        # Widget connections with functions for Agilent using signals

        self.pushButton_6.clicked.connect(lambda:self.plotImageAgilent())
        self.spinBox_2.valueChanged.connect(lambda:self.moveSpinBoxAgilent())
        self.radioButton_3.clicked.connect(lambda:self.setSpectrumAgilent())
        self.pushButton_5.clicked.connect(lambda:self.setParamsSpectrumAgilent())
        self.checkBox_4.clicked.connect(lambda:self.conectarAgilent())
        self.pushButton_7.clicked.connect(lambda:self.plotLargeSpectrumAgilent())
        self.comboBox_3.currentIndexChanged.connect(lambda:self.idComboBox3())


        # The GUI connects to all EPICS IOCS records running on the EPICS server
        self.connectEPICS()
        
        
        # Here we create and introduce our own dials or Gauges (not from QT designer) that will be used for Anritsu

        # We put the handsome dials
        self.dial = AnalogGaugeWidget(self.tab)
        self.dial.setObjectName("dial")
        #self.dial.setSizePolicy(sizePolicy)
        self.dial.setMinimumSize(QtCore.QSize(150, 150))
        self.dial.setMaximumSize(QtCore.QSize(600, 600))
        self.dial.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_9.addWidget(self.dial, 1, 0, 2, 1)
        
        self.dial_3 = AnalogGaugeWidget(self.tab)
        self.dial_3.setObjectName("dial_3")
        #self.dial_3.setSizePolicy(sizePolicy)
        self.dial_3.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_3.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_3.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_9.addWidget(self.dial_3, 1, 3, 2, 1)

        # We put one of the dials
        self.dial_2 = AnalogGaugeWidget(self.tab)
        self.dial_2.setObjectName("dial_2")
        #self.dial_2.setSizePolicy(sizePolicy)
        self.dial_2.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_2.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_2.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_2.addWidget(self.dial_2, 1, 2, 2, 1)


        # Here we create and introduce our own dials or Gauges (not from QT designer) that will be used for Agilent


        self.dial_11 = AnalogGaugeWidget(self.tab_2)
        self.dial_11.setObjectName("dial_11")
        self.dial_11.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_11.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_11.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_5.addWidget(self.dial_11, 2, 0, 7, 1)

        self.dial_12 = AnalogGaugeWidget(self.tab_2)
        self.dial_12.setObjectName("dial_12")
        self.dial_12.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_12.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_12.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_5.addWidget(self.dial_12, 2, 2, 7, 1)
        

        # Here we create and introduce our own dials or Gauges (not from QT designer) that will be used for the BLAS


        self.dial_4 = AnalogGaugeWidget2(self.tab_5)
        self.dial_4.setObjectName("dial_4")
        self.dial_4.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_4.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_4.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_4, 1, 0, 2, 1)

        self.dial_5 = AnalogGaugeWidget2(self.tab_5)
        self.dial_5.setObjectName("dial_5")
        self.dial_5.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_5.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_5.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_5, 1, 1, 2, 1)

        self.dial_6 = AnalogGaugeWidget2(self.tab_5)
        self.dial_6.setObjectName("dial_6")
        self.dial_6.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_6.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_6.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_6, 4, 0, 1, 1)

        self.dial_7 = AnalogGaugeWidget2(self.tab_5)
        self.dial_7.setObjectName("dial_7")
        self.dial_7.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_7.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_7.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_7, 4, 1, 1, 1)

        self.dial_8 = AnalogGaugeWidget2(self.tab_5)
        self.dial_8.setObjectName("dial_8")
        self.dial_8.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_8.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_8.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_8, 6, 2, 1, 1)

        self.dial_9 = AnalogGaugeWidget2(self.tab_5)
        self.dial_9.setObjectName("dial_9")
        self.dial_9.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_9.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_9.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_9, 6, 1, 1, 1)

        self.dial_10 = AnalogGaugeWidget2(self.tab_5)
        self.dial_10.setObjectName("dial_10")
        self.dial_10.setMinimumSize(QtCore.QSize(150, 150))
        self.dial_10.setMaximumSize(QtCore.QSize(600, 600))
        self.dial_10.setBaseSize(QtCore.QSize(200, 200))
        self.gridLayout_16.addWidget(self.dial_10, 6, 0, 1, 1)



        

        







########################################################################################################
############ ANRITSU MANAGEMENT FUNCTIONS ##########################################################
########################################################################################################


    # Function that connects to the machine, or disconnects from it
    def conectarAnritsu(self):

        
        # If we are not connected and we hit the connect checkBox to connect with the machine, it connects to the machine automatically and changes the icon to ON
        if self.checkBox.isChecked():

            # connects to the machine and grabs all the data from the machine to output and load into the GUI
            try:
                # connects to the machine creating an object of the class Anritsu
                self.anritsu= AnritsuMS2830A()
                self.conectadoAnritsu = True
                # Get all the data from the machine and load it into the GUI
                self.setInitialParamsAnritsu()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./images/switch-on.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                self.checkBox.setIcon(icon)



                # If we are connected to EPICS server (to EPICS IOC)
                if self.EPICS_connected:

                    #We create the thread that will be in charge of monitoring all the EPICS records referring to Anritsu so that EPICS interacts with the GUI
                    self.startEPICS_Anritsu()

                
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.
            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[2])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[2])

                self.checkBox.setChecked(False)


        # If we are connected and we hit the connect checkBox to disconnect from the machine, it disconnects from the machine automatically and changes the icon to OFF
        else:
            try:

                # It disconnect from the machine
                self.anritsu.disconnect()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./images/switch-off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.checkBox.setIcon(icon)
                # It sets all the data of the widgets to 0 (the default value)
                self.clearParamsAnritsu()
                self.conectadoAnritsu = False
            
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.
            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[2])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[2])
        

##################################################################################################################################################



    # Function that initializes all the GUI widgets to the values collected in the anritsu machine as soon as we connect to it

    def setInitialParamsAnritsu(self):
        
        # Anritsu library function that collects all machine data and stores it in anritsu object attributes
        self.anritsu.getInitialParamsAnritsu()

        # We modify the state of the GUI widgets conveniently with the data obtained

        self.doubleSpinBox.setValue(self.anritsu.power)
        self.lcdNumber.display(self.anritsu.power)
        self.spinBox.setValue(int(self.anritsu.referenceLevel))
        self.lcdNumber_2.display(self.anritsu.referenceLevel)
        self.dial_2.value = int(self.anritsu.frequency/1e6)
        self.dial_3.value = int(self.anritsu.finalFreq )
        self.dial.value = int(self.anritsu.inicialFreq)
        
        # if the machine is in spectrum analyzer mode, its rarioButton is checked

        if "SPECT" in self.anritsu.instAnritsu:
            self.radioButton_2.setChecked(True)
        
        # if the machine is in signal generator mode, its rarioButton is checked

        if "SG" in self.anritsu.instAnritsu:
            self.radioButton.setChecked(True)

        # if the generator is on, its checkBox is checked and the icon is changed to on

        if self.anritsu.state == 1:
            self.checkBox_2.setChecked(True)
            self.checkBox_2.setIcon(QtGui.QIcon("./images/power.png"))


##################################################################################################################################################           

    # Function that clear all the values of the widgets and load to them defaults values

    def clearParamsAnritsu(self):

        self.doubleSpinBox.setValue(0)
        self.lcdNumber.display(0)
        self.spinBox.setValue(0)
        self.lcdNumber_2.display(0)
        self.dial_2.value = int(0)
        self.dial_3.value = int(0)
        self.dial.value = int(0)

        # if the machine is in spectrum analyzer mode, its rarioButton is unchecked

        if "SPECT" in self.anritsu.instAnritsu:
            self.radioButton_2.setChecked(False)
        
        # if the machine is in signal generator mode, its rarioButton is unchecked

        if "SG" in self.anritsu.instAnritsu:
            self.radioButton.setChecked(False)

        # if the generator is on, its checkBox is unchecked and the icon is changed to off

        if self.anritsu.state == 1:
            self.checkBox_2.setChecked(False)
            self.checkBox_2.setIcon(QtGui.QIcon("./images/power-off.png"))


##################################################################################################################################################

    #Function that turns the generator on or off

    def turnOnGenerator(self):

        # If we check the Generator checkBox to activate the generator
        if self.checkBox_2.isChecked():
            try:
                # And the signal generator mode is selected
                if self.radioButton.isChecked():

                    # we activate the generator
                    self.anritsu.setStateGenerator(1)

                    # and change the icon to power on
                    self.checkBox_2.setIcon(QtGui.QIcon("./images/power.png"))

                    # If we are connected to EPICS server (to EPICS IOC)
                    if self.EPICS_connected:

                        # we modify the record of the state of the generator indicating that it is on (1)
                        self.Anritsu_SG_State.put(1)
                        # and we tell the record that monitors all changes in Anritsu, that there has been a change
                        self.Anritsu_SomeValueChanged.put(1)

                #  if the signal generator mode is not selected, we create an exception with raise so that the exception code below is executed
                else:
                    raise
            
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.

            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[3])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[3])

                # we uncheck the checkBox because the generator was not activated
                self.checkBox_2.setChecked(False)

        # If we check the Generator checkBox to deactivate the generator
        else:
            try:
                # And the signal generator mode is selected

                if self.radioButton.isChecked():

                    # we deactivate the generator
                    self.anritsu.setStateGenerator(0)

                    # and change the icon to power off
                    self.checkBox_2.setIcon(QtGui.QIcon("./images/power-off.png"))

                    # If we are connected to EPICS server (to EPICS IOC)
                    if self.EPICS_connected:

                        # we modify the record of the state of the generator indicating that it is off (0)
                        self.Anritsu_SG_State.put(0)
                        # and we tell the record that monitors all changes in Anritsu, that there has been a change
                        self.Anritsu_SomeValueChanged.put(1)
                
                #  if the signal generator mode is not selected, we create an exception with raise so that the exception code below is executed
                else:
                    raise
            
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.
            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[3])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[3])

                # we check the checkBox because the generator was not deactivated
                self.checkBox_2.setChecked(True)



##################################################################################################################################################

    # Function that selects the signal generator mode in the machine
    def setGenerator(self):

        # if we are connected to the machine
        if self.conectadoAnritsu:
            
            # we select the signal generator mode
            self.anritsu.setSignalGen()
            
            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # we modify the register of the chosen mode to "SG" (signal generator)
                self.Anritsu_Instrument_Choosed.put('SG')
                # and we tell the record that monitors all changes in Anritsu, that there has been a change
                self.Anritsu_SomeValueChanged.put(1)

        # if we are not connected to the machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])

            # and we reset the radioButton
            self.radioButton.setCheckable(False)
            self.radioButton.setCheckable(True)
            

##################################################################################################################################################

    # Function that selects the spectrum analyzer mode in the machine
    def setSpectrum(self):

        # if we are connected to the machine
        if self.conectadoAnritsu:
            # we select the spectrum analyzer mode
            self.anritsu.setSpectrum()

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # we modify the register of the chosen mode to "SPECT" (spectrum analyzer)
                self.Anritsu_Instrument_Choosed.put('SPECT')
                # and we tell the record that monitors all changes in Anritsu, that there has been a change
                self.Anritsu_SomeValueChanged.put(1)
        
        # if we are not connected to the machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])

            # and we reset the radioButton
            self.radioButton_2.setCheckable(False)
            self.radioButton_2.setCheckable(True)
            



##################################################################################################################################################

    # Function that establishes the selected parameters of the signal generator in the GUI sending them to the machine modifying the parameters of said machine

    def setParamsGenerator(self):

        # If the signal generator mode is selected
        if self.radioButton.isChecked():
            # we send the parameters established in the GUI to the Anritsu machine
            self.anritsu.setParamsGenerator(self.doubleSpinBox.value(),int(self.dial_2.value))

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # we modify the registers of the power and frequency of the signal generator
                self.Anritsu_SG_Power.put(self.doubleSpinBox.value())
                self.Anritsu_SG_Frequency.put(int(self.dial_2.value))
                # and we tell the record that monitors all changes in Anritsu, that there has been a change
                self.Anritsu_SomeValueChanged.put(1)

        # If the signal generator mode is not selected, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[3])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[3])


##################################################################################################################################################


    # Function that establishes the selected parameters of the spectrum analyzer (in Anritsu machine) in the GUI sending them to the machine modifying the parameters of said machine

    def setParamsSpectrumAnritsu(self):

        # If the spectrum analyzer mode is selected
        if self.radioButton_2.isChecked():
            
            # we send the parameters established in the GUI to the Anritsu machine
            self.anritsu.setParamsSpectrum(int(self.dial.value),int(self.dial_3.value),self.spinBox.value())

            # and we create the thread to start making measurements of the maximum power every 30 seconds
            self.startAnritsu()

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # we modify the registers of the initial, final frequency and reference level of the spectrum analyzer
                self.Anritsu_SPECT_InitialFrequency.put(int(self.dial.value))
                self.Anritsu_SPECT_ReferenceLevel.put(self.spinBox.value())
                self.Anritsu_SPECT_FinalFrequency.put(int(self.dial_3.value))
                # and we tell the record that monitors all changes in Anritsu, that there has been a change
                self.Anritsu_SomeValueChanged.put(1)

        # If the spectrum analyzer mode is not selected, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])



##################################################################################################################################################

    # Function that plots the information collected by the spectrum analyzer at a given time in an image

    def plotImageAnritsu(self):

        # If we are connected to the Anritsu machine
        if self.conectadoAnritsu:

            # And the spectrum analyzer mode is selected on the machine

            if self.radioButton_2.isChecked():

                # We create the image of the information trace of the machine
                self.anritsu.plotInfoAnritsu()

                # And plot it into the graphicsView widget
                self.scene = QtWidgets.QGraphicsScene()
                self.pixmap = QtGui.QPixmap("./images/graphAnritsu.jpg")
                self.scene.addPixmap(self.pixmap)
                self.graphicsView.setScene(self.scene)

            # If the spectrum analyzer mode is not selected on the machine, it is notified by a pop-up window, a warning message.

            else:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])    

        # If we are not connected to the Anritsu machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])


##################################################################################################################################################

    # Function that plots the information collected by the spectrum analyzer in the range of 100 MHz and 1.5 GHz, at a given time in an image


    def plotLargeSpectrumAnritsu(self):

        # If we are connected to the Anritsu machine
        if self.conectadoAnritsu:

            # And the spectrum analyzer mode is selected on the machine
            if self.radioButton_2.isChecked():
                
                # we save the values of the final and initial frequency that have the spectrum analyzer established at that instant of time
                freqIni = self.anritsu.inicialFreq
                freqFin = self.anritsu.finalFreq

                # we change the parameters of the spectrum analyzer so that it measures between 100 MHz and 1.5GHz

                self.anritsu.setParamsSpectrum(100,1500,self.anritsu.referenceLevel)

                time.sleep(0.5)

                # We create the image of the information trace of the machine

                self.anritsu.plotInfoAnritsu()

                # And plot it into the graphicsView widget
                self.scene = QtWidgets.QGraphicsScene()
                self.pixmap = QtGui.QPixmap("./images/graphAnritsu.jpg")
                self.scene.addPixmap(self.pixmap)
                self.graphicsView_3.setScene(self.scene)

                # once the image is plotted, we return to change the parameters of the spectrum analyzer to those that had been established before making this measurement
                self.anritsu.setParamsSpectrum(freqIni,freqFin,self.anritsu.referenceLevel)


                # HERE WE CALCULATE THE HARMONICS POWERS

                NumpyDatosCapturados = np.array(self.anritsu.datosCapturados)

                # determine the indices of the local maxima
                max_ind , _ = find_peaks(NumpyDatosCapturados,distance=400)


                # get the actual values using these indices
                
                maximosDbm = np.array(NumpyDatosCapturados[max_ind])  
                
                maxindices2,_ = find_peaks(maximosDbm)
                maximosDbm = maximosDbm[maxindices2]
                maximosDbm = maximosDbm.tolist()

                maximosDbmDefinitve=[]

                #print(maximosDbm)
                
                for i in maximosDbm:
                    
                    if i > -59.0:
                        maximosDbmDefinitve.append(i)
                        

                
                #print(maximosDbmDefinitve)
                
                # FINALLY, ONCE WE CALCULATED THE HARMONICS POWERS, WE CALCULATE THE THD AND WE CHANGE THE VALUE OF THE LABEL TO THE VALUE OF THE CALCULATED THD

                maximosW=self.convertDbmToW(maximosDbmDefinitve)

                THD = self.calculateTHD(maximosW)

                self.label_15.setText("THD= "+ str(THD))

                # If we are connected to EPICS server (to EPICS IOC)
                if self.EPICS_connected:

                    # we modify the register referring to the THD
                    self.Anritsu_SPECT_THD.put(THD)
                        
                

            # If the spectrum analyzer mode is not selected on the machine, it is notified by a pop-up window, a warning message.
            else:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])    

        # If we are not connected to the Anritsu machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])


##################################################################################################################################################


    # Function that plots the image of the monitoring of the maximum power in time (every 30 seconds)
    # It receives the parameter of the power from the thread that is performing said measurement in the background
    
    def plotMaxFreqPowerTimeAnritsu(self,power):

        # we modify the list of units measured so far in time (each unit of measurement represents 30 seconds)
        self.maxFreqTimeAnritsu.append(self.numeroAnritsu)
        self.numeroAnritsu +=1

        # we modify the list of powers measured so far in time we modify the list of units measured so far adding the power measured at that instant to the end of the list
        self.maxPowerTimeAnritsu.append(power)

        # and we show in real time the maximum power at that moment and the frequency where said power is located in the following labels
        maxfreq=self.anritsu.maxfreq
        
        self.label_37.setText(str(maxfreq)+"MHz")
        
        self.label_38.setText(str(power) + "dBm")

        # we create an image with the information previously collected in lists (as we saw before)

        plot2.clf()
        # Label for x-axis
        plot2.xlabel("Time Progress (each unit is 30 seconds)")
 
        # Label for y-axis
        plot2.ylabel("Maximum power (dBm)")
 
        # title of the plot
        plot2.title("Monitoring maximun power value progress")

        # we mark the points on the graph
        plot2.scatter(self.maxFreqTimeAnritsu,self.maxPowerTimeAnritsu)
        
        #I generate the image with the units of time and the powers offered by the machine
        
        plot2.plot(self.maxFreqTimeAnritsu,self.maxPowerTimeAnritsu) 
        plot2.savefig('./images/graphAnritsuTimeMax.jpg') # Relative address where you want the created image to be saved
        #plot.show()

        # If we are connected to EPICS server (to EPICS IOC)
        if self.EPICS_connected:

            # we modify the registers with the lists of the samples taken (units of time and list of maximum frequencies over time)
            self.Anritsu_SPECT_unitsTime.put(self.maxFreqTimeAnritsu)
            self.Anritsu_SPECT_MaximumPowers.put(self.maxPowerTimeAnritsu)
                        

        # And plot it into the graphicsView widget

        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtGui.QPixmap("./images/graphAnritsuTimeMax.jpg")
        self.scene.addPixmap(self.pixmap)
        self.graphicsView_2.setScene(self.scene)


##################################################################################################################################################

    # Function that modifies the value of the lcdnumber widget at the same time that we modify the value of the doubleSpinBox widget

    def moveDoubleSpinBox(self):
        self.lcdNumber.display(round(self.doubleSpinBox.value(),1))

##################################################################################################################################################

    # Function that modifies the value of the lcdnumber widget at the same time that we modify the value of the SpinBox widget

    def moveSpinBox(self):
        self.lcdNumber_2.display(self.spinBox.value())




########################################################################################################
########################################################################################################















########################################################################################################
############ AGILENT MANAGEMENT FUNCTIONS ##########################################################
########################################################################################################



    # Function that connects to the machine, or disconnects from it
    def conectarAgilent(self):

    
        # If we are not connected and we hit the connect checkBox to connect with the machine, it connects to the machine automatically and changes the icon to ON
        if self.checkBox_4.isChecked():
            # connects to the machine and grabs all the data from the machine to output and load into the GUI
            try:
                # connects to the machine creating an object of the class Agilent
                self.agilent= Agilent_MXA_N9020A()
                self.conectadoAgilent = True
                # Get all the data from the machine and load it into the GUI
                self.setInitialParamsAgilent() 
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./images/switch-on.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                self.checkBox_4.setIcon(icon)

                # If we are connected to EPICS server (to EPICS IOC)
                if self.EPICS_connected:

                    #We create the thread that will be in charge of monitoring all the EPICS records referring to Agilent so that EPICS interacts with the GUI
                    self.startEPICS_Agilent()

                
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.
            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[2])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[2])

                self.checkBox_4.setChecked(False)

        # If we are connected and we hit the connect checkBox to disconnect from the machine, it disconnects from the machine automatically and changes the icon to OFF
        else:
            try:
                # It disconnect from the machine
                self.agilent.disconnect()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./images/switch-off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.checkBox_4.setIcon(icon)
                # It sets all the data of the widgets to 0 (the default value)
                self.clearParamsAgilent()
                self.conectadoAgilent = False
            
            # if there is an exception (some failure) it is notified by a pop-up window, a warning message.
            except:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[2])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[2])
        


##################################################################################################################################################


    # Function that initializes all the GUI widgets to the values collected in the anritsu machine as soon as we connect to it

    def setInitialParamsAgilent(self):
        
        # Agilent library function that collects all machine data and stores it in agilent object attributes
        self.agilent.getInitialParamsAgilent()

        # We modify the state of the GUI widgets conveniently with the data obtained

        self.spinBox_2.setValue(int(self.agilent.referenceLevel))
        self.lcdNumber_6.display(self.agilent.referenceLevel)
        self.dial_12.value = self.agilent.finalFreq 
        self.dial_11.value = self.agilent.inicialFreq
        
        # if the machine is in spectrum analyzer mode, its rarioButton is checked
        if "SA" in self.agilent.instAgilent:
            self.radioButton_3.setChecked(True)
        

##################################################################################################################################################

    # Function that clear all the values of the widgets and load to them defaults values

    def clearParamsAgilent(self):

        self.spinBox_2.setValue(0)
        self.lcdNumber_6.display(0)
        self.dial_12.value = int(0)
        self.dial_11.value = int(0)
        
        # if the machine is in spectrum analyzer mode, its rarioButton is unchecked

        if "SA" in self.agilent.instAgilent:
            self.radioButton_3.setChecked(False)


##################################################################################################################################################

    # Function that selects the spectrum analyzer mode in the machine

    def setSpectrumAgilent(self):
        
        # if we are connected to the machine
        if self.conectadoAgilent:
            # we select the spectrum analyzer mode
            self.agilent.setSpectrum()

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:
                # we modify the register of the chosen mode to "SA" (spectrum analyzer)
                self.Agilent_Instrument_Choosed.put('SA')
                # and we tell the record that monitors all changes in Agilent, that there has been a change
                self.Agilent_SomeValueChanged.put(1)
        
        # if we are not connected to the machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])

            # and we reset the radioButton
            self.radioButton_3.setCheckable(False)
            self.radioButton_3.setCheckable(True)


##################################################################################################################################################

    # Function that establishes the selected parameters of the spectrum analyzer (in Agilent machine) in the GUI sending them to the machine modifying the parameters of said machine

    def setParamsSpectrumAgilent(self):

        # If the spectrum analyzer mode is selected
        if self.radioButton_3.isChecked():
            
            # we send the parameters established in the GUI to the Anritsu machine
            self.agilent.setParamsSpectrum(int(self.dial_11.value),int(self.dial_12.value),self.spinBox_2.value())
            
            # and we create the thread to start making measurements of the maximum power every 30 seconds
            self.startAgilent()

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # we modify the registers of the initial, final frequency and reference level of the spectrum analyzer
                self.Agilent_InitialFrequency.put(int(self.dial_11.value))
                self.Agilent_ReferenceLevel.put(self.spinBox_2.value())
                self.Agilent_FinalFrequency.put(int(self.dial_12.value))
                # and we tell the record that monitors all changes in Agilent, that there has been a change
                self.Agilent_SomeValueChanged.put(1)

        # If the spectrum analyzer mode is not selected, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])


##################################################################################################################################################

    # Function that plots the information collected by the spectrum analyzer at a given time in an image

    def plotImageAgilent(self):

        # If we are connected to the Agilent machine
        if self.conectadoAgilent:

            # And the spectrum analyzer mode is selected on the machine
            if self.radioButton_3.isChecked():

                # We create the image of the information trace of the machine
                self.agilent.plotInfoAgilent()

                # And plot it into the graphicsView widget
                self.scene = QtWidgets.QGraphicsScene()
                self.pixmap = QtGui.QPixmap("./images/graphAgilent.jpg")
                self.scene.addPixmap(self.pixmap)
                self.graphicsView_6.setScene(self.scene)

            # If the spectrum analyzer mode is not selected on the machine, it is notified by a pop-up window, a warning message.
            else:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])    

        # If we are not connected to the Agilent machine, it is notified by a pop-up window, a warning message.
        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])


##################################################################################################################################################
    

    # Function that plots the information collected by the spectrum analyzer in the range of 100 MHz and 1.5 GHz, at a given time in an image

    def plotLargeSpectrumAgilent(self):

        # If we are connected to the Agilent machine
        if self.conectadoAgilent:

            # And the spectrum analyzer mode is selected on the machine
            if self.radioButton_3.isChecked():
                

                # we save the values of the final and initial frequency that have the spectrum analyzer established at that instant of time
                freqIni = self.agilent.inicialFreq
                freqFin = self.agilent.finalFreq

                # we change the parameters of the spectrum analyzer so that it measures between 100 MHz and 1.5GHz
                self.agilent.setParamsSpectrum(100,1500,self.agilent.referenceLevel)
                time.sleep(0.5)

                # We create the image of the information trace of the machine
                self.agilent.plotInfoAgilent()

                # And plot it into the graphicsView widget
                self.scene = QtWidgets.QGraphicsScene()
                self.pixmap = QtGui.QPixmap("./images/graphAgilent.jpg")
                self.scene.addPixmap(self.pixmap)
                self.graphicsView_5.setScene(self.scene)

                # once the image is plotted, we return to change the parameters of the spectrum analyzer to those that had been established before making this measurement
                self.agilent.setParamsSpectrum(freqIni,freqFin,self.agilent.referenceLevel)


                # HERE WE CALCULATE THE HARMONICS POWERS

                NumpyDatosCapturados = np.array(self.agilent.datosCapturados)


                # determine the indices of the local maxima
                max_ind , _ = find_peaks(NumpyDatosCapturados,distance=400)


                # get the actual values using these indices
                
                maximosDbm = np.array(NumpyDatosCapturados[max_ind])  
                
                maxindices2,_ = find_peaks(maximosDbm)
                maximosDbm = maximosDbm[maxindices2]
                maximosDbm = maximosDbm.tolist()

                maximosDbmDefinitve=[]

                #print(maximosDbm)
                
                for i in maximosDbm:
                    
                    if i > -59.0:
                        maximosDbmDefinitve.append(i)
                        

                
                #print(maximosDbmDefinitve)
                
                # FINALLY, ONCE WE CALCULATED THE HARMONICS POWERS, WE CALCULATE THE THD AND WE CHANGE THE VALUE OF THE LABEL TO THE VALUE OF THE CALCULATED THD

                maximosW=self.convertDbmToW(maximosDbmDefinitve)

                THD = self.calculateTHD(maximosW)

                self.label_36.setText("THD= "+ str(THD))

                # If we are connected to EPICS server (to EPICS IOC)
                if self.EPICS_connected:
                    # we modify the register referring to the THD
                    self.Agilent_THD.put(THD)
                        


            # If the spectrum analyzer mode is not selected on the machine, it is notified by a pop-up window, a warning message.
            else:
                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[4])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[4])    

        # If we are not connected to the Agilent machine, it is notified by a pop-up window, a warning message.

        else:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[1])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[1])


##################################################################################################################################################

    # Function that plots the image of the monitoring of the maximum power in time (every 30 seconds)
    # It receives the parameter of the power from the thread that is performing said measurement in the background

    def plotMaxFreqPowerTimeAgilent(self,power):
        
        # we modify the list of units measured so far in time (each unit of measurement represents 30 seconds)
        self.maxFreqTimeAgilent.append(self.numeroAgilent)
        self.numeroAgilent += 1

        # we modify the list of powers measured so far in time we modify the list of units measured so far adding the power measured at that instant to the end of the list
        self.maxPowerTimeAgilent.append(power)

        # and we show in real time the maximum power at that moment and the frequency where said power is located in the following labels
        maxfreq=self.agilent.maxfreq

        self.label_39.setText(str(maxfreq)+"MHz")
        
        self.label_40.setText(str(power) + "dBm")

        # we create an image with the information previously collected in lists (as we saw before)

        plot.clf()
        # Label for x-axis
        plot.xlabel("Time Progress (each unit is 30 seconds)")
 
        # Label for y-axis
        plot.ylabel("Maximum power (dBm)")
 
        # title of the plot
        plot.title("Monitoring maximun power value progress")

        # we mark the points on the graph
        plot2.scatter(self.maxFreqTimeAgilent,self.maxPowerTimeAgilent)
        
        #I generate the image with the units of time and the powers offered by the machine
        
        plot.plot(self.maxFreqTimeAgilent,self.maxPowerTimeAgilent) 
        plot.savefig('./images/graphAgilentTimeMax.jpg') # Relative address where you want the created image to be saved
        #plot.show()

        # If we are connected to EPICS server (to EPICS IOC)
        if self.EPICS_connected:

            # we modify the registers with the lists of the samples taken (units of time and list of maximum frequencies over time)
            self.Agilent_SA_unitsTime.put(self.maxFreqTimeAgilent)
            self.Agilent_SA_MaximumPowers.put(self.maxPowerTimeAgilent)
                        
                        

        # And plot it into the graphicsView widget
        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtGui.QPixmap("./images/graphAgilentTimeMax.jpg")
        self.scene.addPixmap(self.pixmap)
        self.graphicsView_4.setScene(self.scene)

##################################################################################################################################################

    # Function that modifies the value of the lcdnumber widget at the same time that we modify the value of the SpinBox widget
    def moveSpinBoxAgilent(self):
        self.lcdNumber_6.display(self.spinBox_2.value())


########################################################################################################
########################################################################################################













########################################################################################################
############ FUNCTIONS FOR EPICS MANAGEMENT ############################################################
########################################################################################################
    
    #Function that is responsible for connecting to all the PVs (process variables), that is, to all the records of our EPICS IOC
    def connectEPICS(self):

        #try to connect to them
        try:

            # connects with the EPICS IOC records referring to the Anritsu MS2830A machine in the GUI
            self.Anritsu_SomeValueChanged = epics.PV('Anritsu:SomeValueChanged')
            
            self.Anritsu_SPECT_InitialFrequency = epics.PV('Anritsu:SPECT_InitialFrequency')
            self.Anritsu_SPECT_FinalFrequency= epics.PV('Anritsu:SPECT_FinalFrequency')
            self.Anritsu_SPECT_ReferenceLevel= epics.PV('Anritsu:SPECT_ReferenceLevel')
            self.Anritsu_SPECT_MaximumFrequency = epics.PV('Anritsu:SPECT_MaximumFrequency')
            self.Anritsu_SPECT_MaximumPower = epics.PV('Anritsu:SPECT_MaximumPower')
            self.Anritsu_SPECT_THD = epics.PV('Anritsu:SPECT_THD')
            self.Anritsu_SPECT_Frequencies = epics.PV('Anritsu:SPECT_Frequencies')
            self.Anritsu_SPECT_Powers = epics.PV('Anritsu:SPECT_Powers')
            self.Anritsu_SPECT_unitsTime = epics.PV('Anritsu:SPECT_unitsTime')
            self.Anritsu_SPECT_MaximumPowers = epics.PV('Anritsu:SPECT_MaximumPowers')
            self.Anritsu_SG_Power = epics.PV('Anritsu:SG_Power')
            self.Anritsu_SG_Frequency = epics.PV('Anritsu:SG_Frequency')
            self.Anritsu_SG_State = epics.PV('Anritsu:SG_State')
            self.Anritsu_Instrument_Choosed = epics.PV('Anritsu:Instrument_Choosed')
            


            # connects with the EPICS IOC records referring to the Agilent N9020A machine in the GUI
            self.Agilent_SomeValueChanged = epics.PV('Agilent:SomeValueChanged')
            
            self.Agilent_InitialFrequency = epics.PV('Agilent:InitialFrequency')
            self.Agilent_FinalFrequency = epics.PV('Agilent:FinalFrequency')
            self.Agilent_ReferenceLevel = epics.PV('Agilent:ReferenceLevel')
            self.Agilent_MaximumFrequency = epics.PV('Agilent:MaximumFrequency')
            self.Agilent_MaximumPower = epics.PV('Agilent:MaximumPower')
            self.Agilent_THD = epics.PV('Agilent:THD')
            self.Agilent_SA_Frequencies = epics.PV('Agilent:SA_Frequencies')
            self.Agilent_SA_Powers = epics.PV('Agilent:SA_Powers')
            self.Agilent_SA_unitsTime = epics.PV('Agilent:SA_unitsTime')
            self.Agilent_SA_MaximumPowers = epics.PV('Agilent:SA_MaximumPowers')
            self.Agilent_Instrument_Choosed = epics.PV('Agilent:Instrument_Choosed')


            # connects with the EPICS IOC records referring to the BLAS simulated values in the GUI
            self.BLAS_SomeValueChanged = epics.PV('BLAS:SomeValueChanged')
            
            self.BLAS_waterTemperature = epics.PV('BLAS:waterTemperature')
            self.BLAS_waterFlow = epics.PV('BLAS:waterFlow')
            self.BLAS_IlockFlow = epics.PV('BLAS:IlockFlow')
            self.BLAS_Fail0 = epics.PV('BLAS:Fail0')
            self.BLAS_Fail1 = epics.PV('BLAS:Fail1')
            self.BLAS_PD_MI = epics.PV('BLAS:PD_MI')
            self.BLAS_IlockPatchPanel = epics.PV('BLAS:IlockPatchPanel')
            self.BLAS_VSEL0 = epics.PV('BLAS:VSEL0')
            self.BLAS_VSEL1 = epics.PV('BLAS:VSEL1')
            self.BLAS_12V_DC = epics.PV('BLAS:12V_DC')
            self.BLAS_DriverStart = epics.PV('BLAS:DriverStart')
            self.BLAS_AmplifierStart = epics.PV('BLAS:AmplifierStart')

            # we initialize the records that monitor changes in all records to 0
            # 0 = there are no changes in IOC records
            # 1 = there are changes in IOC records
            self.Anritsu_SomeValueChanged.put(0)
            self.Agilent_SomeValueChanged.put(0)
            self.BLAS_SomeValueChanged.put(0)

            # EPICS has been correctly connected
            self.EPICS_connected = True


            # If those record has value None, it means that we have not connected with the EPICS IOC
            # so we generate an exception so that the code of the exception is executed
            if self.Anritsu_SomeValueChanged.value == None or self.Agilent_SomeValueChanged.value == None:
                raise

        # if there are any exceptions or errors, nothing is done and the GUI is run by itself, without connecting to any EPICS server. This is done so that it can work anyway.
        except:
            self.EPICS_connected = False
            
            
            


##################################################################################################################################################
    
    # Function that if it receives a signal with value 1 (meaning that there have been changes in the IOC records referring to the Anritsu machine),
    # it modifies in the GUI those records that have changed in the EPICS IOC
    def setEpicsAnritsu(self,changed):
        
        # If the value of the signal it receives is 1 (some record's value changed)
        if changed == 1:

            # we check what values have changed in the EPICS with respect to those of Anritsu's attributes in the GUI
            # and those records that have changed, we modify the values of the Anritsu attributes in the GUI with these new values from the EPICS IOC
            # and we also modify the state of the corresponding widgets in the GUI accordingly
            
            if int(self.Anritsu_SPECT_InitialFrequency.value) != int(self.anritsu.inicialFreq):
                self.anritsu.inicialFreq = int(self.Anritsu_SPECT_InitialFrequency.value)
                self.dial.value = self.anritsu.inicialFreq

            if int(self.Anritsu_SPECT_FinalFrequency.value) != int(self.anritsu.finalFreq):
                self.anritsu.finalFreq = int(self.Anritsu_SPECT_FinalFrequency.value)
                self.dial_3.value = self.anritsu.finalFreq
            
            if int(self.Anritsu_SPECT_ReferenceLevel.value) != int(self.anritsu.referenceLevel):
                self.anritsu.referenceLevel = int(self.Anritsu_SPECT_ReferenceLevel.value)
                self.spinBox.setValue(self.anritsu.referenceLevel)

            if float(self.Anritsu_SG_Power.value) != float(self.anritsu.power):
                self.anritsu.power = float(self.Anritsu_SG_Power.value)
                self.doubleSpinBox.setValue(self.anritsu.power)    
        
            if int(self.Anritsu_SG_Frequency.value) != int(self.anritsu.frequency):
                self.anritsu.frequency = int(self.Anritsu_SG_Frequency.value)
                self.dial_2.value = self.anritsu.frequency 

            if str(self.anritsu.instAnritsu) not in str(self.Anritsu_Instrument_Choosed.value) :
                
                if "SG" in str(self.Anritsu_Instrument_Choosed.value):
                    self.anritsu.instAnritsu = 'SG'
                    self.radioButton.setChecked(True)

                elif "SPECT" in str(self.Anritsu_Instrument_Choosed.value):
                    self.anritsu.instAnritsu = 'SPECT'
                    self.radioButton_2.setChecked(True)


            if int(self.Anritsu_SG_State.value) != int(self.anritsu.state):

                if int(self.Anritsu_SG_State.value) == 1:
                    self.anritsu.state =1
                    self.checkBox_2.setChecked(True)
                    # and change the icon to power on
                    self.checkBox_2.setIcon(QtGui.QIcon("./images/power.png"))
                elif int(self.Anritsu_SG_State.value) == 0:
                    self.anritsu.state = 0
                    self.checkBox_2.setChecked(False)
                    # and change the icon to power off
                    self.checkBox_2.setIcon(QtGui.QIcon("./images/power-off.png"))

            # When we finish checking everything and changing what corresponds
            # we put the record that monitors changes in Anritsu's records back to 0 (that is, there are no pending changes anymore)
            self.Anritsu_SomeValueChanged.put(0)


##################################################################################################################################################

    # Function that if it receives a signal with value 1 (meaning that there have been changes in the IOC records referring to the Agilent machine),
    # it modifies in the GUI those records that have changed in the EPICS IOC
    def setEpicsAgilent(self,changed):
        
        # If the value of the signal it receives is 1 (some record's value changed)
        if changed == 1:

            # we check what values have changed in the EPICS with respect to those of Agilent's attributes in the GUI
            # and those records that have changed, we modify the values of the Agilent attributes in the GUI with these new values from the EPICS IOC
            # and we also modify the state of the corresponding widgets in the GUI accordingly

            if int(self.Agilent_InitialFrequency.value) != int(self.agilent.inicialFreq):
                self.agilent.inicialFreq = int(self.Agilent_InitialFrequency.value)
                self.dial_11.value = self.agilent.inicialFreq

            if int(self.Agilent_FinalFrequency.value) != int(self.agilent.finalFreq):
                self.agilent.finalFreq = int(self.Agilent_FinalFrequency.value)
                self.dial_12.value = self.agilent.finalFreq
            
            if int(self.Agilent_ReferenceLevel.value) != int(self.agilent.referenceLevel):
                self.agilent.referenceLevel = int(self.Agilent_ReferenceLevel.value)
                self.spinBox_2.setValue(self.agilent.referenceLevel)

            if str(self.agilent.instAgilent) not in str(self.Agilent_Instrument_Choosed.value) :
                
                if "SA" in str(self.Agilent_Instrument_Choosed.value):
                    self.agilent.instAgilent = 'SA'
                    self.radioButton_3.setChecked(True)

            # When we finish checking everything and changing what corresponds
            # we put the record that monitors changes in Agilent's records back to 0 (that is, there are no pending changes anymore)
            self.Agilent_SomeValueChanged.put(0)



##################################################################################################################################################

    # Function that if it receives a signal with value 1 (meaning that there have been changes in the IOC records referring to the BLAS API),
    # it modifies in the GUI those records that have changed in the EPICS IOC

    # IT IS NOT NECESSARY RIGHT NOW, SINCE THE VALUES OF THE BLAS ARE COLLECTED FROM THE API, AND THESE VALUES ARE RANDOM
    # WHEN THE BLAS SIGNALS ARE CONNECTED TO THE RASPBERRY IN THE FUTURE, THIS SHOULD BE CHANGED
    def setEpicsBLAS(self,changed):
        pass


########################################################################################################
########################################################################################################














########################################################################################################
############ FUNCTIONS FOR BLAS MANAGEMENT ############################################################
########################################################################################################

    # Function that receives the information (monitored by the created thread) of the simulated BLAS input and output signals through an API.
    def setBlas(self,datos):
        
        # If the length of the list that we receive with the information is 0, it means that it has not connected with the API, so we show a warning popup
        if len(datos)==0:
            if self.comboBox.currentIndex() == 1:
                QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[5])
            else:
                QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[5])

            # we stop the thread that should be monitoring the API
            self.stopBlas()
            # we uncheck the checkBox
            self.checkBox_3.setChecked(False)

            # and we change the icon back to OFF
            self.checkBox_3.setIcon(QtGui.QIcon("./images/switch-off.png"))

        # if we have successfully connected to the API and received information
        else:    
            
            # we transform the received information to the corresponding data types

            temp = float(datos[0])
            #flujo = float(datos[1])
            ilockFlow= float(datos[2])
            fail0= float(datos[3])
            fail1= float(datos[4])
            pd_mi= float(datos[5])
            ilockPatchPanel=float(datos[6])
            vsel0 = float(datos[7])
            vsel1 = float(datos[8])

            # and we send this information to the GUI by modifying the value and state of the GUI widgets

            self.progressBar.setValue(int(float(datos[0])))
            self.label_3.setText(str(datos[0])+"ºC")
            self.progressBar_2.setValue(int(float(datos[1])))
            self.label_16.setText(str(datos[1])+"l/s")
            self.dial_4.updateValue(ilockFlow)
            self.dial_5.updateValue(fail0)
            self.dial_6.updateValue(fail1)
            self.dial_7.updateValue(pd_mi)
            self.dial_10.updateValue(ilockPatchPanel)
            self.dial_9.updateValue(vsel0)
            self.dial_8.updateValue(vsel1)

            # If we are connected to EPICS server (to EPICS IOC)
            if self.EPICS_connected:

                # # we modify the registers referring to the values offered by the BLAS API
                self.BLAS_waterTemperature.put(temp)
                self.BLAS_waterFlow.put(float(datos[1]))
                self.BLAS_IlockFlow.put(ilockFlow)
                self.BLAS_Fail0.put(fail0)
                self.BLAS_Fail1.put(fail1)
                self.BLAS_PD_MI.put(pd_mi)
                self.BLAS_IlockPatchPanel.put(ilockPatchPanel)
                self.BLAS_VSEL0.put(vsel0)
                self.BLAS_VSEL1.put(vsel1)
                        



            # HERE I DEFINE DIFFERENT SITUATIONS THAT MAY OCCUR DEPENDING ON THE VALUES OF THE INFORMATION RECEIVED, SHOWING POP-UP WARNING WINDOWS IF THERE IS ANY PROBLEM IN THE BLAS

            if temp< 65 and ilockFlow== 12 and fail0==0 and fail1==0 and pd_mi==7.6 and ilockPatchPanel==12 and vsel0 >= 0 and vsel0 <= 5 and vsel1 >= 0 and vsel1 <= 5:
                self.lcdNumber_3.display(12)
                self.lcdNumber_4.display(12)
                self.lcdNumber_5.display(12)

            elif temp< 65 and ilockFlow== 12 and fail0==5 and fail1==5 and pd_mi==0 and ilockPatchPanel==0 and vsel0 >= 0 and vsel0 <= 5 and vsel1 >= 0 and vsel1 <= 5:
                self.lcdNumber_3.display(12)
                self.lcdNumber_4.display(0)
                self.lcdNumber_5.display(12)

                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[6])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[6])
            
            elif temp< 65 and ilockFlow== 0 and fail0==5 and fail1==5 and pd_mi==7.6 and ilockPatchPanel==12 and vsel0 >= 0 and vsel0 <= 5 and vsel1 >= 0 and vsel1 <= 5:
                self.lcdNumber_3.display(12)
                self.lcdNumber_4.display(12)
                self.lcdNumber_5.display(0)

                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[7])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[7])

            elif temp< 65 and ilockFlow== 12 and fail0==5 and fail1==5 and pd_mi==0 and ilockPatchPanel==12 and vsel0 >= 0 and vsel0 <= 5 and vsel1 >= 0 and vsel1 <= 5:
                self.lcdNumber_3.display(12)
                self.lcdNumber_4.display(12)
                self.lcdNumber_5.display(12)

                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[8])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[8])

            elif temp > 65 and ilockFlow== 12 and fail0==0 and fail1==0 and pd_mi==7.6 and ilockPatchPanel==12 and vsel0 >= 0 and vsel0 <= 5 and vsel1 >= 0 and vsel1 <= 5:
                self.lcdNumber_3.display(12)
                self.lcdNumber_4.display(12)
                self.lcdNumber_5.display(12)

                if self.comboBox.currentIndex() == 1:
                    QtWidgets.QMessageBox.warning(None,self.traducedMessagesWindows[0],self.traducedMessagesWindows[9])
                else:
                    QtWidgets.QMessageBox.warning(None,self.messagesWindows[0],self.messagesWindows[9])



##################################################################################################################################################           
        
    # Function that initialize the thread that is responsible for monitoring the BLAS

    def connectBlas(self):

        # If we are not connected to the API that simulates the BLAS and we hit the connect checkBox to connect with it, it connects and changes the icon to ON
        if self.checkBox_3.isChecked():
            
            # We start with the simulation of the BLAS
            self.startBlas()

            # And we change the icon of the checkBox to ON
            self.checkBox_3.setIcon(QtGui.QIcon("./images/switch-on.png"))
            
        # If we are connected to the API that simulates the BLAS and we hit the connect checkBox to disconnect with it, it disconnects and changes the icon to OFF
        # And sets all the widget's data in the GUI to default values
        else:
            self.checkBox_3.setIcon(QtGui.QIcon("./images/switch-off.png"))

            # stops the thread
            self.stopBlas()
            self.lcdNumber_3.display(0)
            self.lcdNumber_4.display(0)
            self.lcdNumber_5.display(0)
            self.dial_4.updateValue(0)
            self.dial_5.updateValue(0)
            self.dial_6.updateValue(0)
            self.dial_7.updateValue(0)
            self.dial_10.updateValue(0)
            self.dial_9.updateValue(0)
            self.dial_8.updateValue(0)
            self.progressBar.setValue(0)
            self.progressBar_2.setValue(0)
            self.label_3.setText(str(0)+"ºC")
            self.label_16.setText(str(0)+"l/s")

        


########################################################################################################
########################################################################################################













##########################################################################################################################
############ FUNCTIONS FOR HANDLING MULTITHREADING IN ANRITSU ##########################################################
##########################################################################################################################


    # Function that creates and runs the thread that will monitor the maximum power of the Anritsu machine every 30 seconds
    def startAnritsu(self):
        self.threadAnritsu = ThreadClass(parent=None, anritsu=self.anritsu)
        self.threadAnritsu.start()

        # The power measured at each instant of time is sent to the function "plotMaxFreqPowerTimeAnritsu"
        self.threadAnritsu.any_signal.connect(self.plotMaxFreqPowerTimeAnritsu)


#######     #########       #############       ##########          ##########      ############      ##########

    # Function that stops the created thread
    # In principle we do not need a stop of the thread because we want it to work continuously
    def stopAnritsu(self):
        self.threadAnritsu.stop()


##########################################################################################################################
##########################################################################################################################













##########################################################################################################################
############ FUNCTIONS FOR HANDLING MULTITHREADING IN AGILENT ##########################################################
##########################################################################################################################

    # Function that creates and runs the thread that will monitor the maximum power of the Agilent machine every 30 seconds
    def startAgilent(self):
        self.threadAgilent = ThreadClassAgilent(parent=None, agilent=self.agilent)
        self.threadAgilent.start()

        # The power measured at each instant of time is sent to the function "plotMaxFreqPowerTimeAnritsu"
        self.threadAgilent.any_signal.connect(self.plotMaxFreqPowerTimeAgilent)


#######     #########       #############       ##########          ##########      ############      ##########

    # Function that stops the created thread
    # In principle we do not need a stop of the thread because we want it to work continuously
    def stopAnritsu(self):
        self.threadAgilent.stop()

##########################################################################################################################
##########################################################################################################################














##########################################################################################################################
############ FUNCTIONS FOR HANDLING MULTITHREADING IN THE BLAS ##########################################################
##########################################################################################################################

    # Function that creates and runs the thread that will monitor the values collected from the API that simulates the input and output signals of the BLAS every 5 seconds
    def startBlas(self):
        self.threadBlas = ThreadClassBlas(parent=None)
        self.threadBlas.start()

        # The values (in a list) measured at each instant of time is sent to the function "setBlas"
        self.threadBlas.any_signal.connect(self.setBlas)

#######     #########       #############       ##########          ##########      ############      ##########


    # Function that stops the created thread
    def stopBlas(self):
        self.threadBlas.stop()


##########################################################################################################################
##########################################################################################################################














##########################################################################################################################
############ FUNCTIONS FOR HANDLING MULTITHREADING FOR EPICS ##########################################################
##########################################################################################################################

    # Function that creates and executes the thread that will monitor if there are changes or not in the EPICS IOC records referring to Anritsu
    def startEPICS_Anritsu(self):
        self.threadEPICS_Anritsu = ThreadClassEPICSAnritsu(parent=None , Anritsu_SomeValueChanged=self.Anritsu_SomeValueChanged)
        self.threadEPICS_Anritsu.start()

        # If there have been changes in any Anritsu record, a signal with value 1 is sent to the "setEpicsAnritsu" function so that it is executed
        self.threadEPICS_Anritsu.any_signal.connect(self.setEpicsAnritsu)

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that stops the created thread
    def stopEPICS_Anritsu(self):
        self.threadEPICS_Anritsu.stop()


##########################################################################################################################

    # Function that creates and executes the thread that will monitor if there are changes or not in the EPICS IOC records referring to Agilent
    def startEPICS_Agilent(self):
        self.threadEPICS_Agilent = ThreadClassEPICSAgilent(parent=None , Agilent_SomeValueChanged=self.Agilent_SomeValueChanged)
        self.threadEPICS_Agilent.start()

        # If there have been changes in any Agilent record, a signal with value 1 is sent to the "setEpicsAgilent" function so that it is executed
        self.threadEPICS_Agilent.any_signal.connect(self.setEpicsAgilent)
        
#######     #########       #############       ##########          ##########      ############      ##########
    
    # Function that stops the created thread
    def stopEPICS_Agilent(self):
        self.threadEPICS_Agilent.stop()


##########################################################################################################################

    # Function that creates and executes the thread that will monitor if there are changes or not in the EPICS IOC records referring to the BLAS API
    def startEPICS_BLAS(self):
        self.threadEPICS_BLAS = ThreadClassEPICS_BLAS(parent=None , BLAS_SomeValueChanged = self.BLAS_SomeValueChanged)
        self.threadEPICS_BLAS.start()

        # If there have been changes in any BLAS API record, a signal with value 1 is sent to the "setEpicsBLAS" function so that it is executed
        self.threadEPICS_BLAS.any_signal.connect(self.setEpicsBLAS)

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that stops the created thread
    def stopEPICS_BLAS(self):
        self.threadEPICS_BLAS.stop()


##########################################################################################################################
##########################################################################################################################















########################################################################################################
########################################################################################################

########################################################################################################
############ FUNCTIONS TO MAKE THE GUI MULTI-LANGUAGE ONLINE AND OFFLINE ################################
########################################################################################################

    # Function that assigns all the ToolTips passed as an attribute in a list to the objects of the list "toolTipsObjects" which are the GUI widgets
    def setToolTips(self,tooltips):
        
        for i,j in zip(self.toolTipsObjects,tooltips):
            i.setToolTip(j)


##########################################################################################################################

    # Function that collects the text of all the Widgets of the GUI to be translated in a list
    def getCompleteText(self):

        text = []

        # we collect in text of all the labels of the list "allLabels"
        for i in self.allLabels:
            text.append(i.text())

        # we collect in text of all the pushButtons of the list "allPushButtons"
        for i in self.allPushButtons:
            text.append(i.text())

        # we collect in text of all the radioButtons of the list "allRadioButtons"
        for i in self.allRadioButtons:
            text.append(i.text())

        return text


##########################################################################################################################

    # Function that is responsible for modifying the text of all the Widgets of the GUI to be translated
    def setCompleteText(self, traduccion):

        # we copy de translation list to handle it more easily
        trad = traduccion.copy()

        # we set the text (with the translated text) of all the labels of the list "allLabels" 
        for i in self.allLabels:
            i.setText(trad[0])
            trad.pop(0)

        # we set the text (with the translated text) of all the pushButtons of the list "allPushButtons" 
        for i in self.allPushButtons:
            i.setText(trad[0])
            trad.pop(0)

        # we set the text (with the translated text) of all the radioButtons of the list "allRadioButtons" 
        for i in self.allRadioButtons:
            i.setText(trad[0])
            trad.pop(0)


##########################################################################################################################

# I have done it this way to make it easy when adding more languages
    
    # Function that translates a message online and offline in case there is no internet
    def traducir(self,mensaje):

        traduccion=""

        # If Spanish has been selected in the comboBox
        if self.comboBox.currentIndex() == 1:# Let's do the translation into Spanish:
            # If we have internet, the translation will be done with the Google translator
            try:
                translator = Translator()

                translation = translator.translate(mensaje, dest="es")
                traduccion = translation.text
                
            # If not, it will be done offline with argosmodel
            except:
                from argostranslate import package, translate

                package.install_from_path('./language/en_es.argosmodel') # Address where the dictionary file is located (IMPORTANT)
                installed_languages = translate.get_installed_languages()

                # installed_languages[0] = inglés
                # installed_languages[1] = español

                translation_en_es = installed_languages[0].get_translation(installed_languages[1])

                traduccion = translate=translation_en_es.translate(mensaje)
            
            return traduccion
        # If English has been selected in the comboBox, we do nothing (it is not necessary to translate back to english)
        else:
            pass

##########################################################################################################################
    
    # Function which declares the id of the comboBox to 1 and calls the "translate" function to perform the full GUI translation
    def idComboBox1(self):
        self.indexComboBox = 1
        self.traduce(self.comboBox)

##########################################################################################################################

    # Function which declares the id of the comboBox to 2 and calls the "translate" function to perform the full GUI translation
    def idComboBox2(self):
        self.indexComboBox = 2
        self.traduce(self.comboBox_2)

##########################################################################################################################

    # Function which declares the id of the comboBox to 3 and calls the "translate" function to perform the full GUI translation
    def idComboBox3(self):
        self.indexComboBox = 3
        self.traduce(self.comboBox_3)

##########################################################################################################################

    # Function that translates all the text of the GUI widgets (including Tooltips and warning popup messages)
    def traduce(self,comboBox):
        
        traduccion =[]
        tooltips =[]

        # If Spanish has been selected in the comboBox passed as atribute to the function
        if comboBox.currentIndex() == 1:# Let's do the translation into Spanish:
            # If we have internet, the translation will be done with the Google translator
            self.traducedMessagesWindows.clear()
            try:
                
                translator = Translator()

                # the text of the GUI widgets is translated
                for i in self.text:
                    translation = translator.translate(i, dest="es")
                    traduccion.append(translation.text) 
                
                # ToolTips are translated
                for i in self.toolTips:
                    translation = translator.translate(i, dest="es")
                    tooltips.append(translation.text) 
                
                # warning popup messages are translated
                for i in self.messagesWindows:
                    translation = translator.translate(i, dest="es")
                    self.traducedMessagesWindows.append(translation.text)
                
               
                
                
            # If not, it will be done offline with argosmodel
            except:
                
            
                from argostranslate import package, translate

                package.install_from_path('./language/en_es.argosmodel') # Address where the dictionary file is located (IMPORTANT)
                installed_languages = translate.get_installed_languages()

                # installed_languages[0] = inglés
                # installed_languages[1] = español

                translation_en_es = installed_languages[0].get_translation(installed_languages[1])

                # the text of the GUI widgets is translated
                for i in self.text:
                    translate=translation_en_es.translate(i) # we collect the result of the translation
                    traduccion.append(translate)
                
                # ToolTips are translated
                for i in self.toolTips:
                    translate=translation_en_es.translate(i) # we collect the result of the translation
                    tooltips.append(translate)

                # warning popup messages are translated
                for i in self.messagesWindows:
                    translate=translation_en_es.translate(i) # we collect the result of the translation
                    self.traducedMessagesWindows.append(translate)
            

            # Because comboBox widgets react to "currentIndexChanged" signals

            # To keep the 3 GUI comboBoxes coordinated, we must block the signals of the other 2 comboBoxes (in order to modify the index of the other 2 comboBoxes)
            # while modifying the index of the comboBox we are changing. If we don't do it like this,
            # the functions to which the other 2 comboBoxes are connected will be executed, making the translation process redundant and very slow.

            # If the index of the comboBox that has been modified is 1, the signals of the other 2 comboBoxes (2 and 3) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            if self.indexComboBox == 1:
                self.comboBox_2.blockSignals(True)
                self.comboBox_3.blockSignals(True)

                self.comboBox_2.setCurrentIndex(1)
                self.comboBox_3.setCurrentIndex(1)

                self.comboBox_2.blockSignals(False)
                self.comboBox_3.blockSignals(False)
            
            # If the index of the comboBox that has been modified is 2, the signals of the other 2 comboBoxes (1 and 3) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            elif self.indexComboBox == 2:
                self.comboBox.blockSignals(True)
                self.comboBox_3.blockSignals(True)

                self.comboBox.setCurrentIndex(1)
                self.comboBox_3.setCurrentIndex(1)

                self.comboBox.blockSignals(False)
                self.comboBox_3.blockSignals(False)
            
            # If the index of the comboBox that has been modified is 3, the signals of the other 2 comboBoxes (1 and 2) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            else:
                self.comboBox.blockSignals(True)
                self.comboBox_2.blockSignals(True)

                self.comboBox.setCurrentIndex(1)
                self.comboBox_2.setCurrentIndex(1)

                self.comboBox.blockSignals(False)
                self.comboBox_2.blockSignals(False)

            # finally we change the flags that are located in front of the comboBox widgets for Spanish flags
            self.label.setPixmap(QtGui.QPixmap('./images/spanish.png'))
            self.label_23.setPixmap(QtGui.QPixmap('./images/spanish.png'))
            self.label_34.setPixmap(QtGui.QPixmap('./images/spanish.png'))

            # Executing these functions, all texts, Tooltips and warning popup messages will be changed to Spanish in the GUI.
            self.setCompleteText(traduccion)
            self.setToolTips(tooltips)
        
        # If Eglish has been selected in the comboBox passed as atribute to the function
        else:

            # If the index of the comboBox that has been modified is 1, the signals of the other 2 comboBoxes (2 and 3) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            if self.indexComboBox == 1:
                self.comboBox_2.blockSignals(True)
                self.comboBox_3.blockSignals(True)

                self.comboBox_2.setCurrentIndex(0)
                self.comboBox_3.setCurrentIndex(0)

                self.comboBox_2.blockSignals(False)
                self.comboBox_3.blockSignals(False)
            
            # If the index of the comboBox that has been modified is 2, the signals of the other 2 comboBoxes (1 and 3) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            elif self.indexComboBox == 2:
                self.comboBox.blockSignals(True)
                self.comboBox_3.blockSignals(True)

                self.comboBox.setCurrentIndex(0)
                self.comboBox_3.setCurrentIndex(0)

                self.comboBox.blockSignals(False)
                self.comboBox_3.blockSignals(False)

            # If the index of the comboBox that has been modified is 3, the signals of the other 2 comboBoxes (1 and 2) are blocked,
            # then the indexes of these comboBoxes are modified and then the signals of these 2 comboBoxes are activated again to continue to be pending the signals to changes.
            else:
                self.comboBox.blockSignals(True)
                self.comboBox_2.blockSignals(True)

                self.comboBox.setCurrentIndex(0)
                self.comboBox_2.setCurrentIndex(0)

                self.comboBox.blockSignals(False)
                self.comboBox_2.blockSignals(False)


             # finally we change the flags that are located in front of the comboBox widgets for British flags
            self.label.setPixmap(QtGui.QPixmap('./images/uk.png'))
            self.label_23.setPixmap(QtGui.QPixmap('./images/uk.png'))
            self.label_34.setPixmap(QtGui.QPixmap('./images/uk.png'))

            # Executing these functions, all texts, Tooltips and warning popup messages will be changed to English in the GUI.
            self.setCompleteText(self.text)
            self.setToolTips(self.toolTips)
            
########################################################################################################
########################################################################################################









########################################################################################################
############ MORE GENERIC FUNCTIONS ###################################################################
########################################################################################################

    # Function that is responsible for converting all the elements of a list from Dbm to W
    def convertDbmToW(self,datos):

        datosW=[]
        datosMW=[]

        # here we convert from Dbm to mW
        for i in datos:
            datosMW.append(float(10**(i/10)))
        
        # here we convert from mW to W
        for i in datosMW:
            datosW.append(float(i)/1000)

        #print(datosW)
        return datosW

##########################################################################################################################

    # Function that calculates the THD value 
    def calculateTHD(self,datos):
        return float(sum(datos)/max(datos))

########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
######################################                    ##############################################
###################################### END OF GUI's CLASS ##############################################
######################################                    ##############################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################













########################################################################################################
############ CLASS FOR MANAGEMENT OF MULTITHREADING FOR ANRITSU ##########################################
########################################################################################################

# class that is responsible for creating the threads for managing and monitoring the maximum power of the Anritsu machine (in spectrum analyzer mode)

class ThreadClass(QtCore.QThread):

    # we define a signal that will handle a float number (the maximum power each time)
    any_signal = QtCore.pyqtSignal(float)

    # in the constructor we define the object of the class that will point through a pointer to the object of the AnritsuMS2830A class 
    # (object created in the GUI class that handles all the functions of the library)
    def __init__(self, parent=None, anritsu=None):
        super(ThreadClass, self).__init__(parent)
        self.is_running = True
        self.anritsu = anritsu

########################################################################################################

    # Function that is responsible for calling the getMaxFreqPower function to calculate said value
    # and emits the value of said maximum power through the signal defined at the beginning of the class
    # all this is done indefinitely every 30 seconds
    def run(self):
        while (True):
            power=self.anritsu.getMaxFreqPower()
            time.sleep(0.01)
            self.any_signal.emit(power)
            time.sleep(30)

########################################################################################################

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()



########################################################################################################
########################################################################################################








########################################################################################################
############ CLASS FOR MANAGEMENT OF MULTITHREADING FOR AGILENT #######################################################
########################################################################################################

# class that is responsible for creating the threads for managing and monitoring the maximum power of the agilent machine (in spectrum analyzer mode)

class ThreadClassAgilent(QtCore.QThread):

    # we define a signal that will handle a float number (the maximum power each time)
    any_signal = QtCore.pyqtSignal(float)

    # in the constructor we define the object of the class that will point through a pointer to the object of the AgilentN9020A class 
    # (object created in the GUI class that handles all the functions of the library)
    def __init__(self, parent=None, agilent=None):
        super(ThreadClassAgilent, self).__init__(parent)
        self.is_running = True
        self.agilent = agilent

########################################################################################################

    # Function that is responsible for calling the getMaxFreqPower function to calculate said value
    # and emits the value of said maximum power through the signal defined at the beginning of the class
    # all this is done indefinitely every 30 seconds
    def run(self):
        while (True):
            power=self.agilent.getMaxFreqPower()
            time.sleep(0.01)
            self.any_signal.emit(power)
            time.sleep(30)

########################################################################################################

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()



########################################################################################################
########################################################################################################








########################################################################################################
############ CLASS FOR MANAGEMENT OF MULTITHREADING FOR EPICS #######################################################
########################################################################################################

# class that is responsible for creating the threads for managing and monitoring any changes to the EPICS IOC records
# each 2 seconds. A 1 will be issued if there is any change in any record of the Anritsu machine
# If there is no change, nothing will be issued

class ThreadClassEPICSAnritsu(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    # In the constructor we define a variable that will point through a pointer 
    # to the PV (record) "Anritsu_SomeValueChanged" to monitor if any EPICS IOC record modifies its value.
    def __init__(self, parent=None, Anritsu_SomeValueChanged=None):
        super(ThreadClassEPICSAnritsu, self).__init__(parent)
        self.is_running = True
        self.Anritsu_SomeValueChanged = Anritsu_SomeValueChanged

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for emitting a 1 through the signal defined at the beginning of the class
    # if the value of the PV (record) "Anritsu_SomeValueChanged" of our EPICS IOCS is 1 
    # (that is, if there has been any record related to the Anritsu machine has been modified)
    # all this is done indefinitely every 2 seconds
    def run(self):
        while (True):

            if int(self.Anritsu_SomeValueChanged.value) == 1:
                recordAnritsuChanged=1
                self.any_signal.emit(recordAnritsuChanged)

            time.sleep(2)

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()


##################################################################################################################


# class that is responsible for creating the threads for managing and monitoring any changes to the EPICS IOC records
# each 2 seconds. A 1 will be issued if there is any change in any record of the Agilent machine
# If there is no change, nothing will be issued

class ThreadClassEPICSAgilent(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    # In the constructor we define a variable that will point through a pointer 
    # to the PV (record) "Agilent_SomeValueChanged" to monitor if any EPICS IOC record modifies its value.
    def __init__(self, parent=None, Agilent_SomeValueChanged=None):
        super(ThreadClassEPICSAgilent, self).__init__(parent)
        self.is_running = True
        self.Agilent_SomeValueChanged = Agilent_SomeValueChanged

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for emitting a 1 through the signal defined at the beginning of the class
    # if the value of the PV (record) "Agilent_SomeValueChanged" of our EPICS IOCS is 1 
    # (that is, if there has been any record related to the Agilent machine has been modified)
    # all this is done indefinitely every 2 seconds
    def run(self):
        while (True):
            if int(self.Agilent_SomeValueChanged.value) == 1:
                recordAgilentChanged=1
                self.any_signal.emit(recordAgilentChanged)

            time.sleep(2)

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()



##################################################################################################################


# class that is responsible for creating the threads for managing and monitoring any changes to the EPICS IOC records
# each 2 seconds. A 1 will be issued if there is any change in any record of the BLAS API
# If there is no change, nothing will be issued

class ThreadClassEPICS_BLAS(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(float)

    # In the constructor we define a variable that will point through a pointer 
    # to the PV (record) "BLAS_SomeValueChanged" to monitor if any EPICS IOC record modifies its value.
    def __init__(self, parent=None, BLAS_SomeValueChanged=None):
        super(ThreadClassEPICS_BLAS, self).__init__(parent)
        self.is_running = True
        self.BLAS_SomeValueChanged = BLAS_SomeValueChanged

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for emitting a 1 through the signal defined at the beginning of the class
    # if the value of the PV (record) "BLAS_SomeValueChanged" of our EPICS IOCS is 1 
    # (that is, if there has been any record related to the BLAS API has been modified)
    # all this is done indefinitely every 2 seconds
    def run(self):
        while (True):
            if int(self.BLAS_SomeValueChanged.value) == 1:
                recordBLASChanged=1
                self.any_signal.emit(recordBLASChanged)

            time.sleep(2)

#######     #########       #############       ##########          ##########      ############      ##########

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()



########################################################################################################
########################################################################################################








########################################################################################################
############ CLASS FOR HANDLING MULTITHREADING FOR BLAS #######################################################
########################################################################################################


# class that is responsible for creating the threads for managing and monitoring the values offered by the API that simulates the input and output signals of the BLAS

class ThreadClassBlas(QtCore.QThread):

    # we define a signal that will handle a list (with the values of the BLAS)
    any_signal = QtCore.pyqtSignal(list)

    # in the constructor we are going to define the addresses where we can extract each of the BLAS values from the API
    def __init__(self, parent=None):
        super(ThreadClassBlas, self).__init__(parent)
        self.is_running = True
        self.apiURL = "http://127.0.0.1:8000/"
        self.temperature = self.apiURL + "getTemperature"
        self.flow = self.apiURL + "getFlow"
        self.iLockFlow = self.apiURL + "getIlockFlow"
        self.fail0 = self.apiURL + "getFail0"
        self.fail1 = self.apiURL + "getFail1"
        self.PdMi = self.apiURL + "getPdMi"
        self.ilockPatchPanel = self.apiURL + "getIlockPatchPanel"
        self.vsel0 = self.apiURL + "getVsel0"
        self.vsel1 = self.apiURL + "getVsel1"

##################################################################################################################

    # Function that is responsible, through the Python REQUESTS package, for taking the values directly from the API and saving them in a list,
    # to finally emit said list through the signal defined at the beginning of the class.
    # all this is done indefinitely every 5 seconds
    def run(self):
        while (True):
            datosBlas=[]
            try:
                r = requests.get(self.temperature)
                datosBlas.append(r.text)

                r = requests.get(self.flow)
                datosBlas.append(r.text)

                r = requests.get(self.iLockFlow)
                datosBlas.append(r.text)

                r = requests.get(self.fail0)
                datosBlas.append(r.text)

                r = requests.get(self.fail1)
                datosBlas.append(r.text)

                r = requests.get(self.PdMi)
                datosBlas.append(r.text)

                r = requests.get(self.ilockPatchPanel)
                datosBlas.append(r.text)

                r = requests.get(self.vsel0)
                datosBlas.append(r.text)

                r = requests.get(self.vsel1)
                datosBlas.append(r.text)



                time.sleep(0.01)
                self.any_signal.emit(datosBlas)
                time.sleep(5)
            
            # in case of any failure, an empty list is issued
            except:
                self.any_signal.emit(datosBlas)
                time.sleep(5)

##################################################################################################################

    # Function that is responsible for stopping the thread of the class
    def stop(self):
        self.is_running = False
        #print('Stopping thread...',self.index)
        self.terminate()



########################################################################################################
########################################################################################################




# Execution of the entire GUI

app = QtWidgets.QApplication(sys.argv)
mainWindow = MiTFG()
mainWindow.show()
sys.exit(app.exec_())