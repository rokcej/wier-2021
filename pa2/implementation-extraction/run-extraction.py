import sys

import regex_extraction
import xpath_extraction
import roadrunner_extraction

if __name__ == "__main__":
	# Get parameter
	if len(sys.argv) < 2:
		print("[ERROR] Please specify a parameter A, B or C")
		sys.exit(1)
	parameter = sys.argv[1]

	# Get html
	html_overstock = [
		open("../input-extraction/overstock.com/jewelry01.html", "r").read(),
		open("../input-extraction/overstock.com/jewelry02.html", "r").read()
	]
	html_rtvslo = [
		open("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r", encoding="utf8").read(),
		open("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html", "r", encoding="utf8").read()
	]
	html_manazara = [
		open("../input-extraction/manazara.si/Jakne - Bunde - Plašči - Kolekcija 2020 Manzara.html", "r", encoding="utf8").read(),
		open("../input-extraction/manazara.si/Puloverji - Naroči Online. Nova Kolekcija 2020 Manzara.html", "r", encoding="utf8").read()
	]

	# Run selected algorithm
	if parameter == 'A': # Regex
		regex_extraction.processOverstock(html_overstock[0])
		regex_extraction.processOverstock(html_overstock[1])

		regex_extraction.processRtvslo(html_rtvslo[0])
		regex_extraction.processRtvslo(html_rtvslo[1])

		regex_extraction.processManazara(html_manazara[0])
		regex_extraction.processManazara(html_manazara[1])
	elif parameter == 'B': # XPath
		xpath_extraction.processOverstock(html_overstock[0])
		xpath_extraction.processOverstock(html_overstock[1])

		xpath_extraction.processRtvslo(html_rtvslo[0])
		xpath_extraction.processRtvslo(html_rtvslo[1])
		
		xpath_extraction.processManazara(html_manazara[0])
		xpath_extraction.processManazara(html_manazara[1])
	elif parameter == 'C': # RoadRunner
		print("[Overstock.com wrapper]\n")
		roadrunner_extraction.match(html_overstock[0], html_overstock[1])
		print("[Rtvslo.si wrapper]\n")
		roadrunner_extraction.match(html_rtvslo[0], html_rtvslo[1])
		print("[Namazara.si wrapper]\n")
		roadrunner_extraction.match(html_manazara[0], html_manazara[1])
	else:
		print(f"[ERROR] Invalid parameter {parameter}")
		sys.exit(1)

