import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection, parse_wechat_signup

# Clean up test meeting
try:
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTFIX')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTFIX')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTFIX'")
    conn.commit()
except:
    pass
conn.close()

# Test client
app.config['TESTING'] = True
client = app.test_client()

# Step 1: Parse a post with timer role
post = "测试会议 #TESTFIX\n日期：2026年5月8日\n时间：19:30~21:30\n地址：测试地址\n时间官 Timer：TestPerson"
print("Step 1: Parsing post...")
meeting_info, registrations = parse_wechat_signup(post)
print(f"  meeting_id present: {bool(meeting_info.get('meeting_id'))}")
print(f"  registrations count: {len(registrations)}")
if registrations:
    role, member = registrations[0]
    # Only print if ASCII
    if all(ord(c) < 128 for c in role + member):
        print(f"  first registration: {role} - {member}")
    else:
        print(f"  first registration: [non-ASCII content]")

# Store in session
with client.session_transaction() as sess:
    sess['preview_meeting_info'] = meeting_info
    sess['preview_registrations'] = registrations

# Step 2: Confirm
print("\nStep 2: Confirming meeting creation...")
resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print(f"  Status: {resp.status_code}")
print(f"  Location: {resp.headers.get('Location')}")

if resp.status_code == 302 and '/meeting/' in resp.headers.get('Location', ''):
    location = resp.headers.get('Location')
    try:
        meeting_db_id = int(location.split('/meeting/')[1])
        print(f"  Meeting created with DB ID: {meeting_db_id}")
    except:
        print(f"  Could not parse meeting DB ID from location: {location}")
        meeting_db_id = None
    
    if meeting_db_id:
        # Step 3: Check agenda
        print("\nStep 3: Checking agenda page...")
        resp_agenda = client.get(f'/meeting/{meeting_db_id}/agenda')
        print(f"  Agenda status: {resp_agenda.status_code}")
        
        if resp_agenda.status_code == 200:
            html = resp_agenda.data.decode('utf-8')
            # Look for timer in the agenda - check for both Chinese and English
            if '时间官' in html:
                print("  SUCCESS: Found '时间官' in agenda!")
            elif 'Timer' in html:
                print("  SUCCESS: Found 'Timer' in agenda!")
            else:
                print("  ISSUE: Neither '时间官' nor 'Timer' found in agenda")
                # Show what we DO see around the init phase
                import re
                # Find the init phase section
                init_match = re.search(r'签到与开场.*?</tbody>', html, re.DOTALL | re.IGNORECASE)
                if not init_match:
                    init_match = re.search(r'Init.*?</tbody>', html, re.DOTALL | re.IGNORECASE)
                if init_match:
                    print("  Init phase section (first 500 chars):")
                    print(init_match.group(0)[:500])
                else:
                    # Show first 1000 chars of agenda
                    print("  First 1000 chars of agenda:")
                    print(html[:1000])
        else:
            print(f"  Agenda fetch failed: {resp_agenda.status_code}")
else:
    print("  Meeting creation failed!")
    if resp.status_code == 200:
        print("  Response (first 500 chars):")
        print(resp.data.decode('utf-8')[:500])
    else:
        print(f"  Unexpected status: {resp.status_code}")