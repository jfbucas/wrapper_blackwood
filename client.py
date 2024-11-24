import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
from multiprocessing import Queue
import subprocess


# Start a client
def client( host, serverPort ): 

	q_p_c = Queue()
	job = client_thread(host, c, q_p_c)
	job.start()
	job.join()


# A simple thread for multicore support
class client_thread(threading.Thread):

	host = None
	stop = False
	number = 0
	queue = None

	def __init__(self, host="localhost", number=0, queue=None):
		threading.Thread.__init__(self)
		self.host = host
		self.number = number
		self.queue = queue
		self.stop = False

	def run(self):

		while not self.stop:

			# Get a job
			r = None
			try:
				print("Connecting to "+self.host+":"+str(serverPort)+"...")
				r = requests.get('http://'+self.host+":"+str(serverPort)+'/')
			except:
				print("Couldn't connect to "+self.host+":"+str(serverPort)+". Try again in 5 sec.")
				time.sleep(5)
				

			if r != None:

				# check status code for response received
				if r.status_code != 200:
					print("Status code", r.status_code, ". Try again in 5 sec.")
					time.sleep(5)
					continue

				job = None
				try:
					job = json.loads(r.content)
				except json.decoder.JSONDecodeError as error:
					print("Wrong job data: ", r.content)


				# Do the job
				if job != None:
					print("Working on Job ID",job["job_id"], "with Prefix", job["prefix"], "in", job["timelimit"], "minutes")

					os.environ["PREFIX"] = job["prefix"]
					os.environ["TIMELIMIT"] = str(job["timelimit"])
					os.environ["EXTRA_NAME"] = "_"+str(self.number).zfill(4) 

					backtracker_result = subprocess.run(["python3", "libblackwood.py", "--simple"], stdout=subprocess.PIPE)
					print(backtracker_result.stdout) 

					job["result"] = json.dumps(str(backtracker_result.stdout))


				# Submit results
				try:
					r = requests.put('http://'+self.host+":"+str(serverPort)+'/', data = json.dumps({ "job_id":job["job_id"], "result" : job["result"] }))
				except:
					print("Couldn't send results for job ID ", job["job_id"]," to "+self.host+". Status ", r.status_code, ". Moving on to the next job.")



