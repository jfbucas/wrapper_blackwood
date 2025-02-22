import re
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
import numpy

import puzzle
import templating

HOOK=''
if os.environ.get('HOOK'): 
	HOOK = os.environ.get('HOOK')


jblackwood_heuristic_array_variations = [
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3, 1, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
] 


def get_heuristic_array_from_variations(variations):
	max_i = 0
	for i in reversed(range(len(variations))):
		if variations[i] != 0:
			max_i =i
			break

	heuristic_array = []
	cumulated = 0
	for i in range(len(variations)):
		if i <= max_i:
			cumulated += variations[i]
			heuristic_array.append( cumulated )
		else:
			heuristic_array.append( 0 )


	return heuristic_array



default_template_params = {
	"HEURISTIC_SIDES"       : "13, 16, 10",
	"NODE_COUNT_LIMIT"      : 50000000000,
	"MAX_HEURISTIC_INDEX"   : 160,
	"HEURISTIC_ARRAY"       : str(get_heuristic_array_from_variations( jblackwood_heuristic_array_variations)).replace("[","{").replace("]","}"),
	"BREAK_INDEXES_ALLOWED" : "201, 206, 211, 216, 221, 225, 229, 233, 237, 239",
	"NB_CORES"              : 1, # 1 or more
	"NUMBER_SOLVEPUZZLE"    : 5,
	"NUMBER_LOOPS"          : 2,
	"HOOK"                  : '',
	"BOARD_ORDER"		: [
	    [ 196,  197,    198,    199,    200,    205,    210,    215,    220,    225,    230,    235,    243,    249,    254,    255 ],
	    [ 191,  192,    193,    194,    195,    204,    209,    214,    219,    224,    229,    234,    242,    248,    252,    253 ],
	    [ 186,  187,    188,    189,    190,    203,    208,    213,    218,    223,    228,    233,    241,    247,    250,    251 ],
	    [ 181,  182,    183,    184,    185,    202,    207,    212,    217,    222,    227,    232,    240,    244,    245,    246 ],
	    [ 176,  177,    178,    179,    180,    201,    206,    211,    216,    221,    226,    231,    236,    237,    238,    239 ],
	    [ 160,  161,    162,    163,    164,    165,    166,    167,    168,    169,    170,    171,    172,    173,    174,    175 ],
	    [ 144,  145,    146,    147,    148,    149,    150,    151,    152,    153,    154,    155,    156,    157,    158,    159 ],
	    [ 128,  129,    130,    131,    132,    133,    134,    135,    136,    137,    138,    139,    140,    141,    142,    143 ],
	    [ 112,  113,    114,    115,    116,    117,    118,    119,    120,    121,    122,    123,    124,    125,    126,    127 ],
	    [ 96,   97,     98,     99,     100,    101,    102,    103,    104,    105,    106,    107,    108,    109,    110,    111 ],
	    [ 80,   81,     82,     83,     84,     85,     86,     87,     88,     89,     90,     91,     92,     93,     94,     95  ],
	    [ 64,   65,     66,     67,     68,     69,     70,     71,     72,     73,     74,     75,     76,     77,     78,     79  ],
	    [ 48,   49,     50,     51,     52,     53,     54,     55,     56,     57,     58,     59,     60,     61,     62,     63  ],
	    [ 32,   33,     34,     35,     36,     37,     38,     39,     40,     41,     42,     43,     44,     45,     46,     47  ],
	    [ 16,   17,     18,     19,     20,     21,     22,     23,     24,     25,     26,     27,     28,     29,     30,     31  ],
	    [ 0,    1,      2,      3,      4,      5,      6,      7,      8,      9,      10,     11,     12,     13,     14,     15  ]
	    ]
}

#print(default_template_params)


