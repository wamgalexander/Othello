import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (sys.argv[1], 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
	print >>sys.stderr, 'waiting for a connection'
	connection, client_address = sock.accept()
	try:
		print >>sys.stderr, 'connection from', client_address

		# Receive the data in small chunks and retransmit it
		recv = ""
		while True:
			data = connection.recv(16)
			if data:
				print(time.ctime())
				print >>sys.stderr, 'received: "%s"' % data
				recv += data
			else:
				break


		if(recv == 'mode:On'):
			f = open('config.txt', 'r')
			cmd = f.read().splitlines()
			f.close()
			f = open('config.txt', 'w')
			cmd[0] = '1'
			for c in cmd:
				c += '\n'
				f.write(c)
			f.close()
		elif(recv == 'mode:Off'):
			f = open('config.txt', 'r')
			cmd = f.read().splitlines()
			f.close()
			f = open('config.txt', 'w')
			cmd[0] = '0'
			for c in cmd:
				c += '\n'
				f.write(c)
			f.close()
		elif(recv == 'result:0'):
			result = open('chess.txt', 'a')
			result.write('0\n')
			result.close()
		elif(recv == 'result:1'):
			result = open('chess.txt', 'a')
			result.write('1\n')
			result.close()
		elif(recv == 'result:2'):
			result = open('chess.txt', 'a')
			result.write('2\n')
			result.close()
		elif(recv == 'result:3'):
			result = open('chess.txt', 'a')
			result.write('3\n')
			result.close()
			# if data:
			# 	print >>sys.stderr, 'sending data back to the client'
			# 	connection.sendall(data)
			# else:
			# 	print >>sys.stderr, 'no more data from', client_address
			# 	break

	finally:
		# Clean up the connection
		connection.close()
