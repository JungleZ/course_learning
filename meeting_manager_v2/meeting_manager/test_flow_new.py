import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app

app.config['TESTING'] = True
client = app.test_client()

# Clear session
with client.session_transaction() as sess:
    sess.clear()

# Use a new meeting ID
post = '''GZ Galaxy 头马例会 #983
日期：2026年5月7日
时间：19:30~21:30
地址：珠江新城
会议主席 MM：Christina Fang'''

# Step 1: Parse
print('=== STEP 1: PARSE ===')
resp = client.post('/create-from-post', data={'post_text': post, 'action': 'parse'})
print('Parse status:', resp.status_code)

# Check session
with client.session_transaction() as sess:
    has_info = 'preview_meeting_info' in sess
    has_regs = 'preview_registrations' in sess
    print('Session has meeting info:', has_info)
    print('Session has registrations:', has_regs)
    if has_info:
        info = sess['preview_meeting_info']
        print('Meeting ID in session:', info.get('meeting_id'))

# Step 2: Confirm
print('')
print('=== STEP 2: CONFIRM ===')
resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print('Confirm status:', resp.status_code)
print('Location:', resp.headers.get('Location'))

if resp.status_code != 302:
    print('Response data (first 500 chars):')
    print(resp.data.decode('utf-8')[:500])
else:
    print('SUCCESS - Redirected as expected')
    # Follow the redirect to see if we get to meeting detail
    location = resp.headers.get('Location')
    if location:
        resp2 = client.get(location)
        print('Followed to:', location, ', status:', resp2.status_code)
        if resp2.status_code == 200:
            html = resp2.data.decode('utf-8')
            if '会议详情' in html or 'Meeting Detail' in html:
                print('SUCCESS: Reached meeting detail page!')
            else:
                print('Did not reach meeting detail page')
                # Check for flash messages
                if '创建成功' in html:
                    print('But we see success message - maybe we are on the create-from-post page with a success flash?')
                else:
                    # Show a snippet to see what page we are on
                    print('Page title snippet:')
                    # Look for title tag
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    if title_match:
                        print('  Title:', title_match.group(1))
                    else:
                        print('  No title found, showing first 200 chars:')
                        print(html[:200])