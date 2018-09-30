#!/usr/bin/env python3
import threading

# The purpose of this class is keep a short log of the last lines on the console
# To be sent to a new client when connected, to give a little bit of context

# This history is stored in the RAM only, so smaller is better

class History():

	def __init__(self,length):

		self._enabled = bool(length)

		self._lock = threading.RLock()

		if self._enabled:
			self._history = []
			self._maxlen = length

	# Add one line to the history
	def addLine(self,line):
		with self._lock:
			if not self._enabled:
				return

			self._history.append(line)

			if len(self._history) > self._maxlen: # because we add history line by line
				del self._history[:1] # deleting the first entry without any extra calculation is sufficent (we use del for quicker free up)

	# fetch the last history entries
	def fetchLines(self,lines=None):
		with self._lock:
			if not self._enabled:
				return []

			if lines and lines < self._maxlen:
				len = lines
			else:
				len = self._maxlen


			return self._history[-len:]
