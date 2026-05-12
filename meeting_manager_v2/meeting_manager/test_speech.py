import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection, parse_wechat_signup

# Clean up test meeting
try:
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTSPEECH')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTSPEECH')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTSPEECH')")
    conn.commit()
except:
    pass
conn.close()

# Test client
app.config['TESTING'] = True
client = app.test_client()

# Step 1: Parse a post with TOM and PS1
post = """测试会议 #TESTSPEECH
日期：2026年5月8日
时间：19:30~21:30
地址：测试地址
总主持 TOM：主持人
备稿演讲1 PS1：演讲者1"""
print("Step 1: Parsing post...")
meeting_info, registrations = parse_wechat_signup(post)
print(f"  meeting_id present: {bool(meeting_info.get('meeting_id'))}")
print(f"  registrations count: {len(registrations)}")
if registrations:
    for i, (role, member) in enumerate(registrations):
        # Only print if ASCII to avoid encoding issues
        if all(ord(c) < 128 for c in role + member):
            print(f"  registration {i+1}: {role} - {member}")
        else:
            print(f"  registration {i+1}: [non-ASCII content]")

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
            # Look for speech phase content
            import re
            
            # Find speech phase section
            speech_match = re.search(r'备稿演讲.*?</tbody>', html, re.DOTALL | re.IGNORECASE)
            if not speech_match:
                speech_match = re.search(r'Prepared Speech.*?</tbody>', html, re.DOTALL | re.IGNORECASE)
            
            if speech_match:
                print("  Speech phase section:")
                print(speech_match.group(0))
            else:
                # Show first 1500 chars of agenda to see structure
                print("  First 1500 chars of agenda:")
                print(html[:1500])
        else:
            print(f"  Agenda fetch failed: {resp_agenda.status_code}")
else:
    print("  Meeting creation failed!")
    if resp.status_code == 200:
        print("  Response (first 500 chars):")
        print(resp.data.decode('utf-8')[:500])
    else:
        print(f"  Unexpected status: {resp.status_code}")