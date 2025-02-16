#!/usr/bin/python3

import os
import sys
import time

# Local Classes
import server
import client
import analyse


# ----- Parameters
def run( role, hostname="", batch="" ):

	# <Timer>
	startTime = time.time()

	# -------------------------------------------
	# Start

	if role == "server":
		server.server("", server.serverPort, batch)
	elif role == "client":
		client.client(hostname, server.serverPort)

	elif role == "analyse":
		ar = analyse.load_results(batch)
		analyse.count(ar, display=True)
		#analyse.find_fastest(ar)
		analyse.machines_stats(ar)
		#analyse.get_stats_html()

	elif role == "help":
		print( sys.argv[0], "[ [client] hostname | server | analyse | help ] | [--batch batch]")
		print( )
		exit(0)

	# </Timer>
	print()
	print( "Execution time: ", time.time() - startTime )



if __name__ == "__main__":

	role     = "help"
	batch    = ""
	hostname = ""

	# Get Params
	if len(sys.argv) > 1:
		argp = 1
		while argp < len(sys.argv):
			a = sys.argv[argp]
			if a in [ "client", "server", "analyse", "help" ]:
				role = a
			elif a.startswith("--batch"):
				if argp+1 < len(sys.argv):
					batch = sys.argv[argp+1]
					argp += 1

			else:
				hostname = a

			argp += 1
		
	run( role, hostname, batch)
