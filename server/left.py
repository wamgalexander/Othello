from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import pyqtSignal, QTimer
import functools
import sys # We need sys so that we can pass argv to QApplication
import constants
import os
import datetime

class QRightClickButton(QtWidgets.QPushButton):
	def __init__(self, parent):
		QtWidgets.QPushButton.__init__(self, parent)

	# custom define singal
	rightClicked = pyqtSignal()

class Ui_MainWindow(object):

####### declare variable #######
	setting = False
	timer = []
	checkcmd = []
	cycle = [] * 4
	cross = []
	text = []
	grid = []
	T = []
	ST = []
	cmd = []
	block_type = 'b'
	cont = 5000
	suspend = 0
	delay = 2000
	last_time = ''
	layoutmode = 'left'
#	layoutmode = 'normal'
#	layoutmode = 'right'

	F = constants.ONE_SEC/constants.FREQ[0]
	isBlink = False
	lastBlink = 2
	screenWidth = 0
	screenHeight = 0
	startPosX = 0
	startPosY = 0
	buttonWidth = 0
	buttonHeight = 0
	spaceWidth = 10
	spaceHeight = 10
	crossWidth = 0
	crossHeight = 0

	freqButtonXPos = 0
	freqButtonYPos = 0
	freqButtonWidth = 0
	freqButtonHeight = 0

	freqCtrlXPos = 0
	freqCtrlYPos = 0
	freqCtrlWidth = 0
	freqButtonHeight = 0

	crossXPos = 0
	crossYPos = 0
####### UI ########
	def setupUi(self, MainWindow):
		# set layout variable
		self.layoutSizeVar()
		# read config.txt
		self.layoutMode()
		# main window
		self.setMainWindow(MainWindow)
		# freq ctrl
		self.setFreqCtrl()
		# cross
		self.setCross()
		# cycle
		self.setCycle()
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
		self.checkcmd[0].start(self.F)
		self.ST[0].stop()

	def blink(self, block):
		if(self.block_type == 'b'):
			V = self.cross[0].isVisible()
			self.cnt = self.cnt + 0.5
			self.cross[block].setVisible(not V)
		elif(self.block_type == 'c'):
			running = [5, 6, 10, 9]
			index = running[self.lastBlink]
			V = self.cycle[index].isVisible()
			self.cycle[index].setVisible(not V)

			if not V:
				self.lastBlink = (self.lastBlink + 1) % 4


	def blinkControl(self, block, allSwitch = False):
		self.isBlink = not self.isBlink
		if(self.isBlink):
			if(self.block_type == 'c'):
					for i in range(0, 16):
						self.cycle[i].setVisible(True)
			self.contBlink(block)
		else:
			self.T[0].stop()
			self.timer[block].stop()
			self.checkcmd[0].stop()
			self.showBlockGrid(block)

		self.menuBlinkControl()

	def menuBlinkControl(self):
		self.actionUpper_Left_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Upper-Left:"  + ("ON" if self.timer[constants.UPPER_LEFT].isActive() else "OFF")))
## Block ##
	def showBlockGrid(self, block):
		if(self.block_type == 'b'):
			self.cross[block].setVisible(True)
		elif(self.block_type == 'c'):
			for i in range(0, 4):
				self.cycle[i].setVisible(True)

## cross ##
	def setCrossPos(self, block, XPos, YPos):
		self.cross[block].setGeometry(QtCore.QRect(XPos, YPos, self.crossWidth, self.crossHeight))
## cycle ##
	def setCyclePos(self, block, XPos, YPos):
		self.cycle[block].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth, self.buttonHeight))

