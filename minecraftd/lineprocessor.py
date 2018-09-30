#!/usr/bin/env python3
import clientswapper
import threading
import weakref

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

			line = self._clientSwapper.readLine(5) # 5 sec as timeout

			if line:
				p = self._process_ref()
				if not p:
					break

				p.sendCmd(line)


		self._active = False


	def passLine(self,line): # called by the process's line reader, because of a bug there is no better way to do this :(
		self._clientSwapper.sendLine(line)


	def shutdown(self):
		self._clientSwapper.close()
		self._active = False
