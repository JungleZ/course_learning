import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

# Set Doris as Guest (is_member=0)
conn.execute("UPDATE members SET is_member = 0 WHERE name = 'Doris Huang'")
conn.commit()

# Verify
row = conn.execute("SELECT id, name, is_member FROM members WHERE name = 'Doris Huang'").fetchone()
if row:
    tag = 'Member' if row[2] else 'Guest'
    print(f"Doris Huang -> {tag}")

conn.close()
print("Done!")