import sys
import wx
import logging

# 1051108
import ctypes    #library used here for handling/accessing dlls
from scipy.signal import butter, filtfilt # 1051121

# The recommended way to use wx with mpl is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import numpy as np
import pylab
import threading
from threading import Timer

import socket
from time import sleep
import time
import functools
import os


global en_flag
en_flag = True


fs = 500
amplify = 100

# Butterworth filter
cutoff = 10
order = 5
windowLen = 2.5 * fs
overlap = 1 * fs

# -----------------------------------------------------------
# --------------------- 1051108 NIDAQ -----------------------
# -----------------------------------------------------------

#this loads the dll for the NIDAQ
nidaq = ctypes.windll.nicaiu

# typedefs are setup to correspond to NIDAQmx.h
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
written = int32()
pointsRead = uInt32()

#constants are setup to correspond to NIDAQmx.h
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByScanNumber = 1
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_Diff = 10106
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_RSE = 10083
DAQmx_Val_ChanForAllLines = 1

# initialize variables
taskHandle = TaskHandle(0)

#range of the DAQ
min1 = float64(-10.0)
max1 = float64(10.0)
timeout = float64(10.0)

#sampling rate
sampleRate = float64(fs)
samplesPerChan = uInt64(fs)

#specifiy the channels
global chan
chan = 'Dev1/ai0'
devChoice = ['Dev0/ai0', 'Dev1/ai0', 'Dev2/ai0', 'Dev3/ai0']
chanLen = 1
clockSource = ctypes.create_string_buffer('OnboardClock')


class NI:
	def __init__(self):
		self.initTask()

	# Check and print error msg
	def CHK(self, err):
		if err < 0:
			buf_size = 100
			buf = ctypes.create_string_buffer('\000' * buf_size)
			nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)

			logging.basicConfig(filename='test.log',
						filemode='a',
						format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
						datefmt='%H:%M:%S',
						level=logging.DEBUG)
			logging.info('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

			global en_flag
			en_flag = False
			print RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
			return -1

	def initTask(self):
		# set up the task in the required channel and
		#fix sampling through internal clock
		self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(taskHandle)))
		self.CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle, chan, "",
									   DAQmx_Val_Cfg_Default,
									   min1, max1, DAQmx_Val_Volts, None))
		self.CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle, clockSource, sampleRate,
			DAQmx_Val_Rising, DAQmx_Val_ContSamps, samplesPerChan))
		self.CHK(nidaq.DAQmxCfgInputBuffer(taskHandle, 200000))

		#Start Task
		self.CHK(nidaq.DAQmxStartTask (taskHandle))

	#Read Samples
	def ReadSamples(self, points):
		bufferSize = uInt32(points)
		pointsToRead = points
		data = np.empty(points)
		data.fill(np.float64(-1))
		self.CHK(nidaq.DAQmxReadAnalogF64(taskHandle, -1, timeout,
					DAQmx_Val_GroupByScanNumber, data.ctypes.data,
					uInt32(bufferSize.value), ctypes.byref(pointsRead), None))
		i = 0
		while i < data.size:
			if data[i] == np.float64(-1):
				break
			i += 1
		return data[:i]

	#stop and clear
	def StopAndClearTask(self):
		if taskHandle.value != 0:
			nidaq.DAQmxStopTask(taskHandle)
			nidaq.DAQmxClearTask(taskHandle)

	#On specifying the number of points to be sampled, it gets
	#the voltage value and returns it as a list data
	def get(self, points = fs):
		data = self.ReadSamples(points)
		for i in range(data.size):
			data[i] = data[i] * amplify
		return data

# -----------------------------------------------------------

