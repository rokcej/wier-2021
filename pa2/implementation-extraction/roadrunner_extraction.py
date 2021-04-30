from bs4 import BeautifulSoup
from bs4 import element # Tag, NavigableString


class Node:
	def __init__(self, t, val, data):
		self.t = t
		self.val = val
		self.data = data
		self.c = []

	def copy(self):
		node = Node(self.t, self.val, self.data)
		for child in self.c:
			node.c.append(child.copy())
		return node
		

def _makeTree(bs_node):
	if type(bs_node) is element.Tag:
		node = Node("TAG", bs_node.name, bs_node)
		for bs_child in bs_node.children:
			child = _makeTree(bs_child)
			if child:
				node.c.append(child)
		return node
	elif type(bs_node) is element.NavigableString:
		string = bs_node.string.strip()
		if string:
			return Node("STRING", string, bs_node)
		else:
			return None
	else:
		return None



def tree2ufre(node, depth=0):
	padding = depth * " "
	ufre = ""

	if node.t == "STRING":
		if node.val == "#TEXT":
			ufre = padding + node.val + "\n"
	else:
		if node.t == "TAG":
			pre  = f"<{node.val}>\n"
			post = f"</{node.val}>\n"
		elif node.t == "OPTIONAL":
			pre  = "(\n"
			post = ")?\n"
		elif node.t == "ITERATOR":
			pre  = "(\n"
			post = ")+\n"
		else:
			raise Exception("Invalid node type")
		
		rec = ""
		for child in node.c:
			rec += tree2ufre(child, depth + 1)
			
		if rec:
			ufre = padding + pre + rec + padding + post
	
	return ufre


def makeTree(html_content):
	soup = BeautifulSoup(html_content, 'html.parser')

	unwanted_tags = ["br", "hr", "script", "input", "option"]
	for tag in unwanted_tags:
		for el in soup.select(tag):
			el.extract()

	bs_root = soup.body
	root = _makeTree(bs_root)

	return root


def printTree(node, depth=0):
	print(2 * depth * " " + str(node.val))
	for c in node.c:
		printTree(c, depth + 1)


def _matchPattern(wrapper_nodes, sample_nodes):
	if (len(wrapper_nodes) != len(sample_nodes)):
		return None

	matches = [w.copy() for w in wrapper_nodes]
	for i in range(len(matches)):
		matches[i] = _match(matches[i], sample_nodes[i])
		if matches[i] == None:
			return None
	for i in range(len(matches)):
		wrapper_nodes[i] = matches[i]
	return wrapper_nodes


