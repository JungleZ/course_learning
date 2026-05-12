import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import parse_wechat_signup

# Very simple test with ASCII only
post = "#123\n时间官 Timer：Test"
meeting_info, registrations = parse_wechat_signup(post)
print("meeting_id present:", bool(meeting_info.get('meeting_id')))
print("meeting_id length:", len(meeting_info.get('meeting_id', '')))
print("registrations count:", len(registrations))
if registrations:
    print("first registration role type:", type(registrations[0][0]))
    print("first registration member type:", type(registrations[0][1]))
    # Check lengths instead of printing content
    print("first role length:", len(registrations[0][0]))
    print("first member length:", len(registrations[0][1]))