import sqlite3

###########################################
# Empty SQLite database for page indexing #
###########################################

# Connect to DB
conn = sqlite3.connect("inverted-index.db")
cur = conn.cursor()

# Empty tables # Commented to prevent accidental deletion
cur.execute("DELETE FROM Posting")
cur.execute("DELETE FROM IndexWord")

# Save DB changes and close connection
conn.commit()
conn.close()
