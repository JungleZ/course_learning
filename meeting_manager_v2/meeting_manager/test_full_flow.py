import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection, parse_wechat_signup

# Clean up test meeting
try:
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = '982')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = '982')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = '982')")
    conn.commit()
except:
    pass
conn.close()

# Test client
app.config['TESTING'] = True
client = app.test_client()

# Parse the exact user post
post = '''GZ Galaxy 头马例会 #982
欢迎每一位热爱表达、想要成长的伙伴加入头马是锻炼公众演讲、逻辑表达与领导力的成长平台，无论新手还是资深会员，都可以在这里大胆开口、刻意练习、同频成长！
📅 会议日期：2026 年 5 月 7 日 周四
⏰ 会议时间：19:30 ~ 21:30
📍 会议地址：珠江新城 - 星辰大厦 1904
所有岗位均可报名，新手配有岗位指引，零门槛可上手，欢迎主动占位挑战自己！
参会规则
部分岗位 仅限头马会员
嘉宾可旁听、可报名空余角色，欢迎围观体验
会议角色安排
会议主席 MM：Christina Fang
后勤主持组
会议主持 / 技术支持 TOM & IT：Coco Chen
会场官 SAA：Scott Peng
时间官 Timer：Mei
哼唧官 Ah-Counter：Tony
语言官 Grammarian：Christina Fang
自由分享：Doris Huang（嘉宾）
摄影师 Photographer：【空缺 可报名】
总点评官 General Evaluator：Alex Lee

💡 成长工作坊
工作坊主讲：【空缺 可报名】分享主题：【后续待定】
🎤 即兴演讲环节
即兴主持人：Ken Luo即兴点评官：Lavender Li
📝 备稿演讲环节
演讲者 1：Rocky Jiang
点评官 1：Joyce Chen
演讲者 2：Rebecca Fu
点评官 2：Dom Zhu
演讲者 3：【空缺 可报名】
点评官 3：【空缺 可报名】
演讲者 4：【空缺 可报名】
点评官 4：【空缺 可报名】
🧰 后备替补
后备人员：【空缺 可报名】
👥 参会接龙名单
1. Rocky Jiang
2. Rebecca Fu
3. Joyce Chen
4. Dom Zhu
5. Christina Fang
6. Lavender Li
7. Mei
8. Alex Lee
9. Coco Chen
10. Queeny Jin
11. Ken Luo
12. Tony
13. Scott Peng
14. Doris Huang（guest）
15.
16.'''

print("Step 1: Parsing post...")
meeting_info, registrations = parse_wechat_signup(post)
print(f"  meeting_id: {meeting_info.get('meeting_id')}")
print(f"  registrations count: {len(registrations)}")

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
            # Check if timer appears in agenda
            if '时间官' in html:
                print("  SUCCESS: Found '时间官' in agenda!")
            elif 'Timer' in html:
                print("  SUCCESS: Found 'Timer' in agenda!")
            else:
                print("  ISSUE: Neither '时间官' nor 'Timer' found in agenda")
                # Look for the init phase which should contain timer intro
                import re
                # Try multiple patterns for the init phase
                patterns = [
                    r'签到与开场.*?</tbody>',
                    r'Init.*?</tbody>',
                    r'时间官.*?</td>',
                    r'Timer.*?</td>'
                ]
                found = False
                for pattern in patterns:
                    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                    if match:
                        print(f"  Found match for pattern '{pattern}':")
                        print(match.group(0)[:500])
                        found = True
                        break
                if not found:
                    # Show first 2000 chars to see what's there
                    print("  No matches found. First 2000 chars of agenda:")
                    print(html[:2000])
        else:
            print(f"  Agenda fetch failed: {resp_agenda.status_code}")
else:
    print("  Meeting creation failed!")
    if resp.status_code == 200:
        print("  Response (first 500 chars):")
        print(resp.data.decode('utf-8')[:500])
    else:
        print(f"  Unexpected status: {resp.status_code}")