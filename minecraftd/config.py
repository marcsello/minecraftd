#!/usr/bin/env python3
import json
import logging

class Config():

	_loglevel_table = {} # okay, I know that those have a numerical value as well, but I'd like to present a nicer way to set those in the config file
	_loglevel_table['DEBUG'] 	= logging.DEBUG
	_loglevel_table['INFO'] 	= logging.INFO
	_loglevel_table['WARNING'] 	= logging.WARNING
	_loglevel_table['ERROR'] 	= logging.ERROR
	_loglevel_table['CRITICAL'] 	= logging.CRITICAL

	def __init__(self,fname): # may throw various exceptions

		with open(fname) as f:
			self._cfg = json.load(f)


	def logLevel(self):


		try:
			lvl_str = self._cfg['minecraftd']['log_level']
			return Config._loglevel_table[lvl_str] # this is a static table

		except KeyError:
			return logging.INFO # default
		
		
	def logFilePath(self):

		try:
			return self._cfg['minecraftd']['logfile']

		except KeyError:
			return "" # default = no logfile


	def compileCommand(self): # no default

		cmd = [ self._cfg['server']['java'] ] # the first parameter is the java command

		# then we add the jvm arguments
		cmd += self._cfg['server']['jvm_arguments']

		# then add the minecraft

		cmd += ['-jar',self._cfg['server']['server_jar'],'nogui']

		return cmd # done


	def cwd(self): # no default
		return self._cfg['server']['server_path']


	def socketPath(self):

		try: # using .get() would result in some similar uglyness, because of the two levels
			return self._cfg['minecraftd']['console_socket_path']

		except KeyError:
			return "/var/lib/minecraftd/control.sock"


	def historyLen(self):

		try:
			return self._cfg['minecraftd']['history_length']

		except KeyError:
			return 24


	def shutdownCommands(self):

		try:
			return self._cfg['server']['shutdown_commands']

		except KeyError:
			return ['stop']
