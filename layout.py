# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'othello.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

class QRightClickButton(QtWidgets.QPushButton):
	def __init__(self, parent):
		QtWidgets.QPushButton.__init__(self, parent)
	rightClicked = pyqtSignal()

class Ui_MainWindow(object):

	def eventFilter(self, obj, event):
		if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
			if event.button() == QtCore.Qt.LeftButton:
				return False
			elif event.button() == QtCore.Qt.RightButton:
				obj.rightClicked.emit()
				return False
		return False
	def gridOnClick(self):
		 print("Button " + str(self.sender().objectName()) + " left clicked")

	def gridOnRightClick(self):
         print("Button " + str(self.sender().objectName()) + " right clicked")

	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(640, 640)
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
				self.grid[x + y * 8].setText("")
				self.grid[x + y * 8].setAutoDefault(False)
				self.grid[x + y * 8].setObjectName(str(x+y*8))
				self.grid[x + y * 8].setMouseTracking(True)
				self.grid[x + y * 8].clicked.connect(self.gridOnClick)
				self.grid[x + y * 8].installEventFilter(self)
				self.grid[x + y * 8].rightClicked.connect(self.gridOnRightClick)
#				connect(self.grid[x + y * 8], SIGNAL(onRightClick), self.grid[x + y * 8], SLOT(gridOnRightClick))
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
