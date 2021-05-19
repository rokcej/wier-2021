import os
import re
import bs4
import nltk
import sqlite3
from tqdm import tqdm

import stopwords

PRINT_PROGRESS = True

INPUT_PATH = "../input-indexing/"
INPUT_SITES = [
	"e-prostor.gov.si",
	"e-uprava.gov.si",
	"evem.gov.si",
	"podatki.gov.si",
]

HTML_BLACKLIST = [
	"script",
	"style",
	"head",
	"meta",
	"[document]"
]


# def text_filter(element):
# 	# Check if parent tag is blacklisted
# 	if (element.parent.name in HTML_BLACKLIST):
# 		return False
# 	# Check if element is a comment
# 	if isinstance(element, bs4.element.Comment):
# 		return False
# 	return True

# Extract text from page
def extract_text(html):
	soup = bs4.BeautifulSoup(html, "html.parser")
	# V1
	for el in soup(HTML_BLACKLIST):
		el.extract() # Remove element
	text = soup.get_text()
	# # V2
	# texts = soup.find_all(text=True)
	# texts = filter(text_filter, texts)
	# text = " ".join(t.strip() for t in texts)

	return text


# Convert text into a list of words
def preprocess_text(text):
	# Split text by whitespace
	strings = text.split()
	words = []
	for index, string in enumerate(strings):
		# Tokenize words
		tokens = nltk.tokenize.word_tokenize(string)
		for token in tokens:
			# Convert to lowercase
			token = token.lower()
			# Remove stopwords and punctuation marks
			if token in stopwords.STOPWORDS_SLOVENE or token in stopwords.PUNCTUATION_MARKS:
				continue
			# Remove dot sequences
			if (re.match(r"\.{2,}$", token) is not None):
				continue
			# Remove leading apostrophes
			for prefix in ["''", "'"]: # Must be ordered by descending length!
				if token.startswith(prefix):
					token = token[len(prefix):]
					break
			words.append((token, index))
	
	return words
def preprocess_text_old(text):
	# Tokenize words
	words = nltk.tokenize.word_tokenize(text)
	i = 0
	while i < len(words):	
		# Convert to lowercase
		words[i] = words[i].lower()
		# Remove stopwords and punctuation marks
		if words[i] in stopwords.STOPWORDS_SLOVENE or words[i] in stopwords.PUNCTUATION_MARKS:
			words.pop(i)
			continue
		# Remove dot sequences
		if (re.match(r"\.{2,}$", words[i]) is not None):
			words.pop(i)
			continue
		# Remove leading apostrophes
		for prefix in ["''", "'"]: # Must be ordered by descending length!
			if words[i].startswith(prefix):
				words[i] = words[i][len(prefix):]
				break
		i += 1
	
	return words


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

	for site in INPUT_SITES:
		site_path = INPUT_PATH + site
		padding = (max([len(x) for x in INPUT_SITES]) - len(site)) * " " # Add spaces to align progress bars
		for page in tqdm(os.listdir(site_path), desc=f"Indexing {site}{padding}", unit="pages", disable=not PRINT_PROGRESS):
			page_path = site_path + "/" + page
			with open(page_path, "r", encoding="utf-8") as f:
				# Read page
				html = f.read()

				# Extract text from page
				text = extract_text(html)

				# Process words
				words = preprocess_text(text)
				for word, index in words:
					index_word(cur, word, index, site + "/" + page)

				# for word, index in words:
				# 	if "'" in word:
				# 		print(f">>>{word}<<< {i} {page_path}")
	
	# Save DB changes and close connection
	conn.commit()
	conn.close()