class ComportPanel(wx.Panel):
	def __init__(self, parent, ID):
		wx.Panel.__init__(self, parent, ID)

		LSize = (150, 50)
		cpbox = wx.StaticBox(self, -1)
		cpsizer = wx.StaticBoxSizer(cpbox, wx.VERTICAL)
		self.file_text = wx.StaticText(self, -1, "File Name:")
		self.file_text.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, u'Consolas'))
		self.file_textctrl = wx.TextCtrl(self, -1,)
		self.dev_comboBox = wx.ComboBox(self, -1, size=LSize, choices=devChoice, style=wx.CB_DROPDOWN)
		self.dev_comboBox.SetFont(wx.Font(14, wx.DEFAULT, wx.SLANT, wx.NORMAL, 0, u'Consolas'))
		self.connect_button = wx.Button(self, -1, label="Connect", size=LSize)
		self.connect_button.SetFont(wx.Font(14, wx.DEFAULT, wx.SLANT, wx.NORMAL, 0, u'Consolas'))
		self.connect_button.SetForegroundColour("FOREST GREEN")
		self.disconnect_button = wx.Button(self, -1, label="Disconnect", size=LSize)
		self.disconnect_button.SetFont(wx.Font(14, wx.DEFAULT, wx.SLANT, wx.NORMAL, 0, u'Consolas'))
		self.disconnect_button.SetForegroundColour("RED")

		self.Bind(wx.EVT_BUTTON, parent.GetParent().connect, self.connect_button)
		self.Bind(wx.EVT_BUTTON, parent.GetParent().disconnect, self.disconnect_button)
		self.Bind(wx.EVT_COMBOBOX, parent.GetParent().devSelect, self.dev_comboBox)

		cptsizer = []
		for i in range(4):
			cptsizer.append(wx.BoxSizer(wx.HORIZONTAL))
			if i != 0:
				cptsizer[i].AddSpacer(30)
			else:
				cptsizer[0].Add(self.file_text)
				cptsizer[0].Add(self.file_textctrl)

		cptsizer[1].Add(self.dev_comboBox, wx.ALL|wx.ALIGN_CENTER_VERTICAL)
		cptsizer[2].Add(self.connect_button, wx.ALL|wx.ALIGN_CENTER_VERTICAL)
		cptsizer[3].Add(self.disconnect_button, wx.ALL|wx.ALIGN_CENTER_VERTICAL)

		for i in range(4):
			cpsizer.Add(cptsizer[i], 0, wx.ALL, 10)

		self.SetSizer(cpsizer)
		cpsizer.Fit(self)

