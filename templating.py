import os
import sys
import subprocess
import socket

import parameters

def get_path():
	hostname = socket.gethostname()
	return "solver/"+hostname

def gen_template(filename, template_params):
	# Create a subfolder for that machine
	path = get_path()
	if not os.path.exists( path ):
		try:
			os.makedirs( path )
		except OSError as error:
			print("Couldn't create", path )

	new_file = path+"/"+filename.replace(".template","")
	if new_file == filename:
		print(filename, "is not a template")
		return

	with open(filename, 'r') as fin:
		with open(new_file, 'w') as fout:
			for line in fin:
				for t in template_params.keys():
					if "%%"+t+"%%" in line:
						line = line.replace("%%"+t+"%%", str(template_params[t]))	
				fout.write(line)



def gen_templates(template_params):
	gen_template("solver/Program.cs.template", template_params)
	gen_template("solver/Util.cs.template", template_params)
	gen_template("solver/Structs.cs.template", template_params)

def compile():
	path = get_path()
	#print("Compiling :: cd solver; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
	os.system("cd "+path+"; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
 
def execute():
	path = get_path()
	return subprocess.run(["mono", path+"/Program.exe"], stdout=subprocess.PIPE)

