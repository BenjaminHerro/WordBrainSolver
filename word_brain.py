import requests
import json
import os
import sys
import itertools

from copy import deepcopy
from collections import defaultdict
from puzzle_downloader import *

class WordBrain:

	def __init__(self,
		puzzle_fetch=False,
		difficulty='easy'
		):

		if not 'dictionary.json' in os.listdir():
			resp = requests.get('https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt')
			self.dictionary = resp.content.decode('utf-8').split('\r\n')
			with open('dictionary.json','w') as d:
				json.dump(self.dictionary,d)
		else:
			with open('dictionary.json') as d:
				self.dictionary = json.load(d)

		with open('all_word_brain_words.txt') as wbw:
			self.word_brain_words = [w.strip('\n') for w in wbw.readlines()]

		if not puzzle_fetch:
			try:
				puzzle_file = [e for e in os.listdir(os.getcwd()+'\\puzzles') if difficulty in e][0]
				with open(os.getcwd()+'\\puzzles\\'+puzzle_file) as pf:
					self.puzzles = json.load(pf)
					self.puzzle_located = random.choice(self.puzzles)

					self.solution = self.puzzle_located['solution']
					self.puzzle = self.puzzle_located['puzzle']
					self.word_lengths = [len(w) for w in self.solution]
			except Exception as e:
				return e
				sys.exit()
		else:
			try:
				self.downloader = WBDownloader(difficulty=difficulty)
			except Exception as e:
				return e
				sys.exit()
			self.puzzle_downloaded = self.downloader.download_one_puzzle()

			self.solution = self.puzzle_downloaded['solution']
			self.puzzle = self.puzzle_downloaded['puzzle']
			self.word_lengths = [len(w) for w in self.solution]

		if self.puzzle:
			self.grid_coords = [[(x,y) for y in range(len(i))] for x,i in enumerate(self.puzzle)]
			self.total_avalable_coords = list(itertools.chain.from_iterable(self.grid_coords))
			self.words = defaultdict(list)
			self.total_possible_words = []

	def input_own_puzzle(self,puzzle,word_lengths):
		self.puzzle = [[e.upper() for e in line] for line in puzzle]
		self.solution = None
		self.word_lengths = word_lengths

	def search_for_word(self,
		loc=(0,0),
		visited=[(0,0)],
		words=[],
		word_lengths=None,
		curr_word_length=None,
		graph=None):

		# if len(visited) == curr_word_length \
		# and ''.join([graph[c[0]][c[1]] for c in visited]).lower() in self.dictionary:
		print(visited)
		if len(visited) == curr_word_length \
		and ''.join([graph[c[0]][c[1]] for c in visited]).lower() in self.word_brain_words:
			if not word_lengths:
				self.total_possible_words.append(words + [''.join([graph[c[0]][c[1]] for c in visited])])
				return
			new_graph = self.rearrange_graph(visited,graph)
			print(new_graph)
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
			graph[c[0]][c[1]] = ''
		for i,line in enumerate(graph[:-1]):
			for j,letter in enumerate(line):
				if letter and graph[i+1][j] == '':
					graph[i+1][j] = letter
					graph[i][j] = ''
		return graph

	def solve_puzzle(self,word_lengths=None):
		if not word_lengths:
			word_lengths = self.word_lengths
		self.total_possible_words = []
		for coord in self.total_avalable_coords:
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
		return [pos for pos in [(x-1,y),(x-1,y+1),(x,y+1),(x+1,y+1),
		(x+1,y),(x+1,y-1),(x,y-1),(x-1,y-1)]
		if pos in self.total_avalable_coords and pos not in visited
		and graph[pos[0]][pos[1]] != '']
