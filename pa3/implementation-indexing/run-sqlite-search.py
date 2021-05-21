import sys
import time
import sqlite3
from tqdm import tqdm

import config
import searching
import preprocessing

#####################################
# Data retrieval using SQLite index #
#####################################

PRINT_PROGRESS = True
OUTPUT_FILE = None # Set to None to print to console


if __name__ == "__main__":
	# Parse parameters
	if len(sys.argv) < 2:
		print(f"Error: Missing search parameter!")
		sys.exit(1)
	query_text = sys.argv[1]

	# Connect to DB
	conn = sqlite3.connect('inverted-index.db')
	cur = conn.cursor()

	time_start = time.process_time() # Start timer

	# Preprocess query
	query_words, _, _ = preprocessing.preprocess_text(query_text)
	query_words = searching.remove_duplicates(query_words)
	
	search_results = []

	# Start search
	if len(query_words) > 0:
		# Generate format string for SQLite query in the form (?, ?, ...)
		query_words_format = ", ".join("?" * len(query_words))

		# Find all matches
		cur_select = cur.execute(f"""
			SELECT p.documentName, SUM(p.frequency) AS freqSum, GROUP_CONCAT(p.indexes)
			FROM Posting p
			WHERE
				p.word IN ({query_words_format})
			GROUP BY p.documentName
			ORDER BY freqSum DESC;
		""", query_words)

		num_results = 0
		for row in tqdm(cur_select, desc=f"Processing query results", unit="results", disable=not PRINT_PROGRESS):
			# Limit number of results if specified
			if searching.MAX_RESULTS > 0 and num_results >= searching.MAX_RESULTS:
				break
			num_results += 1

			# Extract data from query results
			document_name = row[0]
			frequency = row[1]
			indexes = list(map(int, row[2].split(",")))
			indexes.sort()

			page_path = config.INPUT_PATH + "/" + document_name
			with open(page_path, "r", encoding="utf-8") as f:
				# Extract text from page
				page_html = f.read()
				page_text = preprocessing.extract_text(page_html)
				page_strings = page_text.split()

				# Get snippets
				snippets_str = searching.extract_snippets(indexes, page_strings)

				# Add to search results
				search_results.append((frequency, document_name, snippets_str))

	time_diff = time.process_time() - time_start # Stop timer

	# Print results
	searching.print_results(query_text, time_diff, search_results, OUTPUT_FILE)

	# Close DB connection
	conn.close()