def get_next_job_params( next_job ):

	template_params = default_template_params.copy()
	for k in next_job.keys():
		template_params[k] = next_job[k]

	return template_params


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

	if "batch00" in batch:

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

	elif "batch01" in batch:

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )

		best_edges_combo = [
			"13-10-16",
			"1-10-16",
			"9-15-19",
			"5-15-19",
			"17-16-20",
			"13-3-10",
			"5-3-4",
			"9-10-15",
			"13-16-20",
			"17-3-22",
			"1-16-20",
			"13-3-4",
			"5-15-20",
			"5-3-22",
			"9-12-15",
			"5-4-18",
			"17-12-15",
			"13-3-22",
			"5-19-21",
			]

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

	elif "batch02" in batch:

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )

		best_edges_combo = [
			"13-10-16",
			"17-16-20",
			"5-3-22",
			"9-15-19",
			"1-10-16",
			"13-3-22",
			"13-3-16",
			"1-16-20",
			"17-3-22",
			"13-16-20",
			"13-3-4",
			"5-19-21",
			"5-3-4",
			"9-12-15",
			"5-4-22",
			"5-16-20",
			"5-4-19",
			"5-15-19",
			"9-10-15",
			"13-3-10",
			"17-3-4",
			"5-12-15",
			"1-10-15",
			"5-3-19",
			"5-3-15",
			"5-15-20",
			"5-4-18",
			]

		random.shuffle(best_edges_combo)

		next_job = {
			"job_title": "Best Edges Combo Mapping With 500000000 Node_Count_Limit",
			"job_description": "Edges Combo "+str(best_edges_combo[0]),
			"job_batch": "batch02_edges_combo_500000000",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : 500000000,
			"NUMBER_LOOPS"          : 50,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch03" in batch:

		best_edges_combo = [
			"13-10-16",
			"5-3-4",
			"9-10-15",
			"13-3-22",
			"9-15-19",
			"9-12-15",
			"5-19-21",
			"13-16-20",
			"5-15-19",
			"5-3-15",
			"1-12-15",
			"13-3-10",
			"9-19-21",
			"5-21-22",
			]

		random.shuffle(best_edges_combo)
		node_count_limit = random.randint(100000000,100000000000)

		next_job = {
			"job_title": "Variations on Node Count Limit",
			"job_description": str(best_edges_combo[0]+" / "+str(node_count_limit)),
			"job_batch": "batch03_variations_on_node_count_limit",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : node_count_limit,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"NUMBER_LOOPS"          : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch04" in batch:

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )

		best_edges_combo = [
			"13-10-16",
			"17-16-20",
			"5-3-22",
			"9-15-19",
			"1-10-16",
			"13-3-22",
			"13-3-16",
			"1-16-20",
			"17-3-22",
			"13-16-20",
			"13-3-4",
			"5-19-21",
			"5-3-4",
			"9-12-15",
			"5-4-22",
			"5-16-20",
			"5-4-19",
			"5-15-19",
			"9-10-15",
			"13-3-10",
			"17-3-4",
			"5-12-15",
			"1-10-15",
			"5-3-19",
			"5-3-15",
			"5-15-20",
			"5-4-18",
			]

		random.shuffle(best_edges_combo)

		next_job = {
			"job_title": "Best Edges Combo Mapping With 500000000 Node_Count_Limit 500 loops",
			"job_description": "Edges Combo "+str(best_edges_combo[0])+" 500 loops",
			"job_batch": "batch04_edges_combo_500000000",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : 500000000,
			"NUMBER_LOOPS"          : 500,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch05" in batch:

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )
		
		random.shuffle(best_edges_combo)

		node_count_limit = random.randint(1000000000,100000000000)
		next_job = {
			"job_title": "All Edges Combo With random Node_Count_Limit 10 loops",
			"job_description": "Edges Combo "+str(best_edges_combo[0])+" 10 loops with "+str(node_count_limit)+" node_count_limit",
			"job_batch": "batch05_all_edges_combo_with_random_node_count_limit",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : node_count_limit,
			"NUMBER_LOOPS"          : 10,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch06" in batch:

		best_edges_combo = []
		for i,j,k in puzzle.get_edges_combo():
			best_edges_combo.append( str(i)+"-"+str(j)+"-"+str(k) )
		
		random.shuffle(best_edges_combo)

		node_count_limit = random.randint(5000000000,100000000000)
		next_job = {
			"job_title": "All Edges Combo With random Node_Count_Limit 10 loops",
			"job_description": "Edges Combo "+str(best_edges_combo[0])+" 1 loops with "+str(node_count_limit)+" node_count_limit",
			"job_batch": "batch06_all_edges_combo_with_random_node_count_limit",
			"job_path" : best_edges_combo[0],
			"HEURISTIC_SIDES" : best_edges_combo[0].replace("-",","),
			"NODE_COUNT_LIMIT" : node_count_limit,
			"NUMBER_LOOPS"          : 1,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch07" in batch:
		variations = list(jblackwood_heuristic_array_variations)
		
		vcount = 0
		while vcount < 32:
			i1 = random.randint(0, len(variations)-1)
			if variations[i1] > 0:
				i2 = random.randint(0, numpy.max(numpy.nonzero(variations))-1)
				if i1 != i2:
					variations[i1] -= 1
					variations[i2] += 1
					
					vcount += 1 

		next_job = {
			"job_title": "Heuristic array variations, 32 variations",
			"job_description": "32 Variations on on the heuristic array variations",
			"job_batch": "batch07_heuristic_array_variations_32_variations",
			"HEURISTIC_ARRAY"       : str(get_heuristic_array_from_variations( variations )).replace("[","{").replace("]","}"),
			"NODE_COUNT_LIMIT" : 100000000000,
			"NUMBER_LOOPS"          : 2,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch08" in batch:
		break_indexes = list(map(int, default_template_params["BREAK_INDEXES_ALLOWED"].split(",")))
		
		vcount = 0
		while vcount < 16:
			i = random.randint(0, len(break_indexes)-1)
			m = random.randint(0,2)-1
			if m == 0:
				continue

			if break_indexes[i]+m in break_indexes:
				continue
			break_indexes[i]= break_indexes[i]+m
			vcount += 1 

		next_job = {
			"job_title": "Break Indexes variations, 16 variations",
			"job_description": "16 Variations on on the break indexes allowed",
			"job_batch": "batch08_break_indexes_16_variations",
			"BREAK_INDEXES_ALLOWED" : ",".join(map(str,break_indexes)),
			"NODE_COUNT_LIMIT" : 100000000000,
			"NUMBER_LOOPS"          : 2,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch09" in batch:
		break_indexes = list(map(int, default_template_params["BREAK_INDEXES_ALLOWED"].split(",")))
		
		vcount = 0
		while vcount < 32:
			i = random.randint(0, len(break_indexes)-1)
			m = random.randint(0,2)-1
			if m == 0:
				continue

			if break_indexes[i]+m in break_indexes:
				continue
			break_indexes[i]= break_indexes[i]+m
			vcount += 1 

		next_job = {
			"job_title": "Break Indexes variations, 32 variations",
			"job_description": "32 Variations on on the break indexes allowed",
			"job_batch": "batch09_break_indexes_32_variations",
			"BREAK_INDEXES_ALLOWED" : ",".join(map(str,break_indexes)),
			"NODE_COUNT_LIMIT" : 100000000000,
			"NUMBER_LOOPS"          : 2,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch10" in batch:
		break_indexes = list(map(int, default_template_params["BREAK_INDEXES_ALLOWED"].split(",")))
		
		vcount = 0
		while vcount < 128:
			i = random.randint(0, len(break_indexes)-1)
			m = random.randint(0,4)-2
			if m == 0:
				continue

			if break_indexes[i]+m in break_indexes:
				continue
			break_indexes[i]= break_indexes[i]+m
			vcount += 1 

		next_job = {
			"job_title": "Break Indexes variations",
			"job_description": "Variations on on the break indexes allowed",
			"job_batch": "batch10_break_indexes_32_variations",
			"BREAK_INDEXES_ALLOWED" : ",".join(map(str,sorted(break_indexes))),
			"NODE_COUNT_LIMIT" : 100000000000,
			"NUMBER_LOOPS"          : 2,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	elif "batch11" in batch:
		#board_order = list(map(int, default_template_params["BOARD_ORDER"].split(",")))
		board_order = default_template_params["BOARD_ORDER"]
		
		board_order = []
		for i in range(16):
			board_order.append([None] * 16)	

		board = []
		order = 0
		for i in range(17):
			board.append(list("                 "))
		for i in range(17):
			board[i][16] = "#"
			board[16][i] = "#"

		for j in range(15,7,-1):
			for i in range(16):
				board[j][i] = "#"
				board_order[j][i] = order
				order += 1

				#for i in range(17):
				#	print("".join(board[i]))
				#print("-----")

		while True:
			next_possibilities = []
			for j in range(15,-1,-1):
				if board[j+1][0] == " ":
					continue
				for i in range(0,16):
					if board[j][i] == "#":
						continue
					if board[j][i-1] == " ":
						break
					if board[j][i-1] == "#" and board[j+1][i] == "#":
						next_possibilities.append((j,i))
					
			if len(next_possibilities) == 0:
				break

			random.shuffle(next_possibilities)	
			#print(next_possibilities)

			(j,i) = next_possibilities[0]
			board[j][i] = "#"
			board_order[j][i] = order
			order += 1
				
			#for i in range(17):
			#	print("".join(board[i]))
			#print("-----")

		next_job = {
			"job_title": "Board Order",
			"job_description": "Board Order",
			"job_batch": "batch11_board_order",
			"BOARD_ORDER" : str(board_order).replace("[","{").replace("],","},\n").replace("]]","}}"),
			"NODE_COUNT_LIMIT" : 100000000000,
			"NUMBER_LOOPS"          : 2,
			"NUMBER_SOLVEPUZZLE"    : 1,
			"HOOK" : HOOK,
			}

		return next_job

	
	return None
	#global job_list
	#if len(job_list) == 0:
	#	job_list = prepare_next_jobs()
	#
	#return job_list.pop(0)
