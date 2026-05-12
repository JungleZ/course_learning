import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import app, get_db_connection, parse_wechat_signup
from app import PHASE_TEMPLATES

# Clean up
try:
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTPSFIX')")
    conn.execute("DELETE FROM meeting_roles WHERE meeting_id IN (SELECT id FROM meetings WHERE meeting_id = 'TESTPSFIX')")
    conn.execute("DELETE FROM meetings WHERE meeting_id = 'TESTPSFIX'")
    conn.commit()
except:
    pass
finally:
    if 'conn' in locals():
        conn.close()

# Test client
app.config['TESTING'] = True
client = app.test_client()

# Step 1: Parse post with TOM and PS1
post = """GZ Galaxy #TESTPSFIX
日期：2026年5月8日
时间：19:30~21:30
地址：测试地址
总主持 TOM：Coco Chen
备稿演讲1 PS1：Rocky Jiang"""

print("Step 1: Parsing...")
meeting_info, registrations = parse_wechat_signup(post)
print(f"  meeting_id: {meeting_info.get('meeting_id')}")
print(f"  registrations: {registrations}")

# Store in session
with client.session_transaction() as sess:
    sess['preview_meeting_info'] = meeting_info
    sess['preview_registrations'] = registrations

# Step 2: Confirm
print("\nStep 2: Confirming...")
resp = client.post('/create-from-post', data={'action': 'confirm'}, follow_redirects=False)
print(f"  Status: {resp.status_code}")
print(f"  Location: {resp.headers.get('Location')}")

if resp.status_code == 302 and '/meeting/' in resp.headers.get('Location', ''):
    meeting_db_id = int(resp.headers.get('Location').split('/meeting/')[1])
    print(f"  Meeting created with DB ID: {meeting_db_id}")
    
    # Step 3: Check the reg_dict that agenda function uses
    conn = get_db_connection()
    regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', 
                     (meeting_db_id,)).fetchall()
    reg_dict = {r['role_name']: r['member_name'] for r in regs}
    
    print("\n  reg_dict contents:")
    for k, v in reg_dict.items():
        print(f"    {repr(k)}: {repr(v)}")
    
    # Now simulate what agenda function does for speech phase
    print("\n  Simulating agenda speech phase generation:")
    for i in range(1, 5):
        ps_member = None
        for role_name, member in reg_dict.items():
            if f'备稿演讲{i}' in role_name or f'PS{i}' in role_name:
                ps_member = member
                break
        
        if ps_member:
            print(f"    PS{i}: ps_member={repr(ps_member)}")
            
            # Also check TOM
            tom_member = None
            for role_name, member in reg_dict.items():
                if '总主持' in role_name or 'TOM' in role_name:
                    tom_member = member
                    break
            print(f"    TOM intro would show: {repr(tom_member)}")
            print(f"    PS{i} activity would show: PS{i} 备稿演讲{i}（{ps_member}）")
        else:
            print(f"    PS{i}: No member found")
    
    conn.close()
else:
    print(f"  Meeting creation failed!")