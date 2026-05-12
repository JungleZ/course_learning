import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

# Check meeting 24 registrations
print("Meeting 24 registrations:")
rows = conn.execute("""
    SELECT r.role_name, r.member_name, m.is_member
    FROM registrations r
    LEFT JOIN members m ON r.member_name = m.name
    WHERE r.meeting_id = 24
""").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} is_member={r[2]}")

conn.close()