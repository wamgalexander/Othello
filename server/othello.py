from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import pyqtSignal, QTimer
import functools
import sys
import constants
import os
import datetime
import numpy as np
import math


class QRightClickButton(QtWidgets.QPushButton):
	def __init__(self, parent):
		QtWidgets.QPushButton.__init__(self, parent)

	# custom define singal
	rightClicked = pyqtSignal()

class Ui_MainWindow(object):
####### declare variable #######
	playerColor = constants.BLACK
	state = constants.MAIN
	zoomInIndex = -1
	setting = False

	placed = [constants.EMPTY] * 64
	timer = []
	text = []
	grid = []
	blinkShelter = []
	current = []
	validMoveList = []
	curMove = []
	curBoard = []
	curPlayer = []
	curCmd = []
	curTime = ""

	screenWidth = 0
	screenHeight = 0
	startPosX = 0
	startPosY = 0
	buttonWidth = 0
	buttonHeight = 0
	spaceWidth = 0
	spaceHeight = 0
	resetButtonWidth = 0
	resetButtonHeight = 0
	resetButtonXPos = 0
	resetButtonYPos = 0
	returnButtonWidth = 0
	returnButtonHeight = 0
	returnButtonXPos = 0
	returnButtonYPos = 0
	freqXPos = 0
	freqYPos = 0
	playerXPos = 0
	playerYPos = 0

####### UI ########
	def setupUi(self, MainWindow):
		# set layout variable
		self.layoutSizeVar()
		# main window
		self.setMainWindow(MainWindow)
		# board
		self.setBoard()
		# refresh button
		self.setRefreshButton()
		# return button
		self.setReturnButton()
		# freq ctrl
		self.setFreqCtrl()
		# player trun window
		self.setPlayer()
		# state
		self.setState()
		# menubar
		self.setMenubar(MainWindow)
		# menu
		self.setMenu(MainWindow)
		# Shelter
		#self.setShelter()
		# timer
		self.setTimer()
		#init
		self.init()

####### Fuction #######
## blink ##
	def blink(self, block):
		self.blinkShelter[block].setVisible(False if self.blinkShelter[block].isVisible() else True)

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

## Block ##
	def showBlockGrid(self, block):
		self.blinkShelter[block].setVisible(False)

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
															"font: 550 40pt \"Helvetica\";"
															"color: white;")

## Zoom ##
	# zoom out
	def zoomOut(self):
		if(self.state == constants.ZOOM_IN1):
			self.hideAllGrids()
			for y in range(0, 8):
				for x in range(0, 8):
					XPos = self.startPosX + x * (self.buttonWidth+self.spaceWidth) + (constants.XSPACE if int(x / 4) else 0)
					YPos = self.startPosY + y * (self.buttonHeight+self.spaceHeight) + (constants.YSPACE if int(y / 4) else 0)
					self.grid[x + y * 8].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth, self.buttonHeight))
					self.grid[x + y * 8].setVisible(True)
			self.state = constants.MAIN
		elif(self.state == constants.ZOOM_IN2):
			self.hideAllGrids()
			self.zoomInIndex = constants.ZOOM_IN1_TABLE[self.zoomInIndex]
			for y in range(0, 4):
				for x in range(0, 4):
					XPos = self.startPosX + x * (self.buttonWidth+self.spaceWidth) * 2 + (constants.XSPACE if int(x / 2) else 0)
					YPos = self.startPosY + y * (self.buttonHeight+self.spaceHeight) * 2 + (constants.YSPACE if int(y / 2) else 0)
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth * 2, self.buttonHeight * 2))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)
			self.state = constants.ZOOM_IN1
		for i in range(0, 4):
			self.gridColor(i)

	# zoom in
	def zoomIn(self, grid):
		index = int(grid.objectName())
		if(self.state == constants.MAIN):
			self.zoomInIndex = constants.ZOOM_IN1_TABLE[index]
			self.state = constants.ZOOM_IN1
			self.hideAllGrids()
			for y in range(0, 4):
				for x in range(0, 4):
					XPos = self.startPosX + x * (self.buttonWidth+self.spaceWidth) * 2 + (constants.XSPACE if int(x / 2) else 0)
					YPos = self.startPosY + y * (self.buttonHeight+self.spaceHeight) * 2 + (constants.YSPACE if int(y / 2) else 0)
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth * 2, self.buttonHeight * 2))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)

		elif(self.state == constants.ZOOM_IN1):
			self.zoomInIndex = constants.ZOOM_IN2_TABLE[index]
			self.state = constants.ZOOM_IN2
			self.hideAllGrids()
			for y in range(0, 2):
				for x in range(0, 2):
					XPos = self.startPosX + x * (self.buttonWidth+self.spaceWidth) * 4 + (constants.XSPACE if x else 0)
					YPos = self.startPosY + y * (self.buttonHeight+self.spaceHeight) * 4 + (constants.YSPACE if y else 0)
					self.grid[self.zoomInIndex + x + y * 8].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth * 4, self.buttonHeight * 4))
					self.grid[self.zoomInIndex + x + y * 8].setVisible(True)

		for i in range(0, 4):
			self.gridColor(i)
