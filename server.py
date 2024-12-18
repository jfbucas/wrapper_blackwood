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

job_list = []

def make_results_folders():
	for i,j,k in puzzle.edges_combo:
		path = "results/"+str(i)+"-"+str(j)+"-"+str(k)
		if not os.path.exists( path ):
			try:
				os.makedirs( path )
			except OSError as error:
				print("Couldn't create", path)


def prepare_next_jobs():
	
	all_results = analyse.load_results()
	counting = analyse.count(all_results)

	j = []
	for path, count in sorted(counting.items(), key=lambda x:x[1]):
		j.append( (path,count) )
	
	# We keep only the first 10% lowest
	return j[0:len(j)//10] * 10


def get_next_job():

	best_edges_combo = [
		("17-10-22", 250.04),
		("9-15-20", 250.07),
		("17-3-21", 250.25),
		("13-4-19", 250.26),
		("5-15-19", 250.29),
		("9-15-21", 250.31),
		("5-7-19", 250.38),
		("5-8-19", 250.40),
		("13-3-11", 250.44),
		("13-3-7", 250.45),
		("17-19-21", 250.47),
		("9-15-19", 250.48),
		("17-4-19", 250.48),
		("1-3-10", 250.49),
		("5-3-15", 250.53),
		("1-12-15", 250.55),
		("17-21-22", 250.56),
		("17-4-22", 250.58),
		("5-8-21", 250.61),
		("9-19-21", 250.61),
		("5-21-22", 250.65),
		("13-3-22", 250.65),
		("9-12-15", 250.86),
		("9-10-15", 250.96),
		]

	best_edges_combo = [
		("9-10-15", 250.96),
		("9-12-15", 250.86),
		("13-3-22", 250.65),
		("5-21-22", 250.65),
		("9-19-21", 250.61),
		("5-8-21", 250.61),
		]

	best_edges_combo = [
		("9-10-15", 250.88),
		("13-3-22", 250.81),
		("9-12-15", 250.78),
		("9-19-21", 250.62),
		("17-21-22", 250.60),
		("5-21-22", 250.58),
		("5-3-15", 250.58),
		("17-4-19", 250.55),
		("9-15-19", 250.55),
		("1-12-15", 250.55),
		("5-8-21", 250.54),
		("17-4-22", 250.53),
		("17-19-21", 250.49),
		("1-3-10", 250.47),
		("13-3-7", 250.44),
		("13-3-11", 250.41),
		("5-8-19", 250.41),
		]

	best_edges_combo = [
		("5-15-19", 250.39),
		("9-15-21", 250.36),
		("5-7-19", 250.34),
		("17-3-21", 250.30),
		("13-4-19", 250.23),
		("17-10-22", 250.11),
		("9-15-20", 250.11),
		("5-3-22", 249.98),
		("5-4-22", 249.98),
		("5-19-21", 249.97),
		("13-16-20", 249.97),
		("9-16-20", 249.87),
		("5-7-11", 249.86),
		("1-10-12", 249.78),
		("1-3-15", 249.75),
		("17-3-16", 249.74),
		("13-3-10", 249.74),
		("5-3-7", 249.71),
		("1-11-15", 249.69),
		("9-3-21", 249.58),
		("5-12-15", 249.55),
		("1-3-16", 249.48),
		("17-8-11", 249.46),
		("1-15-21", 249.45),
		("17-10-15", 249.39),
		("1-6-21", 249.35),
		("5-3-16", 249.29),
		("1-3-4", 249.27),
		("17-10-16", 249.24),
		("13-10-22", 249.23),
		]

	random.shuffle(best_edges_combo)

	return best_edges_combo[0]

	global job_list
	if len(job_list) == 0:
		job_list = prepare_next_jobs()

	return job_list.pop(0)

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
			if "results/" not in job_result["job_path"]:
				job_result["job_path"] = "results/"+job_result["job_path"]
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




