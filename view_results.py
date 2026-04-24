import sqlite3

conn = sqlite3.connect('phish_tracker.db')
c = conn.cursor()

# Pull everything from the interactions table
c.execute("SELECT * FROM interactions")
rows = c.fetchall()

print(f"{'ID':<5} | {'User ID':<20} | {'Action':<10} | {'Timestamp'}")
print("-" * 60)
for row in rows:
    print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<10} | {row[3]}")

conn.close()