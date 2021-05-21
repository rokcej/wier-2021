import sqlite3

##################################
# Get stats from SQLite database #
##################################

# Connect to DB
conn = sqlite3.connect("inverted-index.db")
cur = conn.cursor()

# Get stats
cur.execute("SELECT COUNT(word) FROM IndexWord")
row = cur.fetchone()
print(f"Indexed words: {row[0]}")

cur.execute("SELECT word, SUM(frequency) as freqSum FROM Posting GROUP BY word ORDER BY freqSum DESC")
print("Words with highest frequencies:")
for _ in range(3):
	row = cur.fetchone()
	print(f"\t{row[0]}, {row[1]}")

cur.execute("SELECT documentName, SUM(frequency) as freqSum FROM Posting GROUP BY documentName ORDER BY freqSum DESC")
print("Documents with highest frequencies:")
for _ in range(3):
	row = cur.fetchone()
	print(f"\t{row[0]}, {row[1]}")

cur.execute("SELECT word, COUNT(*) as wordCount FROM Posting GROUP BY word ORDER BY wordCount DESC")
print("Words that appear in most documents:")
for _ in range(3):
	row = cur.fetchone()
	print(f"\t{row[0]}, {row[1]}")


# Close DB connection
conn.close()