## Click ##
	# on click event
	def eventFilter(self, obj, event):
		if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
			if event.button() == QtCore.Qt.LeftButton:
				return False
			elif event.button() == QtCore.Qt.RightButton:
				obj.rightClicked.emit()
				return False
		return False

	# left click
	def gridOnClick(self):
		self.placeChess(self.sender())

	# right click
	def gridOnRightClick(self):
		self.zoomIn(self.sender())

## action ##
	def init(self):
		self.playerColor = constants.BLACK
		self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))
		self.grid[68].setVisible(False)
		self.grid[69].setVisible(False)
		self.grid[68].setIcon(QtGui.QIcon(""))
		self.grid[69].setIcon(QtGui.QIcon(""))
		self.state = constants.MAIN
		self.zoomInIndex = -1
		for i in range (0, 64):
			self.placed[i] = constants.EMPTY
			self.grid[i].setStyleSheet("background-color:"+ constants.COLOR[1] +";")
		self.drawChess(self.grid[27], constants.WHITE)
		self.drawChess(self.grid[28], constants.BLACK)
		self.drawChess(self.grid[36], constants.WHITE)
		self.drawChess(self.grid[35], constants.BLACK)
		self.ValidMove()

	def restart(self):
		self.curMove = []
		self.curBoard = []
		self.curPlayer = []
		for i in range(0, 64):
			self.grid[i].setIcon(QtGui.QIcon())
			self.grid[i].setText("")
		while self.state != constants.MAIN:
			self.zoomOut()
		self.init()

	def placeChess(self, grid):
		pos = int(grid.objectName())

		if(self.placed[pos] != constants.EMPTY):
			return

		if(self.isValidMove(pos, True)):
			self.grid[68].setVisible(False)
			self.drawChess(grid, self.playerColor)
			self.curPlayer.append(self.playerColor)
			self.playerColor =  constants.BLACK if self.playerColor == constants.WHITE else constants.WHITE
			if self.playerColor == constants.WHITE:
				self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
			else:
				self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))
			if(self.ValidMove() == 0):
				self.curPlayer.append(self.playerColor)
				self.playerColor =  constants.BLACK if self.playerColor == constants.WHITE else constants.WHITE
				self.JudgeState(self.ValidMove())

	def drawChess(self, grid, color):
		if color == constants.WHITE:
			grid.setIcon(QtGui.QIcon("./src/white.png"))
		else:
			grid.setIcon(QtGui.QIcon("./src/black.png"))

		grid.setText("")
		self.placed[int(grid.objectName())] = color

	def hideAllGrids(self):
		for i in range(0, 64):
			self.grid[i].setVisible(False)

	def isOnBoard(self, x, y):
		fact = False
		if(0 <= x and x <= 7 and 0 <= y and y <= 7):
			fact = True
		return fact

	def reverseChess(self, pos_start):
		reverse_pos = []
		x_start, y_start = int(pos_start%8), int(pos_start/8)
		other = constants.BLACK if self.playerColor == constants.WHITE else constants.WHITE
		move_dir = [ [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1] ]
		for x_dir, y_dir in move_dir:
			x, y = x_start, y_start
			x += x_dir
			y += y_dir
			if (self.isOnBoard(x, y) and self.placed[x + y * 8] == other):
				x += x_dir
				y += y_dir
				if not self.isOnBoard(x, y):
					continue

				while self.placed[x + y * 8] == other:
					x += x_dir
					y += y_dir
					if not self.isOnBoard(x, y):
						break

				if not self.isOnBoard(x, y):
					continue

				if self.placed[x + y * 8] == self.playerColor:
					while True:
						x -= x_dir
						y -= y_dir
						if x == x_start and y == y_start:
						    break
						reverse_pos.append(x + y * 8)

		return reverse_pos

	def isValidMove(self, pos_start, isPlaceChess):
		if(not self.isOnBoard(int(pos_start%8), int(pos_start/8)) or self.placed[pos_start] != constants.EMPTY):
			return False

		self.placed[pos_start] = self.playerColor

		reverse_pos = self.reverseChess(pos_start)

		self.placed[pos_start] = constants.EMPTY

		if len(reverse_pos) == 0:
			return False

		if(isPlaceChess):
			self.curBoard.append(self.placed.copy())
			for pos in reverse_pos:
				self.drawChess(self.grid[pos], self.playerColor)
			self.curMove.append(pos_start)

		return True

	def ValidMove(self):
		self.current = self.validMoveList.copy()
		for pos in self.current:
			self.grid[pos].setStyleSheet("background-color:"+ constants.COLOR[1] +";")
			self.grid[pos].setText("")

		if(len(self.curMove) > 1):
			self.grid[self.curMove[-2]].setStyleSheet("background-color:"+ constants.COLOR[1] +";")

		if(len(self.curMove) > 0):
			self.grid[self.curMove[-1]].setStyleSheet("background-color:"+ constants.COLOR[0] +";")

		self.validMoveList = []
		for x in range(0, 8):
			for y in range(0, 8):
				pos = x + y * 8
				if(self.isValidMove(pos, False)):
					self.validMoveList.append(pos)

		L = range(0, int(len(self.validMoveList)/2))
		R = range(int(len(self.validMoveList)/2), len(self.validMoveList))

		for i in L:
			pos = self.validMoveList[i]
			self.grid[pos].setStyleSheet("border-color: rgb(255, 255, 255);"
										"font: 550 40pt \"Helvetica\";"
										"color: white;"
										"background-color:"+ constants.COLOR[2] +";")
			self.grid[pos].setText(str(i + 1))

		for i in R:
			pos = self.validMoveList[i]
			self.grid[pos].setStyleSheet("border-color: rgb(255, 255, 255);"
										"font: 550 40pt \"Helvetica\";"
										"color: black;"
										"background-color:"+ constants.COLOR[3] +";")
			self.grid[pos].setText(str(i + 1))

		return len(self.validMoveList)

	def SplitCheck(self):
			self.current = self.validMoveList.copy()
			for pos in self.current:
				self.grid[pos].setStyleSheet("background-color:"+ constants.COLOR[1] +";")
				self.grid[pos].setText("")

			if(len(self.curMove) > 1):
				self.grid[self.curMove[-2]].setStyleSheet("background-color:"+ constants.COLOR[1] +";")

			if(len(self.curMove) > 0):
				self.grid[self.curMove[-1]].setStyleSheet("background-color:"+ constants.COLOR[0] +";")

			self.validMoveList = []
			for x in range(0, 8):
				for y in range(0, 8):
					pos = x + y * 8
					if(self.isValidMove(pos, False)):
						self.validMoveList.append(pos)

			split_list = self.split_by_binary_serach(self.validMoveList, self.curCmd)
			if(len(self.curCmd) > 0 and self.curCmd[-1] == "X"):
				return split_list[0]

			L = range(0, int(len(split_list)/2))
			R = range(int(len(split_list)/2), len(split_list))

			for i in L:
				pos = split_list[i]
				self.grid[pos].setStyleSheet("border-color: rgb(255, 255, 255);"
											"font: 550 40pt \"Helvetica\";"
											"color: white;"
											"background-color:"+ constants.COLOR[2] +";")
				self.grid[pos].setText(str(i + 1))

			for i in R:
				pos = split_list[i]
				self.grid[pos].setStyleSheet("border-color: rgb(255, 255, 255);"
											"font: 550 40pt \"Helvetica\";"
											"color: black;"
											"background-color:"+ constants.COLOR[3] +";")
				self.grid[pos].setText(str(i + 1))

			return len(self.validMoveList)

	def split_by_binary_serach(self, target, commands):
		split_list = list(target)
		X_index = np.where(np.array(commands)=="X")

	    # cut off by "X"
		if len(X_index[0]) > 0:
			if X_index[0][-1] == len(commands) - 1:
				return split_list
			valid_commands = list(commands[X_index[0][-1]+1:])
		else:
			valid_commands = list(commands)

		for item in valid_commands:
			if len(split_list) == 1:
				commands.append("X")
				break
			index = math.floor(len(split_list)/2)
			if item == "2":
				split_list = split_list[:index]
			elif item == "3":
				split_list = split_list[index:]

			if len(split_list) == 1:
				continue

		return split_list

	def modification_date(self,filename):
	    t = os.path.getmtime(filename)
	    return datetime.datetime.fromtimestamp(t)

	def getCommand(self):
		t = self.modification_date('chess.txt')
		if(self.curTime != t):
			self.curTime = t
			f = open('chess.txt', 'r')
			cmd = f.read().splitlines()
			f.close()
			if(len(cmd)>0):
				if(cmd[-1] == "0"):
					self.grid[67].setIcon(QtGui.QIcon("./src/reject.png"))
					print(self.curCmd)
				elif(cmd[-1] == "1"):
					self.CommandRevert()
					if self.playerColor == constants.WHITE:
						self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
					else:
						self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))
				else:
					self.curCmd.append(cmd[-1])
					pos = self.SplitCheck()
					if self.playerColor == constants.WHITE:
						self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
					else:
						self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))
					print(self.curCmd)
					if(len(self.curCmd) > 0 and self.curCmd[-1] == "X"):
						self.placeChess(self.grid[pos])


	def CommandRevert(self):
		if (len(self.curCmd) > 0 and self.curCmd[-1] == "X"):
			self.curCmd.pop()
			self.BackToCurMove()
			self.curCmd.pop()

			self.SplitCheck()
			print(self.curCmd)
		else:
			if (len(self.curCmd) > 0):
				self.curCmd.pop()
				if(len(self.curCmd) > 0 and self.curCmd[-1] == "X"):
					self.ValidMove()
				else:
					self.SplitCheck()
				print(self.curCmd)

	def BackToCurMove(self):
		if(len(self.curMove) > 0):
			pos = self.curMove.pop()
			self.placed[pos] = constants.EMPTY
			self.grid[pos].setIcon(QtGui.QIcon(""))
			self.playerColor = self.curPlayer.pop()
			if self.playerColor == constants.WHITE:
				self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
			else:
				self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))

			self.placed = self.curBoard.pop()

			for x in range(0, 8):
				for y in range(0, 8):
					pos = x + y * 8
					if(self.placed[pos] == constants.BLACK):
						self.grid[pos].setIcon(QtGui.QIcon("./src/black.png"))
					elif(self.placed[pos] == constants.WHITE):
						self.grid[pos].setIcon(QtGui.QIcon("./src/white.png"))
					elif(self.placed[pos] == constants.EMPTY):
						self.grid[pos].setIcon(QtGui.QIcon(""))

			if(self.ValidMove()==0):
				if self.playerColor == constants.WHITE:
					self.grid[68].setIcon(QtGui.QIcon("./src/black.png"))
					self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
				else:
					self.grid[68].setIcon(QtGui.QIcon("./src/white.png"))
					self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))

	def JudgeState(self, state):
		if(state == 0):
			#game over
			b = self.placed.count(constants.BLACK)
			w = self.placed.count(constants.WHITE)
			if (w > b):
				self.grid[69].setIcon(QtGui.QIcon("./src/white.png"))
			elif (b > w):
				self.grid[69].setIcon(QtGui.QIcon("./src/black.png"))
			elif (b == w):
				self.grid[69].setText("平手")
			self.grid[69].setVisible(True)
			print(b,w,self.curPlayer[-1],'game over')
		elif(state > 0):
			#pass
			passPlayer = self.curPlayer.pop()
			if passPlayer == constants.WHITE:
				self.grid[68].setIcon(QtGui.QIcon("./src/white.png"))
			else:
				self.grid[68].setIcon(QtGui.QIcon("./src/black.png"))

			if self.playerColor == constants.WHITE:
				self.grid[67].setIcon(QtGui.QIcon("./src/white.png"))
			else:
				self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))

			self.grid[68].setVisible(True)

