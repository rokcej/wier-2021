# -*- coding: UTF-8 -*-
import re
import bs4
import nltk

from stopwords import STOPWORDS_SLOVENE


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
	"-", "_", "/", "|", ":", ";", # Separators
	"(", ")", "[", "]", "{", "}", "<", ">" # Brackets
])


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
			if token in STOPWORDS_SLOVENE or token in PUNCTUATION_MARKS:
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
		if words[i] in STOPWORDS_SLOVENE or words[i] in PUNCTUATION_MARKS:
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
