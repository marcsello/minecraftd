#!/usr/bin/env python3
import socket
import select

#
# This reader handles reading from a scoket "line-by-line"
#

class BetterSocketReader():

	def __init__(self,_sock,delimiter=b"\n"):

		if len(delimiter) != 1:
			raise ProgrammingError("Delimiter must be 1 byte long")


		if not isinstance(_sock,socket.socket):
			raise TypeError("Socket must be an instance of socket.socket")


		self._sock = _sock
		self._buffer = bytes()
		self._delimiter = delimiter


	def _popOneFromBuffer(self):

		if self._delimiter in self._buffer:
			pos = self._buffer.find(self._delimiter)

			data = self._buffer[:pos] # data from the beginning until the delimtiter
			self._buffer = self._buffer[pos+1:] # skip delimiter

			return data

		return None


	def readline(self,chunksize=1024): # timeouting and nonblocking sockets both expected as well as blocking, expected to be called in a loop

		data = self._popOneFromBuffer() # before recieve, check if there is a valid data in the buffer
		if data:
			return data

		# actual recieving won't start until there is no more valid message left in the buffer

		try:
			chunk = self._sock.recv(chunksize) # recieve a chunk
		except socket.timeout:
			return None
		except socket.error as e:
			if e.errno == socket.errno.EWOULDBLOCK: # nothing to read
				return None
			else:
				raise # everything else should be raised

		if chunk:
			self._buffer += chunk # append the recieved chunk to the buffer
			return self._popOneFromBuffer() # and check if a valid message recieved
		else:
			raise ConnectionResetError() # chunk is only none when the connection is dropped



#
# This writer handles Sending to nonblocking sockets properly
#

class BetterSocketWriter():

	def __init__(self,_sock):

		if not isinstance(_sock,socket.socket):
			raise TypeError("Socket must be an instance of socket.socket")

		self._sock = _sock


	def sendall(self,data):

		writable = select.select([],[self._sock],[])[1]

		if writable:
			self._sock.sendall(data)