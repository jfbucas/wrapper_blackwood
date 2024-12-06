import os
import json
import numpy
import math

import puzzle
import palette
import motifs

#def array_add(a1,a2):
#	a1=numpy.array(a1)
#	a2=numpy.array(a2)
#	return numpy.add(a1,a2)

def load_results():

	# Get the folder with the least amount of samples
	all_results = {}
	for i,j,k in puzzle.edges_combo:
		path = "results/"+str(i)+"-"+str(j)+"-"+str(k)
		all_results[path] = []
		try:
			for fn in [os.path.join(path, name) for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]:
				with open(fn, 'r') as f:
					data = json.load(f)

					if sum(data["index_counts"]) == (data["NODE_COUNT_LIMIT"]+1) * data["NUMBER_SOLVEPUZZLE"] * data["NUMBER_LOOPS"] or \
						data["index_counts"][256] != 0:
						all_results[path].append(data)
					else:
						print("Incorrect data:", fn, data)
				if len(all_results[path]) > 10:
					break
		except OSError as error:
			print(path,"doesn't exists")

	return all_results

def count(all_results, display=False):

	counting={}
	for path in all_results.keys():
		counting[path] = len(all_results[path])

	if display:
		for path, count in sorted(counting.items(), key=lambda x:x[1]):
			print(path, count)

		total = sum([ x[1] for x in counting.items() ])
		print(total)

	return counting


def find_fastest(all_results):

	fastest=10000000
	for path in all_results.keys():
		for r in all_results[path]:
			if "runtime" in r:
				if r["runtime"] < fastest:
					fastest = r["runtime"]

	print(fastest)


def machines_stats(all_results):

	machines={}
	for path in all_results.keys():
		for r in all_results[path]:
			if "hostname" in r.keys():
				if r["hostname"] not in machines.keys():
					machines[r["hostname"]] = []

				if "runtime" in r.keys():
					machines[r["hostname"]].append(r["runtime"])

	for m in machines.keys():
		print(m, "Results=",len(machines[m]), "Avg=", int(sum(machines[m])/len(machines[m])))


def get_index_counts(all_results):

	index_counts={}
	for path in all_results.keys():
		if path not in index_counts.keys():
			index_counts[path] = []
		
		for r in all_results[path]:
			index_counts[path].append(numpy.array(r["index_counts"]+[0]))

	return index_counts



def get_stats_html():

	all_results = load_results()
	index_counts = get_index_counts(all_results)

	stats_max     = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) ), dtype=int)
	stats_avg     = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) ), dtype=int)
	stats_samples = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) ), dtype=int)

	for path in index_counts.keys():
		total_ic = numpy.zeros((258), dtype=int)
		zeroes = [] 
		for ic in index_counts[path]:
			total_ic = numpy.add(total_ic, ic)
			zeroes.append( numpy.where(ic == 0)[0][1] )

		z = numpy.where(total_ic == 0)[0]

		i, j, k = puzzle.path_to_edge_combo(path)
		i = puzzle.SIDE_EDGES.index(i)
		j = puzzle.MIDDLE_EDGES.index(j)
		k = puzzle.MIDDLE_EDGES.index(k)
		stats_max[i,j,k] = max(zeroes)
		stats_avg[i,j,k] = sum(zeroes)//len(zeroes)
		stats_samples[i,j,k] = len(zeroes)

		#print(i, j, k, "Max: "+str(max(zeroes)), "Avg: "+str(sum(zeroes)//len(zeroes)), "Samples: "+str(len(zeroes)))

	edges_motifs_top = {}
	edges_motifs_left = {}
	for m in motifs.motifs.keys():
		edges_motifs_top[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(-90), translate(-112,-120)" overflow="visible">"""
		edges_motifs_top[m] += motifs.motifs[m]
		edges_motifs_top[m] += """</svg>"""
		edges_motifs_left[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(180), translate(-112,-120)" overflow="visible">"""
		edges_motifs_left[m] += motifs.motifs[m]
		edges_motifs_left[m] += """</svg>"""

	minimum = 256
	for i in stats_avg:
		for j in i:
			for k in j:
				if k > 0 and k < minimum:
					minimum=k

	stats_avg_ln = numpy.log1p(stats_avg-minimum)
	print(numpy.nanmax(stats_avg_ln))
	stats_avg_ln = stats_avg_ln*(numpy.nanmax(stats_avg_ln)/256)
	print(stats_avg_ln)

	print("minimum=", minimum)
	o = ""
	o += "<style> body {background-image:url('https://e2.bucas.name/img/fabric.png'); background-color: #444;}"
	o += "table {border-spacing:0px;}"
	o += "th,td {height:32px; width:32px;padding:0px; text-align:center; font-size:10px; }"
	o += ".ontop {position:relative; z-index:5} </style>\n"
	#for i in stats_max:
	for i in stats_avg:
		o += "<table>\n"

		o += "<tr><th>\</th>"
		for m in puzzle.MIDDLE_EDGES :
			o += "<th>"+str(edges_motifs_top[m])+"</th>"
		o += "</tr>\n"

		m = iter(puzzle.MIDDLE_EDGES)
		for j in i:
			o += "<tr>"
			o += "<td>"+str(edges_motifs_left[next(m)])+"</td>"
			for k in j:
				c = (k-minimum)*(256/(256-minimum)) if k>0 else 0
				a = 255
				r,g,b = palette.palette[int(c)] 
				if c == 0 and k == 0:
					r,g,b,a = 255,255,255,0
				o += "<td class='ontop' style='background-color:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");'>"+str( k if k>0 else "")+"</td>"
			o += "</tr>\n"
		o += "</table>\n"

	return o

