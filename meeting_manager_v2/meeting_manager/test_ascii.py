import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import parse_wechat_signup

# Test with a simple English-only post to avoid encoding issues in output
post = "Test Meeting #TEST123\nDate: 2026-05-08\nTime: 19:30~21:30\nAddress: Test Address\nTimer: TestPerson"
meeting_info, registrations = parse_wechat_signup(post)
print("meeting_id:", meeting_info.get('meeting_id'))
print("registrations count:", len(registrations))
if registrations:
    # Only print the first registration's role and member if they are ASCII
    role, member = registrations[0]
    # Check if they contain non-ASCII characters
    if all(ord(c) < 128 for c in role) and all(ord(c) < 128 for c in member):
        print("first registration:", role, "-", member)
    else:
        print("first registration: [contains non-ASCII]")