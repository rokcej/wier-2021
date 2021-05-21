# -*- coding: UTF-8 -*-
import re
import bs4
import nltk

import stopwords

###########################################
# Common functions for text preprocessing #
###########################################

HTML_BLACKLIST = [
	"script",
	"style",
	"head",
	"meta",
	"[document]"
]

PUNCTUATION_MARKS = set([
	",", ".", "!", "?", # Basic
	"'", "''", "\"", "`", "``", # Apostrophes
	"-", "--", "_", "/", "|", ":", ";", # Separators
	"(", ")", "[", "]", "{", "}", "<", ">", # Brackets
	"+", "*", "&", "#", "%", "©" # Symbols
])

WORD_MAP = {
	"eur" : ["eur", "euro", "eurov", "evro", "evrov", "€"]
}
# Invert map: { key: [val1, val2] } -> { val1: key, val2: key }
WORD_MAP = {v : k for k, vs in WORD_MAP.items() for v in vs}

# def text_filter(element):
# 	# Check if parent tag is blacklisted
# 	if (element.parent.name in HTML_BLACKLIST):
# 		return False
# 	# Check if element is a comment
# 	if isinstance(element, bs4.element.Comment):
# 		return False
# 	return True

# Extract text from page
# 	html	- page html code
# returns visible text on the page
def extract_text(html):
	soup = bs4.BeautifulSoup(html, "html.parser")
	# Version 1
	for el in soup(HTML_BLACKLIST):
		el.extract() # Remove element
	text = soup.get_text(separator=" ", strip=True)
	# # Version 2
	# texts = soup.find_all(text=True)
	# texts = filter(text_filter, texts)
	# text = " ".join(t.strip() for t in texts)

	return text

# Convert text into a list of words
# 	text -	text extracted from a page
# returns a tuple (list of preprocessed words, indexes of preprocessed words, list of original words)
def preprocess_text(text):
	# Split text by whitespace
	strings = text.split()
	words = []
	indexes = []
	for index, string in enumerate(strings):
		# Tokenize words
		tokens = nltk.tokenize.word_tokenize(string)
		for token in tokens:
			# Convert to lowercase
			token = token.lower()
			# Remove stopwords and punctuation marks
			if token in stopwords.STOPWORDS_SLOVENE or token in PUNCTUATION_MARKS:
				continue
			# Remove dot sequences
			if (re.match(r"\.{2,}$", token) is not None):
				continue
			# Remove leading apostrophes
			for prefix in ["''", "'"]: # Must be ordered by descending length!
				if token.startswith(prefix):
					token = token[len(prefix):]
					break
			# Remove trailing dot
			if token.endswith("."):
				token = token[:-1]
			# Map words
			mapped_token = WORD_MAP.get(token)
			if mapped_token:
				token = mapped_token

			words.append(token)
			indexes.append(index)
	
	return words, indexes, strings
