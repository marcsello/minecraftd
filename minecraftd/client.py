#!/usr/bin/env python3
from . import bettersocket

class Client():

	def __init__(self,cl_sock):

		self.sock = cl_sock
		self._reader = bettersocket.BetterSocketReader(self.sock)
		self._writer = bettersocket.BetterSocketWriter(self.sock)
		self._active = True


	def kick(self):
		if self._active:
			self.sock.close()
			self._active = False


	def readLine(self): # returns: unicode str
		if not self._active:
			raise ConnectResetError() # client was kicked, and the connection closed

		line = self._reader.readline() # none is returned, if there wasn't a whole line to reard

		if line: # if not None then decode
			return line.decode('utf-8')
		else:
			return None


	def sendLine(self,line): # accepts: unicode str
		if self._active:
			self._writer.sendall(line.encode('utf-8'))


	def sendLineList(self,line_list):

		if line_list: # don't send empty list
			for line in line_list:
				self.sendLine(line)
