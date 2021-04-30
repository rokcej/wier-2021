from lxml import html
import json
import re


# Extract data from overstock.com
def processOverstock(html_content):
	print("############################")
	print("# Processing overstock.com #")
	print("############################")

	tree = html.fromstring(html_content)
	
	# 15 and 8 records
	num_records = len(tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]"))

	title = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/a/b/text()")
	list_price = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()")
	price = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()")
	saving = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()")
	content = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[2]/span/text()")

	if not num_records == len(title) == len(list_price) == len(price) == len(saving) == len(content):
		print("[WARNING] Number of records does not match number of item occurrences")

	records = []
	for i in range(num_records):
		record = {}
		record["Title"] = title[i]
		record["ListPrice"] = list_price[i]
		record["Price"] = price[i]
		saving_items = saving[i].split(" ")
		record["Saving"] = saving_items[0]
		record["SavingPercent"] = saving_items[1][1:-1]
		record["Content"] = content[i].replace("\n", " ")
		records.append(record)

	print(json.dumps(records, indent=4))
	print()


# Extract data from rtvslo.si
def processRtvslo(html_content):
	print("########################")
	print("# Processing rtvslo.si #")
	print("########################")

	tree = html.fromstring(html_content)

	# author = tree.xpath("/html/body/div/div[3]/div/div[1]/div[1]/div/text()")
	author = tree.xpath("//div[@class='article-meta']/div[@class='author']/div[@class='author-name']/text()")[0]

	# published_time = tree.xpath("/html/body/div/div[3]/div/div[1]/div[2]/text()")
	published_time = tree.xpath("//div[@class='article-meta']/div[@class='publish-meta']/text()")[0]
	published_time = published_time.strip()

	# title = tree.xpath("/html/body/div/div[3]/div/header/h1/text()")
	title = tree.xpath("//header[@class='article-header']/h1/text()")[0]

	# subtitle = tree.xpath("/html/body/div/div[3]/div/header/div[2]/text()")
	subtitle = tree.xpath("//header[@class='article-header']/div[@class='subtitle']/text()")[0]

	# lead = tree.xpath("/html/body/div/div[3]/div/header/p/text()")
	lead = tree.xpath("//header[@class='article-header']/p[@class='lead']/text()")[0]

	# content = tree.xpath("/html/body/div/div[3]/div/div[2]/article/p/text() | /html/body/div/div[3]/div/div[2]/article/p/strong/text()")
	content_lines = tree.xpath("//div[@class='article-body']/article[@class='article']/p/text() | //div[@class='article-body']/article[@class='article']/p/strong/text()")
	content = "\n".join(content_lines)

	record = {}
	record["Author"] = author
	record["PublishedTime"] = published_time
	record["Title"] = title
	record["SubTitle"] = subtitle
	record["Lead"] = lead
	record["Content"] = content

	print(json.dumps(record, indent=4))
	print()


# Extract data from manazara.si
def processManazara(html_content):
	print("##########################")
	print("# Processing manazara.si #")
	print("##########################")

	tree = html.fromstring(html_content)

	category = tree.xpath("/html/body/div/div/div[4]/div[2]/div/div/div/ul/li/strong/text()")[0]

	# Common denominator for records
	record_xpath = "//div[@class='category-products']/ul[contains(@class, 'columns4')]/li[contains(@class, 'item')]"
	num_records = len(tree.xpath(record_xpath))

	page = {}
	page["Category"] = category
	records = []
	for i in range(num_records):
		# Common denominator for data items
		item_xpath = record_xpath + f"[{i+1}]" + "/div[@class='item-area']/div[@class='details-area']"

		record = {}
		record["Name"] = tree.xpath(item_xpath + "/h2[@class='product-name']/a/text()")[0]
		record["Sizes"] = tree.xpath(item_xpath + "/div[@class='items-size-wrapper']/span[@class='size']/text()")

		price = tree.xpath(item_xpath + "/div[@class='price-box']/span[@class='regular-price']/span[@class='price']/text() | " +
			item_xpath + "/div[@class='price-box']/p[@class='special-price']/span[@class='price']/text()")[0].strip()
		old_price = tree.xpath(item_xpath + "/div[@class='price-box']/p[@class='old-price']/span[@class='price']/text()")
		if old_price:
			old_price = old_price[0].strip()
		else:
			old_price = None
		
		# old_price = None
		# if len(price) > 0: # Regular price
		# 	price = price[0].strip()
		# else: # Special price & old price
		# 	price = tree.xpath(item_xpath + "/div[@class='price-box']/p[@class='special-price']/span[@class='price']/text()")[0].strip()
		# 	old_price = tree.xpath(item_xpath + "/div[@class='price-box']/p[@class='old-price']/span[@class='price']/text()")[0].strip()
		record["Price"] = price
		record["OldPrice"] = old_price

		record["Labels"] = tree.xpath(record_xpath + f"[{i+1}]" + "/div[@class='item-area']/div[@class='product-image-area']/div[@class='product-label']/span/text()")

		records.append(record)
	page["Records"] = records

	print(json.dumps(page, indent=4))
	print()

