import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
import subprocess
import socket

import templating
import lca


# Start a client
def client( host, serverPort ): 

	# Create the threads
	CORES=os.cpu_count()
	if os.environ.get('CPUS') != None:
		CORES=int(os.environ.get('CPUS'))
	if os.environ.get('CORE') != None:
		CORES=int(os.environ.get('CORE'))
	if os.environ.get('CORES') != None:
		CORES=int(os.environ.get('CORES'))

	if CORES < 0:
		CORES=os.cpu_count()-abs(CORES)
	if CORES <= 0:
		CORES=1

	# Leave the CPU alone in case of other users
	lca_thread = lca.Leave_CPU_Alone_Thread(period=2)
	lca_thread.start()

	# Start the jobs
	job_threads = []
	for c in range(CORES):
		job_threads.append(client_thread(host, serverPort, c)) 
	
	for j in job_threads:
		j.start()
	
	try:
		j.join()
	
	except KeyboardInterrupt:
		for j in job_threads:
			j.stop = True

	# Stop LCA
	lca_thread.stop_lca_thread = True


# A simple thread for multicore support
class client_thread(threading.Thread):

	host = None
	stop = False

	def __init__(self, host, serverPort, thread_number):
		threading.Thread.__init__(self)
		self.host = host
		self.serverPort = serverPort
		self.thread_number = thread_number
		self.stop = False

	def run(self):

		while not self.stop:

			# Get a job
			job = None
			r = None

			try:
				print("Connecting to "+self.host+":"+str(self.serverPort)+"...")
				r = requests.get('http://'+self.host+":"+str(self.serverPort)+'/')
			except:
				print("Couldn't connect to "+self.host+":"+str(self.serverPort)+". Try again in 5 sec.")
				time.sleep(5)
				continue

			# Check status code for response received
			if r.status_code != 200:
				print("Status code", r.status_code, ". Try again in 5 sec.")
				time.sleep(5)
				continue

			try:
				job = json.loads(r.content)
			except json.decoder.JSONDecodeError as error:
				print("Wrong job data: ", r.content, ". Try again in 5 sec.")
				time.sleep(5)
				continue


			# Do the thing
			try:
				print("Working on Job ", str(job["HEURISTIC_SIDES"]))
				sys.stdout.flush()
				templating.gen_templates(job, self.thread_number)
				templating.compile(self.thread_number)
				startTime = time.time()
				solver_result = templating.execute(self.thread_number)
				solver_result = str(solver_result.stdout.decode("utf-8")).strip(",")
				#print(solver_result) 
				print("Done.") 

			except KeyboardInterrupt:
				print("Finishing")
				self.stop = True
				continue
			except:
				print(solver_result) 
				print("Couldn't execute. Skipping.")
				time.sleep(1)
				continue
				

			# Convert results
			try:
				job["index_counts"] = list(map(int, solver_result.split(",")))
				job["hostname"] = socket.gethostname()
				job["runtime"] = time.time() - startTime
			except:
				print("Couldn't convert results to index_counts: ", solver_result, ". Skipping.")
				time.sleep(1)
				continue


			# Submit results
			try:
				r = requests.put('http://'+self.host+":"+str(self.serverPort)+'/', data = json.dumps(job))
			except:
				print("Couldn't send results for job", job, ". Moving on to the next job.")
				time.sleep(1)
				continue


