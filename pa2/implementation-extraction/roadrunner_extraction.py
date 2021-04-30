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


def makeTree(html_content):
	soup = BeautifulSoup(html_content, 'html.parser')

	bs_root = soup.body
	root = _makeTree(bs_root)

	return root


def test(node, depth):
	print(2 * depth * " " + str(node.val))
	for c in node.c:
		test(c, depth + 1)


def _matchPattern(wrapper_nodes, sample_nodes):
	matches = [w.copy() for w in wrapper_nodes]
	for i in range(len(matches)):
		matches[i] = _match(matches[i], sample_nodes[i])
		if matches[i] == None:
			return None
	for i in range(len(matches)):
		wrapper_nodes[i] = matches[i]
	return wrapper_nodes


def _match(wrapper, sample):
	K = 4 # Maximum number of candidate squares

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

	# ufre = Node(wrapper.t, wrapper.val, wrapper.data)

	wi = 0
	si = 0

	while wi < len(wrapper.c) or si < len(sample.c):
		# wc = wrapper.c[wi]
		# sc = sample.c[si]

		# if (si < len(sample.c)):
		# 	print(f"<{wc.val}> vs <{sample.c[si].val}>")
		# else:
		# 	print(f"<{wc.val}> vs <MISSING>")

		if False:
			pass
		else:
			if wi < len(wrapper.c) and si < len(sample.c) and _match(wrapper.c[wi], sample.c[si]) != None: # Matched
				wi += 1
				si += 1
			else: # Mismatched
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
					wrapper.c[wi : wi_match] = [opt]
					wi += 1
					continue
				elif si_match != None:
					opt = Node("OPTIONAL", "#OPTIONAL", None)
					opt.c = sample.c[si : si_match]
					wrapper.c.insert(wi, opt)
					wi += 1
					si = si_match
					continue
				else:
					print(">>>>>>>> WARNING - Too many optionals")
					opt1 = Node("OPTIONAL", "#OPTIONAL", None)
					opt2 = Node("OPTIONAL", "#OPTIONAL", None)
					opt1.c = wrapper.c[wi:]
					opt2.c = sample.c[si:]
					wrapper.c[wi:] = [opt1]
					wrapper.append(opt2)
					
					wi = len(wrapper.c)
					si = len(sample.c)
					continue

	return wrapper


def match(html_content1, html_content2):
	wrapper = makeTree(html_content1)
	sample = makeTree(html_content2)

	wrapper = _match(wrapper, sample)
	test(wrapper, 0)


if __name__ == "__main__":
	page1 = open("../input-extraction/test/page1.html", "r").read()
	page2 = open("../input-extraction/test/page2.html", "r").read()
	match(page1, page2)

