import os
import json
import numpy
import math

import puzzle
import palette
import motifs
import jobs


def get_default_batch(batch=""):
	# If batch is empty, we use the last one
	try:
		if batch == "":
			batch = sorted([ f.path for f in os.scandir("results/") if f.is_dir() ])[-1]
		else:
			batch = sorted([ f.path for f in os.scandir("results/") if f.is_dir() and batch in f.path ])[-1]
	except:

		next_job = jobs.get_next_job(batch)

		if next_job == None:
			print("Batch", batch, " not found")
			exit(0)

		batch = next_job["job_batch"]
	
	if "results/" not in batch:
		batch = "results/"+batch

	return batch


def load_results(batch=""):

	batch = get_default_batch(batch)

	# Get the folder with the least amount of samples
	all_results = {}
	for path in sorted([ f.path for f in os.scandir(batch) if f.is_dir() ]):
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

	print("Loaded", sum([len(x[1]) for x in all_results.items()]), "results.")
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

	avg = {}
	for m in machines.keys():
		avg[m] = (len(machines[m]), int(sum(machines[m])/len(machines[m])))

	for m,i in sorted(avg.items(), key=lambda x:x[1][1]):
		print(m, "Results=",i[0], "Avg=", i[1])


def get_index_counts(all_results):

	index_counts={}
	for path in all_results.keys():
		if path not in index_counts.keys():
			index_counts[path] = []
		
		for r in all_results[path]:
			index_counts[path].append(numpy.array(r["index_counts"]+[0]))

	return index_counts



def get_stats_html(batch, all_results):

	# TODO menu

	result = "Not Found"

	for n in [ "00", "01", "02", "04" ]:
		if n in batch:
			result = get_stats_html_edges_combo(all_results)
	
	if "03" in batch or \
	   "05" in batch:
		result = get_stats_html_node_count_limit(all_results)

	print(batch)
	
	# Write result in doc/
	f = open("doc/"+batch+".html", "w")
	f.write(result)
	f.close()

	return result