def _match(wrapper, sample):
	K = 4 # Maximum number of pattern candidates

	if wrapper.t != sample.t:
		return None

	if wrapper.t == "STRING": # and sample.t == "STRING":
		if wrapper.val != sample.val:
			wrapper.val = "#TEXT"
		return wrapper

	if wrapper.t == "TAG": # and sample.t == "TAG":
		if wrapper.val != sample.val:
			return None
	
	# At this point both roots are matching tags

	wi = 0
	si = 0

	while wi < len(wrapper.c) or si < len(sample.c):
		# Check if match
		if wi < len(wrapper.c) and si < len(sample.c) and _match(wrapper.c[wi], sample.c[si]) != None:
			wi += 1
			si += 1
			continue
		
		# Check if optional
		if wi < len(wrapper.c) and wrapper.c[wi].t == "OPTIONAL":
			if _matchPattern(wrapper.c[wi].c, sample.c[si : si + len(wrapper.c[wi].c)]) != None:
				si += len(wrapper.c[wi].c)
				wi += 1
			else:
				wi += 1
			continue
		if si < len(sample.c) and sample.c[si].t == "OPTIONAL":
			if _matchPattern(sample.c[si].c, wrapper.c[wi : wi + len(sample.c[si].c)]) != None:
				wrapper.c[wi : wi + len(sample.c[si].c)] = [sample.c[si]]
				wi += 1
				si += 1
			else:
				wrapper.c.insert(wi, sample.c[si])
				wi += 1
				si += 1
			continue

		# Check if iterator
		if wi < len(wrapper.c) and wrapper.c[wi].t == "ITERATOR":
			count = 0
			while _matchPattern(wrapper.c[wi].c, sample.c[si + count * len(wrapper.c[wi].c) : si + (count + 1) * len(wrapper.c[wi].c)]) != None:
				count += 1
			if count >= 1:
				si += count * len(wrapper.c[wi].c)
				wi += 1
				continue
		if si < len(sample.c) and sample.c[si].t == "ITERATOR":
			count = 0
			while _matchPattern(sample.c[si].c, wrapper.c[wi + count * len(sample.c[si].c) : wi + (count + 1) * len(sample.c[si].c)]) != None:
				count += 1
			if count >= 1:
				wrapper.c[wi : wi + count * len(sample.c[si].c)] = [sample.c[si]]
				wi += 1
				si += 1
				continue

		# At this point the nodes are mismatched

		# Iterator discovery
		if wi > 0 and si > 0: # and wrapper.c[wi-1].t == sample.c[si-1].t and wrapper.c[wi-1].val == sample.c[si-1].val:q
			it = None

			## Candidates on the wrapper
			terminal_tag = wrapper.c[wi-1].val
			# Generate candidates
			candidates = []
			for i in range(wi, min(2 * wi, len(wrapper.c))):
				if wrapper.c[i].val == terminal_tag:
					candidates.append(i)
					if len(candidates) == K:
						break
			# Test candidates
			for wj in candidates:
				matches = [wrapper.c[i].copy() for i in range(wi, wj + 1)]

				found_square = True
				for i in range(len(matches)):
					matches[i] = _match(matches[i], wrapper.c[wi - len(matches) + i])
					if matches[i] == None:
						found_square = False
						break
				if found_square:
					it = Node("ITERATOR", "#ITERATOR", None)
					it.c = matches
					break
			# Generalize wrapper
			if it != None:
				# Left search
				start = wi - 2 * len(it.c)
				count_l = 1
				while start >= 0:
					if _matchPattern(it.c, wrapper.c[start : start + len(it.c)]) == None:
						break
					count_l += 1
					start -= len(it.c)
				# Right search
				start = wi + len(it.c)
				count_r = 0
				while start + len(it.c) <= len(wrapper.c):
					if _matchPattern(it.c, wrapper.c[start : start + len(it.c)]) == None:
						break
					count_r += 1
					start += len(it.c)
				# Update wrapper
				wrapper.c[wi - count_l * len(it.c) : wi + (count_r + 1) * len(it.c)] = [it]
				wi += 1 - count_l * len(it.c)
				continue
						

			## Candidates on the sample
			terminal_tag = sample.c[si-1].val
			# Generate candidates
			candidates = []
			for i in range(si, min(2 * si, len(sample.c))):
				if sample.c[i].val == terminal_tag:
					candidates.append(i)
					if len(candidates) == K:
						break
			# Test candidates
			for sj in candidates:
				matches = [sample.c[i].copy() for i in range(si, sj + 1)]

				found_square = True
				for i in range(len(matches)):
					matches[i] = _match(matches[i], sample.c[si - len(matches) + i])
					if matches[i] == None:
						found_square = False
						break
				if found_square:
					it = Node("ITERATOR", "#ITERATOR", None)
					it.c = matches
					break
			# Generalize wrapper
			if it != None:
				# Left search on the wrapper
				start = wi - len(it.c)
				count_l = 0
				while start >= 0:
					if _matchPattern(it.c, wrapper.c[start : start + len(it.c)]) == None:
						break
					count_l += 1
					start -= len(it.c)
				# Update wrapper
				if count_l > 0:
					# Right search on the sample
					start = wi + len(it.c)
					count_r = 1
					while start + len(it.c) <= len(sample.c):
						if _matchPattern(it.c, sample.c[start : start + len(it.c)]) == None:
							break
						count_r += 1
						start += len(it.c)

					wrapper.c[wi - count_l * len(it.c) : wi] = [it]
					wi += 1 - count_l * len(it.c)
					si += count_r * len(it.c)
					continue

		# test(wrapper, 0)
		# test(sample, 0)

		# Optional discovery
		## Pattern on the wrapper
		wi_match = None
		if si < len(sample.c):
			sc = sample.c[si]
			for i in range(wi + 1, min(wi + 1 + K, len(wrapper.c))):
				wc = wrapper.c[i]
				if wc.t == sc.t and wc.val == sc.val:
					wi_match = i
					break

		## Pattern on the sample
		si_match = None
		if wi < len(wrapper.c):
			wc = wrapper.c[wi]
			for i in range(si + 1, min(si + 1 + K, len(sample.c))):
				sc = sample.c[i]
				if wc.t == sc.t and wc.val == sc.val:
					si_match = i
					break

		# Generalize wrapper
		if wi_match != None and si_match != None:
			print(">>>>>>>> WARNING - Ambiguous optionals")
			if wi_match - wi <= si_match - si:
				si_match = None
			else:
				wi_match = None

		if wi_match != None:
			opt = Node("OPTIONAL", "#OPTIONAL", None)
			opt.c = wrapper.c[wi : wi_match]
			# opt.c = [w.copy() for w in wrapper.c[wi : wi_match]]
			wrapper.c[wi : wi_match] = [opt]
			wi += 1
			# print(f"............{len(opt.c)}")
			continue
		elif si_match != None:
			opt = Node("OPTIONAL", "#OPTIONAL", None)
			opt.c = sample.c[si : si_match]
			# opt.c = [s.copy() for s in sample.c[si : si_match]]
			wrapper.c.insert(wi, opt)
			wi += 1
			si = si_match
			# print(f"............{len(opt.c)}")
			continue
		else:
			# print(">>>>>>>> WARNING - Too many optionals")

			# a = "OOR"
			# b = "OOR"
			# if wi < len(wrapper.c):
			# 	a = wrapper.c[wi].val
			# if si < len(sample.c):
			# 	b = sample.c[si].val
			# print(f"<{a}> vs <{b}>")

			opt1 = Node("OPTIONAL", "#OPTIONAL", None)
			opt2 = Node("OPTIONAL", "#OPTIONAL", None)
			# opt1.c = [w.copy() for w in wrapper.c[wi:]]
			# opt2.c = [s.copy() for s in sample.c[si:]]
			if wi < len(wrapper.c):
				opt1.c = wrapper.c[wi:]
				wrapper.c[wi:] = [opt1]
			if si < len(sample.c):
				opt2.c = sample.c[si:]
				wrapper.c.append(opt2)
			
			wi = len(wrapper.c)
			si = len(sample.c)
			# print(f"............{len(opt1.c)}, {len(opt2.c)}")
			# test(wrapper, 0)
			# print()
			# print()
			continue

		print("========= THIS SHOULD BE UNREACHABLE")

	return wrapper


def match(html_content1, html_content2):
	wrapper = makeTree(html_content1)
	sample = makeTree(html_content2)

	wrapper = _match(wrapper, sample)
	# test(wrapper, 0)
	print(tree2ufre(wrapper))


# if __name__ == "__main__":
# 	page1 = open("../input-extraction/test/page1_complex.html", "r").read()
# 	page2 = open("../input-extraction/test/page2_complex.html", "r").read()
# 	match(page1, page2)

