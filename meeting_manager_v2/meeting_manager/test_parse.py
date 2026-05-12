import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import parse_wechat_signup

post = "测试会议 #TESTAGENDA3\n日期：2026年5月8日\n时间：19:30~21:30\n地址：测试地址\n时间官 Timer：TestPerson"
meeting_info, registrations = parse_wechat_signup(post)
print("meeting_id:", meeting_info.get('meeting_id'))
print("registrations count:", len(registrations))
if registrations:
    print("first registration role:", registrations[0][0])
    print("first registration member:", registrations[0][1])