#!/usr/bin/env python3
import threading
import select
import logging

from . import client
from . import history

# The purpose of this class is to present an abstract client
# Which we assume always connected
# Wheather there really is a client behind it or not

# This class handles the connecting and disconnecting of clients
# And allows only one connected client at a time

# This also handles sending the history when a new client is connected

class ClientSwapper:


	def __init__(self,controlsocket,history_len):

		self._controlSocket = controlsocket

		self._client = None

		self._clientLock = threading.Lock()

		self._history = history.History(history_len) # we store utf-8 strings, disabling this handled inside this class


	def _sendDataToClient(self,data): # this method requires external locking; data can be a single str, or a list of strings that would be transmitted to the client

		if self._client:

			try:

				if isinstance(data,list): # data is a list of strings
					self._client.sendLineList(data)
				elif isinstance(data,str): # data is a string itself
					self._client.sendLine(data)
				else:
					raise ValueError("Data must be a string, or a list of strings")

			except BrokenPipeError: # means the client is disconnected
				self._client = None
				logging.info("Client disconnected")



	# except utf-8 string
	def sendLine(self,line):
		with self._clientLock:
			self._sendDataToClient(line)

		self._history.addLine(line) # history class is thread safe


	# This method handles the accepting of clients
	# And reading new messages from the client
	# It only returns if there is a new message recieved, or the timeout expired
	# returns bytes
	def readLine(self,timeout=None):

		while True: # Don't worry, it will return


			selectable = [self._controlSocket.sock]

			if self._client:
				selectable += [self._client.sock]

			try:
				readable = select.select(selectable, [], [], timeout)[0] # waits for an event to happen, Note: even if the client is set to None by the line sender, this will hold a reference to the socket, however it should not be a problem, because a newly connecting client (or timeout) will trigger the event loop to continue, and at the next loop it will no longer wait on the dead socket

			except ValueError as e: # socked closed during the waiting
				logging.error("Value error in select: {} (Socket closed?)".format(str(e)))
				break

			with self._clientLock:

				if not readable: # timeout expired
					return None

				for s in readable: # timeout not expired

					if s is self._controlSocket.sock: # new connection request arrived

						cl = self._controlSocket.acceptClient()[0] # this returns a tuple of client and address, we only need the client descriptor

						logging.info("New client connected!")

						if self._client: # disconnect the session
							self._client.kick()
							logging.info("Previous session terminated")

						cl.setblocking(False) # this is needed because of the loop bellow, so it can be breaked when nothing else is left to read
						self._client = client.Client(cl)
						self._sendDataToClient(self._history.fetchLines()) # send the log if necessary

					elif self._client and s is self._client.sock: # new message arrived

						while True: # there might be more than one line in one message, we need to read them all

							try:

								line = self._client.readLine() # A value is only returned if a whole line is read, otherwise None is returned

								if line: # only if someting is actually read
									self._history.addLine(line + '\n') # add line to history before returning with it
									return line

								else: # nothing left to read
									break

							except (ConnectionResetError,BrokenPipeError): # connection to the client is lost
								self._client = None
								logging.info("Client disconnected")
								break # because client is set to none, the next loop would get exception


	# kick the user if connected
	# should be called before the shutdown of the program
	def close(self):
		with self._clientLock:
			if self._client:
				self._client.kick()
