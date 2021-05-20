import sqlite3

################################################
# Initialize SQLite database for page indexing #
################################################

# Connect to DB
conn = sqlite3.connect("inverted-index.db")
cur = conn.cursor()

# Create table
cur.execute("""
	CREATE TABLE IndexWord (
		word TEXT PRIMARY KEY
	);
""")

cur.execute("""
	CREATE TABLE Posting (
		word TEXT NOT NULL,
		documentName TEXT NOT NULL,
		frequency INTEGER NOT NULL,
		indexes TEXT NOT NULL,
		PRIMARY KEY(word, documentName),
		FOREIGN KEY (word) REFERENCES IndexWord(word)
	);
""")

# Save DB changes and close connection
conn.commit()
conn.close()
