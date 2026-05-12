import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection

# Clean up first
conn = get_db_connection()
try:
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA3')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTAGENDA3')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTAGENDA3')")
except:
    pass
conn.commit()
conn.close()

# Use test client
app.config['TESTING'] = True
client = app.test_client()

# Create a meeting with timer role via create_from_post flow
from app import parse_wechat_signup
post = "测试会议 #TESTAGENDA3\n日期：2026年5月8日\n时间：19:30~21:30\n地址：测试地址\n时间官 Timer：TestPerson"

# Parse
meeting_info, registrations = parse_wechat_signup(post)
print(f"Parsed: meeting_id={meeting_info.get('meeting_id')}, registrations={len(registrations)}")

# Simulate the confirm flow by storing in session then posting
with client.session_transaction() as sess:
    sess['preview_meeting_info'] = meeting_info
    sess['preview_registrations'] = registrations

resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print(f"Create meeting: status={resp.status_code}, location={resp.headers.get('Location')}")

# Extract meeting ID from location
location = resp.headers.get('Location', '')
if '/meeting/' in location:
    meeting_db_id = int(location.split('/meeting/')[1])
    print(f"Meeting created with DB ID: {meeting_db_id}")
    
    # Now test agenda generation
    resp_agenda = client.get(f'/meeting/{meeting_db_id}/agenda')
    print(f"Agenda page: status={resp_agenda.status_code}")
    
    if resp_agenda.status_code == 200:
        html = resp_agenda.data.decode('utf-8')
        # Check if timer appears in agenda
        if '时间官' in html or 'Timer' in html:
            print("SUCCESS: Timer found in agenda!")
        else:
            print("Timer NOT found in agenda")
            # Show a snippet
            snippet = html[html.find('<table'):html.find('</table>')+8] if '<table' in html else html[:500]
            print("Agenda table snippet:")
            print(snippet[:500])
    else:
        print(f"Agenda page failed: {resp_agenda.status_code}")
else:
    print("Failed to create meeting")

conn.close()