def get_stats_html_edges_combo(all_results):
	index_counts = get_index_counts(all_results)

	stats_max     = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) ), dtype=int)
	stats_avg     = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) )) #, dtype=int)
	stats_samples = numpy.zeros( (len(puzzle.SIDE_EDGES), len(puzzle.MIDDLE_EDGES), len(puzzle.MIDDLE_EDGES) ), dtype=int)

	all_total_ic = {}

	for path in index_counts.keys():
		all_total_ic[path] = numpy.zeros((258), dtype=int)
		zeroes = [] 
		for ic in index_counts[path]:
			all_total_ic[path] = numpy.add(all_total_ic[path], ic)
			zeroes.append( numpy.where(ic == 0)[0][1] )

		z = numpy.where(all_total_ic[path] == 0)[0]

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
	o += "body {background-image:url('https://e2.bucas.name/img/fabric.png'); background-color: #444; text-align:center; zoom:250%;}"
	o += "table {border-spacing:0px; margin:auto;}"
	o += "th,td {height:32px; width:32px;padding:0px; text-align:center; font-size:7px; "
	o += "color: white; font-family: Sans-serif; text-shadow: 0px 0px 1px #222; }"
	o += ".numbers {height:8px}"
	o += ".ontop {position:relative; z-index:5}"
	# Mark the two known 470
	#o += "#td35  #3-5-4    {box-shadow: inset 0px 0px 0px 2px #f0f; cursor: pointer;}"
	#o += "#td482 #13-10-16 {box-shadow: inset 0px 0px 0px 2px #00f; cursor: pointer;}"
	o += "td.jb470    {box-shadow: inset 0px 0px 0px 3px #00f; cursor: pointer;}"
	o += "td.jb470jef {box-shadow: inset 0px 0px 0px 3px #f0f; cursor: pointer;}"
	o += "tr.jb470    {box-shadow: -10px 0px #00f, 10px 0px #00f; cursor: pointer;}"
	o += "tr.jb470jef {box-shadow: -10px 0px #f0f, 10px 0px #f0f; cursor: pointer;}"
	o += "</style>\n"

	o += "<table>\n"
	o += "<tr>"
	for m in range(23):
		o += "<th class='numbers'>"+str(m)+"</th>"
	o += "</tr>\n"
	o += "<tr>"
	for m in range(23):
		o += "<td>"+str(middle_motifs_top[m])+"</td>"
	o += "</tr>\n"
	o += "<tr>"
	for m in range(23):
		o += "<td>"+str(middle_motifs_bottom[m])+"</td>"
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
	o += "</script>\n"


	best_edges_combo = reversed(sorted(best_edges_combo.items(), key=lambda x:x[1]))

	o += "<table>"
	o += "<tr><th>Edges Combo</th><th>Average Max Depth</th><th>Max Depth</th><th># Samples</th><th>Depth Heatmap</th></tr>\n"
	for ec,k in best_edges_combo:
		c = ((k-minimum)/(256-minimum))*256 if k>0 else 0
		r,g,b,a = palette.palette[int(c)] 
		r,g,b,a = int(r*255),int(g*255),int(b*255),int(a*255)
		if k == 0:
			continue

		count = 0
		path = ""
		for path in all_results:
			if path.endswith(ec):
				count = len(all_results[path])
				break
				
		#path = "results/"+batch+"/"+ec
		#if path in all_results:

		ii,jj,kk = puzzle.path_to_edge_combo(path)
		ii=puzzle.SIDE_EDGES.index(ii)
		jj=puzzle.MIDDLE_EDGES.index(jj)
		kk=puzzle.MIDDLE_EDGES.index(kk)

		ic_heatmap = all_total_ic[path]
		ic_heatmap_log = numpy.log1p(ic_heatmap)
		ic_heatmap_normalize = (ic_heatmap_log/math.log(max(ic_heatmap))) * 255
		ic_heatmap_8bits = ic_heatmap_normalize.astype(numpy.uint8)

		heatmap_svg = '<svg height="20" width="512" xmlns="http://www.w3.org/2000/svg">'
		x = 0
		for h in ic_heatmap_8bits:
			rh,gh,bh = palette.palette_heatmap[h] 
			heatmap_svg += '<g><title>'+str(x)+'</title><line x1="'+str(x*2)+'" y1="0" x2="'+str(x*2)+'" y2="20" style="stroke:rgb('+str(rh)+','+str(gh)+','+str(bh)+');stroke-width:3" /></g>'
			x+=1
		heatmap_svg += '</svg>'

		o += "<tr id='tr"+ec.replace("-","_")+"' style='background-color:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");'>"
		o += "<td>"+ec+"</td>"
		o += "<td>"+str( "{:.2f}".format(k) if k>0 else "")+"</td>"
		o += "<td>"+str(stats_max[ii,jj,kk])+"</td>"
		o += "<td>"+str(count)+"</td><td style='background-color:black;'>"+heatmap_svg+"</td>"
		o += "</tr>\n"
	o += "</table>\n"

	o += "<script>"
	o += "document.getElementById('td35').onclick  = function () { window.open('https://e2.bucas.name/#puzzle=JBlackwood+Jef_470','_blank'); };"
	o += "document.getElementById('td35').classList.add('jb470jef');"
	o += "document.getElementById('td482').onclick = function () { window.open('https://e2.bucas.name/#puzzle=Joshua_Blackwood_470','_blank'); };"
	o += "document.getElementById('td482').classList.add('jb470');"

	o += "document.getElementById('tr5_3_4').onclick  = function () { window.open('https://e2.bucas.name/#puzzle=JBlackwood+Jef_470','_blank'); };"
	o += "document.getElementById('tr5_3_4').classList.add('jb470jef');"
	o += "document.getElementById('tr13_10_16').onclick = function () { window.open('https://e2.bucas.name/#puzzle=Joshua_Blackwood_470','_blank'); };"
	o += "document.getElementById('tr13_10_16').classList.add('jb470');"
	o += "</script>\n"
	return o


