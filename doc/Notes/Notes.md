# What makes Joshua Blackwood's algorithm so good?


Joshua Blackwood's algorithm is a classic back-tracker with manually crafted heuristics and optimisations.


## Heuristic :: Patterns prioritisation

### Most overlapping patterns first
The algorithm scores the puzzle pieces based on the sides colors.
It tries to place three colors first:
 - 1 color from the edge
 - 2 internal colors

```
heuristic_sides = new List<int>() { 13, 16, 10 };
```

The current known best scores are using two different sets of patterns
Patterns_Priorization_470_a.png
Patterns_Priorization_470_b.png


Here is a page attempting to represent the results of many samples of runs of the algorithm with different sets of three patterns.
Each of the five half-squares represent one of the edge color, and for each, two of the internal colors.
The number/color in each represents how far the algorithm was able to go for this set of three patterns.
Below that, we have the depth heatmap which shows how many times the algorithm spent on a particular depth.
The orange bars in the middle are the positions around the mandatory piece.
The orange bars towards the end are the edge pieces.
https://github.com/jfbucas/wrapper_blackwood/blob/main/doc/batch00_edge_combos_stats.html

Note: Given the low number of samples, it would be good to attempt to reproduce these results to validate or invalidate.


### How is the prioritisation is done
The pieces are sorted by score, so that the algorithm tries them first.
To place these pieces first, the algorithm initializes a heuristic_array as follows:
```
heuristic_array = new int[256];
for (int i = 0; i < 256; i++) {
  if (i <= 16)
     heuristic_array[i] = 0;
  else if (i <= 26)
     heuristic_array[i] = (int)(((float)i - 16) * (float)2.8);
  else if (i <= 56)
     heuristic_array[i] = (int)((((float)i - 26) * (float)1.43333) + 28);
  else if (i <= 76)
     heuristic_array[i] = (int)(((((float)i - 56) * (float)0.9)) + 71);
  else if (i <= 102)
     heuristic_array[i] = (int)(((((float)i - 76) * (float)0.6538)) + 89);
  else if (i <= 160)
     heuristic_array[i] = (int)(((((float)i - 102) / 4.4615)) + 106);
}
```

Each value of the array represents the number of those three colors that have to be placed to keep going further down the search tree.
If the number is lower, the algorithm simply backtracks.

Using many samples with random variations of the array, the following picture shows how far the algorithm was able to go for each variation, the greener the better.
Joshua Blackwood's manually crafted values, the line in blue is right in the middle of the green area.

 heuristic_array.png

## Heuristic :: The search order
The search starts at the bottom left of the puzzle, which is the nearest to the mandatory piece in the middle.
It starts with a standard row-scan all the way to depth 180.
After depth 180, the algorithm tries to place the remaining border pieces every few steps.
The border pieces have higher constraints and need to be placed progressively, including the third corner.
The search order doesn't spiral-in (a.k.a. starts with the border ring), and it doesn't leave it to the end (like a classic row-scan) either; a "Not too tight and not too loose" approach.

board_order.svg

## Heuristic :: Breaks allowed
Approaching the end of the search, a number of edges mismatches are allowed.
The mismatches are cumulative. This means they are either at that depth or after.

You can have one break from depth 201, but it can be any depth after 201.
You can have a second break from depth 206.
Etc.
```
break_indexes_allowed = new List<int>() { 201, 206, 211, 216, 221, 225, 229, 233, 237, 239 };
```

## Search tactics

### The first row is randomized
In order to try something new at each attempt, the first corner and the bottom pieces are randomly sorted

```
foreach (var m in bottom_side_pieces_rotated)
  bottom_sides[m.Key] = m.Value.OrderByDescending(x => (x.RotatedPiece.Heuristic_Side_Count > 0 ? 100 : 0) + rand.Next(0, 99)).Select(x => x.RotatedPiece).ToArray();

board[0] = corners[0].ToList().OrderBy(x => rand.Next(1, 1000)).First();
```

### Limits
The main loop will stop when the number of nodes explored goes over 50 billions.
The back-tracker algorithm rarely goes back to the first few rows.
This means that the row-scan can get stuck in an impossible situation.
So we want to be sure we abandon the attempt and try to find a more fertile one.

## Optimisation
Joshua Blackwood made sure that the memory footprint of those lists in C# fit in the CPU cache.

The algorithm uses lists of pieces indexed in a global lookup table.
A list of possible pieces is assigned for each position on the puzzle board.
```
master_piece_lookup = new RotatedPiece[256][][];
```

Each piece is described with a small structure:
```
    public struct RotatedPiece
    {
        public ushort PieceNumber { get; set; }
        public byte Rotations { get; set; }
        public byte TopSide { get; set; }
        public byte RightSide { get; set; }
        public byte Break_Count { get; set; }
        public byte Heuristic_Side_Count { get; set; }
    }
```
