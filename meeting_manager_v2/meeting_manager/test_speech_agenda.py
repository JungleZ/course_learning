import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection, parse_wechat_signup

# Clean up test meeting
try:
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA1')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA1')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTAGENDA1'")
    conn.commit()
except:
    pass
finally:
    if 'conn' in locals():
        conn.close()

# Test client
app.config['TESTING'] = True
client = app.test_client()

# Step 1: Parse a post with TOM and PS1
post = """GZ Galaxy 头马例会 #TESTAGENDA1
日期：2026年5月8日
时间：19:30~21:30
地址：测试地址
总主持 TOM：Coco Chen
备稿演讲1 PS1：Rocky Jiang
个评1 IE1：Joyce Chen"""

print("=== STEP 1: Parse ===")
meeting_info, registrations = parse_wechat_signup(post)
print(f"meeting_id: {meeting_info.get('meeting_id')}")
print(f"registrations count: {len(registrations)}")
for role, member in registrations:
    print(f"  {role}: {member}")

# Store in session
with client.session_transaction() as sess:
    sess['preview_meeting_info'] = meeting_info
    sess['preview_registrations'] = registrations

# Step 2: Confirm
print("\n=== STEP 2: Confirm ===")
resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Location: {resp.headers.get('Location')}")

if resp.status_code == 302 and '/meeting/' in resp.headers.get('Location', ''):
    meeting_db_id = int(resp.headers.get('Location').split('/meeting/')[1])
    print(f"Meeting created with DB ID: {meeting_db_id}")
    
    # Step 3: Check agenda
    print("\n=== STEP 3: Check Agenda ===")
    resp_agenda = client.get(f'/meeting/{meeting_db_id}/agenda')
    print(f"Agenda status: {resp_agenda.status_code}")
    
    if resp_agenda.status_code == 200:
        html = resp_agenda.data.decode('utf-8')
        
        # Extract the speech phase section
        import re
        # Look for the speech phase in the HTML table
        # Find all rows in the agenda table
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        print(f"Found {len(rows)} rows in agenda")
        
        # Print rows that contain PS or 备稿
        for i, row in enumerate(rows):
            if 'PS' in row or '备稿' in row or 'TOM' in row or '主持' in row:
                # Clean up HTML tags for display
                clean_row = re.sub(r'<[^>]+>', '', row)
                clean_row = re.sub(r'\s+', ' ', clean_row).strip()
                print(f"Row {i}: {clean_row[:200]}")
        
        # Also check the reg_dict that agenda function uses
        # Let's manually check what's in the database
        conn = get_db_connection()
        regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
        print(f"\nRegistrations in DB for meeting {meeting_db_id}:")
        for r in regs:
            print(f"  {r['role_name']}: {r['member_name']}")
        
        # Check meeting_roles
        roles = conn.execute('SELECT role_name FROM meeting_roles WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
        print(f"\nRoles in DB for meeting {meeting_db_id}:")
        for r in roles:
            print(f"  {r['role_name']}")
        
        conn.close()
else:
    print("Meeting creation failed!")
    if resp.status_code == 200:
        print("Response:", resp.data.decode('utf-8')[:500])