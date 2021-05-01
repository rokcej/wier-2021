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
    re_category = r'<li class="category\d+">\s*<strong>(.*?)</strong>'
    category = re.compile(re_category).search(html_content)

    # Name
    re_name = r'<li class="item">\s*<div class="item-area">(.|\s)*?<div class="details-area">\s*<h2 class="product-name".*>\s*<a .*>(.*?)</a>'
    matches = re.finditer(re_name, html_content)
    names = []
    for match in matches:
        names.append(match.group(2))

    # Sizes
    re_size = r'<span class="size">(.+?)</span>'
    matches = re.finditer(re_size, html_content)
    size = []
    for match in matches:
        size.append(match.group(1))
    
    re_size0 = r'<div class="items-size-wrapper".+?>\s*<span class="size">(.+?)</span>.*\s*</div>'
    matches = re.finditer(re_size0, html_content)
    size0 = []
    for match in matches:
        size0.append(match.group(1))

    sizes = []
    for i in range(1, len(size0)):
        f = size.index(size0[i], 1)
        sizes.append(size[:f])
        size = size[f:]
    sizes.append(size)

    # Label
    re_label = r'<li class="item">(.|\s)*?</a>\s*(<div class="product-label" style="right: 10px;"><span class="sale-product-icon">(.+?)</span>)?'
    matches = re.finditer(re_label, html_content)
    labels = []
    for match in matches:
        label = match.group(3)
        if label:
            labels.append([label])
        else:
            labels.append([])
    
    # Price
    re_price = r'<li class="item">(.|\s)*?<span class="price"(.*?)?>\s*(.+?)\s*</span>'
    matches = re.finditer(re_price, html_content)
    price = []
    price_id = []
    for match in matches:
        price.append(match.group(3))
        price_id.append(match.group(2))
    
    re_new_price = r'<li class="item">(.|\s)*?<span class="price" id="product-price-\d+">\s*(.+?)\s*</span>'
    matches = re.finditer(re_new_price, html_content)
    new_price = []
    for match in matches:
        new_price.append(match.group(2))


    records = []
    new_price_index = 0
    for i in range(len(names)):
        record = {}
        record["Name"] = names[i]
        record["Sizes"] = sizes[i]

        if price_id[i].strip() == "":
            record["Price"] = price[i]
            record["OldPrice"] = None
        else:
            record["Price"] = new_price[new_price_index]
            record["OldPrice"] = price[i]
            new_price_index += 1
        record["Labels"] = labels[i]
        records.append(record)
    
    page = {}
    page["Category"] = category.group(1)
    page["Records"] = records

    print("Manazara output object:")
    print(json.dumps(page, indent=4, ensure_ascii=False))
    print()


