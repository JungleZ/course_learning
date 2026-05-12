import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

# List all members with their is_member status
print("All members (is_member = 0 means Guest):")
rows = conn.execute("SELECT id, name, is_member FROM members ORDER BY id DESC LIMIT 30").fetchall()
for r in rows:
    tag = 'Guest' if r[2] == 0 else 'Member'
    print(f"  id={r[0]} {r[1]} -> {tag}")

conn.close()