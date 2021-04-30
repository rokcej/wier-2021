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
# Extract data from nepremicnine.py
def processManazara(html_content):
	# Import libraries

import re
import json
from unidecode import unidecode

# We rather use the locally-cached file as it may have changed online.
pageContent = open('Urbano-D 149 - Enodružinske hiše _ Montažne hiše NEPREMICNINE.net.html', 'r').read()
#print(pageContent)

# # TITLE
regex = r"<div id=\"opis\">[\s\S]*?<!--<h1>(.*?)<\/h1>"
Title = re.compile(regex)
match = Title.search(pageContent)
Title = str(match.group(1))
# print(Title)

# # SubTitle
regex = r"<div class=\"kratek\">(.*?)<\/div>"
SubTitle = re.compile(regex)
match = SubTitle.search(pageContent)
SubTitle = str(match.group(1))
# print(SubTitle)

# # SPECIFIC INFORMATION

regex = r"(<div (class=\"dsc\">)(<strong>)?(.*?)(<\/strong>)?<\/div>(<br>)?)"
i=0
Specific={}
matches = re.finditer(regex, pageContent)
for match in matches:
    Specific[i] = unidecode(str(match.group(4))).replace("</strong>", "")
    # print(Specific[i])
    i=i+1
    
# # GENERAL DESCRIPTION
regex = r"(<div class=\"opis\">(.*?)[\s\S]*?(?=<\/div>))"
General = re.compile(regex)
match = General.search(pageContent)
General = str(match.group(2)+match.group(1)).replace("<div class=\"opis\">", "")
General=General.replace("<div>", "")
General=General.replace("<br>", "")
General=General.replace("<p>","")
General=General.replace("</p>","")
General=General.replace("</strong>","")
General=General.replace("<strong>","")
General=General.replace("<ul>","")
General=General.replace("<li>","")
General=General.replace("</li>","")
General=General.replace("</ul>","")
# print(General)

# # SELLER
regex = r"(<div class=\"prodajalec\">(<h2>)?(.*?)(<\/h2>)?<\/div>)"
Seller = re.compile(regex)
match = Seller.search(pageContent)
Seller = str(match.group(3))
# print(Seller)

# # LOCATION
regex = r"(((<div class=\"naslov\">([\s\S]*?))<\/div>)[\s\S]*?(?=<div class=\"tel\"><\/div>))"
Location = re.compile(regex)
match = Location.search(pageContent)
Location = str(match.group(3).replace("<br>", " "))
Location= str(Location.replace("<div class=\"naslov\">", ""))
# print(Location)

dataObject = {
        "Title" : unidecode(Title),
        "SubTitle:" : unidecode(SubTitle),
        "Specific Information": Specific,
        "General Information": unidecode(General).replace("\n", "").replace("&nbsp;", " ").replace("\t", " "),
        "Seller": unidecode(Seller),
        "Location": unidecode(Location).replace("\n","").strip()
    }
print("Output object:\n%s" % json.dumps(dataObject, indent = 4))

pass
