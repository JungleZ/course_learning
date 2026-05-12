import sqlite3
conn = sqlite3.connect('meeting.db')
conn.execute("UPDATE members SET is_member = 0 WHERE name = 'Doris Huang'")
conn.commit()
rows = conn.execute("SELECT id, name, is_member FROM members WHERE name LIKE '%Doris%'").fetchall()
for r in rows:
    print(f'id={r[0]}, name={r[1]}, is_member={r[2]}')
conn.close()
print("Done - Doris is now guest (is_member=0)")