from flask import Flask, render_template, jsonify, request
import random
import time
from datetime import datetime
import uuid

app = Flask(__name__)

# 模拟在线用户和聊天记录（实际生产环境应使用数据库）
online_users = {}
chat_messages = []
chat_start_time = None

# List of love and emotional intelligence quotes - 超全版（85+条）
quotes = [
    # 基础恋爱观
    "爱不是占有，而是欣赏。",
    "真正的亲密关系是建立在相互理解和尊重之上的。",
    "爱需要勇气，尤其是面对不确定性时。",
    "健康的关系允许双方成长，而不是互相束缚。",
    "宽恕是爱情中最强大的治愈剂。",
    "真爱的标志是即使在对方最不完美的时候也选择陪伴。",
    "在爱情中，保持独立比完全依赖更重要。",
    "感恩是维持长久关系的秘诀。",
    "爱不是寻找一个完美的人，而是学会以完美的方式看待一个不完美的人。",
    "爱需要持续的努力，而不是一时的热情。",
    "在关系中，小事的积累往往比大事件更重要。",
    
    # 情商与情绪管理
    "情商高的人懂得倾听，而不仅仅是等待说话的机会。",
    "在关系中，脆弱不是弱点，而是建立信任的桥梁。",
    "情商包括认识到自己的情绪并为之负责。",
    "沟通不是为了赢得争论，而是为了更好地理解对方。",
    "情商高的人知道何时说'我需要空间'。",
    "关系中的冲突不可避免，但如何处理冲突决定了关系的质量。",
    "自我爱是建立健康关系的基础。",
    "倾听比提供解决方案更重要，尤其当对方只是需要被理解时。",
    "情商包括在压力下保持冷静和理性。",
    "学会识别并表达自己的情绪，是成熟的表现。",
    "情绪稳定不是没有情绪，而是能够合理管理情绪。",
    
    # 沟通技巧
    "用'我感受到...'代替'你总是...'，减少对方的防御心理。",
    "有效的沟通始于真诚的倾听，终于相互的理解。",
    "不要在愤怒时做决定，不要在开心时许承诺。",
    "说话前先思考：这是真的吗？这是必要的吗？这是善意的吗？",
    "沉默有时比言语更有力量，学会适时保持安静。",
    "表达需求时，使用'我希望...'而非'你应该...'。",
    "道歉不是示弱，而是展现成熟和担当。",
    "赞美要具体，批评要私下，建议要温和。",
    "学会说'不'，是建立健康边界的第一步。",
    "真正的沟通是心与心的对话，不只是信息的交换。",
    
    # 相处之道
    "给彼此空间，让爱有呼吸的余地。",
    "记住重要的日子，细节体现用心。",
    "一起做饭比一起吃饭更浪漫，因为那是共同的创造。",
    "不要试图改变对方，而是欣赏彼此的差异。",
    "定期约会，即使在一起很久，也要保持仪式感。",
    "分享彼此的梦想，成为对方追梦路上的支持者。",
    "学会妥协，但不是放弃原则。",
    "在争吵后主动和解，这不是认输，而是珍惜。",
    "培养共同的兴趣爱好，但也尊重各自的独处时间。",
    "遇到困难时，记住你们是队友，不是对手。",
    "每天至少一次真诚的拥抱，胜过千言万语。",
    "学会欣赏对方的优点，包容对方的缺点。",
    
    # 信任与忠诚
    "信任如同镜子，一旦破碎很难复原，请小心呵护。",
    "诚实是爱情的基石，即使是善意的谎言也会侵蚀信任。",
    "给对方查看手机的权利，但不需要有查看的欲望。",
    "忠诚不仅是身体的专一，更是心灵的归属。",
    "疑心病是感情的毒药，信任是解药。",
    "透明的沟通能消除大部分猜疑。",
    
    # 成长与支持
    "最好的爱情是让彼此成为更好的人。",
    "支持对方的事业和梦想，即使这意味着暂时的分离。",
    "共同成长比单方面付出更能维系长久的关系。",
    "鼓励对方追求个人目标，而不是要求对方为你牺牲。",
    "在对方低谷时给予支持，在高峰时给予掌声。",
    "一起学习新事物，让关系保持新鲜感。",
    
    # 处理冲突
    "争吵时对事不对人，避免人身攻击。",
    "冷静期不是冷战，而是给彼此思考的空间。",
    "承认错误不可耻，死不认错才可怕。",
    "找到问题的根源，而不是只解决表面现象。",
    "学会换位思考，理解对方的立场和感受。",
    "不要在第三者面前批评你的伴侣。",
    "设定'吵架规则'：不翻旧账、不骂人、不离家出走。",
    
    # 亲密与浪漫
    "浪漫不需要昂贵，用心就是最好的礼物。",
    "身体接触是爱的语言之一，不要忽视拥抱和牵手。",
    "制造惊喜，让生活充满期待和甜蜜。",
    "写一封手写信，在这个数字时代显得格外珍贵。",
    "回忆初次相遇的美好，重温当初的心动。",
    "偶尔的小别胜新婚，距离产生美。",
    
    # 长期关系维护
    "爱情需要经营，就像花园需要浇灌。",
    "定期回顾关系状态，及时调整和改进。",
    "不要把对方的付出视为理所当然。",
    "保持好奇心，持续了解对方的变化。",
    "共同制定未来计划，让关系有方向感。",
    "学会在平淡中发现美好，在平凡中创造浪漫。",
    "经济独立是感情独立的基础。",
    "处理好与原生家庭的关系，避免影响小家庭。",
    
    # 自我提升
    "先爱自己，才有能力爱别人。",
    "保持个人成长，不要让关系成为停滞的理由。",
    "有自己的社交圈，不要把所有情感需求都寄托在伴侣身上。",
    "培养独立的兴趣爱好，让自己成为一个有趣的人。",
    "身心健康是对关系最大的贡献。",
    "学会独处，享受孤独，这样才能更好地相聚。",
    
    # 智慧金句
    "爱情不是1+1=2，而是0.5+0.5=1，各自去掉一半个性才能完整。",
    "真正爱你的人，不会让你一直猜。",
    "合适的两个人，不是天生一对，而是互相磨合后的契合。",
    "爱情最美的样子：你有我的包容，我有你的理解。",
    "好的感情，是乍见之欢，更是久处不厌。",
    "爱对了人，每天都是情人节；爱错了人，每天都是愚人节。",
    
    # 新增：异地恋专题
    "异地恋考验的不是距离，而是信任和坚持。",
    "视频通话不能替代拥抱，但能传递思念。",
    "为下次见面制定计划，让等待变得有期待。",
    "分享日常生活的小事，让彼此感觉从未远离。",
    "异地恋需要更多的沟通，而不是更多的猜测。",
    "把分离的时间当作自我成长的机遇。",
    "定期的见面计划是维系异地恋的关键。",
    "不要因为距离而降低对关系的要求。",
    
    # 新增：婚姻与家庭
    "婚姻不是爱情的终点，而是另一种形式的开始。",
    "家务分工要公平，但更要体谅对方的辛苦。",
    "在孩子面前展现相爱的父母形象，是最好的教育。",
    "婆媳关系的核心是丈夫的态度和智慧。",
    "财务透明是婚姻稳定的重要保障。",
    "记住结婚纪念日，重温当年的誓言。",
    "给彼此独处的时间，即使是夫妻也需要空间。",
    "共同承担育儿责任，不要让一方独自承受。",
    
    # 新增：分手与疗愈
    "分手不是失败，而是不合适的及时止损。",
    "允许自己悲伤，但不要沉溺其中。",
    "删除联系方式不是绝情，而是给自己愈合的空间。",
    "从每段关系中学习和成长，而不是自责和后悔。",
    "时间是最好的疗伤药，但主动 healing 更重要。",
    "不要因为害怕受伤而拒绝再次去爱。",
    "结束一段关系前，确保你已经尽力沟通和处理。",
    "单身不是惩罚，而是重新认识自己的机会。",
    
    # 新增：约会与初识
    "第一次约会，真诚比完美更重要。",
    "观察对方如何对待服务员，能看出ta的真实品格。",
    "不要太快投入，给彼此足够了解的时间。",
    "共同的价值观比共同的兴趣更重要。",
    "注意对方的言行是否一致，这反映诚信度。",
    "约会时放下手机，专心陪伴对方。",
    "不要为了迎合对方而隐藏真实的自己。",
    "第一印象很重要，但深入了解更需要耐心。",
    
    # 新增：边界与尊重
    "健康的边界不是疏远，而是相互尊重的表现。",
    "学会拒绝不合理的要求，保护自己的能量。",
    "尊重对方的隐私，不等于不信任。",
    "每个人都有自己的底线，触碰前要三思。",
    "边界清晰的关系反而更加亲密和持久。",
    "不要以爱的名义控制对方的自由。",
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bus-chat')
def bus_chat():
    """等公交聊天室页面"""
    return render_template('bus_chat.html')

@app.route('/profile')
def profile():
    """个人资料页面"""
    return render_template('profile.html')

@app.route('/api/quote')
def get_quote():
    # Return a random quote with category info
    quote = random.choice(quotes)
    return jsonify({
        'quote': quote,
        'timestamp': time.time(),
        'total_quotes': len(quotes)
    })

@app.route('/api/chat/join', methods=['POST'])
def join_chat():
    """加入聊天室"""
    global chat_start_time
    data = request.json
    username = data.get('username', f'用户{random.randint(1000, 9999)}')
    user_id = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
    
    online_users[user_id] = {
        'username': username,
        'join_time': time.time(),
        'last_active': time.time()
    }
    
    # 如果是第一个用户，记录聊天开始时间
    if len(online_users) == 1:
        chat_start_time = time.time()
    
    # 发送系统消息
    system_msg = {
        'type': 'system',
        'message': f'{username} 加入了等公交聊天室',
        'timestamp': time.time(),
        'online_count': len(online_users)
    }
    chat_messages.append(system_msg)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'username': username,
        'online_count': len(online_users),
        'messages': chat_messages[-50:],  # 返回最近50条消息
        'chat_start_time': chat_start_time
    })

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """发送消息"""
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message', '').strip()
    
    if not message or user_id not in online_users:
        return jsonify({'success': False, 'error': '无效请求'})
    
    # 更新最后活跃时间
    online_users[user_id]['last_active'] = time.time()
    
    msg_data = {
        'type': 'message',
        'user_id': user_id,
        'username': online_users[user_id]['username'],
        'message': message,
        'timestamp': time.time()
    }
    chat_messages.append(msg_data)
    
    return jsonify({'success': True})