## freq ##
	def editFreq(self):
		for i in range(0, 4):
			constants.FREQ[i] = int(self.text[i].toPlainText())
			if(self.timer[i].isActive()):
				self.timer[i].stop()
			if(constants.FREQ[i] > 0):
				self.timer[i].start(constants.ONE_SEC/constants.FREQ[i])

	def showFreqControl(self, MainWindow):
		self.setting = not self.setting
		self.grid[66].setVisible(self.setting)
		for i in range(0, 4):
			self.text[i].setVisible(self.setting)

## Key ##
	def retranslateUi(self, MainWindow):
		# menu setting #
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

		self.setFreq.setText(_translate("MainWindow", "Set-Freq"))

		# set short-key #
		self.actionNew_Game.setShortcut(_translate("MainWindow", "Ctrl+N"))
		self.actionReturn.setShortcut(_translate("MainWindow", "Ctrl+R"))

		self.actionWhole_Board_ON.setShortcut(_translate("MainWindow", "Ctrl+E"))
		self.actionWhole_Board_OFF.setShortcut(_translate("MainWindow", "Ctrl+D"))

		self.actionUpper_Left_ON.setShortcut(_translate("MainWindow", "Ctrl+1"))
		self.actionUpper_Right_ON.setShortcut(_translate("MainWindow", "Ctrl+2"))
		self.actionLower_Left_ON.setShortcut(_translate("MainWindow", "Ctrl+3"))
		self.actionLower_Right_ON.setShortcut(_translate("MainWindow", "Ctrl+4"))

		self.setFreq.setShortcut(_translate("MainWindow", "Ctrl+F"))

