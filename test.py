from word_brain import *
w=WordBrain()

w.input_own_puzzle(
	[['G', 'A', 'E', 'T', 'E', 'B'], ['L', 'R', 'R', 'E', 'R', 'R'], ['E', 'E', 'H', 'G', 'E', 'I'],
	 ['B', 'C', 'T', 'T', 'R', 'W'], ['B', 'U', 'I', 'H', 'O', 'C'], ['I', 'L', 'R', 'G', 'S', 'K']],
	[len(w) for w in ['butter', 'iceberg', 'shower', 'lighter', 'large', 'brick']]
	)

w.input_own_puzzle(
	[['D', 'L', 'L', 'O', 'T'], ['L', 'O', 'B', 'L', 'K'], ['O', 'B', 'O', 'A', 'O'], ['G', 'G', 'O', 'V', 'O'], ['F', 'A', 'B', 'X', 'B']],
	[len(w) for w in ['book', 'bag', 'oval', 'box', 'bolt', 'log', 'fold']]
	)

w.input_own_puzzle(
	[['Y', 'S', 'E', 'A', 'C', 'H', 'N'], ['S', 'S', 'D', 'P', 'E', 'N', 'O'], ['G', 'R', 'A', 'R', 'E', 'W', 'C'], 
	['R', 'N', 'E', 'I', 'A', 'T', 'B'], ['E', 'F', 'P', 'S', 'R', 'H', 'S'], ['E', 'A', 'R', 'M', 'E', 'A', 'A'],
	 ['D', 'A', 'S', 'S', 'S', 'E', 'D']],
	[len(w) for w in ['sad', 'prism', 'bacon', 'heart', 'swan', 'cheese', 'grenade', 'safe', 'dress', 'spray']]
	)
words=w.solve_puzzle()

w.puzzle=[['J', 'N', 'T'], ['A', 'A', 'F'], ['P', 'L', 'E']]
w.solution = ['left', 'japan']
w.word_lengths = [4,5]