## freq ##
	def editFreq(self):
		if(self.timer[0].isActive()):
			self.timer[0].stop()
		if(constants.FREQ[0] > 0):
			constants.FREQ[0] = int(self.text[0].toPlainText())
			self.F = constants.ONE_SEC/constants.FREQ[0]
			self.isBlink = True
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
		self.checkcmd.append(QTimer())
		self.T.append(QTimer())
		self.ST.append(QTimer())

		r = QtWidgets.QDesktopWidget().screenGeometry()

		self.screenWidth = r.width()
		self.screenHeight = r.height()
		self.buttonWidth = self.screenWidth * (50/840)
		self.buttonHeight = self.screenHeight * (60/680)
		self.boardWidth = self.screenWidth * (670/840)
		self.boardHeight = self.screenHeight
		self.startPosX = self.screenWidth * (314/840)
		self.startPosY = self.screenHeight * (180/680)

		self.crossWidth = self.screenWidth * (12/840)
		self.crossHeight = self.screenHeight * (16/680)

		self.freqButtonXPos = self.screenWidth*(670/840)
		self.freqButtonYPos = self.screenHeight*(470/680)
		self.freqButtonWidth = self.screenWidth*(90/840)
		self.freqButtonHeight = self.screenHeight*(35/680)

		self.freqCtrlXPos = self.screenWidth*(670/840)
		self.freqCtrlYPos = self.screenHeight*(515/680)
		self.freqCtrlWidth = self.screenWidth*(40/840)
		self.freqCtrlHeight = self.screenHeight*(40/680)

		self.crossXPos = self.screenWidth * (414/840)
		self.crossYPos = self.screenHeight * (332/680)

	def layoutMode(self):
		modify_time = self.modification_date('config.txt')
		if(self.last_time != modify_time):
			self.cmd = open('config.txt', 'r').read().splitlines()
			act = False
			if(self.layoutmode == 'left'):
				c = self.cmd[1].split()
				self.suspend = self.delay if c[0] == '2' else 0
				act = True if c[0] != '0' else False
				self.block_type = c[1]
				constants.FREQ[0] = int(c[2])
				self.left()
			elif(self.layoutmode == 'normal'):
				c = self.cmd[1].split()
				self.suspend = self.delay if c[0] == '2' else 0
				act = True if c[0] != '0' else False
				self.block_type = c[1]
				constants.FREQ[0] = int(c[2])
				self.left()
			elif(self.layoutmode == 'right'):
				c = self.cmd[2].split()
				self.suspend = self.delay if c[0] == '2' else 0
				act = True if c[0] != '0' else False
				self.block_type = c[1]
				constants.FREQ[0] = int(c[2])
				self.right()
			self.F = constants.ONE_SEC/constants.FREQ[0]

			if(self.last_time != ''):
				self.text[0].setText(str(constants.FREQ[0]))
				if(self.block_type == 'b'):
					self.cross[0].setVisible(True)
					for i in range(0, 16):
						self.cycle[i].setVisible(False)
				elif(self.block_type == 'c'):
					self.cross[0].setVisible(False)
					for i in range(0, 16):
						self.cycle[i].setVisible(True)

			if(self.cmd[0] != '0' and act):
				self.isBlink = True
				self.timer[0].start(self.F)
			else:
				self.isBlink = False
				self.timer[0].stop()
				self.T[0].stop()
				self.ST[0].stop()
			self.last_time = modify_time
			print(self.last_time)


	def center(self):
		window = self.frameGeometry()
		center = QDesktopWidget().availableGeometry().center()
		window.moveCenter(center)
		self.move(window.topLeft())

	def left(self):
		window = self.frameGeometry()
		window.moveLeft(0)
		self.move(window.topLeft())

	def right(self):
		window = self.frameGeometry()
		window.moveRight(self.screenWidth)
		self.move(window.topRight())

	def setMainWindow(self, MainWindow):
		self.checkcmd[0].start(self.F)
		if(self.layoutmode != 'normal'):
			self.screenWidth = self.screenWidth / 2
			self.startPosX = self.startPosX / 3
			self.freqButtonXPos = self.freqButtonXPos / 2
			self.freqCtrlXPos = self.freqCtrlXPos / 2
			self.crossXPos = self.crossXPos / 2

		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(self.screenWidth, self.screenHeight)
		MainWindow.setMinimumSize(QtCore.QSize(self.screenWidth, self.screenHeight))
		MainWindow.setAutoFillBackground(False)
		MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setAutoFillBackground(False)
		self.centralwidget.setObjectName("centralwidget")

	def setFreqCtrl(self):
		# freq set button
		XPos = self.freqButtonXPos
		YPos = self.freqButtonYPos
		W = self.freqButtonWidth
		H = self.freqButtonHeight
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
		XPos = self.freqCtrlXPos
		YPos = self.freqCtrlYPos
		W = self.freqCtrlWidth
		H = self.freqCtrlHeight
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

	def setCross(self):
		self.cross.append(QRightClickButton(self.centralwidget))
		XPos = self.crossXPos
		YPos = self.crossYPos
		self.setCrossPos(0, XPos, YPos)
		self.cross[0].setStyleSheet("background-color:" + constants.COLOR[0] + ";")
		self.cross[0].setObjectName(str(0))
		self.cross[0].setEnabled(False)
		self.cross[0].setFocusPolicy(QtCore.Qt.NoFocus)
		if(self.block_type != 'b'):
			self.cross[0].setVisible(False)


	def setCycle(self):
		for y in range(0, 4):
			for x in range(0, 4):
				i = x + y * 4
				self.cycle.append(QRightClickButton(self.centralwidget))
				Xpos = self.startPosX + x * (self.buttonWidth+self.spaceWidth)
				Ypos = self.startPosY + y * (self.buttonHeight+self.spaceHeight)
				self.setCyclePos(i, Xpos, Ypos)
				self.cycle[i].setStyleSheet("background-color:" + constants.COLOR[0] + ";")
				self.cycle[i].setStyleSheet("background-color:" + constants.COLOR[0] + ";")
				self.cycle[i].setObjectName(str(i))
				self.cycle[i].setEnabled(False)
				self.cycle[i].setFocusPolicy(QtCore.Qt.NoFocus)
				if(self.block_type != 'c'):
					self.cycle[i].setVisible(False)

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
		self.checkcmd[0].timeout.connect(self.layoutMode)
		self.T[0].timeout.connect(functools.partial(self.suspendTime, block=constants.UPPER_LEFT))
		self.ST[0].timeout.connect(functools.partial(self.contBlink, block=constants.UPPER_LEFT))

	def modification_date(self,filename):
	    t = os.path.getmtime(filename)
	    return datetime.datetime.fromtimestamp(t)

class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined

def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = App()                 # We set the form to be our App (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app



if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function
