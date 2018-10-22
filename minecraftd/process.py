#!/usr/bin/env python3
import subprocess
import os

# an instance of a minecraft server process
class Process:

	@staticmethod
	def _preexec(): # do not forward signals (Like. SIGINT) we want to process those differently
		os.setpgrp()

	def __init__(self,command,_cwd):

		self.process = subprocess.Popen(command,cwd = _cwd,stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=Process._preexec)


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

		return self.process.poll() # returns None if the process is still running


	def sendCommandList(self,command_list):

		for cmd in command_list:
			self.sendCmd(cmd)