## UI setting ##
	def layoutSizeVar(self):
		# creat timer
		for i in range(0, 4):
			self.timer.append(QTimer())

		# layout var
		r = QtWidgets.QDesktopWidget().screenGeometry()
		self.screenWidth = r.width()
		self.screenHeight = r.height()
		# constants.XSPACE = r.width() * (40/840)
		# constants.YSPACE = r.height() * (40/680)
		constants.XSPACE = 0
		constants.YSPACE = 0

		self.spaceWidth = self.screenWidth * (6/840)
		self.spaceHeight = self.screenHeight * (8/680)

		self.buttonWidth = self.screenWidth * (50/840)
		self.buttonHeight = self.screenHeight * (60/680)

		self.resetButtonWidth = self.screenWidth * (80/840)
		self.resetButtonHeight = self.screenHeight * (100/680)
		self.resetButtonXPos = self.screenWidth*(670/840) + constants.XSPACE
		self.resetButtonYPos = self.screenHeight*(30/680) + constants.YSPACE

		self.returnButtonWidth = self.screenWidth * (80/840)
		self.returnButtonHeight = self.screenHeight * (100/680)
		self.returnButtonXPos = self.screenWidth*(670/840) + constants.XSPACE
		self.returnButtonYPos = self.screenHeight*(160/680) + constants.YSPACE

		self.playerWidth = self.screenWidth * (80/840)
		self.playerHeight = self.screenHeight * (100/680)
		self.playerXPos = self.screenWidth*(670/840)+constants.XSPACE
		self.playerYPos = self.screenHeight*(300/680)+constants.YSPACE

		self.stateWidth = self.screenWidth * (80/840)
		self.stateHeight = self.screenHeight * (50/680)
		self.stateXPos = self.screenWidth*(670/840) + constants.XSPACE
		self.stateYPos = self.screenHeight*(450/680) + constants.YSPACE

		self.freqXPos = self.screenWidth*(670/840)+constants.XSPACE
		self.freqYPos = self.screenHeight*(470/680)+constants.YSPACE

		self.boardWidth = self.screenWidth * (670/840)
		self.boardHeight = self.screenHeight

		self.startPosX = self.screenWidth * (1/7)
		self.startPosY = self.screenHeight * (30/680)

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

	def setBoard(self):
		for y in range(0, 8):
			for x in range(0, 8):
				i = x + y * 8
				self.grid.append(QRightClickButton(self.centralwidget))
				XPos = self.startPosX + x * (self.buttonWidth+self.spaceWidth) + (constants.XSPACE if int(x / 4) else 0)
				YPos = self.startPosY + y * (self.buttonHeight+self.spaceHeight) + (constants.YSPACE if int(y / 4) else 0)
				self.grid[i].setGeometry(QtCore.QRect(XPos, YPos, self.buttonWidth, self.buttonHeight))
				self.grid[i].setStyleSheet("border-color: rgb(255, 255, 255);"
												"font: 550 40pt \"Helvetica\";"
												#"color: white;"
												#"background-color:"+ constants.COLOR[int(x / 4) + int(y / 4) * 2] +";")
												"background-color:"+ constants.COLOR[1] +";")
				#self.grid[i].setText(str(i + 1))
				self.grid[i].setAutoDefault(False)
				self.grid[i].setObjectName(str(i))
				self.grid[i].setIconSize(QtCore.QSize(55, 55))
				#  connect click event with gridOnClick
				self.grid[i].clicked.connect(self.gridOnClick)
				#  creat event filter
				self.grid[i].installEventFilter(self)
				#  connect right click event with gridOnRightClick
				self.grid[i].rightClicked.connect(self.gridOnRightClick)
				self.grid[i].setFocusPolicy(QtCore.Qt.NoFocus)

	def setRefreshButton(self):
		XPos = self.resetButtonXPos
		YPos = self.resetButtonYPos
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[64].setObjectName("refresh")
		self.grid[64].setGeometry(QtCore.QRect(XPos, YPos, self.resetButtonWidth, self.resetButtonHeight))
		self.grid[64].setIcon(QtGui.QIcon("./src/refresh.png"))
		self.grid[64].setIconSize(QtCore.QSize(55, 55))
		self.grid[64].setEnabled(True)
		self.grid[64].setAutoDefault(False)
		self.grid[64].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[64].clicked.connect(self.restart)
		self.grid[64].setStyleSheet("border-color: rgb(255, 255, 255);"
									"background-color: rgb(19, 146, 59);")

	def setReturnButton(self):
		XPos = self.returnButtonXPos
		YPos = self.returnButtonYPos
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[65].setObjectName("return")
		#self.grid[65].setText("")
		self.grid[65].setGeometry(QtCore.QRect(XPos, YPos, self.returnButtonWidth, self.returnButtonHeight))
		self.grid[65].setIcon(QtGui.QIcon("./src/return.png"))
		self.grid[65].setIconSize(QtCore.QSize(55, 55))
		self.grid[65].setEnabled(True)
		self.grid[65].setAutoDefault(False)
		self.grid[65].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[65].clicked.connect(self.BackToCurMove)
		self.grid[65].setStyleSheet("border-color: rgb(255, 255, 255);"
									"background-color: rgb(19, 146, 59);")

	def setFreqCtrl(self):
		# freq set button
		XPos = self.freqXPos
		YPos = self.freqYPos
		W = self.screenWidth*(90/840)
		H = self.screenHeight*(35/680)
		self.grid.append(QtWidgets.QPushButton(self.centralwidget))
		self.grid[66].setObjectName("set")
		self.grid[66].setText("Set")
		self.grid[66].setText(str(constants.FREQ[0]))
		self.grid[66].setGeometry(QtCore.QRect(XPos, YPos , W, H))
		self.grid[66].setEnabled(True)
		self.grid[66].setAutoDefault(False)
		self.grid[66].setVisible(False)
		self.grid[66].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[66].clicked.connect(self.editFreq)
		self.grid[66].setStyleSheet("background-color: rgb(0, 128, 255);"
								   "selection-color: rgb(128, 255, 0);"
								   "border-color: rgb(102, 102, 255);"
								   "font: 14pt \"Courier\";")

	# player turn window
	def setPlayer(self):
		XPos = self.playerXPos
		YPos = self.playerYPos
		self.grid.append(QRightClickButton(self.centralwidget))
		self.grid[67].setObjectName("Player")
		self.grid[67].setGeometry(QtCore.QRect(XPos, YPos, self.playerWidth, self.playerHeight))
		self.grid[67].setIcon(QtGui.QIcon("./src/black.png"))
		self.grid[67].setIconSize(QtCore.QSize(55, 55))
		self.grid[67].setEnabled(True)
		self.grid[67].setAutoDefault(False)
		self.grid[67].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[67].clicked.connect(self.restart)
		self.grid[67].setStyleSheet("border-color: rgb(255, 255, 255);"
									"background-color: rgb(19, 146, 59);")



		# freq ctrl
		for i in range(0, 4):
			XPos = self.screenWidth*(670/840) + (i%2) * self.screenWidth*(50/840) + constants.XSPACE
			YPos = self.screenHeight*(480/680) + int(i/2) * self.screenHeight*(50/680) + constants.YSPACE
			W = self.screenWidth*(40/840)
			H = self.screenHeight*(40/680)
			self.text.append(QtWidgets.QTextEdit(self.centralwidget))
			self.text[i].setObjectName(str(i))
			self.text[i].setText(str(constants.FREQ[i]))
			self.text[i].setGeometry(QtCore.QRect(XPos, YPos , W, H))
			self.text[i].setEnabled(True)
			self.text[i].setVisible(False)
			self.text[i].setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
			self.text[i].setStyleSheet("background-color: " + constants.COLOR[i] +";"
									   "border-color: rgb(102, 102, 255);"
									   "font: 14pt \"Courier\";")

	def setState(self):
		XPos = self.stateXPos
		YPos = self.stateYPos
		self.grid.append(QRightClickButton(self.centralwidget))
		self.grid[68].setText("Pass")
		self.grid[68].setObjectName("place state")
		self.grid[68].setGeometry(QtCore.QRect(XPos, YPos, self.stateWidth, self.stateHeight))
		self.grid[68].setIcon(QtGui.QIcon(""))
		self.grid[68].setIconSize(QtCore.QSize(30, 30))
		self.grid[68].setEnabled(True)
		self.grid[68].setAutoDefault(False)
		self.grid[68].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[68].setVisible(False)
		self.grid[68].setStyleSheet("border-color: rgb(255, 255, 255);"
									"background-color: rgb(19, 146, 59);")

		XPos = self.stateXPos
		YPos = self.stateYPos + self.stateHeight + self.spaceHeight
		self.grid.append(QRightClickButton(self.centralwidget))
		self.grid[69].setText("Win")
		self.grid[69].setObjectName("game state")
		self.grid[69].setGeometry(QtCore.QRect(XPos, YPos, self.stateWidth, self.stateHeight))
		self.grid[69].setIcon(QtGui.QIcon(""))
		self.grid[69].setIconSize(QtCore.QSize(30, 30))
		self.grid[69].setEnabled(True)
		self.grid[69].setAutoDefault(False)
		self.grid[69].setFocusPolicy(QtCore.Qt.NoFocus)
		self.grid[69].setVisible(False)
		self.grid[69].setStyleSheet("border-color: rgb(255, 255, 255);"
									"background-color: rgb(19, 146, 59);")

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

		self.setFreq = QtWidgets.QAction(MainWindow)
		self.setFreq.setObjectName("set_Frequence")
		self.setFreq.triggered.connect(functools.partial(self.showFreqControl, MainWindow))

		# set menu action #
		self.menuMenu.addAction(self.actionNew_Game)
		self.menuMenu.addAction(self.actionReturn)

		self.menuBlink.addAction(self.actionWhole_Board_ON)
		self.menuBlink.addAction(self.actionWhole_Board_OFF)
		self.menuBlink.addAction(self.actionUpper_Left_ON)
		self.menuBlink.addAction(self.actionUpper_Right_ON)
		self.menuBlink.addAction(self.actionLower_Left_ON)
		self.menuBlink.addAction(self.actionLower_Right_ON)

		self.menuBlink.addAction(self.setFreq)

		self.menuSettings.addAction(self.menuBlink.menuAction())
		self.menubar.addAction(self.menuMenu.menuAction())
		self.menubar.addAction(self.menuSettings.menuAction())

		# connect action slot to menu #
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def setShelter(self):
		# add shelter for blinking
		constants.BLOCK_WIDTH = self.buttonWidth * 4 + self.spaceWidth * 3
		constants.BLOCK_HEIGHT = self.buttonHeight * 4 + self.spaceHeight * 3
		for i in range(0, 4):
			self.blinkShelter.append(QtWidgets.QWidget(self.centralwidget))
			self.blinkShelter[i].setObjectName("shelter" + str(i))

			XPos = self.startPosX + ((constants.BLOCK_WIDTH + constants.XSPACE + self.spaceWidth) if (i % 2) else 0)
			YPos = self.startPosY + ((constants.BLOCK_HEIGHT + constants.YSPACE + self.spaceHeight) if (i > 1) else 0)
			self.blinkShelter[i].setGeometry(QtCore.QRect(XPos, YPos, constants.BLOCK_WIDTH, constants.BLOCK_HEIGHT))

	def setTimer(self):
		# connect QTimer
		# self.timer[0].timeout.connect(functools.partial(self.blink, block=constants.UPPER_LEFT))
		# self.timer[1].timeout.connect(functools.partial(self.blink, block=constants.UPPER_RIGHT))
		# self.timer[2].timeout.connect(functools.partial(self.blink, block=constants.LOWER_LEFT))
		# self.timer[3].timeout.connect(functools.partial(self.blink, block=constants.LOWER_RIGHT))
		self.timer[0].timeout.connect(self.getCommand)
		self.timer[0].start(0.25)
		# start QTimer (start to blink)
		# for i in range(0, 4):
		# 	self.timer[i].start(constants.ONE_SEC/constants.FREQ[i])

class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
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
    form = ExampleApp()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function
