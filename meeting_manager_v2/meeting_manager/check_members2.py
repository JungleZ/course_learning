import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

# Add is_member=1 for members that don't have it
rows = conn.execute("SELECT id, name, is_member FROM members").fetchall()
for r in rows:
    print(f"id={r[0]} name={r[1]} is_member={r[2]}")

conn.close()