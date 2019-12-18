import os
from word_brain import *

solver = WordBrain(puzzle_fetch=True)
for file in [os.getcwd()+'\\puzzles\\'+file+'.json' for file in solver.downloader.difficulties.keys()]:
	print(file)
	with open(file) as puzzles:
		puzzles = json.load(puzzles)
	for num,puzzle in enumerate(puzzles):
		solver.input_own_puzzle(puzzle['puzzle'],[len(w) for w in puzzle['solution']])
		words = solver.solve_puzzle()
		print(file.split('\\')[-1]+f'_{num+1}:',words)

# for file in os.listdir(os.getcwd()+'\\puzzles'):
# 	if file.split('.')[0] in solver.downloader.difficulties.keys():
# 		continue
# 	with open(os.getcwd()+'\\puzzles\\'+file) as puzzles:
# 		puzzles = json.load(puzzles)
# 	for num,puzzle in enumerate(puzzles):
# 		solver.input_own_puzzle(puzzle['puzzle'],[len(w) for w in puzzle['solution']])
# 		words = solver.solve_puzzle()
# 		print(file+f'_{num+1}:',words)