@app.route('/api/chat/messages')
def get_messages():
    """获取最新消息"""
    user_id = request.args.get('user_id')
    
    # 清理不活跃的用户（超过2分钟未活动）
    current_time = time.time()
    inactive_users = [uid for uid, data in online_users.items() 
                     if current_time - data['last_active'] > 120]
    for uid in inactive_users:
        removed_user = online_users.pop(uid)
        system_msg = {
            'type': 'system',
            'message': f'{removed_user["username"]} 离开了聊天室',
            'timestamp': time.time(),
            'online_count': len(online_users)
        }
        chat_messages.append(system_msg)
    
    return jsonify({
        'messages': chat_messages[-50:],
        'online_count': len(online_users),
        'chat_duration': int(current_time - chat_start_time) if chat_start_time else 0,
        'can_add_friend': chat_start_time and (current_time - chat_start_time >= 300)  # 5分钟=300秒
    })

@app.route('/api/chat/bus-status')
def bus_status():
    """获取公交车状态"""
    current_time = time.time()
    
    # 模拟公交车到站时间（每2分钟一趟）
    minutes_since_midnight = (current_time % 86400) / 60
    next_bus_in = 2 - (minutes_since_midnight % 2)
    
    # 随机生成延误原因
    delay_reasons = [
        "前方路段拥堵，交通流量较大",
        "遇到红灯较多，行驶速度较慢",
        "有乘客上下车，停留时间较长",
        "道路施工，需要绕行",
        "天气原因，路面湿滑需谨慎驾驶",
        "高峰期乘客较多，上车时间长",
        "车辆故障检修，临时调度其他车辆",
        "司机休息换班，稍作等待"
    ]
    
    is_delayed = next_bus_in > 2.5  # 如果超过2.5分钟算延误
    
    return jsonify({
        'next_bus_in': round(next_bus_in, 1),
        'is_delayed': is_delayed,
        'delay_reason': random.choice(delay_reasons) if is_delayed else None,
        'scheduled_interval': 2,
        'online_users': len(online_users)
    })

@app.route('/api/chat/leave', methods=['POST'])
def leave_chat():
    """离开聊天室"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id in online_users:
        username = online_users[user_id]['username']
        del online_users[user_id]
        
        # 添加系统消息
        system_message = {
            'id': str(uuid.uuid4()),
            'type': 'system',
            'message': f'{username} 离开了聊天室',
            'timestamp': datetime.now().isoformat()
        }
        chat_messages.append(system_message)
        
        # 清理超过50条的消息
        if len(chat_messages) > 50:
            chat_messages[:] = chat_messages[-50:]
    
    return jsonify({'success': True})

@app.route('/api/chat/user-profile', methods=['GET'])
def get_user_profile():
    """获取用户的个人资料（模拟从localStorage获取）"""
    user_id = request.args.get('user_id')
    
    # 在实际应用中，这里应该从数据库或Redis获取
    # 由于我们使用localStorage，前端会直接访问自己的存储
    # 这个API主要用于验证和返回基本用户信息
    
    if user_id and user_id in online_users:
        user_info = online_users[user_id]
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': user_info['username'],
            'join_time': user_info['join_time']
        })
    
    return jsonify({'success': False, 'error': '用户不存在'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
