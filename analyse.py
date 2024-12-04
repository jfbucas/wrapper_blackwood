import os
import json
import numpy

import puzzle
import palette

#def array_add(a1,a2):
#	a1=numpy.array(a1)
#	a2=numpy.array(a2)
#	return numpy.add(a1,a2)

def count():

	# Get the folder with the least amount of samples
	counting = {}
	for i,j,k in puzzle.edges_combo:
		path = "results/"+str(i)+"-"+str(j)+"-"+str(k)
		try:
			counting[path] = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
		except OSError as error:
			print(path,"doesn't exists")

	for path, count in sorted(counting.items(), key=lambda x:x[1]):
		print(path, count)

	total = sum([ x[1] for x in counting.items() ])
	print(total)
	return total

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
		except OSError as error:
			print(path,"doesn't exists")

	return all_results

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

	m0 = """
<svg height="16" width="32" transform="scale(0.125), rotate(-90), translate(0,-128)" overflow="visible">
<polygon points="0,0  128,128   0,256" style="fill:#26638e;stroke:black;stroke-width:1" />
<path d="M0,56
a16,16 0 1,1 8,32 v 32 
h 32
a16,16 0 1,1 0,16 h -32
v 32
a16,16 0 1,1 -8,32"
fill="#f38622" stroke="#c1732d" stroke-width="1"  />
</svg>
"""
	o = ""
	#for i in stats_max:
	for i in stats_avg:
		o += "<table>\n"

		o += "<tr><th>\</th>"
		for m in puzzle.MIDDLE_EDGES :
			o += "<th>"+str(m0)+"</th>"
		o += "</tr>\n"

		m = iter(puzzle.MIDDLE_EDGES)
		for j in i:
			o += "<tr>"
			o += "<td>"+str(next(m))+"</td>"
			for k in j:
				c = k if k>0 else ""
				r,g,b = palette.palette[k] 
				o += "<td style='background-color:rgb("+str(r)+","+str(g)+","+str(b)+");'>"+str( k if k>0 else "")+"</td>"
			o += "</tr>\n"
		o += "</table>\n"

	return o

