import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
from multiprocessing import Queue
import subprocess

import puzzle
import templating

# Status codes
status_eror = -2
status_none = -1
status_todo = 0
status_wait = 1
status_done = 2

exit()


start_timestamp = str(time.time())

def server(hostName, serverPort):
	globals()["all_jobs"] = readJobs()

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
		next_job = None
		for k in all_jobs.keys():
			if all_jobs[k]["status"] == status_todo:
				next_job = k
				break

		if next_job != None:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			print("Sending job ID", next_job)
			all_jobs[next_job]["status"] = status_wait
			self.wfile.write(bytes(json.dumps({"job_id" : next_job, "prefix": all_jobs[next_job]["prefix"], "timelimit": timelimit}), "utf-8"))
		else:
			self.send_response(404)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			#self.wfile.write(bytes(json.dumps({"job_id" : -1, "prefix": ""}), "utf-8"))

	def do_POST(self):

		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)
		result = None
		try:
			result = json.loads(post_data)
		except json.decoder.JSONDecodeError as error:
			print("Wrong data: ", post_data)
			self.send_response(404)
			self.end_headers()
			#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))

		if result != None:
			print(result)

			if "job_id" in result:
				job_id = result["job_id"]
				if all_jobs[ job_id  ][ "status" ] == status_wait:
					print("Received result for job ID", job_id)
					all_jobs[ job_id ][ "result" ] = result
					all_jobs[ job_id ][ "status" ] = status_done

					# Write to disk
					job_file = open("jobs/depth_014/EternityII_jobs.txt."+start_timestamp, "a")	
					job_file.write(str(all_jobs[ job_id ])+"\n")
					job_file.close()

					self.send_response(200)
					self.send_header('Content-Type', 'application/json')
					self.end_headers()
					self.wfile.write(bytes(json.dumps({ "status": status_done }), "utf-8"))
				else:
					print("Job ID", job_id, "was not waiting.")
					self.send_response(404)
					self.end_headers()
					#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))
			else:
				print("No 'job_id' found : ", result)
				self.send_response(404)
				self.end_headers()
				#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))
		

	def do_PUT(self):
		self.do_POST()




def readJobs():
	
	jobs = {}

	#filename = "jobs/depth_014/"+self.getFileFriendlyName( self.puzzle.name )+".txt"
	filename = "jobs/depth_014/EternityII.txt"

	if os.path.exists(filename):
		
		# Read the data
		job_id = 0
		jobsfile = open( filename, "r" )
		for line in jobsfile:
			if line.startswith('#'):
				continue
			line = line.strip('\n').strip(' ')
			prefix = line.split("|")[1]
			jobs[job_id] = { "job_id" : job_id, "line": line, "prefix" : prefix, "status" : status_todo }
			job_id += 1
		jobsfile.close()
	
	print("Found", len(jobs.keys()), "jobs")

	return jobs
		

