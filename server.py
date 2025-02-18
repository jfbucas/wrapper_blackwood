import re
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
import analyse
import jobs

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


def server(hostName, serverPort, batch=""):

	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.batch = analyse.get_default_batch(batch)
	print("Server started http://%s:%s %s" % (hostName, serverPort, webServer.batch))

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
			next_job = jobs.get_next_job(self.server.batch)

			if next_job != None:
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				print("\t\tSending job", next_job["job_description"])
				job_params = jobs.get_next_job_params(next_job)
				self.wfile.write(bytes(json.dumps( job_params ), "utf-8"))
			else:
				self.send_response(404)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()

		elif self.path.startswith("/stats.html"):
			url_batch = ""

			url_batch_pattern = r"batch=(\w+)"

			match = re.search(url_batch_pattern, self.path)
			if match:
				url_batch = match.group(1)

			# Display some statistics
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			print("\t\tProviding Stats for "+url_batch)
			all_results = analyse.load_results(url_batch)
			self.wfile.write(bytes(analyse.get_stats_html(url_batch, all_results), "utf-8"))
			

	def do_POST(self):

		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)
		try:
			job_result = json.loads(post_data)

			print("\t\tReceiving", job_result["job_description"])
			#print(job_result)

			# Build up name
			job_path = "results/"+job_result["job_batch"]
			if "job_path" in job_result:
				job_path += "/"+job_result["job_path"].replace("results/","")

			# Create folder
			if not os.path.exists( job_path ):
				try:
					os.makedirs( job_path )
				except OSError as error:
					print("Couldn't create", job_path)

			# Write result
			job_file = open(job_path+"/"+str(time.time())+".json", "wb")	
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




