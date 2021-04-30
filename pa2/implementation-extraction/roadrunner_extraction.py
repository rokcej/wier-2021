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
			if wi < len(wrapper.c) and si < len(sample.c) and _match(wrapper.c[wi], sample.c[si]) != None:
				wi += 1
				si += 1
			else: # Mismatched
				# Iterator
				if wi > 0 and si > 0: # and wrapper.c[wi-1].t == sample.c[si-1].t and wrapper.c[wi-1].val == sample.c[si-1].val:q
					iter = None

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
							iter = Node("ITERATOR", "#ITERATOR", None)
							iter.c = matches
							break
					# Generalize wrapper
					if iter != None:
						# Left search
						start = wi - 2 * len(iter.c)
						count_l = 1
						while start >= 0:
							if _matchPattern(iter.c, wrapper.c[start : start + len(iter.c)]) == None:
								break
							count_l += 1
							start -= len(iter.c)
						# Right search
						start = wi + len(iter.c)
						count_r = 0
						while start + len(iter.c) <= len(wrapper.c):
							if _matchPattern(iter.c, wrapper.c[start : start + len(iter.c)]) == None:
								break
							count_r += 1
							start += len(iter.c)
						# Update wrapper
						wrapper.c[wi - count_l * len(iter.c) : wi + (count_r + 1) * len(iter.c)] = [iter]
						wi += 1 - count_l * len(iter.c)
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
							iter = Node("ITERATOR", "#ITERATOR", None)
							iter.c = matches
							break
					# Generalize wrapper
					if iter != None:
						# Left search on the wrapper
						start = wi - len(iter.c)
						count_l = 0
						while start >= 0:
							if _matchPattern(iter.c, wrapper.c[start : start + len(iter.c)]) == None:
								break
							count_l += 1
							start -= len(iter.c)
						# Update wrapper
						if count_l > 0:
							# Right search on the sample
							start = wi + len(iter.c)
							count_r = 1
							while start + len(iter.c) <= len(sample.c):
								if _matchPattern(iter.c, sample.c[start : start + len(iter.c)]) == None:
									break
								count_r += 1
								start += len(iter.c)

							wrapper.c[wi - count_l * len(iter.c) : wi] = [iter]
							wi += 1 - count_l * len(iter.c)
							si += count_r * len(iter.c)
							continue

				# Optional
				# TODO

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

