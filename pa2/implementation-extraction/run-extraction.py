import sys

import xpath_extraction

if __name__ == "__main__":
	# Get parameter
	if len(sys.argv) < 2:
		print("Error: Please specify a parameter A, B or C")
		sys.exit(1)
	parameter = sys.argv[1]

	# Get html
	html_overstock = [
		open("../input-extraction/overstock.com/jewelry01.html", "r").read(),
		# open("../input-extraction/overstock.com/jewelry02.html", "r").read()
	]
	html_rtvslo = [
		# open("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r", encoding="utf8").read(),
		# open("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html", "r", encoding="utf8").read()
	]

	# Run selected algorithm
	if parameter == 'A': # Regex
		# TODO
		pass
	elif parameter == 'B': # XPath
		for html in html_overstock:
			xpath_extraction.processOverstock(html)
		for html in html_rtvslo:
			xpath_extraction.processRtvslo(html)
	elif parameter == 'C': # RoadRunner
		# TODO
		pass
	else:
		print(f"Error: Invalid parameter {parameter}")
		sys.exit(1)

