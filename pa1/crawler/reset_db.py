import psycopg2

conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
conn.autocommit = True

cur = conn.cursor()


# cur.execute("TRUNCATE TABLE crawler.site RESTART IDENTITY CASCADE")
# cur.execute("TRUNCATE TABLE crawler.page RESTART IDENTITY CASCADE")
# cur.execute("TRUNCATE TABLE crawler.link CASCADE")
# cur.execute("TRUNCATE TABLE crawler.image RESTART IDENTITY CASCADE")
# cur.execute("TRUNCATE TABLE crawler.page_data RESTART IDENTITY CASCADE")
# cur.execute("TRUNCATE TABLE crawler.email CASCADE")
# cur.execute("TRUNCATE TABLE crawler.tel CASCADE")

# # cur.execute("TRUNCATE TABLE crawler.page_type CASCADE")
# # cur.execute("TRUNCATE TABLE crawler.data_type CASCADE")
# # cur.execute("INSERT INTO crawler.page_type VALUES ('HTML'), ('BINARY'), ('DUPLICATE'), ('UNAVAILABLE'), ('DISALLOWED'), ('FRONTIER'), ('PROCESSING')")
# # cur.execute("INSERT INTO crawler.data_type VALUES ('PDF'), ('DOC'), ('DOCX'), ('DOCM'), ('PPT'), ('PPTX'), ('PPTM'), ('XLS'), ('XLSX'), ('XLSM'), ('ZIP'), ('RAR'), ('CSV')")


cur.close()

conn.close()
