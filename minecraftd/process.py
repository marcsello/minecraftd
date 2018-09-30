#!/usr/bin/env python3
import subprocess

# an instance of a minecraft server process
class Process:

	def __init__(self,command,_cwd):

		self.process = subprocess.Popen(command,cwd = _cwd,stdout=subprocess.PIPE, stdin=subprocess.PIPE)


	def sendLine(self,line): # takes: unicode str

		self.process.stdin.write(line.encode('utf-8'))
		self.process.stdin.flush()

	def sendCmd(self,cmd): # takes: unicode str

		line = cmd.strip().encode('utf-8') + b"\r\n" # replace the newline with a sequence that should work everywhere

		self.process.stdin.write(line)
		self.process.stdin.flush()

	def getStdout(self):

		return self.process.stdout


	def getReturnCode(self):

		return self.process.returncode


	def stop(self):

		self.sendCmd('save-all')
		self.sendCmd('stop')
