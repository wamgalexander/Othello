from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
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

	# initialize
	def init(self):
		playerColor = constants.BLACK
		state = constants.MAIN
		zoomInIndex = -1
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
		if(self.placed[int(grid.objectName())]):
			return

		if self.playerColor:
			grid.setIcon(QtGui.QIcon("./src/white.png"))
			grid.setText("")
			self.placed[int(grid.objectName())] = constants.WHITE
		else:
			grid.setIcon(QtGui.QIcon("./src/black.png"))
			grid.setText("")
			self.placed[int(grid.objectName())] = constants.BLACK
		self.playerColor =  0 if self.playerColor else 1

	def hideAllGrids(self):
		for i in range(0, 64):
			self.grid[i].setVisible(False)

	# zoom out
	def zoomOut(self):
		if(self.state == constants.ZOOM_IN1):
			self.hideAllGrids()
			for y in range(0, 8):
				for x in range(0, 8):
					self.grid[x + y * 8].setGeometry(QtCore.QRect(10 + x * 70, 10 + y * 70, 65, 65))
					self.grid[x + y * 8].setVisible(True)
			self.state = constants.MAIN
		elif(self.state == constants.ZOOM_IN2):
			self.hideAllGrids()
			number = constants.ZOOM_IN1_TABLE[self.zoomInIndex]
			self.zoomInIndex = number
			for y in range(0, 4):
				for x in range(0, 4):
					self.grid[number + x + y * 8].setGeometry(QtCore.QRect(10 + x * 70 * 2, 10 + y * 70 * 2, 65 * 2, 65 * 2))
					self.grid[number + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN1

	# zoom in
	def zoomIn(self, grid):
		index = int(grid.objectName())
		if(self.state == constants.MAIN):
			self.zoomInIndex = constants.ZOOM_IN1_TABLE[index]
			self.hideAllGrids()
			for y in range(0, 4):
				for x in range(0, 4):
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(10 + x * 70 * 2, 10 + y * 70 * 2, 65 * 2, 65 * 2))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN1
		elif(self.state == constants.ZOOM_IN1):
			self.zoomInIndex = constants.ZOOM_IN2_TABLE[index]
			self.hideAllGrids()
			for y in range(0, 2):
				for x in range(0, 2):
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(10 + x * 70 * 4, 10 + y * 70 * 4, 65 * 4, 65 * 4))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN2

	# left click
	def gridOnClick(self):
		self.placeChess(self.sender())

	# right click
	def gridOnRightClick(self):
		self.zoomIn(self.sender())

	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800, 640)
		MainWindow.setMinimumSize(QtCore.QSize(800, 640))
		MainWindow.setAutoFillBackground(False)
		MainWindow.setStyleSheet("background-color: rgb(76, 76, 76);")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setAutoFillBackground(False)
		self.centralwidget.setObjectName("centralwidget")

		self.grid = []

		for y in range(0, 8):
			for x in range(0, 8):
				self.grid.append(QRightClickButton(self.centralwidget))
				self.grid[x + y * 8].setGeometry(QtCore.QRect(10 + x * 70, 10 + y * 70, 65, 65))
				self.grid[x + y * 8].setStyleSheet("border-color: rgb(255, 255, 255);\n"
												   "background-color: rgb(19, 146, 59);")
				self.grid[x + y * 8].setText(str(x + y * 8 + 1))
				self.grid[x + y * 8].setAutoDefault(False)
				self.grid[x + y * 8].setObjectName(str(x + y * 8))
				self.grid[x + y * 8].setIconSize(QtCore.QSize(55, 55))
				#  connect click event with gridOnClick
				self.grid[x + y * 8].clicked.connect(self.gridOnClick)
				#  creat event filter
				self.grid[x + y * 8].installEventFilter(self)
				#  connect right click event with gridOnRightClick
				self.grid[x + y * 8].rightClicked.connect(self.gridOnRightClick)

		# refresh button
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[64].setEnabled(True)
		self.grid[64].setGeometry(QtCore.QRect(610, 70, 160, 160))
		self.grid[64].setStyleSheet("border-color: rgb(255, 255, 255);\n"
									"background-color: rgb(19, 146, 59);")
		self.grid[64].setIcon(QtGui.QIcon("./src/refresh.png"))
		self.grid[64].setIconSize(QtCore.QSize(55, 55))
		self.grid[64].setText("")
		self.grid[64].setAutoDefault(False)
		self.grid[64].setObjectName("refresh")
		self.grid[64].clicked.connect(self.restart)

		# return button
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[65].setEnabled(True)
		self.grid[65].setGeometry(QtCore.QRect(610, 280, 160, 160))
		self.grid[65].setStyleSheet("border-color: rgb(255, 255, 255);\n"
									"background-color: rgb(19, 146, 59);")
		self.grid[65].setIcon(QtGui.QIcon("./src/return.png"))
		self.grid[65].setIconSize(QtCore.QSize(55, 55))
		self.grid[65].setText("")
		self.grid[65].setAutoDefault(False)
		self.grid[65].setObjectName("return")
		self.grid[65].clicked.connect(self.zoomOut)

		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 575, 48))
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
		self.menuMenu.setObjectName("menuMenu")
		self.menuCtrl = QtWidgets.QMenu(self.menubar)
		self.menuCtrl.setObjectName("menuCtrl")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)
		self.menubar.addAction(self.menuMenu.menuAction())
		self.menubar.addAction(self.menuCtrl.menuAction())

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.menuMenu.setTitle(_translate("MainWindow", "o&pt"))
		self.menuCtrl.setTitle(_translate("MainWindow", "&ctrl"))
