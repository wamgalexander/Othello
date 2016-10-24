"""
This demo demonstrates how to draw a dynamic mpl (matplotlib)
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value
affect the plot.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008
"""
import os
import pprint
import random
import sys
import wx
import logging
from scipy.signal import butter, lfilter

# The recommended way to use wx with mpl is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
import serial
import threading

global en_flag
en_flag = True



class ComportPanel(wx.Panel):
	def __init__(self, parent, ID):
		wx.Panel.__init__(self, parent, ID)

		cpbox = wx.StaticBox(self, -1)
		cpsizer = wx.StaticBoxSizer(cpbox, wx.VERTICAL)
		self.com_port_text = wx.StaticText(self, -1, "COM port:")
		self.com_port_text.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, u'Consolas'))
		self.com_port_textctrl = wx.TextCtrl(self, -1,)
		self.file_text = wx.StaticText(self, -1, "File Name:")
		self.file_text.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, u'Consolas'))
		self.file_textctrl = wx.TextCtrl(self, -1,)
		self.connect_button = wx.Button(self, -1, label="Connect", size=(150,50))
		self.connect_button.SetFont(wx.Font(14, wx.DEFAULT, wx.SLANT, wx.NORMAL, 0, u'Consolas'))
		self.connect_button.SetForegroundColour("FOREST GREEN")
		self.disconnect_button = wx.Button(self, -1, label="Disconnect",size=(150, 50))
		self.disconnect_button.SetFont(wx.Font(14, wx.DEFAULT, wx.SLANT, wx.NORMAL, 0, u'Consolas'))
		self.disconnect_button.SetForegroundColour("RED")
		self.Bind(wx.EVT_BUTTON, parent.GetParent().connect, self.connect_button)
		self.Bind(wx.EVT_BUTTON, parent.GetParent().disconnect, self.disconnect_button)


		cptsizer = wx.BoxSizer(wx.HORIZONTAL)
		cptsizer.Add(self.com_port_text,wx.ALL|wx.ALIGN_LEFT)
		cptsizer.Add(self.com_port_textctrl,wx.ALL|wx.ALIGN_LEFT)
		cptsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		cptsizer2.Add(self.file_text)
		cptsizer2.Add(self.file_textctrl)
		cptsizer3 = wx.BoxSizer(wx.HORIZONTAL)
		cptsizer3.AddSpacer(30)
		cptsizer3.Add(self.connect_button,wx.ALL|wx.ALIGN_CENTER_VERTICAL)
		cptsizer4 = wx.BoxSizer(wx.HORIZONTAL)
		cptsizer4.AddSpacer(30)
		cptsizer4.Add(self.disconnect_button,wx.ALL|wx.ALIGN_CENTER_VERTICAL)

		cpsizer.Add(cptsizer, 0, wx.ALL, 20)
		cpsizer.Add(cptsizer2, 0, wx.ALL, 20)
		cpsizer.Add(cptsizer3, 0, wx.ALL, 20)
		cpsizer.Add(cptsizer4, 0, wx.ALL, 20)

		self.SetSizer(cpsizer)
		cpsizer.Fit(self)

class GraphFrame(wx.Frame):
	""" The main frame of the application
	"""
	title = 'Demo: dynamic matplotlib graph'

	def __init__(self):
		wx.Frame.__init__(self, None, -1, self.title)

		self.showSPO2 = 0
		self.showPulse = 0
		self.paused = False
		self.rawData = list()
		self.rawData = [[0],[0],[0]]
		self.dataLen = list()
		self.dataLen = [1]
		self.showLen = list()
		self.showLen = [1,1]
		self.ser = list()
		self.data_lock = threading.Lock()
		self.create_main_panel()
		self.offset = [0]

		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
		self.redraw_timer.Start(100)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		global en_flag
		#self.WriteData(False,50)
		print("closing")
		en_flag = False
		self.Destroy()

		#dataThread.WriteData(False,50)


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
		#self.axes.yaxis.set_ticks([0,255,511,767,1023,1279,1535,1791,2047])
		self.axes.yaxis.set_ticks([ ])

		pylab.setp(self.axes.get_xticklabels(), fontsize=8)
		pylab.setp(self.axes.get_yticklabels(), fontsize=8)


		# plot the data as a line series, and save the reference
		# to the plotted line series
		#
		self.plot_data = []
		for order in range(3):
			if order%2 == 0:
				self.plot_data.extend(
					self.axes.plot(
						np.arange(self.showLen[0]),
						self.rawData[order][:],
						'y',
						linewidth=1,
						)
					)
			else:
				self.plot_data.extend(
					self.axes.plot(
						np.arange(self.showLen[0]),
						self.rawData[order][:],
						'#77DDFF',
						linewidth=1,

						)
					)


	def draw_plot(self):
		""" Redraws the plot
		"""
		show_len = 7500
		fs = 200
		points = 15*fs
		#print self.dataLen[0]
		if self.data_lock.acquire():
			ymin = 0
			ymax = 800
			xmax = self.showLen[0] if self.showLen[0] > show_len else show_len
			xmin = xmax - show_len
			xmax = xmax/float(fs)
			xmin = xmin/float(fs)
			self.axes.set_xbound(lower=xmin, upper=xmax)
			self.axes.set_ybound(lower=ymin, upper=ymax)
			self.axes.grid(True, color='gray')

			pylab.setp(self.axes.get_xticklabels(),
				visible=True)


			if self.showLen[0] < show_len:
				for order in range(3):
					self.plot_data[order].set_xdata(np.arange(0,self.showLen[0],1.0)/float(fs))
					#print len(np.arange(0,self.showLen[0],1.0))
					self.plot_data[order].set_ydata(np.array(self.rawData[order])+np.array((order * 255)))
					# modified by Wei (order+1)

					#print len(np.array(self.rawData[order])+np.array(order * 255))
			else:
				for order in range(3):
					self.plot_data[order].set_xdata(np.arange(self.showLen[0]-show_len,self.showLen[0],1.0)/float(fs))
					self.plot_data[order].set_ydata(np.array(self.rawData[order][-show_len:])+np.array((order * 255)))
					# modified by Wei (order+1)


			self.data_lock.release()

		self.canvas.draw()




	def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
		#if not self.paused:
			#self.serData.append(self.datagen.next())
		self.draw_plot()


	def on_exit(self, event):
		self.Destroy()


	def connect(self, event):
		global en_flag
		en_flag = True
		self.dataLen[0] = 1
		self.showLen[0] = 0
		self.showLen[1] = 0


		for i in range(3):
			del self.rawData[i][:]
			self.rawData[i].extend([])
		self.offset = [0]
			#print self.rawData[i]

		if self.comport_control.com_port_textctrl.GetValue()=="" or self.comport_control.file_textctrl.GetValue()=="":
			return

		port="COM"+self.comport_control.com_port_textctrl.GetValue()
		filename = self.comport_control.file_textctrl.GetValue()+".txt"

		try:
			self.ser=serial.Serial(port, 115200)
			print(port)
		except Exception as ex:
			print(ex)
			return

		dataThread = SerialThread(self.ser, self.rawData, self.dataLen, self.data_lock, self.showLen, filename)
		self.comport_control.connect_button.Disable()
		self.comport_control.disconnect_button.Enable()
		dataThread.start()

	def disconnect(self, event):
		#self.ser.close()
		global en_flag
		en_flag = False
		#self.ser.close()
		self.comport_control.connect_button.Enable()
		self.comport_control.disconnect_button.Disable()
		print("disconnect!")


