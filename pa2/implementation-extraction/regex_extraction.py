# Extract data from overstock.com
def processOverstock(html_content):
	
	pass


# Extract data from rtvslo.si
def processRtvslo(html_content):
	# TODO: Process page using regex
	pass


# Extract data from manazara.si
def processManazara(html_content):
	# Import libraries

import re
import json
from unidecode import unidecode
pageContent = open('Jakne.html' ,encoding="utf8").read()
#print(pageContent)

# CATEGORY
regex = r"<li class=\"home\">[\s\S]*?<a (.*?)>(.*?)<\/a>[\s\S]*?<strong>(.*?)<\/strong>"
Category = re.compile(regex)
match = Category.search(pageContent)
CATEGORY=match.group(2)+ "/"+ match.group(3)
# print("Category:", match.group(2)+"/"+match.group(3))

#NOT GOOD
# i=0
# Title={}
# regex = r"<h2 class=\"product-name\" (.*) title(.*?)>(.*?)<\/a>[\s\S]*?[\s\S]*?(<p class=\"old-price\">[\s]+?<span class=\"price-label\">(.*?)<\/span>[\s]*<span class=\"price\" (.*?)>[\s]+(.*?)<\/span>)+?[\s\S]*?(<p class=\"special-price\">[\s\S]+?<span class=\"price\" (.*?)>[\s]+(.*?)<\/span>)+?[\s\S]*?(<p class=\"old-price regular-price-old-price-container\"><\/p>[\s]+<span class=\"regular-price\"(.*?)>[\s\S]+?<span class=\"price\">(.*?)<\/span>)+?<div class=\"actions\">"
# matches = re.finditer(regex, pageContent)
# for match in matches:
#     Title[i]=str(match.group(10)) + match.group(13)
#     print(Title[i])
#     i=i+1


i=0
PRODUCTNAME={}
#  PRODUCT NAME
regex = r"<h2 class=\"product-name\" (.*) title(.*?)>(.*?)<\/a>"
matches = re.finditer(regex, pageContent)
for match in matches:
    PRODUCTNAME[i]=str(match.group(3))
    i=i+1

# SIZES
SIZES={}
i=0
regex = r"(<span class=\"size\">(.*)<\/span>)+?"
matches = re.finditer(regex, pageContent)
for match in matches:
    SIZES[i] = str(match.group(2)).replace("<span class=\"size\">"," ").replace("</span>", " ")
    # print(SIZES[i])
    i=i+1


# GOOD BUT NOT RELEVANT
# i=0
# OLD={}
# Auth={}
# #  OLD PRICE
# regex = r"<span class=\"price\" id=\"old-price-(.*?)>[\s](.*?)<\/span>[\s\S]+?<div class=\"actions\">"
# matches = re.finditer(regex, pageContent)
# for match in matches:
#     OLD[i]=str(match.group(1))
#     OLD[i]=int(OLD[i][0:(len(OLD[i])-1)])
#     Auth[i]=str(match.group(2))
#     print(Auth[i],OLD[i])
#     i=i+1
# GOOD BUT NOT RELEVANT
# i=0
# Current={}
# Price={}
# #  CURRENT PRICE
# regex = r"<span class=\"price\" id=\"product-price-(.*?)>[\s](.*?)<\/span>[\s\S]+?<div class=\"actions\">"
# matches = re.finditer(regex, pageContent)
# for match in matches:
#     Current[i]=str(match.group(1))
#     Current[i]=int(Title1[i][0:(len(Title1[i])-1)])
#     Price[i]=str(match.group(2))
#     print(Price[i],Title1[i])
#     i=i+1
for j in range(len(SIZES)):
    dataObject = {
        "Category" : CATEGORY,        
        "Product Name:" : (PRODUCTNAME[j]),
        "Sizes": SIZES[j],

    }
    print("Output object:\n%s" % json.dumps(dataObject, indent = 4))




	pass

