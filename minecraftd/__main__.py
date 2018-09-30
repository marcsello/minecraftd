#!/usr/bin/env python3
import sys
import logging
from lineprocessor import LineProcessor
from process import Process
from controlsocket import ControlSocket


def runDaemon():
	logging.basicConfig(filename="", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
	logging.info("Minecraftd is starting...")

	cs = ControlSocket("/tmp/mc.sock")
	pr = Process(['java','-jar','server.jar'],'/home/marcsello/superscreen/minecraft')

	lp = LineProcessor(pr,cs)
	lp.start()

	# and now the ugly part:
	for l in pr.getStdout():
		lp.passLine(l.decode('utf-8'))

	logging.info("Minecraftd is shutting down")
	lp.shutdown()
	cs.close()

	return pr.getReturnCode()


def main():

	if '--daemon' in sys.argv: # start daemon

		rc = runDaemon()
		sys.exit(rc)

	else: # attach screen

		# TODO
		pass



if __name__ == '__main__':
	 main()
