from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import pyqtSignal, QTimer, QTime
import functools

import constants

class QRightClickButton(QtWidgets.QPushButton):
	def __init__(self, parent):
		QtWidgets.QPushButton.__init__(self, parent)

	# custom define singal
	rightClicked = pyqtSignal()

class Ui_MainWindow(object):
####### declare variable #######
	setting = False
	timer = []
	cross = []
	text = []
	grid = []
	result = []
	T = []
	ST = []
	cont = 5000
	suspend = 2000

	F = constants.ONE_SEC/constants.FREQ[0]
	isBlink = False
	cnt = 0
	screenWidth = 0
	screenHeight = 0
	startPosX = 0
	startPosY = 0
	crossWidth = 0
	crossHeight = 0

####### UI ########
	def setupUi(self, MainWindow):
		# set layout variable
		self.layoutSizeVar()
		# main window
		self.setMainWindow(MainWindow)
		# freq ctrl
		self.setFreqCtrl()
		# cross
		self.setCross()
		# menubar
		self.setMenubar(MainWindow)
		# menu
		self.setMenu(MainWindow)
		# timer
		self.setTimer()

####### Fuction #######
## blink ##
	def suspendTime(self, block):
		self.isBlink = False
		self.T[0].stop()
		self.timer[block].stop()
		self.showBlockGrid(block)
		self.ST[0].start(self.suspend)

	def contBlink(self, block):
		self.isBlink = True
		self.T[0].start(self.cont)
		self.timer[block].start(self.F)
		self.ST[0].stop()

	def blink(self, block):
		V = self.cross[block].isVisible()
		self.cnt = self.cnt + 0.5
		self.cross[block].setVisible(not V)

	def blinkControl(self, block, allSwitch = False):
		self.isBlink = not self.isBlink
		if(self.isBlink):
			for i in range(0, 4):
				self.result[i].setVisible(False)
			self.cnt = 0
			self.contBlink(block)

		else:
			self.T[0].stop()
			self.timer[block].stop()
			self.showBlockGrid(block)
			#self.setFreqResult(self.T[0].elapsed())

		self.menuBlinkControl()

	def menuBlinkControl(self):
		self.actionUpper_Left_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Upper-Left:"  + ("ON" if self.timer[constants.UPPER_LEFT].isActive() else "OFF")))
## Block ##
	def showBlockGrid(self, block):
		self.cross[block].setVisible(True)

	def gridColor(self, block):
		self.cross[block].setStyleSheet("background-color:" + constants.COLOR[block] + ";")

## cross ##
	def setCrossPos(self, block, XPos, YPos):
		self.cross[block].setGeometry(QtCore.QRect(XPos, YPos, self.crossWidth, self.crossHeight))

## freq ##
	def setFreqResult(self, t):
		self.result[0].setPlainText("-------------------------")
		self.result[1].setPlainText("f = " + str((self.cnt*1000)/t))
		self.result[2].setPlainText("cnt = " + str(self.cnt) + " times")
		self.result[3].setPlainText("t = " + str(t/1000) + "s")
		for i in range(0, 4):
			self.result[i].setVisible(True)

	def editFreq(self):
		if(self.timer[0].isActive()):
			self.timer[0].stop()
		if(constants.FREQ[0] > 0):
			constants.FREQ[0] = int(self.text[0].toPlainText())
			self.F = constants.ONE_SEC/constants.FREQ[0]
			self.isBlink = True
			self.cnt = 0
			self.contBlink(0)

	def showFreqControl(self, MainWindow):
		self.setting = not self.setting
		self.grid[0].setVisible(self.setting)
		self.text[0].setVisible(self.setting)

## Key ##
	def retranslateUi(self, MainWindow):
		# menu setting #
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.menuMenu.setTitle(_translate("MainWindow", "Game"))

		self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
		self.menuBlink.setTitle(_translate("MainWindow", "Blink"))

		self.actionUpper_Left_ON.setText(_translate("MainWindow", "Upper-Left:ON"))
		self.setFreq.setText(_translate("MainWindow", "Set-Freq"))

		# set short-key #
		self.actionUpper_Left_ON.setShortcut(_translate("MainWindow", "Ctrl+1"))
		self.setFreq.setShortcut(_translate("MainWindow", "Ctrl+F"))

