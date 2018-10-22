#!/usr/bin/env python3
import sys
import logging
from .lineprocessor import LineProcessor
from .process import Process
from .controlsocket import ControlSocket
from .sessionclient import SessionClient
from .config import Config

CONFIG_FILE="/etc/minecraftd.json"

def runDaemon(cfg):
	logging.basicConfig(filename="", level=cfg.logLevel(), format="%(asctime)s - %(levelname)s: %(message)s")
	logging.info("Minecraftd is starting...")

	try:
		cs = ControlSocket(cfg.socketPath())

	except FileNotFoundError:
		logging.critical("Failed to create socket: Path not found")
		sys.exit(1)

	except PermissionError:
		logging.critical("Failed to create socket: Permission denied")
		sys.exit(1)

	try:
		pr = Process(cfg.compileCommand(),cfg.cwd()) # starts the process

	except FileNotFoundError as e:
		logging.critical("Failed to start process: {}".format(str(e)))
		sys.exit(1)

	lp = LineProcessor(pr,cs,cfg.historyLen())
	lp.start()

	# and now the ugly part:
	while True:
		try:
			for l in pr.getStdout(): # Okay this miiiiiight not be the best way to do this... We could merge it into the socket's select, and make the whole program single threaded... I just couldn't think of a nicer way to separate this
				lp.passLine(l.decode('utf-8')) # line processor expects strings

			break # stdout reading ended without exceptions

		except KeyboardInterrupt: # SIGINT sends a "stop" command to the server, and it will shutdown greacefully (using Popen.wait to wait for termination would end up in deadlock, because we use stdin/stdout instead of communicate)
			logging.info("Stopping minecraft server...")
			lp.passLine("Minecraftd: Daemon is shuttig down! Stopping minecraft server...\n")
			pr.sendCommandList(cfg.shutdownCommands()) # should contain "stop"


	logging.info("Minecraftd is shutting down...")
	lp.shutdown() # stops the thread and disconnects the user
	lp.join() # wait for line processor to close, before closing the control socket
	cs.close()

	return pr.getReturnCode()


def attachSession(cfg):

	try:
		sc = SessionClient(cfg.socketPath())

	except (ConnectionRefusedError,FileNotFoundError):
		print("Couldn't connect to Minecraftd console (is the daemon running?)")
		return

	except PermissionError:
		print("You have no permission to attach to Minecraftd console")
		return

	try:
		sc.run()

	except KeyboardInterrupt:
		sc.close()

	print("Session closed")


def main():

	try:
		cfg = Config(CONFIG_FILE)

	except Exception as e:
		print("CRITICAL: Failed to load config file: {}".format(str(e)))
		sys.exit(1)

	if '--daemon' in sys.argv: # start daemon

		rc = runDaemon(cfg)
		sys.exit(rc) # the return code of minecraftd daemon is the return code of the minecraft server

	else: # attach screen

		attachSession(cfg)


if __name__ == '__main__':
	 main()
