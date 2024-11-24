import os
import sys
import subprocess

import parameters

def gen_template(filename, template_params):

	new_file = filename.replace(".template","")
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

def compile():
	#print("Compiling :: cd solver; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
	os.system("cd solver; mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs")
 
def execute():
	return subprocess.run(["mono", "solver/Program.exe"], stdout=subprocess.PIPE)

