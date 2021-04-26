import psycopg2
from datetime import datetime
import matplotlib.pyplot as plt

conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
conn.autocommit = True

cur = conn.cursor()



# # Images

# img_type = ["JPG", "PNG", "GIF", "SVG", "Other"] #"BMP", "TIFF" ]
# img_count = [26940, 104241, 77716, 95040, 109] #22, 87] 

# plt.rcParams.update({'font.size': 14})
# fig = plt.figure()
# ax = fig.add_axes([0,0,1,1])
# ax.axis('equal')
# ax.pie(img_count, explode=(0.02, 0.02, 0.02, 0.02, 0.02), labels = img_type, autopct='%1.2f%%')
# plt.show()

# plt.show()




# Files

file_type = ["PDF", "PPT*", "DOC*", "XLS*", "ZIP/RAR", "CSV"]
file_count = [26481, 161, 7425, 2332, 5899, 478] 
file_color = colors=('tab:blue','tab:purple','tab:orange','tab:green','tab:red','tab:brown')

plt.rcParams.update({'font.size': 14})

fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
ax.pie(file_count, labels=file_type, explode=(0.02, 0.02, 0.02, 0.02, 0.02, 0.02), autopct='%1.2f%%', colors=file_color)
#plt.legend()
plt.show()




# # Pages with time
# cur.execute("SELECT accessed_time FROM crawler.page " +
# 	"WHERE page_type_code = 'HTML' OR page_type_code = 'BINARY' OR page_type_code = 'DUPLICATE' " +
# 	"ORDER BY accessed_time ASC LIMIT 1")
# time_start = cur.fetchone()[0]
# cur.execute("SELECT accessed_time FROM crawler.page " +
# 	"WHERE page_type_code = 'HTML' OR page_type_code = 'BINARY' OR page_type_code = 'DUPLICATE' " +
# 	"ORDER BY accessed_time DESC LIMIT 1")
# time_end = cur.fetchone()[0]

# print(time_start)
# print(time_end)

# duration = (time_end - time_start).total_seconds()
# N = 1000
# dt = duration / N
# t = 0


# data = [0] * N
# data_html = [0] * N
# data_bin = [0] * N
# data_dup = [0] * N

# cur.execute("SELECT accessed_time, page_type_code FROM crawler.page " +
# 	"WHERE page_type_code = 'HTML' OR page_type_code = 'BINARY' OR page_type_code = 'DUPLICATE' " +
# 	"ORDER BY accessed_time ASC")
# res_list = cur.fetchall()
# for res in res_list:
# 	elapsed = (res[0] - time_start).total_seconds()
# 	index = int((elapsed / duration) * (N - 1))
# 	if res[1] == "HTML":
# 		data_html[index] += 1
# 	elif res[1] == "BINARy":
# 		data_bin[index] += 1
# 	elif res[1] == "DUPLICATE":
# 		data_dup[index] += 1

# 	data[index] += 1

# for i in range(1, len(data)):
# 	data_html[i] += data_html[i-1]
# 	data_bin[i] += data_bin[i-1]
# 	data_dup[i] += data_dup[i-1]
# 	data[i] += data[i-1]

# duration_hours = duration / 3600.0
# data_y = [(i/(N-1)) * duration_hours for i in range(len(data))]

# print(f"Runtime: {duration_hours} hours")

# plt.grid(alpha=0.2)
# plt.plot(data_y, data_bin, label="Binary", color='tab:green')
# plt.plot(data_y, data_dup, label="Duplicate", color='tab:red')
# plt.plot(data_y, data_html, color='tab:orange', label="HTML")
# plt.plot(data_y, data, label="Total", color='tab:blue', linewidth=2)
# plt.ylabel("Number of pages")
# plt.xlabel("Hours")
# plt.legend()
# plt.show()









# # Links

# edges = {}
# nodes = set()
# max_count = 0

# cur.execute("SELECT pg1.site_id, pg2.site_id " +
# 	"FROM crawler.link AS lnk " +
# 	"INNER JOIN crawler.page AS pg1 ON lnk.from_page = pg1.id " +
# 	"INNER JOIN crawler.page AS pg2 ON lnk.to_page = pg2.id " + 
# 	"WHERE (pg1.page_type_code = 'HTML' OR pg1.page_type_code = 'BINARY' OR pg1.page_type_code = 'DUPLICATE') " +
# 		"AND (pg2.page_type_code = 'HTML' OR pg2.page_type_code = 'BINARY' OR pg2.page_type_code = 'DUPLICATE') ")
# res_list = cur.fetchall()
# for res in res_list:
# 	key = (res[0], res[1])
# 	if key in edges:
# 		edges[key] += 1
# 	else:
# 		edges[key] = 1

# 	if edges[key] > max_count:
# 		max_count = edges[key]
	
# 	nodes.add(res[0])
# 	nodes.add(res[1])


# f = open("edge.csv", "w")
# f.write("Source\tTarget\tWeight\n")

# for key in edges:
# 	f.write(f"{key[0]}\t{key[1]}\t{edges[key]}\n")

# f.close()

# f = open("node.csv", "w")
# f.write("ID\tLabel\n")

# cur.execute("SELECT id, domain FROM crawler.site")
# res_list = cur.fetchall()
# for res in res_list:
# 	if res[0] in nodes:
# 		f.write(f"{res[0]}\t{res[1]}\n")

# f.close()




# # Statistics
# cur.execute("SELECT COUNT(*) FROM crawler.site")
# number_of_sites=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page")
# number_of_pages=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.image")
# number_of_img=cur.fetchone()[0]
# avg_img_perpage=number_of_img/number_of_pages
# avg_pages_persite=number_of_pages/number_of_sites
# cur.execute("SELECT COUNT(*) FROM crawler.page WHERE code = 'DUPLICATE'")
# number_of_duplicates=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page WHERE code = 'UNAVAILABLE'")
# number_of_unavailable=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page WHERE code = 'BINARY'")
# number_of_binary=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page_data WHERE code = 'PDF'")
# number_of_PDF=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page_data WHERE code = 'DOC'")
# number_of_DOC=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page_data WHERE code = 'DOCX'")
# number_of_DOCX=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page_data WHERE code = 'PPT'")
# number_of_PPT=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page_data WHERE code = 'PPTX'")
# number_of_PPTX=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page WHERE http_status_code = 404")
# number_of_Notfoundstatcode=cur.fetchone()[0]
# cur.execute("SELECT COUNT(*) FROM crawler.page WHERE http_status_code = 200")
# number_of_OKstatcode=cur.fetchone()[0]

# f = open("binary.csv", "w")
# f.write("TYPE,NUMBER\n")
# f.write(f"PDF,{number_of_PDF}\n")
# f.write(f"DOC,{number_of_DOC}\n")
# f.write(f"DOCX,{number_of_DOCX}\n")
# f.write(f"PPT,{number_of_PPT}\n")
# f.write(f"PPTX,{number_of_PPTX}\n")
# f.close()


cur.close()
conn.close()
