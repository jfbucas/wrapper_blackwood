# EternityII_Solver
Solver For The Eternity II Puzzle

For Linux you'll want to:
1. Change the number of cores/threads
2. Change the save function to save to a place that you're happy with
3. Install Mono
   ```apt install mono-mcs libmono-system-net4.0-cil libmono-system-net-http4.0-cil```
4. Compile
   ```mcs -unsafe -r:System.Net.Http  Program.cs Util.cs Structs.cs```
5. Execute with
   ```mono Program.exe```