def get_stats_html_node_count_limit(all_results):

	#node_count_limit = random.randint(100000000,100000000000)
	ncl_min = 100000000
	ncl_max = 100000000000
	#ncl_list = []
	#for r in all_results[path]:
	#	ncl_list.append(r["node_count_limit"])

	#ncl_min = min(ncl_list)
	#ncl_max = max(ncl_list)

	all_total_ic = {}

	index_counts_and_node_count_limit = {}
	stats_max = {}
	stats_avg = {}
	stats_samples = {}
	nb_groups = 2048
	ncl_group_size = (ncl_max-ncl_min)//nb_groups
	for path in all_results.keys():
		if path not in index_counts_and_node_count_limit.keys():
			index_counts_and_node_count_limit[path] = []
			stats_max[path] = [0] * nb_groups
			stats_avg[path] = [0] * nb_groups
			stats_samples[path] = [0] * nb_groups
			for group in range(nb_groups):
				index_counts_and_node_count_limit[path].append( [] )
		

		for r in all_results[path]:
			ncl_group = (r["NODE_COUNT_LIMIT"] - ncl_min) // ncl_group_size
			index_counts_and_node_count_limit[path][ncl_group].append(numpy.array(r["index_counts"]+[0]))


		for group in range(nb_groups):
			#total_ic = numpy.zeros((258), dtype=int)

			zeroes = [] 
			for ic in index_counts_and_node_count_limit[path][group]:
				#total_ic = numpy.add(total_ic, ic)
				zeroes.append( numpy.where(ic == 0)[0][1] )

			#z = numpy.where(all_total_ic[path][group] == 0)[0]

			
			if len(zeroes) > 0:
				stats_samples[path][group] = len(zeroes)
				stats_max[path][group] = max(zeroes)
				stats_avg[path][group] = sum(zeroes)/len(zeroes)

		#print(i, j, k, "Max: "+str(max(zeroes)), "Avg: "+str(sum(zeroes)//len(zeroes)), "Samples: "+str(len(zeroes)))

		
	o = "<html>"
	o += "<head>"
	o += "<style>"
	o += "body {background-image:url('https://e2.bucas.name/img/fabric.png'); background-color: #444; text-align:center; zoom:100%;}"
	o += "table {border-spacing:0px; margin:auto;}"
	o += "color: white; font-family: Sans-serif; text-shadow: 0px 0px 1px #222; }"
	# Mark the two known 470
	#o += "#td35  #3-5-4    {box-shadow: inset 0px 0px 0px 2px #f0f; cursor: pointer;}"
	#o += "#td482 #13-10-16 {box-shadow: inset 0px 0px 0px 2px #00f; cursor: pointer;}"
	o += "polyline.jb470    {stroke:#00f; cursor: pointer;}"
	o += "polyline.jb470jef {stroke:#f0f; cursor: pointer;}"
	o += "</style>\n"
	o += "</head>"
	o += "<body>"


	o_svg = '<svg height="1024" width="2048" xmlns="http://www.w3.org/2000/svg">'
	zoom=150
	for path in all_results.keys():
		sp = path.split("/")[-1].replace("-","_")
		#print(list(map(int, sp.split("_"))))
		v = (sum( map(int, sp.split("_")) )*5) % 256
		g = f"{v:#0{4}x}".replace("0x","")
		sp_color = "#"+ g+g+g #"".join([chr(ord("0")+(c%10)) for c in map(int, sp.split("_"))])
		o_svg += '<polyline id="line'+sp+'" points="'
		for group in range(nb_groups):
			if stats_avg[path][group] > 0:
				o_svg+=str(group)+","+str((stats_avg[path][group]*zoom)-(245*zoom))+" "
		o_svg += '" style="fill:none;stroke:'+sp_color+';stroke-width:1" />'
	o_svg += '</svg>'

	oj = "<script>"
	oj += "jb470jef = document.getElementById('line5_3_4');"
	oj += "jb470jef.onclick = function () { window.open('https://e2.bucas.name/#puzzle=JBlackwood+Jef_470','_blank'); };"
	oj += "jb470jef.style.stroke = '#f0f';"
	oj += "jb470 = document.getElementById('line13_10_16');"
	oj += "jb470.onclick = function () { window.open('https://e2.bucas.name/#puzzle==Joshua_Blackwood_470','_blank'); };"
	oj += "jb470.style.stroke = '#00f';"
	oj += "</script>"
	oj += "</body>"
	oj += "</html>"

	return o+o_svg+oj
