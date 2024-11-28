#!/usr/bin/python3

import os
import sys
import time

# Local Classes
import server
import client
import analyse


# ----- Parameters
def run( role ):

	# timer
	startTime = time.time()

	# -------------------------------------------
	# Start

	if role == "server":
		server.server("", server.serverPort)
	elif role == "client":
		if len(sys.argv) > 2:
			client.client(sys.argv[2], server.serverPort)
		else:
			run( "help" )

	elif role == "help":
		print( "+ Roles")
		print( " [--server|-s] | hostname | [--analyse|-a] | [-h|--help]")
		print( )
	else:
		print( "ERROR: unknown parameter:", role )

	if role in [ "server", "client" ]:
		print()
		print( "Execution time: ", time.time() - startTime )



if __name__ == "__main__":

	role = "client"

	# Get Role
	if len(sys.argv) > 1:
		a = sys.argv[1]
		if a.startswith("--server") or a.startswith("-s"):
			role = "server"
		elif a.startswith("--analyse") or a.startswith("-a"):
			role = "server"
		elif a.startswith("-h") or a.startswith("--help"):
			role = "help"
	
	run( role )

