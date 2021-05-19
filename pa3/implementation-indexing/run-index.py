import os
import re
import bs4
import nltk
import sqlite3
from tqdm import tqdm

import config
import preprocessing

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

	for site in config.INPUT_SITES:
		site_path = config.INPUT_PATH + "/" + site
		padding = (max([len(x) for x in config.INPUT_SITES]) - len(site)) * " " # Add spaces to align progress bars
		for page in tqdm(os.listdir(site_path), desc=f"Indexing {site}{padding}", unit="pages", disable=not PRINT_PROGRESS):
			page_path = site_path + "/" + page
			with open(page_path, "r", encoding="utf-8") as f:
				# Read page
				html = f.read()

				# Extract text from page
				text = preprocessing.extract_text(html)

				# Process words
				words = preprocessing.preprocess_text(text)
				for word, index in words:
					index_word(cur, word, index, site + "/" + page)

				# for word, index in words:
				# 	if "'" in word:
				# 		print(f">>>{word}<<< {i} {page}")
	
	# Save DB changes and close connection
	conn.commit()
	conn.close()
