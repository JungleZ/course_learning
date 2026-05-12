import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import parse_wechat_signup

# Test with the exact format from the user's example
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

try:
    meeting_info, registrations = parse_wechat_signup(post)
    
    # Write results to file to avoid encoding issues
    with open('parse_result.txt', 'w', encoding='utf-8') as f:
        f.write(f"meeting_id: {repr(meeting_info.get('meeting_id'))}\n")
        f.write(f"theme: {repr(meeting_info.get('theme'))}\n")
        f.write(f"time: {repr(meeting_info.get('time'))}\n")
        f.write(f"address: {repr(meeting_info.get('address'))}\n")
        f.write(f"registrations count: {len(registrations)}\n")
        for i, (role, member) in enumerate(registrations):
            f.write(f"registration {i+1}: {repr(role)} - {repr(member)}\n")
    
    print("Results written to parse_result.txt")
    print("Meeting ID:", meeting_info.get('meeting_id'))
    print("Registrations count:", len(registrations))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()