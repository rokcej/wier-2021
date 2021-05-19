import sqlite3

# Connect to DB
conn = sqlite3.connect("inverted-index.db")
cur = conn.cursor()

# Empty tables
cur.execute("DELETE FROM Posting")
cur.execute("DELETE FROM IndexWord")

# Save DB changes and close connection
conn.commit()
conn.close()
