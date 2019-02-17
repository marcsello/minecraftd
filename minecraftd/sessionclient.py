#!/usr/bin/env python3
import sys
import socket
import select

from . import bettersocket

# This is a very simple telnet (or netcat) like class
# Well, it could be a function instead of a class
# But this allows us better error handling

class SessionClient:

	def __init__(self,socket_path):
		self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.sock.connect(socket_path) # may throw various exceptions
		self.sock.setblocking(False) # nonblocking
		self.sock_reader = bettersocket.BetterSocketReader(self.sock)


	def run(self):

		while True:

			try:
				readable = select.select([sys.stdin, self.sock], [], [])[0] # wait for either one

			except ValueError: # some exception in the selector
				return

			if not readable: # this could happen only on timeout expire... but we came prepared for the unknown
				return

			for s in readable:
				if s is sys.stdin: # user typed a command
					line = s.readline()

					if not line: # an empty line means the stdin is closed
						self.sock.close()
						return

					try:
						self.sock.sendall(line.encode('utf-8'))

					except (BrokenPipeError,ConnectionResetError):
						return # socket closed


				elif s is self.sock: # data arrived from the server

					while True: # there might be more than one line in one message, we need to read them all
						try:
							line = self.sock_reader.readline() # only reads one line

						except (BrokenPipeError,ConnectionResetError):
							return # socket closed

						if line: # none means there is more data to read
							print(line.decode('utf-8'))
						else:
							break # break the reading loop, as there is nothing left to read


	def close(self):
		self.sock.close()
