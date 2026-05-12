import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

meeting = conn.execute("SELECT id, meeting_id FROM meetings WHERE id = 23").fetchone()
print(f"Meeting: id={meeting[0]}, meeting_id={meeting[1]}")

print("\nRegistrations:")
regs = conn.execute("""
    SELECT r.role_name, r.member_name, m.is_member
    FROM registrations r
    LEFT JOIN members m ON r.member_name = m.name
    WHERE r.meeting_id = 23
""").fetchall()
for r in regs:
    tag = 'Member' if r[2] else 'Guest'
    print(f"  {r[0]}: {r[1]} [{tag}]")

conn.close()