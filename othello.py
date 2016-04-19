from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import functools

import constants


class QRightClickButton(QtWidgets.QPushButton):
	def __init__(self, parent):
		QtWidgets.QPushButton.__init__(self, parent)

	# custom define singal
	rightClicked = pyqtSignal()

class Ui_MainWindow(object):

	# declare variable
	playerColor = constants.BLACK
	state = constants.MAIN
	zoomInIndex = -1
	placed = [constants.EMPTY] * 64
	timer = []
	grid = []

	def blinkControl(self, block, allSwitch = False, switch = False):
		if(not allSwitch):
			if(self.timer[block].isActive()):
				self.timer[block].stop()
				self.showBlockGrid(block)
			else:
				self.timer[block].start(constants.ONE_SEC/constants.FREQ[block])
		else:
			if(switch == constants.ON):
				for i in range(0, 4):
					if(not self.timer[i].isActive()):
						self.timer[i].start(constants.ONE_SEC/constants.FREQ[i])
			else:
				for i in range(0, 4):
					self.timer[i].stop()
					self.showBlockGrid(i)
		self.menuBlinkControl()

	def menuBlinkControl(self):
		self.actionUpper_Left_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Upper-Left:"  + ("ON" if self.timer[constants.UPPER_LEFT].isActive() else "OFF")))
		self.actionUpper_Right_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Upper-Right:" + ("ON" if self.timer[constants.UPPER_RIGHT].isActive() else "OFF")))
		self.actionLower_Left_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Lower-Left:" + ("ON" if self.timer[constants.LOWER_LEFT].isActive() else "OFF")))
		self.actionLower_Right_ON.setText(QtCore.QCoreApplication.translate("MainWindow", \
																		   "Lower-Right:" + ("ON" if self.timer[constants.LOWER_RIGHT].isActive() else "OFF")))


	def showBlockGrid(self, block):
		index = []
		length = None
		if(self.state == constants.MAIN):
			index = constants.MAIN_BLOCK[block]
			length = constants.MAIN_BLOCK_LENGTH
		elif(self.state == constants.ZOOM_IN1):
			index = self.zoomInIndex + constants.ZOOM_IN1_BLOCK[block]
			length = constants.ZOOM_IN1_BLOCK_LENGTH
		else:
			index = self.zoomInIndex + constants.ZOOM_IN2_BLOCK[block]
			length = constants.ZOOM_IN2_BLOCK_LENGTH
		for y in range(0, length):
			for x in range(0, length):
				self.grid[index + y + x * 8].setVisible(True)

	def blink(self, block):
		index = []
		length = None
		if(self.state == constants.MAIN):
			index = constants.MAIN_BLOCK[block]
			length = constants.MAIN_BLOCK_LENGTH
		elif(self.state == constants.ZOOM_IN1):
			index = self.zoomInIndex + constants.ZOOM_IN1_BLOCK[block]
			length = constants.ZOOM_IN1_BLOCK_LENGTH
		else:
			index = self.zoomInIndex + constants.ZOOM_IN2_BLOCK[block]
			length = constants.ZOOM_IN2_BLOCK_LENGTH
		for y in range(0, length):
			for x in range(0, length):
				self.grid[index + y + x * 8].setVisible(False if self.grid[index + y + x * 8].isVisible() else True)

	def gridColor(self, block):
		index = []
		length = None
		if(self.state == constants.MAIN):
			index = constants.MAIN_BLOCK[block]
			length = constants.MAIN_BLOCK_LENGTH
		elif(self.state == constants.ZOOM_IN1):
			index = self.zoomInIndex + constants.ZOOM_IN1_BLOCK[block]
			length = constants.ZOOM_IN1_BLOCK_LENGTH
		else:
			index = self.zoomInIndex + constants.ZOOM_IN2_BLOCK[block]
			length = constants.ZOOM_IN2_BLOCK_LENGTH
		for y in range(0, length):
			for x in range(0, length):
				self.grid[index + y + x * 8].setStyleSheet("background-color: " + constants.COLOR[block] + ";"
															"font: 550 40pt \"Helvetica\";\n"
															"color: white;\n")

	# initialize
	def init(self):
		self.playerColor = constants.BLACK
		self.state = constants.MAIN
		self.zoomInIndex = -1
		for i in range (0, 64):
			self.placed[i] = constants.EMPTY

	# on click event
	def eventFilter(self, obj, event):
		if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
			if event.button() == QtCore.Qt.LeftButton:
				return False
			elif event.button() == QtCore.Qt.RightButton:
				obj.rightClicked.emit()
				return False
		return False

	# restart
	def restart(self):
		for i in range(0, 64):
			self.grid[i].setIcon(QtGui.QIcon())
			self.grid[i].setText(str(i + 1))
		while self.state != constants.MAIN:
			self.zoomOut()
		self.init()


	# places chess
	def placeChess(self, grid):
		if(self.placed[int(grid.objectName())] != constants.EMPTY):
			return

		if self.playerColor == constants.WHITE:
			grid.setIcon(QtGui.QIcon("./src/white.png"))
			grid.setText("")
			self.placed[int(grid.objectName())] = constants.WHITE
		else:
			grid.setIcon(QtGui.QIcon("./src/black.png"))
			grid.setText("")
			self.placed[int(grid.objectName())] = constants.BLACK
		self.playerColor =  constants.BLACK if self.playerColor == constants.WHITE else constants.WHITE

	def hideAllGrids(self):
		for i in range(0, 64):
			self.grid[i].setVisible(False)

	# zoom out
	def zoomOut(self):
		if(self.state == constants.ZOOM_IN1):
			self.hideAllGrids()
			for y in range(0, 8):
				for x in range(0, 8):
					xPosition = 10 + x * 70 + (constants.XSPACE if int(x / 4) else 0)
					yPosition = 10 + y * 70 + (constants.YSPACE if int(y / 4) else 0)
					self.grid[x + y * 8].setGeometry(QtCore.QRect(xPosition, yPosition, 65, 65))
					self.grid[x + y * 8].setVisible(True)
			self.state = constants.MAIN
		elif(self.state == constants.ZOOM_IN2):
			self.hideAllGrids()
			number = constants.ZOOM_IN1_TABLE[self.zoomInIndex]
			self.zoomInIndex = number
			for y in range(0, 4):
				for x in range(0, 4):
					xPosition = 10 + x * 70 * 2 + (constants.XSPACE if int(x / 2) else 0)
					yPosition = 10 + y * 70 * 2 + (constants.YSPACE if int(y / 2) else 0)
					self.grid[number + x + y * 8].setGeometry(QtCore.QRect(xPosition, yPosition, 65 * 2, 65 * 2))
					self.grid[number + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN1
		for i in range(0, 4):
			self.gridColor(i)

	# zoom in
	def zoomIn(self, grid):
		index = int(grid.objectName())
		if(self.state == constants.MAIN):
			self.zoomInIndex = constants.ZOOM_IN1_TABLE[index]
			self.hideAllGrids()
			for y in range(0, 4):
				for x in range(0, 4):
					xPosition = 10 + x * 70 * 2 + (constants.XSPACE if int(x / 2) else 0)
					yPosition = 10 + y * 70 * 2 + (constants.YSPACE if int(y / 2) else 0)
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(xPosition, yPosition, 65 * 2, 65 * 2))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN1
		elif(self.state == constants.ZOOM_IN1):
			self.zoomInIndex = constants.ZOOM_IN2_TABLE[index]
			self.hideAllGrids()
			for y in range(0, 2):
				for x in range(0, 2):
					xPosition = 10 + x * 70 * 4 + (constants.XSPACE if x else 0)
					yPosition = 10 + y * 70 * 4 + (constants.YSPACE if y else 0)
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(xPosition, yPosition, 65 * 4, 65 * 4))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN2
		for i in range(0, 4):
			self.gridColor(i)

	# left click
	def gridOnClick(self):
		self.placeChess(self.sender())

	# right click
	def gridOnRightClick(self):
		self.zoomIn(self.sender())

	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800 + constants.XSPACE, 640 + constants.YSPACE)
		MainWindow.setMinimumSize(QtCore.QSize(800 + constants.XSPACE, 640 + constants.YSPACE))
		MainWindow.setAutoFillBackground(False)
		MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setAutoFillBackground(False)
		self.centralwidget.setObjectName("centralwidget")

		# create QTimer for blinking
		for i in range(0, 4):
			self.timer.append(QTimer())

		# board
		for y in range(0, 8):
			for x in range(0, 8):
				index = x + y * 8
				self.grid.append(QRightClickButton(self.centralwidget))
				xPosition = 10 + x * 70 + (constants.XSPACE if int(x / 4) else 0)
				yPosition = 10 + y * 70 + (constants.YSPACE if int(y / 4) else 0)
				self.grid[index].setGeometry(QtCore.QRect(xPosition, yPosition, 65, 65))
				self.grid[index].setStyleSheet("border-color: rgb(255, 255, 255);\n"
												"font: 550 40pt \"Helvetica\";\n"
												"color: white;\n"
												"background-color: " + constants.COLOR[int(x / 4) + int(y / 4) * 2] + ";")
				self.grid[index].setText(str(index + 1))
				self.grid[index].setAutoDefault(False)
				self.grid[index].setObjectName(str(index))
				self.grid[index].setIconSize(QtCore.QSize(55, 55))
				#  connect click event with gridOnClick
				self.grid[index].clicked.connect(self.gridOnClick)
				#  creat event filter
				self.grid[index].installEventFilter(self)
				#  connect right click event with gridOnRightClick
				self.grid[index].rightClicked.connect(self.gridOnRightClick)
				self.grid[index].setFocusPolicy(QtCore.Qt.NoFocus)

		# refresh button
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[64].setEnabled(True)
		self.grid[64].setGeometry(QtCore.QRect(610 + constants.XSPACE, 70, 160, 160))
		self.grid[64].setStyleSheet("border-color: rgb(255, 255, 255);\n"
									"background-color: rgb(19, 146, 59);")
		self.grid[64].setIcon(QtGui.QIcon("./src/refresh.png"))
		self.grid[64].setIconSize(QtCore.QSize(55, 55))
		self.grid[64].setText("")
		self.grid[64].setAutoDefault(False)
		self.grid[64].setObjectName("refresh")
		self.grid[64].clicked.connect(self.restart)
		self.grid[64].setFocusPolicy(QtCore.Qt.NoFocus)

		# return button
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[65].setEnabled(True)
		self.grid[65].setGeometry(QtCore.QRect(610 + constants.XSPACE, 280 + constants.YSPACE, 160, 160))
		self.grid[65].setStyleSheet("border-color: rgb(255, 255, 255);\n"
									"background-color: rgb(19, 146, 59);")
		self.grid[65].setIcon(QtGui.QIcon("./src/return.png"))
		self.grid[65].setIconSize(QtCore.QSize(55, 55))
		self.grid[65].setText("")
		self.grid[65].setAutoDefault(False)
		self.grid[65].setObjectName("return")
		self.grid[65].clicked.connect(self.zoomOut)
		self.grid[65].setFocusPolicy(QtCore.Qt.NoFocus)

		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 38))
		self.menubar.setStyleSheet("background-color: rgb(0, 128, 255);\n"
								   "selection-color: rgb(128, 255, 0);\n"
								   "border-color: rgb(102, 102, 255);\n"
								   "font: 14pt \"Courier\";")
		self.menubar.setNativeMenuBar(False)
		self.menubar.setObjectName("menubar")
		self.menuMenu = QtWidgets.QMenu(self.menubar)
		self.menuMenu.setStyleSheet("background-color: rgb(0, 128, 255);\n"
									"selection-color: rgb(128, 255, 0);\n"
									"border-color: rgb(102, 102, 255);\n"
									"font: 14pt \"Courier\";")

		# menu
		self.menuMenu.setObjectName("menuMenu")
		self.menuSettings = QtWidgets.QMenu(self.menubar)
		self.menuSettings.setObjectName("menuSettings")
		self.menuBlink = QtWidgets.QMenu(self.menuSettings)
		self.menuBlink.setObjectName("menuBlink")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)
		self.actionNew_Game = QtWidgets.QAction(MainWindow)
		self.actionNew_Game.setObjectName("actionNew_Game")
		self.actionNew_Game.triggered.connect(self.restart)
		self.actionReturn = QtWidgets.QAction(MainWindow)
		self.actionReturn.setObjectName("actionReturn")
		self.actionReturn.triggered.connect(self.zoomOut)
		self.actionWhole_Board_ON = QtWidgets.QAction(MainWindow)
		self.actionWhole_Board_ON.setObjectName("actionWhole_Board_ON")
		self.actionWhole_Board_ON.triggered.connect(functools.partial(self.blinkControl, 4, True, constants.ON))
		self.actionWhole_Board_OFF = QtWidgets.QAction(MainWindow)
		self.actionWhole_Board_OFF.setObjectName("actionWhole_Board_OFF")
		self.actionWhole_Board_OFF.triggered.connect(functools.partial(self.blinkControl, 4, True, constants.OFF))
		self.actionUpper_Left_ON = QtWidgets.QAction(MainWindow)
		self.actionUpper_Left_ON.setObjectName("actionUpper_Left_ON")
		self.actionUpper_Left_ON.triggered.connect(functools.partial(self.blinkControl, constants.UPPER_LEFT, False))
		self.actionUpper_Right_ON = QtWidgets.QAction(MainWindow)
		self.actionUpper_Right_ON.setObjectName("actionUpper_Right_ON")
		self.actionUpper_Right_ON.triggered.connect(functools.partial(self.blinkControl, constants.UPPER_RIGHT, False))
		self.actionLower_Left_ON = QtWidgets.QAction(MainWindow)
		self.actionLower_Left_ON.setObjectName("action_Lower_Left_ON")
		self.actionLower_Left_ON.triggered.connect(functools.partial(self.blinkControl, constants.LOWER_LEFT, False))
		self.actionLower_Right_ON = QtWidgets.QAction(MainWindow)
		self.actionLower_Right_ON.setObjectName("actionLower_Right_ON")
		self.actionLower_Right_ON.triggered.connect(functools.partial(self.blinkControl, constants.LOWER_RIGHT, False))
		self.menuMenu.addAction(self.actionNew_Game)
		self.menuMenu.addAction(self.actionReturn)
		self.menuBlink.addAction(self.actionWhole_Board_ON)
		self.menuBlink.addAction(self.actionWhole_Board_OFF)
		self.menuBlink.addAction(self.actionUpper_Left_ON)
		self.menuBlink.addAction(self.actionUpper_Right_ON)
		self.menuBlink.addAction(self.actionLower_Left_ON)
		self.menuBlink.addAction(self.actionLower_Right_ON)
		self.menuSettings.addAction(self.menuBlink.menuAction())
		self.menubar.addAction(self.menuMenu.menuAction())
		self.menubar.addAction(self.menuSettings.menuAction())

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		# connect QTimer
		self.timer[0].timeout.connect(functools.partial(self.blink, block=constants.UPPER_LEFT))
		self.timer[1].timeout.connect(functools.partial(self.blink, block=constants.UPPER_RIGHT))
		self.timer[2].timeout.connect(functools.partial(self.blink, block=constants.LOWER_LEFT))
		self.timer[3].timeout.connect(functools.partial(self.blink, block=constants.LOWER_RIGHT))

		# start QTimer (start to blink)
		for i in range(0, 4):
			self.timer[i].start(constants.ONE_SEC/constants.FREQ[i])


	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.menuMenu.setTitle(_translate("MainWindow", "Game"))
		self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
		self.menuBlink.setTitle(_translate("MainWindow", "Blink"))
		self.actionNew_Game.setText(_translate("MainWindow", "New Game"))
		self.actionReturn.setText(_translate("MainWindow", "Return"))
		self.actionWhole_Board_ON.setText(_translate("MainWindow", "Whole Board ON"))
		self.actionWhole_Board_OFF.setText(_translate("MainWindow", "Whole Board OFF"))
		self.actionUpper_Left_ON.setText(_translate("MainWindow", "Upper-Left:ON"))
		self.actionUpper_Right_ON.setText(_translate("MainWindow", "Upper-Right:ON"))
		self.actionLower_Left_ON.setText(_translate("MainWindow", "Lower-Left:ON"))
		self.actionLower_Right_ON.setText(_translate("MainWindow", "Lower-Right:ON"))
		self.actionNew_Game.setShortcut(_translate("MainWindow", "Ctrl+N"))
		self.actionReturn.setShortcut(_translate("MainWindow", "Ctrl+R"))
		self.actionWhole_Board_ON.setShortcut(_translate("MainWindow", "Ctrl+E"))
		self.actionWhole_Board_OFF.setShortcut(_translate("MainWindow", "Ctrl+D"))
		self.actionUpper_Left_ON.setShortcut(_translate("MainWindow", "Ctrl+1"))
		self.actionUpper_Right_ON.setShortcut(_translate("MainWindow", "Ctrl+2"))
		self.actionLower_Left_ON.setShortcut(_translate("MainWindow", "Ctrl+3"))
		self.actionLower_Right_ON.setShortcut(_translate("MainWindow", "Ctrl+4"))
