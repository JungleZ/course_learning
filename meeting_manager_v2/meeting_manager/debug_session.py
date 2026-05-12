import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app

app.config['TESTING'] = True
client = app.test_client()

# Clear any existing session
with client.session_transaction() as sess:
    sess.clear()

# Parse the post - use simple ASCII to avoid encoding issues in debug
post = '''GZ Galaxy 头马例会 #982
日期：2026年5月7日
时间：19:30~21:30
地址：珠江新城
会议主席 MM：Christina Fang'''

print("=== STEP 1: PARSE ===")
resp = client.post('/create-from-post', data={'post_text': post, 'action': 'parse'})
print(f"Status: {resp.status_code}")

# Check what's in session after parse
with client.session_transaction() as sess:
    print(f"Session has preview_meeting_info: {'preview_meeting_info' in sess}")
    print(f"Session has preview_registrations: {'preview_registrations' in sess}")
    if 'preview_meeting_info' in sess:
        info = sess['preview_meeting_info']
        print(f"Meeting info has meeting_id: {'meeting_id' in info}")
        if 'meeting_id' in info:
            print(f"  meeting_id value: {info['meeting_id']}")
    if 'preview_registrations' in sess:
        regs = sess['preview_registrations']
        print(f"Registrations count: {len(regs)}")

print("\n=== STEP 2: CONFIRM ===")
# Now test the confirm step
resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Location: {resp.headers.get('Location')}")

if resp.status_code != 302:
    print("Response data (first 500 chars):")
    print(resp.data.decode('utf-8')[:500])
else:
    print("SUCCESS - Redirected as expected")