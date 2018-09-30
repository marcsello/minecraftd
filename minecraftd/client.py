#!/usr/bin/env python3
from . import bettersocket

class Client():

	def __init__(self,cl_sock):

		self.sock = cl_sock
		self._reader = bettersocket.BetterSocketReader(self.sock)
		self._active = True


	def kick(self):
		if self._active:
			self.sock.close()
			self._active = False


	def readLine(self): # returns: unicode str
		if not self._active:
			raise ConnectResetError() # client was kicked, and the connection closed

		return self._reader.readline().decode('utf-8')


	def sendLine(self,line): # accepts: unicode str
		if self._active:
			self.sock.sendall(line.encode('utf-8'))