class GraphFrame(wx.Frame):
	""" The main frame of the application
	"""
	title = 'Demo: dynamic matplotlib graph'
	T = []
	def __init__(self):
		wx.Frame.__init__(self, None, -1, self.title)

		self.showSPO2 = 0
		self.showPulse = 0
		self.paused = False
		self.plotData = [0]
		self.data_lock = threading.Lock()
		self.create_main_panel()
		self.flag = ""

		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
		self.redraw_timer.Start(fs)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.on_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, functools.partial(self.Send, msg='mode:On'), self.on_timer)

		self.off_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, functools.partial(self.Send, msg='mode:Off'), self.off_timer)

		self.check_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.check_file, self.check_timer)

		self.disconnect_timer = wx.Timer(self)
		self.T = []
		# self.T.append(self.on_timer)
		# self.T.append(self.off_timer)
		# self.T.append(self.disconnect_timer)


	def OnClose(self, event):
		global en_flag
		print "closing"
		en_flag = False
		self.Destroy()

	def create_main_panel(self):
		self.panel = wx.Panel(self)

		self.init_plot()
		self.canvas = FigCanvas(self.panel, -1, self.fig)

		self.comport_control = ComportPanel(self.panel,-1)
		self.comport_control.disconnect_button.Disable()

		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2.Add(self.comport_control, border=5, flag=wx.ALL)

		self.vbox = wx.BoxSizer(wx.HORIZONTAL)
		self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_CENTER | wx.TOP)
		self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)

		self.panel.SetSizer(self.vbox)
		self.vbox.Fit(self)

	def init_plot(self):
		self.dpi = 100
		self.fig = Figure((3.0, 3.0), dpi=self.dpi)
		self.axes = self.fig.add_subplot(111)
		self.fig.subplots_adjust(left=0.03, right=0.995, bottom = 0.03, top = 0.95)
		self.axes.set_axis_bgcolor('black')
		self.axes.set_title('MiniPSG', size=12)
		self.axes.get_yaxis().set_visible(True)
		self.axes.yaxis.set_ticks([ ])

		pylab.setp(self.axes.get_xticklabels(), fontsize=8)
		pylab.setp(self.axes.get_yticklabels(), fontsize=8)

		# plot the data as a line series, and save the reference
		# to the plotted line series
		#
		self.plot_data = []
		self.plot_data.extend(
			self.axes.plot(
				np.arange(len(self.plotData)),
				self.plotData[:],
				'r',
				linewidth=1,
			)
		)

	def draw_plot(self):
		""" Redraws the plot
		"""
		show_len = 30 * fs
		if self.data_lock.acquire():
			ymin = 0
			ymax = 300
			xmax = len(self.plotData) if len(self.plotData) > show_len else show_len
			xmin = xmax - show_len
			xmax = xmax/float(fs)
			xmin = xmin/float(fs)
			self.axes.set_xbound(lower=xmin, upper=xmax)
			self.axes.set_ybound(lower=ymin, upper=ymax)
			self.axes.grid(True, color='gray')

			pylab.setp(self.axes.get_xticklabels(), visible=True)

			if len(self.plotData) < show_len:
				self.plot_data[0].set_xdata(np.arange(0,len(self.plotData),1.0)/float(fs))
				self.plot_data[0].set_ydata(np.array(self.plotData))
			else:
				self.plot_data[0].set_xdata(np.arange(len(self.plotData)-show_len,len(self.plotData),1.0)/float(fs))
				self.plot_data[0].set_ydata(np.array(self.plotData[-show_len:]))

			self.data_lock.release()

		self.canvas.draw()

	def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #

		self.draw_plot()

	def on_exit(self, event):
		self.Destroy()

	def connect(self, event):
		global en_flag
		en_flag = True
		self.plotData = []

		if (self.check_timer.IsRunning()):
			self.check_timer.Stop()
		if self.comport_control.file_textctrl.GetValue()=="":
			filename = "./rawData/test.txt"
		else:
			filename = "./rawData/"+self.comport_control.file_textctrl.GetValue()+".txt"

		dataThread = SerialThread(self.plotData, self.data_lock, filename)
		self.comport_control.connect_button.Disable()
		self.comport_control.disconnect_button.Enable()
		dataThread.start()
		self.Bind(wx.EVT_TIMER, functools.partial(self.auto_disconnect, e=event), self.disconnect_timer)
		self.schedule()

	def schedule(self):
		self.on_timer.Start(5000)
		self.off_timer.Start(25000)
		self.disconnect_timer.Start(30000)

	def check_file(self, event):
		if(os.path.exists('result.txt')):
			f = open('result.txt', 'r')
			r = f.read().splitlines()
			result = 'result:' + r[0]
			self.SendTo(result)
			self.check_timer.Stop()
			f.close()
			#os.remove('result.txt')


	def auto_disconnect(self, event, e):
		self.disconnect(e)

	def Send(self, event, msg):
		self.SendTo(msg)

	def disconnect(self, event):
		global en_flag
		en_flag = False
		print(self.disconnect_timer.IsRunning())
		self.disconnect_timer.Stop()
		if(self.on_timer.IsRunning()):
			self.on_timer.Stop()
		if(self.off_timer.IsRunning()):
			self.off_timer.Stop()
		print("stop record",time.ctime())
		self.check_timer.Start(500)
		self.comport_control.connect_button.Enable()
		self.comport_control.disconnect_button.Disable()
		print "disconnect!"

	def SendTo(self, message):
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect the socket to the port where the server is listening
		#server_address = ('localhost', 10000)
		server_address = (sys.argv[1], 10000)
		print ('\n########################')
		print("send", time.ctime())
		print >>sys.stderr, 'connecting to %s port %s' % server_address
		sock.connect(server_address)

		try:
			# Send data
			#message = 'This is the message.  It will be repeated.'
			print ('------------------------')
			print >>sys.stderr, 'send: "%s"' % message
			sock.sendall(message)


			# # Look for the response
			# amount_received = 0
			# amount_expected = len(message)
			#
			# while amount_received < amount_expected:
			# 	data = sock.recv(16)
			# 	amount_received += len(data)
			# 	print >>sys.stderr, 'received "%s"' % data

		finally:
			#print >>sys.stderr, 'closing socket'
			if(message == 'mode:On'):
				print(self.on_timer.IsRunning())
				self.on_timer.Stop()
			elif(message == 'mode:Off'):
				print(self.off_timer.IsRunning())
				self.off_timer.Stop()
			print ('########################')
			sock.close()

	def devSelect(self, event):
		global chan
		index = event.GetSelection()
		chan = devChoice[index]
		print chan

