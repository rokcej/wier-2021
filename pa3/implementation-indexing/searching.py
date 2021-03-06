#######################################
# Common functions for data searching #
#######################################

MAX_RESULTS = 5 # Set to 0 to remove limit
MAX_SNIPPETS = 4 # Set to 0 to remove limit
SNIPPET_LENGTH = 3 # Number of words around matches to include in snippets
OUTPUT_FORMAT = "{:9s}  {:42s}  {:s}\n" # Search result output format

# Remove duplicate terms from a list of words
# 	words	- list containing preprocessed query words
def remove_duplicates(words):
	words_unique = []
	for word in words:
		if word not in words_unique:
			words_unique.append(word)

	return words_unique

# Extract snippets given a list of indexes
# 	indexes	- list of match indexes
# 	strings	- list of words that indexes point to
def extract_snippets(indexes, strings):
	if MAX_SNIPPETS > 0 and len(indexes) >= MAX_SNIPPETS:
		indexes = indexes[0 : MAX_SNIPPETS]

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
		end = min(end, len(strings) - 1)
		# Extract snippet
		snippet = " ".join(strings[begin : end + 1])
		snippets.append(snippet)
		# Continue to next snippet
		i = j
	
	# Merge snippets
	snippets_str = " ... ".join(snippets) # Add in-between dots
	if indexes[0] - SNIPPET_LENGTH > 0: # Add leading dots
		snippets_str = "... " + snippets_str
	if indexes[-1] + SNIPPET_LENGTH < len(strings) - 1: # Add trailing dots
		snippets_str = snippets_str + " ..."
	
	return snippets_str

# Output search results in a structured format
# 	query	- search query text
# 	time	- elapsed search time
# 	results	- list of tuples (frequency, document_name, snippet)
# 	output_file	- (optional) print output to file instead
def print_results(query, time, results, output_file=None):
	output =  f"Results for query: \"{query}\"\n\n"
	output += f"  Results found in {time:.3f}s.\n\n"
	output += f"  {OUTPUT_FORMAT.format('Frequency', 'Document', 'Snippet')}"
	output += f"  {OUTPUT_FORMAT.format('-' * 9, '-' * 42, '-' * 42)}"
	
	for result in results:
		output += f"  {OUTPUT_FORMAT.format(str(result[0]), result[1], result[2])}"

	if output_file:
		with open(output_file, "a", encoding="utf-8") as f:
			f.write(output + "\n")
	else:
		print(output)
