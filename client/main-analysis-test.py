import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.signal import butter, lfilter
import glob, os, math, random
from builtins import range
from io import open
import time
import os.path


FS = 500
NFFT = 500
BAND_PASS_FILTER_ORDER = 10
BAND_PASS_FILTER_LOWCUT = 1
BAND_PASS_FILTER_HIGHCUT = 35
OVERLAP_RATIO = 0.5
DATA_LENGTH = 2              # length of each data : DATA_LENGTH * FS
FEATURE_NUM = 3

BASELINE = 0
ALPHA = 1
SIMULATION_6HZ = 2
SIMULATION_20HZ = 3
TEST = 99999


FEATURE_1_SCALE = 1
FEATURE_2_SCALE = 1
FEATURE_3_SCALE = 1

CLASS_NUM = 4

DELETE_MARK = 99999


def butter_bandpass_filter(signal, lowcut, highcut, fs, order):
	nyq = 0.5 * fs

	low = lowcut / nyq
	high = highcut / nyq

	b, a = butter(order, [low, high], btype='band', analog=True)
	y = lfilter(b, a, signal)
	return y

def load_data(file):
	# fetch data from file
	data = np.loadtxt(file)

	return data.copy()

def load_signal_data(file):
	data = np.loadtxt(file)
	data = preprocess(data)
	label = get_data_label(file)
	data = split_data(data, label)
	return data.copy()

def load_all_data():
	os.chdir("./")
	file_list = glob.glob("*.txt")

	data_list = np.array([[0] * (FEATURE_NUM + 1)])

	for file in file_list:
		# fetch data from file
		data = np.loadtxt(file)
		data = preprocess(data)
		label = get_data_label(file)
		data = split_data(data, label)
		data_list = np.concatenate((data_list, data), axis = 0)

	# remove header
	data_list = np.delete(data_list, 0, axis = 0)

	return data_list.copy()

def preprocess(input):
	return butter_bandpass_filter(input, BAND_PASS_FILTER_LOWCUT, BAND_PASS_FILTER_HIGHCUT, FS, BAND_PASS_FILTER_ORDER)

def split_data(input, label):
	input_with_zero_cent = input - np.mean(input)
	Pxx, freqs, bins, im = stft(input_with_zero_cent)
	time_len = int(math.floor(len(bins) / DATA_LENGTH))
	data = np.zeros((time_len, FEATURE_NUM + 1))

	# get feature
	for i in range(0, time_len):
		unit_Pxx = Pxx[:, (i * DATA_LENGTH): ((i + 1) * DATA_LENGTH)]
		features = get_feature(unit_Pxx, label)
		data[i] = features

	# remove some useless data
	wide_band_list = wide_band_detect(input, time_len)
	for i in wide_band_list:
		data[i] = np.array([DELETE_MARK] * (FEATURE_NUM + 1))
	if (label == BASELINE or label == ALPHA):
		data = data[11:16]
	else: # 6Hz , 20Hz or test
		data = data[9:19]
	remove_index = np.where(data[:, 0] == DELETE_MARK)
	data = np.delete(data, remove_index, 0)

	return data

def wide_band_detect(signal, time_len):
	mean = np.mean(signal)
	threshold = mean * 4 / 3.0
	lists = []

	for i in range(0, time_len):
		begin_index = i * FS
		end_index = (i + 1 ) * FS
		if np.max(signal[begin_index:end_index]) > threshold:
			lists.append(i)

	lists.extend([x+1 for x in lists])
	lists = list(set(lists))
	lists = [x for x in lists if x < time_len]

	return lists

def get_feature(input, label):
	Pxx = np.mean(input, axis=1)
	features = np.zeros(FEATURE_NUM + 1)

	features[0] = np.sum(Pxx[2:8])
	features[1] = np.sum(Pxx[9:12])
	features[2] = np.sum(Pxx[30:36])
	# or features ~ Pxx[12], np.sum(Pxx[15:24])
	features[3] = label

	return features

def get_data_label(input):
	if "baseline" in input:
		return BASELINE
	elif "alpha" in input:
		return ALPHA
	elif "look6" in input:
		return SIMULATION_6HZ
	elif "look20" in input:
		return SIMULATION_20HZ
	elif "test" in input:
		return TEST
	else:
		return -1

def stft(input):
	fig = plt.figure()
	Pxx, freqs, bins, im = plt.specgram(input, NFFT=NFFT, Fs=FS, noverlap=NFFT * OVERLAP_RATIO)
	fig.clear()
	plt.close(fig)
	return Pxx, freqs, bins, im


