from re import search
import sys
import time
import os
import math
import concurrent.futures
import multiprocessing
from tqdm import tqdm

import config
import searching
import preprocessing

#############################################
# Data retrieval without using SQLite index #
# > Parallel version (multiple processes) < #
#############################################

# Note:
# Multithreading in python is executed in a sequential manner (although thread execution is interleaved).
# This makes multithreading appropriate for I/O operations, where threads spend a lot of time waiting.
# However, for heavy computation, multithreading is just as, if not less, efficient than single-threaded execution.
# That is why multiprocessing is used here instead. Processes in Python are actually executed in parallel,
# making them suitable for computationally intensive tasks that can be parallelized.

PRINT_PROGRESS = True
OUTPUT_FILE = None # Set to None to print to console
NUM_WORKERS = 8 # Number of processes to use


# Search function wrapper for multiprocessing
# 	return list	- shared memory list used to return data from a process
def search_process(query_words, document_names, return_list):
	search_results = search(query_words, document_names)
	return_list += search_results

# Search for query matches in given documents
# 	query_words		- list of search terms
# 	document_names	- list of files to process, relative to INPUT_PATH
def search(query_words, document_names):
	search_results = []
	for document_name in document_names:
		page_path = config.INPUT_PATH + "/" + document_name
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
				search_results.append((frequency, document_name, snippets_str))

	return search_results


if __name__ == "__main__":
	# Parse parameters
	if len(sys.argv) < 2:
		print(f"Error: Missing search parameter!")
		sys.exit(1)
	query_text = sys.argv[1]

	# Use perf_counter instead of process_time when multiprocessing
	time_start = time.perf_counter() # Start timer

	# Start search
	query_words, _, _ = preprocessing.preprocess_text(query_text) # Preprocess query
	search_results = []

	# Get list of all documents
	document_names = []
	for site in config.INPUT_SITES:
		site_path = config.INPUT_PATH + "/" + site
		padding = (max([len(x) for x in config.INPUT_SITES]) - len(site)) * " " # Add spaces to align progress bars
		for page in os.listdir(site_path):
			# Only process html files with the same name as site
			if page.startswith(site) and page.endswith(".html"):
				document_names.append(site + "/" + page)
			
	# # Start multithreaded search
	# # MULTITHREADING IN PYTHON IS NOT EXECUTED IN PARALLEL
	# with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
	# 	futures = []
	# 	for i in range(NUM_WORKERS):
	# 		# Split work
	# 		begin = math.ceil(len(document_names) / NUM_WORKERS * i)
	# 		end = math.ceil(len(document_names) / NUM_WORKERS * (i + 1))
	# 		futures.append(executor.submit(search, query_words, document_names[begin : end]))
	# 	# Wait for results
	# 	for future in futures:
	# 		search_results += future.result()

	# Start multiprocess search
	with multiprocessing.Manager() as manager:
		return_lists = [manager.list() for _ in range(NUM_WORKERS)]
		jobs = []
		for pid in range(NUM_WORKERS):
			# Split work
			begin = math.ceil(len(document_names) / NUM_WORKERS * pid)
			end = math.ceil(len(document_names) / NUM_WORKERS * (pid + 1))
			p = multiprocessing.Process(target=search_process, args=(query_words, document_names[begin : end], return_lists[pid]))
			jobs.append(p)
			p.start()

		for pid in range(NUM_WORKERS):
			jobs[pid].join()
			search_results += return_lists[pid]

	# Sort search results by descending frequency
	search_results.sort(reverse=True, key=lambda res: res[0])

	# Limit number of results if specified
	if searching.MAX_RESULTS > 0 and len(search_results) >= searching.MAX_RESULTS:
		search_results = search_results[0 : searching.MAX_RESULTS]

	time_diff = time.perf_counter() - time_start # Stop timer

	# Print results
	searching.print_results(query_text, time_diff, search_results, OUTPUT_FILE)
	