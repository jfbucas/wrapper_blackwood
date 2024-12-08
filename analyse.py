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

					if data["index_counts"][256] != 0:
						print(fn, ":", data)

					if sum(data["index_counts"]) == (data["NODE_COUNT_LIMIT"]+1) * data["NUMBER_SOLVEPUZZLE"] * data["NUMBER_LOOPS"] or \
						data["index_counts"][256] != 0:
						all_results[path].append(data)
					else:
						print("Incorrect data:", fn, data)
				#if len(all_results[path]) > 4:
				#	break
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
	stats_avg     = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) )) #, dtype=int)
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
		stats_avg[i,j,k] = sum(zeroes)/len(zeroes)
		stats_samples[i,j,k] = len(zeroes)

		#print(i, j, k, "Max: "+str(max(zeroes)), "Avg: "+str(sum(zeroes)//len(zeroes)), "Samples: "+str(len(zeroes)))

	side_motifs = {}
	middle_motifs_top = {}
	middle_motifs_left = {}
	middle_motifs_right = {}
	middle_motifs_bottom = {}
	for m in motifs.motifs.keys():
		side_motifs[m]  = """<svg height="16" width="32" transform="scale(0.25), rotate(-90), translate(-16,-120)" overflow="visible">"""
		side_motifs[m] += motifs.motifs[m]
		side_motifs[m] += """</svg>"""
		side_motifs[m] += """<svg height="16" width="32" transform="scale(0.25), rotate(90), translate(-16,-120)" overflow="visible">"""
		side_motifs[m] += motifs.motifs[m]
		side_motifs[m] += """</svg>"""
		middle_motifs_top[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(-90), translate(-112,-120)" overflow="visible">"""
		middle_motifs_top[m] += motifs.motifs[m]
		middle_motifs_top[m] += """</svg>"""
		middle_motifs_left[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(180), translate(-112,-120)" overflow="visible">"""
		middle_motifs_left[m] += motifs.motifs[m]
		middle_motifs_left[m] += """</svg>"""
		middle_motifs_right[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(0), translate(-112,-120)" overflow="visible">"""
		middle_motifs_right[m] += motifs.motifs[m]
		middle_motifs_right[m] += """</svg>"""
		middle_motifs_bottom[m]  = """<svg height="16" width="32" transform="scale(0.125), rotate(90), translate(-112,-120)" overflow="visible">"""
		middle_motifs_bottom[m] += motifs.motifs[m]
		middle_motifs_bottom[m] += """</svg>"""

	minimum = 256
	for i in stats_avg:
		for j in i:
			for k in j:
				if k > 0 and k < minimum:
					minimum=k
	#print("minimum=", minimum)

	# Use logarithm for the colors to highlight the best edge_combo
	#color_ln = list(reversed([ int(256-(math.log(i+1)/math.log(256-minimum))*256) for i in range(256-minimum) ]))
	#color_ln = list(reversed([ int(256-(math.log(i+1)/math.log(256))*256) for i in range(256) ]))

	o = ""
	o += "<style>"
	o += "body {background-image:url('https://e2.bucas.name/img/fabric.png'); background-color: #444; text-align:center; zoom:150%;}"
	o += "table {border-spacing:0px; margin:auto;}"
	o += "th,td {height:32px; width:32px;padding:0px; text-align:center; font-size:7px; "
	o += "color: white; font-family: Sans-serif; text-shadow: 0px 0px 1px #222; }"
	o += ".ontop {position:relative; z-index:5}"
	# Mark the two known 470
	o += "#td35  {box-shadow: inset 0px 0px 0px 2px #f0f; cursor: pointer;}"
	o += "#td482 {box-shadow: inset 0px 0px 0px 2px #00f; cursor: pointer;}"
	o += "</style>\n"

	o += "<table>\n"
	o += "<tr>"
	for m in range(23):
		o += "<th>"+str(m)+str(middle_motifs_top[m])+"</th>"
	o += "</tr>\n"
	o += "</table>\n"

	stats_avg[0] += numpy.rot90(numpy.fliplr(stats_avg[1]))
	stats_avg[2] += numpy.rot90(numpy.fliplr(stats_avg[3]))

	o += "<br/>\n"
	o += "<br/>\n"

	best_edges_combo = {}

	mi=0
	td=0
	for i in [ stats_avg[0], stats_avg[2], stats_avg[4] ]:

		o += "<table>\n"
		mmi = str(side_motifs[puzzle.SIDE_EDGES[mi]])

		o += "<tr><th>"+""+"</th>"
		for m in puzzle.MIDDLE_EDGES :
			o += "<th title='"+str(m)+"'>"+str(middle_motifs_top[m])+"</th>"
		o += "<th title='"+str(puzzle.SIDE_EDGES[mi])+"'>"+(mmi if mi%2==0 else "")+"</th>"
		o += "</tr>\n"
		mi += 1

		m = iter(puzzle.MIDDLE_EDGES)
		for j in i:
			mm = next(m)
			o += "<tr>"
			o += "<td title='"+str(mm)+"'>"+str(middle_motifs_left[mm])+"</td>"
			n = iter(puzzle.MIDDLE_EDGES)
			for k in j:
				nn = next(n)
				c = ((k-minimum)/(256-minimum))*256 if k>0 else 0
				r,g,b,a = palette.palette[int(c)] 
				r,g,b,a = int(r*255),int(g*255),int(b*255),int(a*255)
				if k == 0:
					r,g,b,a = 0,0,0,0.3

				mmmi=puzzle.SIDE_EDGES[mi] if mi < len(puzzle.SIDE_EDGES) else ""
				if mm < nn:
					mmmi=puzzle.SIDE_EDGES[mi-1]

				edges_combo_title=""
				if mmmi != "":
					if mm > nn:
						edges_combo_title=str(mmmi)+"-"+str(nn)+"-"+str(mm)
					else:
						edges_combo_title=str(mmmi)+"-"+str(mm)+"-"+str(nn)
					
				o += "<td id='td"+str(td)+"' title='"+edges_combo_title+"' class='ontop' style='background-color:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");'>"+str( "{:.2f}".format(k) if k>0 else "")+"</td>\n"
				best_edges_combo[edges_combo_title] = k
				td+=1
			o += "<td title='"+str(mm)+"'>"+str(middle_motifs_right[mm])+"</td>"
			o += "</tr>\n"

		mmi = str(side_motifs[puzzle.SIDE_EDGES[mi]]) if mi < len(puzzle.SIDE_EDGES) else ""
		o += "<tr><th title='"+(str(puzzle.SIDE_EDGES[mi])if mi < len(puzzle.SIDE_EDGES) else "")+"'>"+mmi+"</th>"
		for m in puzzle.MIDDLE_EDGES :
			o += "<th title='"+str(m)+"'>"+str(middle_motifs_bottom[m])+"</th>"
		o += "<th>"+""+"</th>"
		o += "</tr>\n"
		mi += 1

		o += "</table>\n"

		o += "<br/>\n"
		o += "<br/>\n"
		

	o += "<script>"
	o += "document.getElementById('td35').onclick  = function () { window.open('https://e2.bucas.name/#puzzle=JBlackwood+Jef_470','_blank'); };"
	o += "document.getElementById('td482').onclick = function () { window.open('https://e2.bucas.name/#puzzle=Joshua_Blackwood_470','_blank'); };"
	o += "</script>\n"


	best_edges_combo = reversed(sorted(best_edges_combo.items(), key=lambda x:x[1]))

	o += "<table>"
	for ec,k in best_edges_combo:
		c = ((k-minimum)/(256-minimum))*256 if k>0 else 0
		r,g,b,a = palette.palette[int(c)] 
		r,g,b,a = int(r*255),int(g*255),int(b*255),int(a*255)
		if k == 0:
			continue

		count = 0
		path = "results/"+ec
		if path in all_results:
			count = len(all_results[path])

		o += "<tr style='background-color:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");'><td>"+ec+"</td><td>"+str( "{:.2f}".format(k) if k>0 else "")+"</td><td>"+str(count)+" samples</td></tr>\n"
	o += "</table>\n"

	return o

