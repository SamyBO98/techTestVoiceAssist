from db import init_db, save_appointment, DB_NAME
import sqlite3

# Init our DB
init_db()
print("Database initialized")

# Test with a random text date
test_date = "2026-03-05"
save_appointment(test_date)
print("Saved appointment:" +str(test_date))

# Get Data to check if it works
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("SELECT * FROM call_end_info")
rows = c.fetchall()
conn.close()

print("Current rows in DB:")
for row in rows:
    print(row)