import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
import subprocess

import templating


# Start a client
def client( host, serverPort ): 

	job = client_thread(host, serverPort)
	job.start()
	job.join()


# A simple thread for multicore support
class client_thread(threading.Thread):

	host = None
	stop = False

	def __init__(self, host, serverPort):
		threading.Thread.__init__(self)
		self.host = host
		self.serverPort = serverPort
		self.stop = False

	def run(self):

		while not self.stop:

			# Get a job
			r = None
			try:
				print("Connecting to "+self.host+":"+str(self.serverPort)+"...")
				r = requests.get('http://'+self.host+":"+str(self.serverPort)+'/')
			except:
				print("Couldn't connect to "+self.host+":"+str(self.serverPort)+". Try again in 5 sec.")
				time.sleep(5)
				continue
				


			# check status code for response received
			if r.status_code != 200:
				print("Status code", r.status_code, ". Try again in 5 sec.")
				time.sleep(5)
				continue

			job = None
			try:
				job = json.loads(r.content)
			except json.decoder.JSONDecodeError as error:
				print("Wrong job data: ", r.content, ". Try again in 5 sec.")
				time.sleep(5)
				continue


			# Do the thing
			print("Working on Job ", str(job["HEURISTIC_SIDES"]))
			templating.gen_templates(job)
			templating.compile()
			solver_result = templating.execute()
			solver_result = str(solver_result.stdout.decode("utf-8")).strip(",")
			print(solver_result) 

			job["index_counts"] = list(map(int, solver_result.split(",")))


			# Submit results
			try:
				r = requests.put('http://'+self.host+":"+str(self.serverPort)+'/', data = json.dumps(job))
			except:
				print("Couldn't send results for job", job, ". Moving on to the next job.")

			time.sleep(1)


