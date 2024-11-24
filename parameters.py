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
	"NB_CORES"              : 2, # 2 or more
	"NUMBER_SOLVEPUZZLE"    : 5,
	"NUMBER_LOOPS"          : 2,
}

#print(default_template_params)


def get_next_job_params( next_job ):
	template_params = default_template_params.copy()
	template_params["JOBGROUP"] = next_job
	template_params["HEURISTIC_SIDES"] = next_job[0].replace("results/","").replace("-",",")

	return template_params





	
