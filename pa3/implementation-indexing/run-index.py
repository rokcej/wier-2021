import os
import re
import bs4
import nltk
import sqlite3
from tqdm import tqdm

import config
import preprocessing

###################################
# Data preprocessing and indexing #
###################################

PRINT_PROGRESS = True


# Insert word into database
def index_word(cur, word, index, document_name):
	index_str = str(index)

	# Insert word into IndexWord
	cur.execute("SELECT * FROM IndexWord WHERE word = ?", (word,))
	res = cur.fetchone()
	if res is None:
		cur.execute("INSERT INTO IndexWord VALUES (?)", (word,))
	
	# Insert word into Posting
	cur.execute("SELECT * FROM Posting WHERE word = ? AND documentName = ?", (word, document_name))
	res = cur.fetchone()
	if res is None:
		cur.execute("INSERT INTO Posting VALUES (?, ?, 1, ?)", (word, document_name, index_str))
	else:
		frequency = res[2]
		indexes_str = res[3]
		if index_str not in indexes_str.split(","):
			frequency += 1
			indexes_str += "," + index_str
			cur.execute("UPDATE Posting SET frequency = ?, indexes = ? WHERE word = ? and documentName = ?",
				(frequency, indexes_str, word, document_name))


if __name__ == "__main__":
	# Connect to DB
	conn = sqlite3.connect('inverted-index.db')
	cur = conn.cursor()

	# Loop over all sites
	for site in config.INPUT_SITES:
		site_path = config.INPUT_PATH + "/" + site
		# Loop over all pages
		padding = (max([len(x) for x in config.INPUT_SITES]) - len(site)) * " " # Add spaces to align progress bars
		for page in tqdm(os.listdir(site_path), desc=f"Indexing {site}{padding}", unit="pages", disable=not PRINT_PROGRESS):
			# Only process html files with the same name as site
			if not (page.startswith(site) and page.endswith(".html")):
				continue

			page_path = site_path + "/" + page
			with open(page_path, "r", encoding="utf-8") as f:
				# Extract text from page
				html = f.read()
				text = preprocessing.extract_text(html)

				# Process words
				words, indexes, _ = preprocessing.preprocess_text(text)
				for word, index in zip(words, indexes):
					index_word(cur, word, index, site + "/" + page)
	
	# Save DB changes and close connection
	conn.commit()
	conn.close()
