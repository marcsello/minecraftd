#!/usr/bin/env python3
import clientswapper
import threading
import weakref
import logging

# the purpose of this class is to control the lines going
# back and forth between the client and the process


class LineProcessor(threading.Thread):

	def __init__(self,process,controlsocket):
		threading.Thread.__init__(self)

		self._process_ref = weakref.ref(process) # only a weak reference is stored to the process... if it's destroyed, well... we exit

		self._active = False

		self._clientSwapper = clientswapper.ClientSwapper(controlsocket) # the client swapper is contained here

	def run(self):
		self._active = True

		while self._active:

			line = self._clientSwapper.readLine(5) # 5 sec as timeout, returns None on timeout

			if line:
				p = self._process_ref()
				if not p: # process not just closed, but even cleaned up by the garbage collector
					break

				p.sendCmd(line)


		logging.debug("Line processor thread closed")
		self._active = False
		self._clientSwapper.close()


	def passLine(self,line): # called by the process's line reader, because of a bug there is no better way to do this :(
		self._clientSwapper.sendLine(line)


	def shutdown(self):
		self._active = False
