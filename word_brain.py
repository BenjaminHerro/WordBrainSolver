import requests
import json
import os
import sys
import itertools

from copy import deepcopy
from collections import defaultdict
from wordbrain_downloader import *
from wordbrain2_downloader import *

class WordBrain:

	def __init__(self,
		puzzle_fetch=False,
		difficulty='easy',
		word_brain=1
		):

		# if not 'dictionary.json' in os.listdir():
		# 	resp = requests.get('https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt')
		# 	self.dictionary = resp.content.decode('utf-8').split('\r\n')
		# 	with open('dictionary.json','w') as d:
		# 		json.dump(self.dictionary,d)
		# else:
		# 	with open('dictionary.json') as d:
		# 		self.dictionary = json.load(d)

		# 	self.dictionary_starts = {s:[w[:s] for w in self.dictionary] for s in range(2,20)}

		if not 'dictionary.json' in os.listdir():
			resp = requests.get('https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt')
			self.dictionary = [w for w in resp.content.decode('utf-8').split('\n') if w]
			with open('dictionary.json','w') as d:
				json.dump(self.dictionary,d)
		else:
			with open('dictionary.json') as d:
				self.dictionary = json.load(d)

			self.dictionary_starts = {s:[w[:s] for w in self.dictionary] for s in range(2,20)}

		if 'all_word_brain_words.txt' in os.listdir():
			with open('all_word_brain_words.txt') as wbw:
				self.word_brain_words = [w.strip('\n').strip(' ') for w in wbw.readlines() if w]
			if 'all_word_brain2_words.txt' in os.listdir():
				with open('all_word_brain2_words.txt') as wbw2:
					self.word_brain_words = [e.strip(' ') for e in [w.strip('\n') for w in wbw2.readlines()] + self.word_brain_words if e]
			self.word_brain_word_starts = {s:[w[:s] for w in self.word_brain_words] for s in range(2,20)}

		try:
			if word_brain == 1:
				self.downloader = WBDownloader(difficulty=difficulty)
			elif word_brain == 2:
				self.downloader = WB2Downloader(difficulty=difficulty)
			else:
				raise Exception('This version of Word Brain does not exist')
				return
		except Exception as e:
			return e
			sys.exit()

		if word_brain == 1:
			folder='wb_puzzles'
		elif word_brain == 2:
			folder='wb2_puzzles'

		if not puzzle_fetch:
			try:
				puzzle_file = [e for e in os.listdir(os.getcwd()+f'\\{folder}') if difficulty in e][0]
			except:
				self.downloader.download_all_puzzles()
				puzzle_file = [e for e in os.listdir(os.getcwd()+f'\\{folder}') if difficulty in e][0]

			with open(os.getcwd()+f'\\{folder}\\'+puzzle_file) as pf:
				self.puzzles = json.load(pf)
				self.puzzle_located = random.choice(self.puzzles)

				self.solution = self.puzzle_located['solution']
				self.puzzle = self.puzzle_located['puzzle']
				self.word_lengths = [len(w) for w in self.solution]
		else:
			self.puzzle_downloaded = self.downloader.download_one_puzzle()

			self.solution = self.puzzle_downloaded['solution']
			self.puzzle = self.puzzle_downloaded['puzzle']
			self.word_lengths = [len(w) for w in self.solution]

		if self.puzzle:
			self.grid_coords = [[(x,y) for y in range(len(i))] for x,i in enumerate(self.puzzle)]
			self.total_available_coords = list(itertools.chain.from_iterable(self.grid_coords))
			self.words = defaultdict(list)
			self.total_possible_words = []

		self.memoize={}

	def input_own_puzzle(self,puzzle,word_lengths):
		self.puzzle = [[e.upper() for e in line] for line in puzzle]
		self.grid_coords = [[(x,y) for y in range(len(i))] for x,i in enumerate(self.puzzle)]
		self.total_available_coords = list(itertools.chain.from_iterable(self.grid_coords))
		self.words = defaultdict(list)
		self.solution = None
		self.word_lengths = word_lengths

	def search_for_word(self,
		loc=(0,0),
		visited=[(0,0)],
		words=[],
		word_lengths=None,
		curr_word_length=None,
		graph=None):
		if tuple(visited) in self.memoize:
			return self.memoize[tuple(visited)]
		self.memoize[tuple(visited)] = [''.join([graph[c[0]][c[1]] for c in visited])]
		if len(self.total_possible_words) > 2:
			return
		if len(visited) in range(2,20) \
		and not ''.join([graph[c[0]][c[1]] for c in visited]).lower() \
		in self.word_brain_word_starts[len(visited)]:
			return
		if len(visited) == curr_word_length \
		and ''.join([graph[c[0]][c[1]] for c in visited]).lower() in self.word_brain_words:
			if not word_lengths:
				self.total_possible_words.append(words + [''.join([graph[c[0]][c[1]] for c in visited])])
				return
			for line in graph:
				print('|',' | '.join(line),'|',end='\n')
			print()
			new_graph = self.rearrange_graph(visited,graph)
			cwl = word_lengths[0]
			if len(word_lengths) == 1:
				wl = []
			else:
				wl = word_lengths[1:]
			words = words + [''.join([graph[c[0]][c[1]] for c in visited])]
			for i,line in enumerate(new_graph):
				for j,l in enumerate(line):
					if l:
						self.search_for_word(
								loc=(i,j),
								visited=[(i,j)],
								words=words,
								word_lengths=wl,
								curr_word_length=cwl,
								graph=new_graph
								)

		else:
			available_coords = self.get_possible_moves(loc,visited,graph)
			for coord in available_coords:
				self.search_for_word(
						loc=coord,
						visited=visited+[coord],
						words=words,
						word_lengths=word_lengths,
						curr_word_length=curr_word_length,
						graph=graph
						)

	def search_for_word(self,
		loc=(0,0),
		visited=[(0,0)],
		words=[],
		word_lengths=None,
		curr_word_length=None,
		graph=None):
		# if len(self.total_possible_words) > 2:
		# 	return
		# if len(visited) in range(2,20) \
		# and not ''.join([graph[c[0]][c[1]] for c in visited]).lower() \
		# in self.dictionary_starts[len(visited)]:
		# 	return
		# if len(visited) == curr_word_length \
		# and ''.join([graph[c[0]][c[1]] for c in visited]).lower() in self.dictionary:
		if len(self.total_possible_words) > 2:
			return
		if len(visited) in range(2,20) \
		and not ''.join([graph[c[0]][c[1]] for c in visited]).lower() \
		in self.word_brain_word_starts[len(visited)]:
			return
		if len(visited) == curr_word_length \
		and ''.join([graph[c[0]][c[1]] for c in visited]).lower() in self.word_brain_words:
			if not word_lengths:
				self.total_possible_words.append(words + [''.join([graph[c[0]][c[1]] for c in visited])])
				return
			for line in graph:
				print('|',' | '.join(line),'|',end='\n')
			print()
			new_graph = self.rearrange_graph(visited,graph)
			cwl = word_lengths[0]
			if len(word_lengths) == 1:
				wl = []
			else:
				wl = word_lengths[1:]
			words = words + [''.join([graph[c[0]][c[1]] for c in visited])]
			for i,line in enumerate(new_graph):
				for j,l in enumerate(line):
					if l:
						self.search_for_word(
								loc=(i,j),
								visited=[(i,j)],
								words=words,
								word_lengths=wl,
								curr_word_length=cwl,
								graph=new_graph
								)
		else:
			available_coords = self.get_possible_moves(loc,visited,graph)
			for coord in available_coords:
				self.search_for_word(
						loc=coord,
						visited=visited+[coord],
						words=words,
						word_lengths=word_lengths,
						curr_word_length=curr_word_length,
						graph=graph
						)

	def rearrange_graph(self,word,graph):
		graph = deepcopy(graph)
		for c in word:
			graph[c[0]][c[1]] = ' '
		graph_rev = graph[::-1]
		for i,line in enumerate(graph_rev):
			if i == len(graph_rev)-1:
				continue
			for j,letter in enumerate(line):
				if letter == ' ':
					num_back = 0
					while True:
						if i + num_back >= len(graph):
							num_back -= 1
							break
						elif graph_rev[i+num_back][j] == ' ':
							num_back += 1
						else:
							break
					graph_rev[i][j] = graph_rev[i+num_back][j]
					graph_rev[i+num_back][j] = ' '
		return graph_rev[::-1]

	def solve_puzzle(self,word_lengths=None):
		if not word_lengths:
			word_lengths = self.word_lengths
		self.total_possible_words = []
		for coord in self.total_available_coords:
			cwl = word_lengths[0]
			if len(word_lengths) == 1:
				wl = []
			else:
				wl = word_lengths[1:]
			word = self.search_for_word(
				loc=coord,
				visited=[coord],
				word_lengths=wl,
				curr_word_length=cwl,
				graph=self.puzzle
				)
		return self.total_possible_words

	def get_possible_moves(self,position,visited,graph):
		x,y = position
		return (({(x-1,y),(x-1,y+1),(x,y+1),(x+1,y+1),
		(x+1,y),(x+1,y-1),(x,y-1),(x-1,y-1)} \
		- set(visited)) \
		& set(self.total_available_coords)) \
		- set(itertools.chain.from_iterable([[(x,y) 
			for y,i2 in enumerate(i) if i2 == '']
		 for x,i in enumerate(graph)]))