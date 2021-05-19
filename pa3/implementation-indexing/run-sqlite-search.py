import sys
import time
import sqlite3

import config
import preprocessing

SNIPPET_LENGTH = 3

OUTPUT_PADDING = "  "
OUTPUT_FORMAT = OUTPUT_PADDING + "{:11s} {:42s} {:s}\n"

if __name__ == "__main__":
	# Parse parameters
	if len(sys.argv) < 2:
		print(f"Error: Missing search parameter!")
		sys.exit(1)
	query = sys.argv[1]

	# Connect to DB
	conn = sqlite3.connect('inverted-index.db')
	cur = conn.cursor()

	time_start = time.process_time()

	# Start search
	output = ""
	words = preprocessing.preprocess_text(query)
	if len(words) > 0:
		words_format = ", ".join("?" * len(words))
		words_data = tuple([w for w, _ in words])

		curSelect = cur.execute(f"""
			SELECT p.documentName, SUM(p.frequency) AS freqSum, GROUP_CONCAT(p.indexes)
			FROM Posting p
			WHERE
				p.word IN ({words_format})
			GROUP BY p.documentName
			ORDER BY freqSum DESC;
		""", words_data)

		for row in curSelect:
			#output += f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}\n"

			document_name = row[0]
			frequency = row[1]
			indexes_str = row[2]

			indexes = list(map(int, indexes_str.split(",")))
			indexes.sort()

			page_path = config.INPUT_PATH + "/" + document_name
			with open(page_path, "r", encoding="utf-8") as f:
				# Extract text from page
				page_html = f.read()
				page_text = preprocessing.extract_text(page_html)
				page_words = page_text.split()

				# Get snippets
				snippets = []
				i = 0
				while i < len(indexes):
					# Snippet start index
					begin = max(indexes[i] - SNIPPET_LENGTH, 0)
					# Snippet end index
					end = indexes[i] + SNIPPET_LENGTH
					j = i + 1
					while j < len(indexes):
						if indexes[j] - SNIPPET_LENGTH > end:
							break
						end = indexes[j] + SNIPPET_LENGTH
						j += 1
					end = min(end, len(page_words) - 1)
					# Extract snippet
					snippet = " ".join(page_words[begin : end + 1])
					snippets.append(snippet)
					# Continue to next snippet
					i = j
				
				# Merge snippets
				snippets_str = " ... ".join(snippets) # Add in-between dots
				if indexes[0] - SNIPPET_LENGTH > 0: # Add leading dots
					snippets_str = "... " + snippets_str
				if indexes[-1] + SNIPPET_LENGTH < len(page_words) - 1: # Add trailing dots
					snippets_str = snippets_str + " ..."

				# Add to output
				output += OUTPUT_FORMAT.format(str(frequency), document_name, snippets_str)

	time_diff = time.process_time() - time_start

	# Print results
	print(f"Results for query: \"{query}\"")
	print()
	print(f"{OUTPUT_PADDING}Results found in {time_diff:.3f}s.")
	print()
	print(OUTPUT_FORMAT.format("Frequencies", "Document", "Snippet"), end="")
	print(OUTPUT_FORMAT.format("-" * 11, "-" * 42, "-" * 42), end="")
	print(output)

	# Close DB connection
	conn.close()
