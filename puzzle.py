import re



SIDE_EDGES = [ 1, 5, 9, 13, 17 ]
MIDDLE_EDGES = [ 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22 ]

pieces = {}
patterns_count = [0] * (len(SIDE_EDGES + MIDDLE_EDGES)+1)
edges_combo = []

def read_pieces():

	with open('solver/Util.cs.template', 'r') as file:
		for line in file:
			# Check if the line starts with "new Piece()"
			if line.strip().startswith("new Piece()"):
				# Use a regular expression to extract the numbers
				match = re.search(r'PieceNumber = (\d+), TopSide = (\d+), RightSide = (\d+), BottomSide = (\d+), LeftSide = (\d+)', line)
				if match:
					# Extract numbers from the regex match
					piece_number = int(match.group(1))
					top = int(match.group(2))
					right = int(match.group(3))
					bottom = int(match.group(4))
					left = int(match.group(5))
					
					# Store the numbers in the dictionary
					pieces[piece_number] = {
						"u": top,
						"r": right,
						"d": bottom,
						"l": left
					}
					patterns_count[top] += 1
					patterns_count[right] += 1
					patterns_count[bottom] += 1
					patterns_count[left] += 1


def get_edges_combo():
	for i in SIDE_EDGES:
		for j in MIDDLE_EDGES:
			for k in MIDDLE_EDGES:
				if j != k:
					if (i, k,j ) not in edges_combo:
						edges_combo.append( (i,j,k) )

"""
	ni = patterns_count[i]
	nj = patterns_count[j]
	nk = patterns_count[k]
	#print(i, j, k, ":", ni, nj, nk, " -> ", ni + nj + nk)
"""

read_pieces()
get_edges_combo()
#print(len(pieces))
#print(patterns_count)
print(len(edges_combo))

#11 to 160



