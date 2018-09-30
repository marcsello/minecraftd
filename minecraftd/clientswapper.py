#!/usr/bin/env python3
import threading
import select
import client
import logging

# The purpose of this class is to present an abstract client
# Which we assume always connected
# Wheather there really is a client behind it or not

# This class handles the connecting and disconnecting of clients
# And allows only one connected client at a time


class ClientSwapper:


	def __init__(self,controlsocket):

		self._controlSocket = controlsocket

		self._client = None

		self._clientLock = threading.Lock()


	def sendLine(self,line):
		with self._clientLock:
			if self._client:
				try:
					self._client.sendLine(line)

				except BrokenPipeError: # means the client is disconnected
					self._client = None
					logging.info("Client disconnected")



	# This method handles the accepting of clients
	# And reading new messages from the client
	# It only returns if there is a new message recieved, or the timeout expired
	def readLine(self,timeout=None):

		while True: # Don't worry, it will return


			selectable = [self._controlSocket.sock]

			if self._client:
				selectable += [self._client.sock]

			try:
				readable, writeable, errored = select.select(selectable, [], [], timeout) # waits for an event to happen

			except ValueError as e: # socked closed during the waiting
				logging.error("Value error in select: {} (Socket closed?)".format(str(e)))
				break


			if not readable: # timeout expired
				return None

			for s in readable: # timeout not expired

				if s is self._controlSocket.sock: # new connection request arrived

					with self._clientLock:

						cl,addr = self._controlSocket.acceptClient()

						logging.info("New client connected!")

						if self._client: # disconnect the session
							self._client.kick()
							logging.info("Previous session terminated")

						self._client = client.Client(cl)


				elif self._client and s is self._client.sock: # new message arrived

					with self._clientLock:

						try:

							line = self._client.readLine() # A value is only returned if a whole line is read, otherwise None is returned

							if line: # only if someting is actually read
								return line

						except (ConnectionResetError,BrokenPipeError): # connection to the client is lost
							self._client = None
							logging.info("Client disconnected")


	# kick the user if connected
	# should be called before the shutdown of the program
	def close(self):
		with self._clientLock:
			if self._client:
				self._client.kick()
