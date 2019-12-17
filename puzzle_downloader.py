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

class WBDownloader:

	def __init__(self,difficulty='easy'):

		self.base_url = 'https://wordbrain.info'
		self.headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
		}
		self.difficulty = difficulty

		home_resp = requests.get(self.base_url + '/en/',headers=self.headers)
		if not home_resp.status_code == 200:
			raise Exception('Cannot connect to WordBrain home page.')
			return
		home_soup = bs(home_resp.content,'html.parser')
		self.endpoints = [pack.a['href'] for pack in home_soup.select('div.pack')]

		self.difficulties = {
		'easy':self.endpoints[:self.endpoints.index('/en/turtle/')+1],
		'medium':self.endpoints[self.endpoints.index('/en/turtle/')+1:self.endpoints.index('/en/lion/')+1],
		'hard':self.endpoints[self.endpoints.index('/en/lion/')+1:self.endpoints.index('/en/minotaur/')+1],
		'impossible':self.endpoints[self.endpoints.index('/en/minotaur/')+1:]
		}

		if not self.difficulty in self.difficulties.keys():
			raise Exception(f'{self.difficulty} is not supported.')
			return

		if not 'puzzles' in os.listdir():
			os.mkdir(os.getcwd()+'\\puzzles')

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

			solution = selected_puzzle.select('span.solution')[0].text.split(',')
			puzzle = selected_puzzle.select('span.letterblock')[0]

			return {'puzzle':[[cell.text.upper() for cell in line] for line in \
			list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution}
		except Exception as e:
			return e

	def download_all_puzzles(self,from_endpoint=False):
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
					solution = selected_puzzle.select('span.solution')[0].text.split(',')
					puzzle = selected_puzzle.select('span.letterblock')[0]
					puzzle_data.append({'puzzle':[[cell.text.upper() for cell in line] for line in \
					list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution})
					by_endpoint[endpoint.split('/')[2]].append({'puzzle':[[cell.text.upper() for cell in line] for line in \
					list(chunks(puzzle.find_all('span'),len(puzzle.find_all('br'))))],'solution':solution})
			if from_endpoint:
				for endpoint in by_endpoint:
					with open(os.getcwd()+'\\puzzles\\'+endpoint+'.json','w') as download_file:
						json.dump(by_endpoint[endpoint],download_file)
			else:
				with open(os.getcwd()+'\\puzzles\\'+difficulty+'.json','w') as download_file:
					json.dump(puzzle_data,download_file)
