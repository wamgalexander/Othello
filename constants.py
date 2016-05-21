
# state
MAIN = 0
ZOOM_IN1 = 1
ZOOM_IN2 = 2


ZOOM_IN1_TABLE = [ 0,  0,  0,  0,  4,  4,  4,  4, \
				   0,  0,  0,  0,  4,  4,  4,  4, \
				   0,  0,  0,  0,  4,  4,  4,  4, \
				   0,  0,  0,  0,  4,  4,  4,  4, \
				  32, 32, 32, 32, 36, 36, 36, 36, \
				  32, 32, 32, 32, 36, 36, 36, 36, \
				  32, 32, 32, 32, 36, 36, 36, 36, \
				  32, 32, 32, 32, 36, 36, 36, 36]

ZOOM_IN2_TABLE = [ 0,  0,  2,  2,  4,  4,  6,  6, \
				   0,  0,  2,  2,  4,  4,  6,  6, \
				  16, 16, 18, 18, 20, 20, 22, 22, \
				  16, 16, 18, 18, 20, 20, 22, 22, \
				  32, 32, 34, 34, 36, 36, 38, 38, \
				  32, 32, 34, 34, 36, 36, 38, 38, \
				  48, 48, 50, 50, 52, 52, 54, 54, \
				  48, 48, 50, 50, 52, 52, 54, 54]


ZOOM_TABLE = [[0]*64, ZOOM_IN1_TABLE, ZOOM_IN2_TABLE]

EMPTY = 0
BLACK = 1
WHITE = 2
ONE_SEC = 1000/2

FREQ = [10, 15, 20, 25]

MAIN_BLOCK = [0, 4, 32, 36]
ZOOM_IN1_BLOCK = [0, 2, 16, 18]
ZOOM_IN2_BLOCK = [0, 1, 8, 9]
ZOOM_COLOR_BLOCK = [MAIN_BLOCK, ZOOM_IN1_BLOCK, ZOOM_IN2_BLOCK]

ZOOM_LENGTH = [4, 2, 1]
MAIN_BLOCK_LENGTH = 4
ZOOM_IN1_BLOCK_LENGTH = 2
ZOOM_IN2_BLOCK_LENGTH = 1

ZOOM_WRAP = [32, 16, 1]
CROSS_BLOCK_LENGTH = 2

ZOOM_END_STATE = [ZOOM_IN2, MAIN]
MOVE_STATE = [1, -1]

UPPER_LEFT = 0
UPPER_RIGHT = 1
LOWER_LEFT = 2
LOWER_RIGHT = 3

OFF = 0
ON = 1

NO_SENDER = -1

COLOR = ["rgb(255, 91, 42)", "rgb(152, 236, 104)", "rgb(255, 141, 255)", "rgb(143, 243, 255)", "rgb(143, 143, 143)"]

XSPACE = 40.0
YSPACE = 40.0

BLOCK_WIDTH = 275 #60 * 4 + 5 * 3
BLOCK_HEIGHT = 275 # 60 * 4 + 5 * 3