## UI setting ##
	def layoutSizeVar(self):
		# creat timer
		self.timer.append(QTimer())
		self.T.append(QTimer())
		self.ST.append(QTimer())

		r = QtWidgets.QDesktopWidget().screenGeometry()
		self.screenWidth = r.width()
		self.screenHeight = r.height()
		self.crossWidth = self.screenWidth * (12/840)
		self.crossHeight = self.screenHeight * (16/680)
		self.buttonWidth = self.screenWidth * (50/840)
		self.buttonHeight = self.screenHeight * (60/680)
		self.boardWidth = self.screenWidth * (670/840)
		self.boardHeight = self.screenHeight
		self.startPosX = self.screenWidth * (414/840)
		self.startPosY = self.screenHeight * (332/680)

	def center(self):
		window = self.frameGeometry()
		center = QDesktopWidget().availableGeometry().center()
		window.moveCenter(center)
		self.move(window.topLeft())

	def setMainWindow(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(self.screenWidth, self.screenHeight)
		MainWindow.setMinimumSize(QtCore.QSize(self.screenWidth, self.screenHeight))
		MainWindow.setAutoFillBackground(False)
		MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setAutoFillBackground(False)
		self.centralwidget.setObjectName("centralwidget")
		self.center()

	def setFreqCtrl(self):
		# freq set button
		XPos = self.screenWidth*(670/840)
		YPos = self.screenHeight*(470/680)
		W = self.screenWidth*(90/840)
		H = self.screenHeight*(35/680)
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[0].setObjectName("set")
		self.grid[0].setText("Set")
		self.grid[0].setGeometry(QtCore.QRect(XPos, YPos , W, H))
		self.grid[0].setEnabled(True)
		self.grid[0].setAutoDefault(False)
		self.grid[0].setVisible(False)
		self.grid[0].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[0].clicked.connect(self.editFreq)
		self.grid[0].setStyleSheet("background-color: rgb(0, 128, 255);"
								   "selection-color: rgb(128, 255, 0);"
								   "border-color: rgb(102, 102, 255);"
								   "font: 14pt \"Courier\";")

		# freq ctrl
		XPos = self.screenWidth*(670/840)
		YPos = self.screenHeight*(515/680)
		W = self.screenWidth*(40/840)
		H = self.screenHeight*(40/680)
		self.text.append(QtWidgets.QTextEdit(self.centralwidget))
		self.text[0].setObjectName(str(0))
		self.text[0].setText(str(constants.FREQ[0]))
		self.text[0].setGeometry(QtCore.QRect(XPos, YPos , W, H))
		self.text[0].setEnabled(True)
		self.text[0].setVisible(False)
		self.text[0].setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
		self.text[0].setStyleSheet("background-color: " + constants.COLOR[0] +";"
								   "border-color: rgb(102, 102, 255);"
								   "font: 14pt \"Courier\";")

		# freq testing result
		W = self.screenWidth*(150/840)
		H = self.screenHeight*(20/680)

		for i in range(0, 4):
			XPos = self.screenWidth*(670/840)
			YPos = self.screenHeight*(300/680) + H * i
			self.result.append(QtWidgets.QTextEdit(self.centralwidget))
			self.result[i].setObjectName("freq result")
			self.result[i].setText("")
			self.result[i].setGeometry(QtCore.QRect(XPos, YPos , W, H))
			self.result[i].setEnabled(True)
			self.result[i].setVisible(False)
			self.result[i].setAcceptRichText(False)
			self.result[i].setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
			self.result[i].setStyleSheet("background-color: rgb(0, 0, 0);"
									   "color: rgb(255, 255, 255);"
									   "border-color: rgb(255, 255, 255);"
									   "font: 12pt \"Courier\";")

	def setCross(self):
		self.cross.append(QRightClickButton(self.centralwidget))
		XPos = self.startPosX
		YPos = self.startPosY
		self.setCrossPos(0, XPos, YPos)
		self.gridColor(0)
		self.cross[0].setObjectName(str(0))
		self.cross[0].setEnabled(False)
		self.cross[0].setFocusPolicy(QtCore.Qt.NoFocus)

	def setMenubar(self, MainWindow):
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 38))
		self.menubar.setStyleSheet("background-color: rgb(0, 128, 255);"
								   "selection-color: rgb(128, 255, 0);"
								   "border-color: rgb(102, 102, 255);"
								   "font: 14pt \"Courier\";")
		self.menubar.setNativeMenuBar(False)

		self.menubar.setObjectName("menubar")
		self.menuMenu = QtWidgets.QMenu(self.menubar)
		self.menuMenu.setStyleSheet("background-color: rgb(0, 128, 255);"
									"selection-color: rgb(128, 255, 0);"
									"border-color: rgb(102, 102, 255);"
									"font: 14pt \"Courier\";")

	def setMenu(self, MainWindow):
		# set menu action object #
		self.menuMenu.setObjectName("menuMenu")
		self.menuSettings = QtWidgets.QMenu(self.menubar)
		self.menuSettings.setObjectName("menuSettings")

		self.menuBlink = QtWidgets.QMenu(self.menuSettings)
		self.menuBlink.setObjectName("menuBlink")
		MainWindow.setMenuBar(self.menubar)

		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.actionUpper_Left_ON = QtWidgets.QAction(MainWindow)
		self.actionUpper_Left_ON.setObjectName("actionUpper_Left_ON")
		self.actionUpper_Left_ON.triggered.connect(functools.partial(self.blinkControl, constants.UPPER_LEFT, False))

		self.setFreq = QtWidgets.QAction(MainWindow)
		self.setFreq.setObjectName("set_Frequence")
		self.setFreq.triggered.connect(functools.partial(self.showFreqControl, MainWindow))

		# set menu action #
		self.menuBlink.addAction(self.actionUpper_Left_ON)
		self.menuBlink.addAction(self.setFreq)

		self.menuSettings.addAction(self.menuBlink.menuAction())
		self.menubar.addAction(self.menuMenu.menuAction())
		self.menubar.addAction(self.menuSettings.menuAction())

		# connect action slot to menu #
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def setTimer(self):
		self.cnt = 0
		self.timer[0].timeout.connect(functools.partial(self.blink, block=constants.UPPER_LEFT))
		self.T[0].timeout.connect(functools.partial(self.suspendTime, block=constants.UPPER_LEFT))
		self.ST[0].timeout.connect(functools.partial(self.contBlink, block=constants.UPPER_LEFT))
