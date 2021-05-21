from re import search
import sys
import time
import os
from tqdm import tqdm

import config
import searching
import preprocessing

#############################################
# Data retrieval without using SQLite index #
# > Sequential version (single process) <   #
#############################################

PRINT_PROGRESS = True
OUTPUT_FILE = None # Set to None to print to console


if __name__ == "__main__":
	# Parse parameters
	if len(sys.argv) < 2:
		print(f"Error: Missing search parameter!")
		sys.exit(1)
	query_text = sys.argv[1]

	time_start = time.process_time() # Start timer

	# Preprocess query
	query_words, _, _ = preprocessing.preprocess_text(query_text)
	query_words = searching.remove_duplicates(query_words)
	
	search_results = []

	# Start search
	for site in config.INPUT_SITES:
		site_path = config.INPUT_PATH + "/" + site
		# Loop over all pages
		padding = (max([len(x) for x in config.INPUT_SITES]) - len(site)) * " " # Add spaces to align progress bars
		for page in tqdm(os.listdir(site_path), desc=f"Searching {site}{padding}", unit="pages", disable=not PRINT_PROGRESS):
			# Only process html files with the same name as site
			if not (page.startswith(site) and page.endswith(".html")):
				continue

			page_path = site_path + "/" + page
			with open(page_path, "r", encoding="utf-8") as f:
				# Extract text from page
				page_html = f.read()
				page_text = preprocessing.extract_text(page_html)

				# Process words
				page_words, page_indexes, page_strings = preprocessing.preprocess_text(page_text)

				# Find query matches
				frequency = 0
				indexes = []
				for page_word, page_index in zip(page_words, page_indexes):
					if page_word in query_words:
						indexes.append(page_index)
						frequency += 1
				
				if frequency > 0:
					# Get snippets
					snippets_str = searching.extract_snippets(indexes, page_strings)

					# Add to search results
					search_results.append((frequency, site + "/" + page, snippets_str))
					
	# Sort search results by descending frequency
	search_results.sort(reverse=True, key=lambda res: res[0])

	# Limit number of results if specified
	if searching.MAX_RESULTS > 0 and len(search_results) >= searching.MAX_RESULTS:
		search_results = search_results[0 : searching.MAX_RESULTS]

	time_diff = time.process_time() - time_start # Stop timer

	# Print results
	searching.print_results(query_text, time_diff, search_results, OUTPUT_FILE)
	