def nearest_neighbor_predict(input, setting, features_max, features_min):
	""" X is N x D where each row is an example we wish to predict label for """
	X = input.copy()
	num_test = X.shape[0]
	# lets make sure that the output type matches the input type
	Ypred = np.zeros(num_test)

	X[:, 0:FEATURE_NUM] = (X[:, 0:FEATURE_NUM] - features_min) / (features_max - features_min)
	X[:, 0:FEATURE_NUM][X[:, 0:FEATURE_NUM] > 1] = 1
	X[:, 0:FEATURE_NUM][X[:, 0:FEATURE_NUM] < 0] = 0

	#
	X[:, 0] *= FEATURE_1_SCALE
	X[:, 1] *= FEATURE_2_SCALE
	X[:, 2] *= FEATURE_3_SCALE

	# loop over all test rows
	for i in range(num_test):
		#distances = np.sum(np.abs(setting - X[i,:]), axis = 1)
		distances = np.sqrt(np.sum(np.square(setting - X[i,0:FEATURE_NUM]), axis = 1))
		#distances = np.square(setting[:, 1] - X[i, 1])
		min_index = np.argmin(distances) # get the index with smallest distance
		Ypred[i] = min_index

	return Ypred

def nearest_neighbor_train(input):
	data = input.copy()
	features = np.zeros((CLASS_NUM, FEATURE_NUM))
	counts = np.zeros(CLASS_NUM)

	# # normalize features
	features_max = np.max(data[:, 0:FEATURE_NUM], axis = 0)
	features_min = np.min(data[:, 0:FEATURE_NUM], axis = 0)
	data[:, 0:FEATURE_NUM] = (data[:, 0:FEATURE_NUM] - features_min) / (features_max - features_min)

	data[:, 0] *= FEATURE_1_SCALE
	data[:, 1] *= FEATURE_2_SCALE
	data[:, 2] *= FEATURE_3_SCALE

	for i in range(0, len(data)):
		features[int(data[i, FEATURE_NUM])] += data[i,0:FEATURE_NUM]
		counts[int(data[i, FEATURE_NUM])] += 1

	for i in range(0, 3):
		features[i] /= counts[i]

	return features, features_max, features_min


def cartesian(arrays, out=None):
	"""
	Generate a cartesian product of input arrays.

	Parameters
	----------
	arrays : list of array-like
	    1-D arrays to form the cartesian product of.
	out : ndarray
	    Array to place the cartesian product in.

	Returns
	-------
	out : ndarray
	    2-D array of shape (M, len(arrays)) containing cartesian products
	    formed of input arrays.

	Examples
	--------
	>>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
	array([[1, 4, 6],
	       [1, 4, 7],
	       [1, 5, 6],
	       [1, 5, 7],
	       [2, 4, 6],
	       [2, 4, 7],
	       [2, 5, 6],
	       [2, 5, 7],
	       [3, 4, 6],
	       [3, 4, 7],
	       [3, 5, 6],
	       [3, 5, 7]])

	"""

	arrays = [np.asarray(x) for x in arrays]
	dtype = arrays[0].dtype

	n = np.prod([x.size for x in arrays])
	if out is None:
		out = np.zeros([n, len(arrays)], dtype=dtype)

	m = n / arrays[0].size
	m = int(m)
	out[:,0] = np.repeat(arrays[0], m)
	if arrays[1:]:
		cartesian(arrays[1:], out=out[0:m,1:])
		for j in range(1, arrays[0].size):
			out[j*m:(j+1)*m,1:] = out[0:m,1:]
	return out

def setTimer(self):
	self.timer[0].timeout.connect(self.getCommand)
	self.timer[0].start(0.25)


setting = np.load("nn_setting.npy")
features_max = np.load("nn_features_max.npy")
features_min = np.load("nn_features_min.npy")

while (True):
	time.sleep(0.25)
	if (os.path.isfile("testing.txt")):
		data = load_signal_data("testing.txt")

		Y = nearest_neighbor_predict(data, setting, features_max, features_min)
		Y = Y.astype(int)

		score = np.zeros(CLASS_NUM)
		for i in range(0, CLASS_NUM):
			score[i] = len(Y[Y == i])

		mode_num = score[score == np.max(score)]
		if (len(mode_num) == 1):
			result = np.argmax(score)
		else:
			result = 0

		print (result)
		f = open("result.txt", "w")
		f.write(unicode(result))    # unicode, not bytes
		f.close()
		os.remove("testing.txt")
