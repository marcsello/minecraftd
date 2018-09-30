#!/usr/bin/env python3

import socket
import os
import logging

class ControlSocket:

	def __init__(self,socket_path): # throws: FileNotFoundError, PermissionError
		self.__socket_path = socket_path

		if os.path.exists(self.__socket_path):
			logging.log(logging.DEBUG, "Removing leftover socket file from previous run")
			os.remove(self.__socket_path)

		self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) # making it public for selector to work

		self.sock.bind(self.__socket_path) # throws: FileNotFoundError, PermissionError

		self.sock.listen(5) # why 5? dunno, python manual said iz fine

		os.chmod(self.__socket_path, 0o660) # only users from the same group may access to this


	def getSocketPath(self):
		return self.__socket_path


	def acceptClient(self): # waits for a client
		return self.sock.accept()


	def close(self):
		self.sock.close()
		os.remove(self.__socket_path)
