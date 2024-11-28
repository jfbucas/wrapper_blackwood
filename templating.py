import os
import sys
import subprocess
import socket

import parameters

SOLVERPATH="solver"
#GENERATEDPATH="generated"

def get_path(thread_number=None):
	hostname = socket.gethostname()
	if thread_number != None:
		return SOLVERPATH+"/"+hostname+"_"+str(thread_number)

def gen_template(filename, template_params, thread_number=None):
	# Create a subfolder for that machine
	path = get_path(thread_number)
	if not os.path.exists( path ):
		try:
			os.makedirs( path )
		except OSError as error:
			print("Couldn't create", path )

	new_file = path+"/"+filename.replace(".template","")
	if new_file == filename:
		print(filename, "is not a template")
		return

	with open(SOLVERPATH+"/"+filename, 'r') as fin:
		with open(new_file, 'w') as fout:
			for line in fin:
				for t in template_params.keys():
					if "%%"+t+"%%" in line:
						line = line.replace("%%"+t+"%%", str(template_params[t]))	
				fout.write(line)



def gen_templates(template_params, thread_number):
	gen_template("Program.cs.template", template_params, thread_number)
	gen_template("Util.cs.template", template_params, thread_number)
	gen_template("Structs.cs.template", template_params, thread_number)

def compile(thread_number):
	path = get_path(thread_number)
	#print("Compiling :: cd solver; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
	os.system("cd "+path+"; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
 
def execute(thread_number):
	path = get_path(thread_number)
	return subprocess.run(["nice", "-n", "19", "mono", path+"/Program.exe"], stdout=subprocess.PIPE)

