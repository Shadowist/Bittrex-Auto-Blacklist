import csv
import requests
import os
import time

from datetime import datetime
import tzlocal

import logging
FORMAT = '%(asctime)-15s [%(levelname)s] %(filename)s(%(lineno)d): %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('test')
logger.setLevel(logging.INFO)

# Settings!
BITTREX_COIN_LOG = "bittrex_coins.csv"
PAIRS_FILE = "PAIRS.properties"
TARGET_AGE = 30  # Days - Disable trading if coin is younger than age
HEARTBEAT = 60  # Seconds - Simple delay between checking for new coins
MARKET = "ETH"  # Markets: BTC/ETH

class bittrex_manager():
	''' An interface for bittrex coin analysis. '''
	coin_list = {}
	pairs_file = []
	old_pairs_file = []

	def __init__(self, reset=False):
		logger.info("Initializing...")
		if os.path.exists(BITTREX_COIN_LOG) and not reset:
			logger.info("Found: {}".format(BITTREX_COIN_LOG))
			self.read_log()
			self.update()
		else:
			self.update()
		logger.info("Initialization Complete!")

	def read_log(self):
		logger.info("Reading: {}".format(BITTREX_COIN_LOG))
		self.coin_list.clear()
		with open(BITTREX_COIN_LOG, 'r') as myfile:
			reader = csv.reader(myfile)
			for row in reader:
				self.coin_list[row[0]] = row[1]

	def update(self, use_log = False):
		if use_log:
			self.read_log()

		logger.info("Updating coin information...")
		response = requests.post("https://bittrex.com/api/v1.1/public/getcurrencies")
		response.raise_for_status()
		currencies = []

		# Query all coins
		for entry in response.json()['result']:
			if entry['Currency'] in self.coin_list or entry['Currency'] == MARKET:
				continue
			else:
				currencies.append(entry['Currency'])

		if len(currencies) == 0:
			logger.info("No new coins found!")
		else:
			check_coin_list = list(self.coin_list.items())

			# Query created date for coins
			for index, coin in enumerate(currencies):
				if coin in self.coin_list or coin == MARKET:
					continue

				logger.info("Query coin: {0:s} ({1:.2f}%)".format(coin, float(index + 1) / len(currencies) * 100))

				if coin == "BTC" and MARKET == "ETH":
					query = requests.post("https://bittrex.com/api/v1.1/public/getmarketsummary?market=BTC-ETH")
				else:
					query = requests.post("https://bittrex.com/api/v1.1/public/getmarketsummary?market={}-{}".format(MARKET, coin))

				if query.json()['success'] == False:
					check_coin_list.append([coin, query.json()['message']])
				else:
					market_summary = query.json()['result'][0]
					created_date = market_summary['Created']
					check_coin_list.append([coin, created_date])

			logger.info("Writing: {}".format(BITTREX_COIN_LOG))
			with open(BITTREX_COIN_LOG, 'w') as myfile:
				wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
				self.coin_list = {}
				for entry in check_coin_list:
					self.coin_list[entry[0]] = entry[1]
					wr.writerow(entry)

		coins = self.coin_list

		logger.info("Generating blacklist...")
		blacklist = []

		today = datetime.today()
		for key, value in coins.items():
			if value == "INVALID_MARKET":
				continue
			convert = value.split(".")[0]
			test_date = datetime.strptime(convert, "%Y-%m-%dT%H:%M:%S")

			if (today - test_date).days < TARGET_AGE:
				blacklist.append("{}_{}_trading_enabled=false".format(MARKET, key))

		# Transfer Blacklist
		logger.info("Formatting blacklist...")
		old_pairs_file = self.pairs_file
		self.pairs_file = []

		with open(PAIRS_FILE, 'r') as f:
			for entry in f:
				self.pairs_file.append(entry.strip('\n'))

		if old_pairs_file == self.pairs_file:
			logger.info("No changes detected!")
		else:
			start_pos = -1
			end_pos = -1
			for index, line in enumerate(self.pairs_file):
				if line == "# [Start Bittrex Auto Blacklist]":
					start_pos = index

			for index, line in enumerate(self.pairs_file):
				if line == "# [End Bittrex Auto Blacklist]":
					end_pos = index

			if start_pos == -1 and end_pos == -1:
				self.pairs_file.append("# [Start Bittrex Auto Blacklist]")

				for entry in blacklist:
					self.pairs_file.append(entry)

				self.pairs_file.append("# [End Bittrex Auto Blacklist]")
			elif start_pos == -1 or end_pos == -1:
				logger.critical("Start or end not found!")
			else:
				del self.pairs_file[start_pos+1:end_pos]
				for index, entry in enumerate(blacklist):
					self.pairs_file.insert(start_pos + index + 1, entry)

			with open(PAIRS_FILE, 'w') as f:
				logger.info("Writing: {}".format(PAIRS_FILE))
				for entry in self.pairs_file:
					f.write(entry + "\n")
				logger.info("{} updated!".format(PAIRS_FILE))

manager = bittrex_manager()

while(1):
	time.sleep(HEARTBEAT)
	logger.info("Heartbeat - Updating")
	manager.update(True)