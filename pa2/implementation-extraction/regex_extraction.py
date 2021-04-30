# Extract data from overstock.com
def processOverstock(html_content):
	# Import libraries

import re
import json


# We rather use the locally-cached file as it may have changed online.
pageContent = open('jewelry02.html', 'r').read()
Description={}
LastPrice={}
Price={}
Saving={}
SavingPercent={}
Title={}
i=0

#TITLE
i=0
regex = r"<a href=(\")http:(\/\/)www.overstock.com(\/)cgi-bin(\/)d2.cgi(\?)PAGE=PROFRAME(\&)amp;PROD_ID=(\d{5,7})(\")><b>(.*)</b>"
matches = re.finditer(regex, pageContent)
for match in matches:
    Title[i] = match.group(9)
    i=i+1

#DESCRIPTION
i=0
regex=r"(?:<td valign=\"top\"><span class=\"normal\">)((.*?)[\s\S]*?)<br>(.*?)\"><span class=\"tiny\"><b>(.*)<\/b>"
matches = re.finditer(regex, pageContent)
for match in matches:
    Description[i] = str(match.group(1)+match.group(4)).replace("\n","")
    i=i+1

#LAST PRICE
i=0
regex=r"<tbody><tr><td align=\"right\" nowrap=\"nowrap\"><b>(.*)<\/b><\/td><td align=\"left\" nowrap=\"nowrap\"><s>(\$(\d{1,5})(\,)?(\d{1,5})?\.(\d{1,5}))<\/s><\/td><\/tr>"
matches = re.finditer(regex, pageContent)
for match in matches:
    LastPrice[i] = match.group(2)
    i=i+1


#REGULAR PRICE
i=0
regex=r"<tr><td align=\"right\" nowrap=\"nowrap\"><b>Price:<\/b><\/td><td align=\"left\" nowrap=\"nowrap\"><span class=\"bigred\"><b>(\$(\d{1,5})(\,)?(\d{1,5})?\.(\d{1,5}))<\/b><\/span><\/td><\/tr>"
matches = re.finditer(regex, pageContent)
for match in matches:
    Price[i] = match.group(1)
    i=i+1

#SAVED
i=0
regex=r"<tr><td align=\"right\" nowrap=\"nowrap\"><b>You Save:<\/b><\/td><td align=\"left\" nowrap=\"nowrap\"><span class=\"littleorange\">(\$(\d{1,5})(\,)?(\d{1,5})?\.(\d{1,5})) (\()[0-9][0-9](\%)(\))<\/span><\/td><\/tr>"
matches = re.finditer(regex, pageContent)
for match in matches:
    Saving[i] = match.group(1)
    i=i+1

#SAVED IN PERCENT
i=0
regex=r"<tr><td align=\"right\" nowrap=\"nowrap\"><b>You Save:<\/b><\/td><td align=\"left\" nowrap=\"nowrap\"><span class=\"littleorange\">(\$(\d{1,5})(\,)?(\d{1,5})?\.(\d{1,5})) ((\()([0-9][0-9](\%))(\)))<\/span><\/td><\/tr>"
matches = re.finditer(regex, pageContent)
for match in matches:
    SavingPercent[i] = match.group(8)
    i=i+1


for j in range(len(LastPrice)):
    dataObject = {
        "Description" : Description[j],
        "Title:" : Title[j],
        "LastPrice": LastPrice[j],
        "Price": Price[j],
        "Saving": Saving[j],
        "SavingPercent": SavingPercent[j]
    }
    print("Output object:\n%s" % json.dumps(dataObject, indent = 4))
	
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
