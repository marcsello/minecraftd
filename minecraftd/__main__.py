#!/usr/bin/env python3
import sys
import logging
from .lineprocessor import LineProcessor
from .process import Process
from .controlsocket import ControlSocket
from .sessionclient import SessionClient

def runDaemon():
	logging.basicConfig(filename="", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
	logging.info("Minecraftd is starting...")

	cs = ControlSocket("/tmp/mc.sock")
	pr = Process(['java','-jar','server.jar'],'/home/marcsello/superscreen/minecraft')

	lp = LineProcessor(pr,cs)
	lp.start()

	# and now the ugly part:
	while True:
		try:
			for l in pr.getStdout():
				lp.passLine(l.decode('utf-8'))

			break # stdout reading ended without exceptions

		except KeyboardInterrupt: # SIGINT sends a "stop" command to the server, and it will shutdown greacefully (using Popen.wait to wait for termination would end up in deadlock, because we use stdin/stdout instead of communicate)
			lp.passLine("Minecraftd: Daemon is shuttig down. Stopping minecraft server.")
			pr.stop() # sends the stop command to the minecraft server


	logging.info("Minecraftd is shutting down...")
	lp.shutdown() # stops the thread and disconnects the user
	lp.join() # wait for line processor to close, before closing the control socket
	cs.close()

	return pr.getReturnCode()


def attachSession():

	try:
		sc = SessionClient('/tmp/mc.sock')

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

	if '--daemon' in sys.argv: # start daemon

		rc = runDaemon()
		sys.exit(rc) # the return code of minecraftd daemon is the return code of the minecraft server

	else: # attach screen

		attachSession()


if __name__ == '__main__':
	 main()
