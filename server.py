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

HOOK=''
if os.environ.get('HOOK'): 
	HOOK = os.environ.get('HOOK')

job_list = []


#def prepare_next_jobs():
#	
#	all_results = analyse.load_results()
#	counting = analyse.count(all_results)
#
#	j = []
#	for path, count in sorted(counting.items(), key=lambda x:x[1]):
#		j.append( (path,count) )
#	
#	# We keep only the first 10% lowest
#	return j[0:len(j)//10] * 10


def get_next_job(batch):

	global HOOK

	if batch == "batch00":

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


		next_job = {
			"job_title": "Best Edges Combo Mapping",
			"job_description": "Edges Combo "+str(best_edges_combo[0][0]),
			"job_batch": "batch00_edges_combo",
			"job_path" : best_edges_combo[0][0],
			"HEURISTIC_SIDES" : best_edges_combo[0][0].replace("-",","),
			"NODE_COUNT_LIMIT" : 50000000000,
			"HOOK" : HOOK,
			}

		return next_job

	elif batch == "batch01":

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )
		
		random.shuffle(best_edges_combo)

		next_job = {
			"job_title": "Best Edges Combo Mapping With Less Node_Count_Limit",
			"job_description": "Edges Combo "+str(best_edges_combo[0]),
			"job_batch": "batch01_edges_combo_shorter",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : 5000000000,
			"HOOK" : HOOK,
			}

		return next_job

	#global job_list
	#if len(job_list) == 0:
	#	job_list = prepare_next_jobs()
	#
	#return job_list.pop(0)

def server(hostName, serverPort):

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
			next_job = get_next_job("batch01")

			if next_job != None:
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				print("Sending job", next_job["job_description"])
				job_params = parameters.get_next_job_params(next_job)
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
			all_results = analyse.load_results()
			self.wfile.write(bytes(analyse.get_stats_html(all_results), "utf-8"))
			

	def do_POST(self):

		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)
		try:
			job_result = json.loads(post_data)

			print("Receiving", job_result["job_description"])
			#print(job_result)

			# Build up name
			job_path = job_result["job_path"].replace("results/","")

			if "job_batch" not in job_result.keys():
				job_result["job_batch"] = "batch00_edge_combos"

			job_path = "results/"+job_result["job_batch"]+"/"+job_path

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