class SerialThread (threading.Thread):
	def __init__(self, data, data_lock, savename):
		threading.Thread.__init__(self)
		self.data_lock = data_lock
		self.fd = open(savename, 'w')
		self.plotData = data
		self.filtedData = np.array([])
		self.epochData = np.array([])
		self.rawData = []
		self.BP_filter = butter_BPFilter(cutoff, order)

	def run(self):
		global en_flag

		ni = NI()
		try:
			print("data", time.ctime())
			while en_flag:
				data = ni.get()
				if data.size != 0:
					self.filtedData = np.append(self.filtedData, data)
					self.WriteData(data)

				if self.filtedData.size >= windowLen:
					break

			self.filtedData = self.BP_filter.butter_bandpass_filter(self.filtedData)
			self.plotData.extend(self.filtedData)
			self.epochData = self.filtedData[-windowLen:]
			self.filtedData = np.array([])

			while en_flag:
				try:
					data = ni.get()
					if data.size != 0:
						self.filtedData = np.append(self.filtedData, data)
						self.WriteData(data)
					if self.filtedData.size >= (overlap):
						self.filtedData = self.BP_filter.butter_bandpass_filter(self.filtedData)
						self.epochData[:-self.filtedData.size] = self.epochData[self.filtedData.size:]
						self.epochData[-self.filtedData.size:] = self.filtedData
						self.plotData.extend(self.filtedData)
						self.filtedData = np.array([])
				except Exception as ex:
					print ex
					logging.basicConfig(filename='test.log',
								filemode='a',
								format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
								datefmt='%H:%M:%S',
								level=logging.DEBUG)
					logging.info("NI exception")
		except Exception as ex:
			print ex
			ni.StopAndClearTask()
			en_flag = False

		ni.StopAndClearTask()
		self.fd.close()

	def WriteData(self, data):
		out = []

		i = 0
		while i < data.size:
			out.append(str(data[i]))
			i += 1

		out = "\n".join(out)
		out = out+"\n"
		self.fd.write(out)

class butter_BPFilter:
	def __init__(self, cutoff, order):
		self.cutoff = cutoff
		self.order = order
		self.b, self.a = self.butter_bandpass()

	def butter_bandpass(self):
		nyq = 0.5 * fs
		b, a = butter(self.order, self.cutoff / nyq, btype='low')
		return b, a

	def butter_bandpass_filter(self, data):
		y = filtfilt(self.b, self.a, data)
		return y





if __name__ == '__main__':
	logging.basicConfig(filename='test.log',
							filemode='a',
							format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
							datefmt='%H:%M:%S',
							level=logging.DEBUG)
	logging.info("Open panel")
	app = wx.PySimpleApp()
	app.frame = GraphFrame()
	app.frame.Show()
	app.MainLoop()
