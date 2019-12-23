import requests
from bs4 import BeautifulSoup as bs

import json
import os
import itertools
import random

from tqdm import tqdm
from copy import deepcopy
from collections import defaultdict

def chunks(l,size):
	for i in range(0,len(l),size):
		yield l[i:i+size]

class WB2Downloader:

	def __init__(self,difficulty='easy'):

		self.base_url = 'https://wordbrain.info'
		self.headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
		}
		self.difficulty = difficulty

		home_resp = requests.get(self.base_url + '/en/themes',headers=self.headers)
		if not home_resp.status_code == 200:
			raise Exception('Cannot connect to WordBrain home page.')
			return
		home_soup = bs(home_resp.content,'html.parser')
		self.endpoints = [pack.a['href'] for pack in home_soup.select('div.theme')]

		self.difficulties = {
		'easy':self.endpoints[:45],
		'medium':self.endpoints[45:90],
		'hard':self.endpoints[90:135],
		'veryhard':self.endpoints[135:180],
		'impossible':self.endpoints[180:]
		}

		if not self.difficulty in self.difficulties.keys():
			raise Exception(f'{self.difficulty} is not supported.')
			return

		if not 'wb2_puzzles' in os.listdir():
			os.mkdir(os.getcwd()+'\\wb2_puzzles')

	def download_one_puzzle(self):
		try:
			endpoint = random.choice(self.difficulties[self.difficulty])
			puzzle_resp = requests.get(self.base_url + endpoint,headers=self.headers)
			if not puzzle_resp.status_code == 200:
				raise Exception('Cannot connect to WordBrain home page.')
				return
			puzzle_soup = bs(puzzle_resp.content,'html.parser')

			all_puzzles = [p for p in puzzle_soup.select('li a') if p.span]
			selected_puzzle = random.choice(all_puzzles)

			solution = [w.strip() for w in selected_puzzle.select('span.solution')[0].text.split(',')]
			puzzle = selected_puzzle.select('span.letterblock')[0]

			return {'puzzle':[[cell.text.upper() for cell in line] for line in \
			list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution}
		except Exception as e:
			return e

	def download_all_puzzles(self,from_endpoint=False):
		word_brain_words = []
		for difficulty in tqdm(self.difficulties):
			puzzle_data = []
			by_endpoint = defaultdict(list)
			for endpoint in self.difficulties[difficulty]:
				puzzle_resp = requests.get(self.base_url + endpoint,headers=self.headers)
				if not puzzle_resp.status_code == 200:
					raise Exception('Cannot connect to WordBrain home page.')
					return
				puzzle_soup = bs(puzzle_resp.content,'html.parser')

				for selected_puzzle in [p for p in puzzle_soup.select('li a') if p.span]:
					solution = [w.strip() for w in selected_puzzle.select('span.solution')[0].text.split(',')]
					puzzle = selected_puzzle.select('span.letterblock')[0]
					puzzle_data.append({'puzzle':[[cell.text.upper() for cell in line] for line in \
					list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution})
					by_endpoint[endpoint.split('/')[3]].append({'puzzle':[[cell.text.upper() for cell in line] for line in \
					list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution})
			if from_endpoint:
				for endpoint in by_endpoint:
					with open(os.getcwd()+'\\wb2_puzzles\\'+endpoint+'.json','w') as download_file:
						json.dump(by_endpoint[endpoint],download_file)
			else:
				for puzzle in puzzle_data:
					word_brain_words += puzzle['solution']
				with open(os.getcwd()+'\\wb2_puzzles\\'+difficulty+'.json','w') as download_file,\
				open('all_word_brain2_words.txt','w') as wbw:
					json.dump(puzzle_data,download_file)
					for word in set(word_brain_words):
						print(word.strip(' '),file=wbw)
