import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
from multiprocessing import Queue
import subprocess
import random

import puzzle
import templating
import parameters
import analyse

# Status codes
status_eror = -2
status_none = -1
status_todo = 0
status_wait = 1
status_done = 2

start_timestamp = str(time.time())


serverPort = 5001
if os.environ.get('PORT') != None:
	serverPort = int(os.environ.get('PORT'))

def make_results_folders():
	for i,j,k in puzzle.edges_combo:
		path = "results/"+str(i)+"-"+str(j)+"-"+str(k)
		if not os.path.exists( path ):
			try:
				os.makedirs( path )
			except OSError as error:
				print("Couldn't create", path)

def get_next_job():

	# Get the folder with the least amount of samples
	counting = {}
	for i,j,k in puzzle.edges_combo:
		path = "results/"+str(i)+"-"+str(j)+"-"+str(k)
		try:
			counting[path] = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
		except OSError as error:
			print(path,"doesn't exists")

	next_job = sorted(counting.items(), key=lambda x:x[1])
	min_count= next_job[0][1]
	next_job = [ x for x in next_job if x[1] == min_count]
	random.shuffle(next_job)
	return next_job[0]

def server(hostName, serverPort):

	make_results_folders()

	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	webServer.server_close()
	print("Server stopped.")


class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):

		#print(self.__dict__)

		if self.path == "/":
			# Get next job
			next_job = get_next_job()

			if next_job != None:
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				print("Sending job", next_job)
				job_params = parameters.get_next_job_params(next_job)
				job_params["job_path"] = next_job[0]
				self.wfile.write(bytes(json.dumps( job_params ), "utf-8"))
			else:
				self.send_response(404)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()

		elif self.path == "/stats.html":

			# Display some statistics
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			print("Providing Stats")
			self.wfile.write(bytes(analyse.get_stats_html(), "utf-8"))
			

	def do_POST(self):

		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)
		try:
			job_result = json.loads(post_data)

			print("Receiving", job_result["JOBGROUP"])
			#print(job_result)

			# Write to disk
			job_file = open(job_result["job_path"]+"/"+str(time.time())+".json", "wb")	
			job_file.write(post_data)
			job_file.close()

			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		except json.decoder.JSONDecodeError as error:
			print("Wrong data: ", post_data)
			self.send_response(404)
			self.end_headers()
		

	def do_PUT(self):
		self.do_POST()