class SerialThread (threading.Thread):

	def __init__(self, ser, data, length, data_lock,slen, savename):
		threading.Thread.__init__(self)
		self.ser = ser
		self.rawData = list()
		self.rawData = data
		#print self.rawData[0]
		self.dataLen = length
		self.data_lock = data_lock
		self.showLen = slen
		self.fileLen = 0
		self.writeIndex = 0
		self.filename = savename
		#print self.filename

	def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
	    nyq = 0.5 * fs
	    low = lowcut / nyq
	    high = highcut / nyq

	    b, a = butter(order, [low, high], btype='band')
	    y = lfilter(b, a, data)
	    return y

	def run(self):
		packet = Package(self.ser)
		while en_flag:
			try:
				packet.load()
			except Exception as ex:
				print(ex)
				logging.basicConfig(filename='test.log',
							filemode='a',
							format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
							datefmt='%H:%M:%S',
							level=logging.DEBUG)
				logging.info("Packet exception")

			if self.data_lock.acquire():
				# filtering recevied data
				filtered_data = [] * 3
				for i in range(3):
					filtered_data[i] = butter_bandpass_filter(packet.psgData[i], 5, 30, 200)

				for i in range(3):
					self.rawData[i].extend(filtered_data[i])
				self.dataLen[0] = self.dataLen[0]+28
				self.showLen[0] = packet.dlen
				#print "rawData[0]"
				#print self.rawData[0]
				if len(self.rawData[0]) > 30000:
				#if len(self.serData) > 30000:
					print("write file")
					logging.basicConfig(filename='test.log',
							filemode='a',
							format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
							datefmt='%H:%M:%S',
							level=logging.DEBUG)
					logging.info("write file")
					self.WriteData(True,15000)

				self.data_lock.release()
		#write last data into file and send a ket to WriteData
		self.WriteData(False,50)
		self.ser.close()
		print("out")

	def WriteData(self, key, write_len = None):
		offset = 0
		if os.path.exists(self.filename):
			fd = open(self.filename, 'a')
		else:
			fd = open(self.filename, 'w+')
		wd = list()
		out = list()

		if key:
			index=0
			while index < write_len:
				for i in range(3):
					self.rawData[i][index] = self.rawData[i][index]  + offset
					wd.append(str(self.rawData[i][index]))
				out.append("\t".join(wd))
				del wd[:]
				index += 1

			out = "\n".join(out)
			out = out+"\n"
			fd.write(out)
			fd.close()
			for i in range(3):
				del self.rawData[i][:write_len]
		else:
			index = 0
			print("last")

			while index < len(self.rawData[0]):
				for i in range(3):
					self.rawData[i][index] = self.rawData[i][index]  + offset
					wd.append(str(self.rawData[i][index]))
				out.append("\t".join(wd))
				del wd[:]
				index += 1
			out = "\n".join(out)
			fd.write(out)
			fd.close()



class Package:
	def __init__(self, ser):
		self.ser = ser
		self.dlen = 0
		self.psgData = list()
		self.psgData = [[],[],[]]
		self.dataSeq = [0,1,2]		# modified by Wei
		self.lastSeq = 0
		self.drop = 0
		self.firstPackage = 0

		for i in range(3):
			self.psgData[i].extend([0])

	def load(self):
		self.first = ord(self.ser.read())

		while True:
			if self.first ==0x04: #4
				self.seq = ord(self.ser.read())
				self.second = ord(self.ser.read())
				if self.second == 0x54:#86
					self.third = ord(self.ser.read())
					if self.third == 0x81:#129
						self.alldata = map(ord, self.ser.read(84))
						break
					else:
						self.first = self.third
				else:
					self.first = self.second
			else:
				self.first = ord(self.ser.read())

		for j in range(3):
			self.psgData[j] = self.alldata[self.dataSeq[j]::3]
			#print "data"+str(self.psgData[j])
		self.dlen = self.dlen+28


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
