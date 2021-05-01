import re
import json
from unidecode import unidecode
from bs4 import BeautifulSoup
import string

# Extract data from overstock.com
def processOverstock(html_content):
	# Import libraries


    # We rather use the locally-cached file as it may have changed online.
    pageContent = html_content
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

    records = []
    for j in range(len(LastPrice)):
        dataObject = {
            "Title" : Title[j],
            "ListPrice": LastPrice[j],
            "Price": Price[j],
            "Saving": Saving[j],
            "SavingPercent": SavingPercent[j],
            "Content" : Description[j]
        }
        records.append(dataObject)
    print("Overstock output object:\n%s\n" % json.dumps(records, indent = 4))
        


# Extract data from rtvslo.si
def processRtvslo(html_content):
	# Import libraries




    # We rather use the locally-cached file as it may have changed online.
    pageContent = html_content
    pageContent = BeautifulSoup(pageContent, 'html.parser')

    # # TITLE
    regex = r"<h1>(.*)<\/h1>"
    Title = re.compile(regex)
    match = Title.search(str(pageContent))
    Title=str(match.group(1))
    #print(Title)


    # # AUTHOR AND PUBLISHED TIME
    regex = r"<div class=\"author-timestamp\">\s*\n?[<strong>]+(.*)<\/strong>\|(.*)"
    Author = re.compile(regex)
    match = Author.search(str(pageContent))
    #print("Author:", match.group(1))
    Author=str(match.group(1))
    #print("PublishedTime",match.group(2))
    PublishedTime=match.group(2)


    # # SUBTITLE
    regex = r"<div class=\"subtitle\">(.*)<\/div>"
    Subtitle = re.compile(regex)
    match = Subtitle.search(str(pageContent))
    #print("Subtitle:", match.group(1))
    Subtitle=str(match.group(1))
    # # LEAD
    regex = r"<p class=\"lead\">(.*)<\/p>"
    Lead = re.compile(regex)
    match = Lead.search(str(pageContent))
    # print("Lead:", match.group(1))
    Lead=match.group(1)

    #DESCRIPTION
    i=1
    Description={}
    regex=r"(<div style=\"position:absolute\; left: -1000px\; top: -1000px\;\"><img (.*?)<p>)*?(<p class=\"Body\">(.*?)<iframe (.*?)<\/p>)?<p>(.*?)(<\/p>)"
    DEscription = re.compile(regex)
    match = DEscription.search(str(pageContent))
    if(str(match.group(4))==None):
        pass
    else:
        Description[i]=match.group(4)
        i=i+1
    matches = re.finditer(regex, str(pageContent))
    for match in matches:
        Description[i] = str(match.group(6))      
        i=i+1
    Dummy=""
    j=1
    while(j<len(Description)): 
        if(Description[j] is None):
            j=j+1
            continue
        Dummy=str(Dummy)+Description[j]
        j=j+1
    Titl=str(Dummy).split('mesec')
    Description=str((Titl[0]+"mesec").replace("<p>","").replace("</p>","").replace("<strong>","").replace("</strong>","").replace("<p class=\"Body\">","").replace("<br>","").replace("<br/>","").replace("<sub>","").replace("</sub>",""))
    # print(Description)
    dataObject = {     
        "Author" : Author,
        "PublishedTime": ' '.join(PublishedTime.split()),
        "Title": Title,
        "SubTitle": Subtitle,
        "Lead": unidecode(Lead),
        "Content" : unidecode(Description)
    }
    print("Rtvslo output object:\n%s\n" % json.dumps(dataObject, indent = 4))



# Extract data from manazara.si
def processManazara(html_content):
    # Does not work
    return

	# # Import libraries
    # pageContent = html_content
    # #print(pageContent)

    # # CATEGORY
    # regex = r"<li class=\"home\">[\s\S]*?<a (.*?)>(.*?)<\/a>[\s\S]*?<strong>(.*?)<\/strong>"
    # Category = re.compile(regex)
    # match = Category.search(pageContent)
    # CATEGORY=match.group(2)+ "/"+ match.group(3)
    # # print("Category:", match.group(2)+"/"+match.group(3))

    # #NOT GOOD
    # # i=0
    # # Title={}
    # # regex = r"<h2 class=\"product-name\" (.*) title(.*?)>(.*?)<\/a>[\s\S]*?[\s\S]*?(<p class=\"old-price\">[\s]+?<span class=\"price-label\">(.*?)<\/span>[\s]*<span class=\"price\" (.*?)>[\s]+(.*?)<\/span>)+?[\s\S]*?(<p class=\"special-price\">[\s\S]+?<span class=\"price\" (.*?)>[\s]+(.*?)<\/span>)+?[\s\S]*?(<p class=\"old-price regular-price-old-price-container\"><\/p>[\s]+<span class=\"regular-price\"(.*?)>[\s\S]+?<span class=\"price\">(.*?)<\/span>)+?<div class=\"actions\">"
    # # matches = re.finditer(regex, pageContent)
    # # for match in matches:
    # #     Title[i]=str(match.group(10)) + match.group(13)
    # #     print(Title[i])
    # #     i=i+1


    # i=0
    # PRODUCTNAME={}
    # #  PRODUCT NAME
    # regex = r"<h2 class=\"product-name\" (.*) title(.*?)>(.*?)<\/a>"
    # matches = re.finditer(regex, pageContent)
    # for match in matches:
    #     PRODUCTNAME[i]=str(match.group(3))
    #     i=i+1

    # # SIZES
    # SIZES={}
    # i=0
    # regex = r"(<span class=\"size\">(.*)<\/span>)+?"
    # matches = re.finditer(regex, pageContent)
    # for match in matches:
    #     SIZES[i] = str(match.group(2)).replace("<span class=\"size\">"," ").replace("</span>", " ")
    #     # print(SIZES[i])
    #     i=i+1


    # # GOOD BUT NOT RELEVANT
    # # i=0
    # # OLD={}
    # # Auth={}
    # # #  OLD PRICE
    # # regex = r"<span class=\"price\" id=\"old-price-(.*?)>[\s](.*?)<\/span>[\s\S]+?<div class=\"actions\">"
    # # matches = re.finditer(regex, pageContent)
    # # for match in matches:
    # #     OLD[i]=str(match.group(1))
    # #     OLD[i]=int(OLD[i][0:(len(OLD[i])-1)])
    # #     Auth[i]=str(match.group(2))
    # #     print(Auth[i],OLD[i])
    # #     i=i+1
    # # GOOD BUT NOT RELEVANT
    # # i=0
    # # Current={}
    # # Price={}
    # # #  CURRENT PRICE
    # # regex = r"<span class=\"price\" id=\"product-price-(.*?)>[\s](.*?)<\/span>[\s\S]+?<div class=\"actions\">"
    # # matches = re.finditer(regex, pageContent)
    # # for match in matches:
    # #     Current[i]=str(match.group(1))
    # #     Current[i]=int(Title1[i][0:(len(Title1[i])-1)])
    # #     Price[i]=str(match.group(2))
    # #     print(Price[i],Title1[i])
    # #     i=i+1

    # for j in range(min(len(SIZES), len(PRODUCTNAME))):
    #     dataObject = {
    #         "Category" : CATEGORY,        
    #         "Product Name:" : (PRODUCTNAME[j]),
    #         "Sizes": SIZES[j],

    #     }
    #     print("Output object:\n%s" % json.dumps(dataObject, indent = 4))
