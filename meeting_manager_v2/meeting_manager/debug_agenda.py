import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import get_db_connection, parse_wechat_signup

# Clean up first
conn = get_db_connection()
conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA2')")
conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA2')")
conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTAGENDA2'")
conn.commit()
conn.close()

# Test with timer role
post = "测试会议 #TESTAGENDA2\n日期：2026年5月8日\n时间：19:30~21:30\n地址：测试地址\n时间官 Timer：TestPerson"
meeting_info, registrations = parse_wechat_signup(post)
print("Parsed registrations count:", len(registrations))

# Store in DB like create_from_post does
conn = get_db_connection()
meeting_id = meeting_info.get('meeting_id')
theme = meeting_info.get('theme')
time_val = meeting_info.get('time')
address = meeting_info.get('address')

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
    print("Role:", r['role_name'], "| Member:", r['member_name'])

# Check what PHASE_TEMPLATES expects for timer
from app import PHASE_TEMPLATES
print("\nPHASE_TEMPLATES for 'init' phase:")
for tpl in PHASE_TEMPLATES.get('init', []):
    if '时间官' in tpl.get('activity_zh', '') or 'Timer' in tpl.get('activity_en', ''):
        print("Template role:", tpl['role'])
        print("Template activity_zh:", tpl['activity_zh'])
        print("Template activity_en:", tpl['activity_en'])

# Test the lookup
reg_dict = {r['role_name']: r['member_name'] for r in regs}
print("\nreg_dict keys:", list(reg_dict.keys()))

# What does the agenda code look for?
# In agenda generation, it uses tpl['role'] directly
for tpl in PHASE_TEMPLATES.get('init', []):
    if '时间官' in tpl.get('activity_zh', '') or 'Timer' in tpl.get('activity_en', ''):
        role_to_lookup = tpl['role']
        print("\nLooking up role:", role_to_lookup)
        member = reg_dict.get(role_to_lookup, '')
        print("Found member:", repr(member), "(empty means TBD)")
        
        # What we SHOULD be looking for:
        # Extract Chinese name part
        if '(' in role_to_lookup:
            chinese_name = role_to_lookup.split('(')[0].strip()
            print("Should look for Chinese name:", chinese_name)
            member_correct = reg_dict.get(chinese_name, '')
            print("With correct lookup, member:", repr(member_correct))

conn.close()