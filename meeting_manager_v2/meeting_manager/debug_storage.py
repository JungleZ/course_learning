import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')
from app import app, get_db_connection

# Clean up any existing test meeting
conn = get_db_connection()
conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA')")
conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA')")
conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTAGENDA'")
conn.commit()
conn.close()

# Test with a simple post
from app import parse_wechat_signup
post = "测试会议 #TESTAGENDA\n日期：2026年5月8日\n时间：19:30~21:30\n地址：测试地址\n时间官 Timer：TestPerson"
meeting_info, registrations = parse_wechat_signup(post)
print("Parsed registrations:", registrations)

# Simulate the confirm step
conn = get_db_connection()
meeting_id = meeting_info.get('meeting_id')
theme = meeting_info.get('theme')
time_val = meeting_info.get('time')
address = meeting_info.get('address')

# Insert meeting
conn.execute("""
    INSERT INTO meetings (meeting_id, theme, english_theme, time, time_en, address, address_en, fee_info, fee_info_en)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (meeting_id, theme, '', time_val, '', address, '', '', ''))

meeting_db_id = conn.execute('SELECT id FROM meetings WHERE meeting_id = ?', (meeting_id,)).fetchone()[0]

# Add default roles
from app import DEFAULT_ROLES
for role in DEFAULT_ROLES:
    conn.execute(
        "INSERT INTO meeting_roles (meeting_id, role_name) VALUES (?, ?)",
        (meeting_db_id, role['name_zh'])
    )

# Add registrations
for role_name, member_name in registrations:
    conn.execute(
        "INSERT INTO registrations (meeting_id, role_name, member_name) VALUES (?, ?, ?)",
        (meeting_db_id, role_name, member_name)
    )

conn.commit()

# Check what's actually stored
regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
print("Stored in registrations table:")
for r in regs:
    print(f"  {r['role_name']}: {r['member_name']}")

# Check meeting_roles
roles = conn.execute('SELECT role_name FROM meeting_roles WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
print("\nStored in meeting_roles table:")
for r in roles:
    print(f"  {r['role_name']}")

conn.close()