from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import re
import json

app = Flask(__name__)
app.secret_key = 'meeting_manager_secret_key'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
DB_PATH = 'meeting.db'

# 全局语言设置路由
@app.route('/set_lang/<lang>')
def set_language(lang):
    """设置全局语言"""
    session['lang'] = lang
    # 返回上一页
    return redirect(request.referrer or url_for('index'))

@app.before_request
def before_request():
    """每个请求默认语言为中文"""
    if 'lang' not in session:
        session['lang'] = 'zh'

def parse_meeting_start_time(time_str):
    """从会议时间字符串中提取开始时间（分钟）
    
    优先使用会议正式时间（如19:30-），而不是签到时间（如19:00 Sign-in）
    支持中英文格式，包括：19:30, 7:30pm, 7:30 PM, 晚上7点半等
    最终统一转换为24小时制
    """
    if not time_str:
        return 19 * 60 + 30  # 默认19:30
    
    # 尝试匹配带 AM/PM 的时间格式 (如 7:30pm, 7:30 PM, 7:30am)
    match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM|a\.m\.|p\.m\.)', time_str, re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).lower()
        
        # 转换为24小时制
        if 'pm' in period or 'p.m.' in period:
            if hour != 12:  # 12pm 是中午12点，不需要加12
                hour += 12
        elif 'am' in period or 'a.m.' in period:
            if hour == 12:  # 12am 是午夜0点
                hour = 0
        
        return hour * 60 + minute
    
    # 匹配中文时间描述 (如 晚上7点半, 下午7点30分)
    match = re.search(r'(?:晚上|下午|傍晚|晚间)(\d{1,2})[:点时](\d{0,2})', time_str)
    if match:
        hour = int(match.group(1))
        minute_str = match.group(2)
        minute = int(minute_str) if minute_str else 0
        
        # 晚上/下午通常是PM，转换为24小时制
        if hour < 12:
            hour += 12
        
        return hour * 60 + minute
    
    # 匹配上午时间 (如 上午9点, 早上10点)
    match = re.search(r'(?:上午|早上|早晨)(\d{1,2})[:点时](\d{0,2})', time_str)
    if match:
        hour = int(match.group(1))
        minute_str = match.group(2)
        minute = int(minute_str) if minute_str else 0
        
        # 处理12am的情况
        if hour == 12:
            hour = 0
        
        return hour * 60 + minute
    
    # 优先匹配会议正式时间（19:30- 这种格式，在括号内 - 中文格式）
    match = re.search(r'[（(](\d{1,2}):(\d{2})', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return hour * 60 + minute
    
    # 备选：匹配 19:30- 这种格式（连字符后）
    match = re.search(r'(\d{1,2}):(\d{2})\s*[-–—]', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return hour * 60 + minute
    
    # Match 19:30 or 19: 30 with optional space
    match = re.search(r'(\d{1,2}):\s*(\d{2})\s*[-–—]', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return hour * 60 + minute
    
    # Match 19:30 or 19: 30 without dash
    match = re.search(r'(\d{1,2}):\s*(\d{2})', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        # Only accept reasonable hour range (7-23)
        if 7 <= hour <= 23:
            return hour * 60 + minute
    
    return 19 * 60 + 30  # 默认19:30

def format_time_24h(time_str):
    """将时间字符串格式化为24小时制 HH:MM 格式"""
    if not time_str:
        return 'TBD'
    
    try:
        total_minutes = parse_meeting_start_time(time_str)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    except Exception:
        return time_str

# 注册为Jinja2全局函数
app.jinja_env.globals['format_time_24h'] = format_time_24h

DEFAULT_ROLES = [
    {'name_zh': '会议经理', 'name_en': 'Meeting Manager', 'abbrev': 'MM', 'member_only': True, 'desc_zh': '负责会议整体统筹和角色预订，确保会议顺利进行', 'desc_en': 'Responsible for overall meeting coordination and role booking'},
    {'name_zh': '接待官', 'name_en': 'Sargeant-at-Arms', 'abbrev': 'SAA', 'member_only': False, 'desc_zh': '负责签到、开场致辞和嘉宾介绍', 'desc_en': 'Responsible for sign-in, opening remarks and guest introduction'},
    {'name_zh': '总主持', 'name_en': 'Toastmaster', 'abbrev': 'TOM', 'member_only': True, 'desc_zh': '控制会议流程，引导各环节顺利衔接', 'desc_en': 'Controls meeting flow and guides transitions between segments'},
    {'name_zh': '时间官', 'name_en': 'Timer', 'abbrev': 'Timer', 'member_only': False, 'desc_zh': '记录每位演讲者时间并做报告', 'desc_en': 'Tracks time for each speaker and reports'},
    {'name_zh': '游戏官', 'name_en': 'Game Master', 'abbrev': 'GM', 'member_only': False, 'desc_zh': '设计互动游戏增加会议趣味性', 'desc_en': 'Designs interactive games for meeting fun'},
    {'name_zh': '摄影师', 'name_en': 'Photographer', 'abbrev': 'Photo', 'member_only': False, 'desc_zh': '捕捉会议精彩瞬间留念', 'desc_en': 'Captures memorable meeting moments'},
    {'name_zh': '总点评', 'name_en': 'General Evaluator', 'abbrev': 'GE', 'member_only': True, 'desc_zh': '整体点评所有演讲者和角色表现', 'desc_en': 'Evaluates all speakers and role holders overall'},
    {'name_zh': '备稿演讲1', 'name_en': 'Prepared Speech 1', 'abbrev': 'PS1', 'member_only': True, 'desc_zh': '准备好的演讲（5-7分钟）', 'desc_en': 'Prepared speech (5-7 minutes)'},
    {'name_zh': '备稿演讲2', 'name_en': 'Prepared Speech 2', 'abbrev': 'PS2', 'member_only': True, 'desc_zh': '准备好的演讲（5-7分钟）', 'desc_en': 'Prepared speech (5-7 minutes)'},
    {'name_zh': '备稿演讲3', 'name_en': 'Prepared Speech 3', 'abbrev': 'PS3', 'member_only': True, 'desc_zh': '准备好的演讲（5-7分钟）', 'desc_en': 'Prepared speech (5-7 minutes)'},
    {'name_zh': '备稿演讲4', 'name_en': 'Prepared Speech 4', 'abbrev': 'PS4', 'member_only': True, 'desc_zh': '准备好的演讲（5-7分钟）', 'desc_en': 'Prepared speech (5-7 minutes)'},
    {'name_zh': '个评1', 'name_en': 'Individual Evaluator 1', 'abbrev': 'IE1', 'member_only': True, 'desc_zh': '点评备稿演讲1', 'desc_en': 'Evaluates Prepared Speech 1'},
    {'name_zh': '个评2', 'name_en': 'Individual Evaluator 2', 'abbrev': 'IE2', 'member_only': True, 'desc_zh': '点评备稿演讲2', 'desc_en': 'Evaluates Prepared Speech 2'},
    {'name_zh': '个评3', 'name_en': 'Individual Evaluator 3', 'abbrev': 'IE3', 'member_only': True, 'desc_zh': '点评备稿演讲3', 'desc_en': 'Evaluates Prepared Speech 3'},
    {'name_zh': '个评4', 'name_en': 'Individual Evaluator 4', 'abbrev': 'IE4', 'member_only': True, 'desc_zh': '点评备稿演讲4', 'desc_en': 'Evaluates Prepared Speech 4'},
    {'name_zh': '哼哈官', 'name_en': 'Ah-Counter', 'abbrev': 'Ah', 'member_only': False, 'desc_zh': '记录选手嗯哈次数帮助改进', 'desc_en': 'Counts fillers to help speakers improve'},
    {'name_zh': '语法官', 'name_en': 'Grammarian', 'abbrev': 'Gram', 'member_only': False, 'desc_zh': '记录好词好句及语言错误', 'desc_en': 'Notes good words and language errors'},
    {'name_zh': '即兴主持', 'name_en': 'Table Topics Master', 'abbrev': 'TTM', 'member_only': True, 'desc_zh': '邀请观众即兴演讲并抽取主题', 'desc_en': 'Invites table topics and selects themes'},
    {'name_zh': '即兴点评', 'name_en': 'Table Topics Evaluator', 'abbrev': 'TTE', 'member_only': True, 'desc_zh': '点评即兴演讲者表现', 'desc_en': 'Evaluates table topics speakers'},
    {'name_zh': '自由分享', 'name_en': 'Free Sharing', 'abbrev': 'Free', 'member_only': False, 'desc_zh': '开场自由分享环节', 'desc_en': 'Free sharing segment at opening'},
    {'name_zh': '嘉宾分享', 'name_en': 'Guest Sharing', 'abbrev': 'Guest', 'member_only': False, 'desc_zh': '会议结尾邀请嘉宾分享', 'desc_en': 'Invites guests to share at closing'},
    {'name_zh': '会长', 'name_en': 'President', 'abbrev': 'President', 'member_only': True, 'desc_zh': '俱乐部最高领导，负责闭幕和颁奖', 'desc_en': 'Club leader, closing and awards', 'default_member': 'Bass'},
]

def get_role_display_name(role, lang='zh'):
    """返回格式化的角色名: 中文名 (缩写) 或 Meeting Manager (MM)"""
    for r in DEFAULT_ROLES:
        if r['name_zh'] == role or r['abbrev'] == role:
            return f"{r['name_zh']} ({r['abbrev']})"
        if r['abbrev'] in role or r['name_zh'] in role:
            return f"{r['name_zh']} ({r['abbrev']})"
    
    # 未找到匹配，返回原样
    return role

def get_role_display_name_lang(role, lang='zh'):
    """根据语言返回格式化的角色名"""
    for r in DEFAULT_ROLES:
        if r['name_zh'] == role or r['abbrev'] == role:
            if lang == 'en':
                return f"{r['name_en']} ({r['abbrev']})"
            return f"{r['name_zh']} ({r['abbrev']})"
        if r['abbrev'] in role or r['name_zh'].replace('演讲','Speech').replace('个评','IE').replace('备稿','PS') in role or r['name_zh'] in role:
            if lang == 'en':
                return f"{r['name_en']} ({r['abbrev']})"
            return f"{r['name_zh']} ({r['abbrev']})"
    return role

def get_role_description(role, lang='zh'):
    """获取角色描述"""
    for r in DEFAULT_ROLES:
        if r['name_zh'] == role or r['abbrev'] == role:
            if lang == 'en':
                return r.get('desc_en', '')
            return r.get('desc_zh', '')
        if r['abbrev'] in role or r['name_zh'] in role:
            if lang == 'en':
                return r.get('desc_en', '')
            return r.get('desc_zh', '')
    return ''

def is_member_only_role(role_name):
    """检查角色是否仅限会员"""
    for r in DEFAULT_ROLES:
        if r['name_zh'] == role_name or r['abbrev'] == role_name:
            return r.get('member_only', False)
        if r['abbrev'] in role_name or r['name_zh'] in role_name:
            return r.get('member_only', False)
    return False

PHASE_CONFIG = [
    {"key": "init", "name_zh": "签到与开场", "name_en": "Init", "color": "bg-init text-dark"},
    {"key": "table_topics", "name_zh": "即兴演讲", "name_en": "Table Topics", "color": "bg-topics text-dark"},
    {"key": "speech", "name_zh": "备稿演讲", "name_en": "Prepared Speech", "color": "bg-speech text-dark"},
    {"key": "break", "name_zh": "中场休息", "name_en": "Break", "color": "bg-break text-dark"},
    {"key": "evaluation", "name_zh": "点评环节", "name_en": "Evaluation", "color": "bg-eval text-dark"},
    {"key": "workshop", "name_zh": "工作坊", "name_en": "Workshop", "color": "bg-workshop text-dark"},
    {"key": "custom", "name_zh": "自定义活动", "name_en": "Custom", "color": "bg-custom text-dark"},
    {"key": "closing", "name_zh": "闭幕总结", "name_en": "Closing", "color": "bg-closing text-dark"},
]

PHASE_TEMPLATES = {
    "init": [
        {"activity_zh": "会员嘉宾签到", "activity_en": "Guest & Members Sign In", "duration": 15, "role": "接待官(SAA)"},
        {"activity_zh": "宣布开会及规则介绍", "activity_en": "Calling for the meeting & rules intro", "duration": 4, "role": "接待官(SAA)"},
        {"activity_zh": "开场致辞及嘉宾介绍", "activity_en": "Opening remarks & Guests Introduction", "duration": 5, "role": "总主持(TOM)"},
        {"activity_zh": "TOM介绍会议角色", "activity_en": "TOM's Introduction of facilitators", "duration": 2, "role": "总主持(TOM)"},
        {"activity_zh": "摄影师介绍", "activity_en": "Introduction of Photographer", "duration": 1, "role": "摄影师(Photographer)"},
        {"activity_zh": "时间官介绍", "activity_en": "Introduction of Timer", "duration": 2, "role": "时间官(Timer)"},
        {"activity_zh": "哼哈官介绍", "activity_en": "Introduction of Ah Counter", "duration": 2, "role": "哼哈官(Ah-Counter)"},
        {"activity_zh": "语法官介绍", "activity_en": "Introduction of Grammarian", "duration": 2, "role": "语法官(Grammarian)"},
        {"activity_zh": "总点评介绍", "activity_en": "Introduction of General Evaluator", "duration": 2, "role": "总点评(GE)"},
        {"activity_zh": "自由分享", "activity_en": "Free Sharing", "duration": 2, "role": "自由分享(Free Sharing)"},
    ],
    "table_topics": [
        {"activity_zh": "TOM过渡到即兴环节", "activity_en": "TOM's Transition for Table Topics", "duration": 1, "role": "总主持(TOM)"},
        {"activity_zh": "即兴演讲", "activity_en": "Table topics speeches", "duration": 16, "role": "即兴主持(TTM)"},
        {"activity_zh": "即兴点评", "activity_en": "Table topics evaluation", "duration": 6, "role": "即兴点评(TTE)"},
    ],
    "speech": [
        {"activity_zh": "TOM过渡到备稿演讲", "activity_en": "TOM's Transition for Prepared Speeches", "duration": 1, "role": "总主持(TOM)"},
    ],
    "break": [
        {"activity_zh": "中场休息", "activity_en": "Break Time", "duration": 5, "role": "All"},
    ],
    "evaluation": [
        {"activity_zh": "TOM过渡到点评环节", "activity_en": "TOM's Transition for Evaluation", "duration": 1, "role": "总主持(TOM)"},
    ],
    "closing": [
        {"activity_zh": "TOM过渡到角色报告", "activity_en": "TOM's transition for facilitators report", "duration": 1, "role": "总主持(TOM)"},
        {"activity_zh": "时间官报告", "activity_en": "Timer report", "duration": 2, "role": "时间官(Timer)"},
        {"activity_zh": "语法官报告", "activity_en": "Grammarian report", "duration": 2, "role": "语法官(Grammarian)"},
        {"activity_zh": "哼哈官报告", "activity_en": "Ah-Counter report", "duration": 2, "role": "哼哈官(Ah-Counter)"},
        {"activity_zh": "总点评报告", "activity_en": "General evaluator report", "duration": 7, "role": "总点评(GE)"},
        {"activity_zh": "最佳投票", "activity_en": "Vote for the Best", "duration": 1, "role": "总主持(TOM)"},
        {"activity_zh": "嘉宾分享", "activity_en": "Guest sharing", "duration": 3, "role": "嘉宾分享(Guest Sharing)", "default_member": "Bass"},
        {"activity_zh": "颁奖环节", "activity_en": "Awarding time", "duration": 3, "role": "President", "default_member": "Bass"},
        {"activity_zh": "闭幕词", "activity_en": "Closing remarks", "duration": 2, "role": "President", "default_member": "Bass"},
        {"activity_zh": "角色预订", "activity_en": "Role booking", "duration": 1, "role": "会议经理(MM)"},
        {"activity_zh": "会议结束", "activity_en": "Meeting Adjourned", "duration": 0, "role": "-"},
    ]
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 先创建表（如果不存在）
        cursor.execute("""CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id TEXT UNIQUE NOT NULL,
            theme TEXT NOT NULL,
            english_theme TEXT,
            time TEXT NOT NULL,
            time_en TEXT,
            address TEXT,
            address_en TEXT,
            fee_info TEXT,
            fee_info_en TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # 然后检查并添加新字段
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加英文字段
        new_fields = [
            ('english_theme', 'TEXT'),
            ('time_en', 'TEXT'),
            ('address_en', 'TEXT'),
            ('fee_info_en', 'TEXT'),
            ('club_name', 'TEXT'),
            ('workshop_zh', 'TEXT'),
            ('workshop_en', 'TEXT'),
            ('workshop_duration', 'INTEGER DEFAULT 30'),
            ('workshop_speaker', 'TEXT'),
            ('workshop_speaker_en', 'TEXT'),
        ]
        for field, dtype in new_fields:
            if field not in columns:
                cursor.execute(f"ALTER TABLE meetings ADD COLUMN {field} {dtype}")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS meeting_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            role_name TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id),
            UNIQUE(meeting_id, role_name)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            is_member BOOLEAN DEFAULT 0
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            role_name TEXT NOT NULL,
            member_name TEXT NOT NULL,
            registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id),
            UNIQUE(meeting_id, role_name)
        )""")
        cursor.execute("PRAGMA table_info(registrations)")
        reg_cols = [col[1] for col in cursor.fetchall()]
        if 'project' not in reg_cols:
            cursor.execute("ALTER TABLE registrations ADD COLUMN project TEXT DEFAULT ''")
        cursor.execute("""CREATE TABLE IF NOT EXISTS custom_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            activity_zh TEXT NOT NULL,
            activity_en TEXT,
            duration INTEGER DEFAULT 5,
            role TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )""")
        for role in DEFAULT_ROLES:
            try:
                cursor.execute("INSERT INTO roles (name) VALUES (?)", (role['name_zh'],))
            except sqlite3.IntegrityError:
                pass
        conn.commit()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_role_member(reg_dict, role_name):
    return reg_dict.get(role_name, '')

@app.route('/')
def index():
    conn = get_db_connection()
    meetings = conn.execute('SELECT * FROM meetings ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', meetings=meetings)

@app.route('/help')
def help():
    """帮助页面"""
    return render_template('help.html')

def normalize_wechat_post_text(text):
    """
    Normalize WeChat post text before parsing.
    """
    if not text:
        return ''

    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split lines that have multiple "role：name" pairs without newline separation
    # e.g., "即兴主持人：Ken Luo即兴点评官：Lavender Li" -> two lines
    # Must do this BEFORE replacing ：→: so we can anchor on Chinese colon
    role_keys_for_split = r'(即兴主持人|即兴点评官|演讲者\s*\d|点评官\s*\d|会议主席|mm|saa|timer|ah-counter|grammarian|ge|总点评官|时间官|哼唧官|哼哈官|语言官|语法官|摄影师|自由分享|嘉宾分享|成长工作坊|后备|工作坊主讲|会议主持|技术支持|后备人员|president|会长|会议经理)'
    text = re.sub(
        r'([^\n])(' + role_keys_for_split + r')[：:]',
        r'\1\n\2: ',
        text
    )
    
    # Now replace Chinese punctuation
    text = text.replace('：', ':').replace('；', ';').replace('，', ',')
    text = text.replace('（', '(').replace('）', ')')
    text = re.sub(r'[—–−]+', '-', text)
    text = re.sub(r'^[\-\*\u2022]\s*', '', text, flags=re.M)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


def parse_wechat_signup(text):
    """
    Parse WeChat group sign-up post and extract registrations.
    Supports multiple post formats, including:
    - GZ Galaxy Toastmasters meeting posts
    - Standard role: member format
    Returns: list of (role_name, member_name) tuples
    """
    registrations = []
    text = normalize_wechat_post_text(text)
    lines = text.strip().split('\n')
    
    # Initialize meeting_info dict
    meeting_info = {
        'meeting_id': '',
        'theme': '',
        'time': '',
        'address': '',
        'english_theme': '',
        'time_en': '',
        'address_en': '',
        'fee_info': '',
        'fee_info_en': '',
    }
    
    lines = text.strip().split('\n')
    
    # Step 1: Extract MEETING_ID using standard format: YYYYMMDD-ClubName-#number
    # Priority: date in text + club name from first line + #number
    date_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
    if date_match:
        year, month, day = date_match.groups()
        date_str = f"{year}{int(month):02d}{int(day):02d}"
        
        # Extract club name from first line
        club_name = 'UnknownClub'
        if lines:
            first = lines[0].strip()
            club = re.sub(r'#\s*\d+', '', first)
            club = re.sub(r'\s+', ' ', club).strip()
            parts = club.split()
            if len(parts) >= 2:
                club_name = parts[0] + parts[1]
            elif parts:
                club_name = parts[0]
        
        # Extract #number
        number_match = re.search(r'#\s*(\d+)', text)
        number = number_match.group(1) if number_match else ''
        
        # Generate standard meeting_id
        if number:
            meeting_info['meeting_id'] = f"{date_str}-{club_name}-#{number}"
        else:
            meeting_info['meeting_id'] = f"{date_str}-{club_name}"
        
        # Set date (without time yet)
        meeting_info['time'] = f"{year}/{int(month):02d}/{int(day):02d}"
        meeting_info['time_en'] = f"{year}/{int(month):02d}/{int(day):02d}"
        print(f"DEBUG: Generated meeting_id: {meeting_info['meeting_id']}")
    
    # Step 2: Extract THEME from "主题:" line
    for line in lines:
        line = line.strip()
        if line.startswith('主题:') or line.startswith('主题：'):
            theme_content = re.split(r'[：:]', line, 1)[1].strip()
            if theme_content:
                meeting_info['theme'] = theme_content
                meeting_info['english_theme'] = theme_content
                break
    
    # Step 3: Extract TIME range (19:30 ~ 21:30 or 19: 30 ~ 21: 30)
    time_match = re.search(r'(\d{1,2}:\s*\d{2})\s*[~～]\s*(\d{1,2}:\s*\d{2})', text)
    if time_match:
        start_time = time_match.group(1).replace(' ', '')
        end_time = time_match.group(2).replace(' ', '')
        if meeting_info['time']:
            meeting_info['time'] += f" ({start_time}-{end_time})"
            meeting_info['time_en'] += f" ({start_time}-{end_time})"
        else:
            meeting_info['time'] = f"{start_time}-{end_time}"
            meeting_info['time_en'] = f"{start_time}-{end_time}"
    
# Step 4: Extract ADDRESS (single line after the marker)
    # Handle both formats: "📍 会议地址：xxx" and "会议地址：xxx"
    addr_match = re.search(r'(?:📍\s*)?会议地址[：:]\s*([^\n]+)', text)
    if not addr_match:
        addr_match = re.search(r'📍\s*([^\n]+)', text)
    if addr_match:
        address = addr_match.group(1).strip()
        if address:
            meeting_info['address'] = address
            meeting_info['address_en'] = address
    
    # Role mapping from Chinese/abbreviated/English to standard DB role names (name_zh from DEFAULT_ROLES)
    role_mapping = {
        # MM
        'mm': '会议经理',
        'master of ceremonies': '会议经理',
        '主持人': '会议经理',
        'meeting manager': '会议经理',
        '会议主席': '会议经理',
        '会议经理': '会议经理',
        
        # SAA
        'saa': '接待官',
        'sergeant at arms': '接待官',
        'sargeant-at-arms': '接待官',
        '迎宾官': '接待官',
        'receptionist': '接待官',
        '会场官': '接待官',
        '后勤': '接待官',
        
        # TOM
        'tom': '总主持',
        'toastmaster': '总主持',
        'toastmaster of evening': '总主持',
        'table topics master': '总主持',
        '即兴主持': '总主持',
        '会议主持': '总主持',
        '技术支持': '总主持',
        
        # Timer
        'timer': '时间官',
        '计时官': '时间官',
        
        # GM
        'gm': '游戏官',
        'game master': '游戏官',
        '游戏官': '游戏官',
        
        # Photographer
        'photographer': '摄影师',
        'photo': '摄影师',
        '摄影师': '摄影师',
        
        # Ah-Counter
        'ah-counter': '哼哈官',
        'ah counter': '哼哈官',
        'ah': '哼哈官',
        '哼哈官': '哼哈官',
        '哼唧官': '哼哈官',
        
        # Grammarian
        'grammarian': '语法官',
        'gram': '语法官',
        '语法官': '语法官',
        '语言官': '语法官',
        
        # GE
        'ge': '总点评',
        'general evaluator': '总点评',
        '总点评': '总点评',
        
        # TTM
        'ttm': '即兴主持',
        'table topics master': '即兴主持',
        '即兴主持': '即兴主持',
        '即兴主持人': '即兴主持',
        
        # TTE
        'tte': '即兴点评',
        'table topics evaluator': '即兴点评',
        '即兴点评': '即兴点评',
        '即兴点评官': '即兴点评',
        
        # Prepared Speeches
        'speaker 1': '备稿演讲1',
        'ps1': '备稿演讲1',
        '备稿演讲1': '备稿演讲1',
        '演讲者 1': '备稿演讲1',
        'speaker 2': '备稿演讲2',
        'ps2': '备稿演讲2',
        '备稿演讲2': '备稿演讲2',
        '演讲者 2': '备稿演讲2',
        'speaker 3': '备稿演讲3',
        'ps3': '备稿演讲3',
        '备稿演讲3': '备稿演讲3',
        '演讲者 3': '备稿演讲3',
        'speaker 4': '备稿演讲4',
        'ps4': '备稿演讲4',
        '备稿演讲4': '备稿演讲4',
        '演讲者 4': '备稿演讲4',
        
        # Individual Evaluations
        'ie 1': '个评1',
        '个评1': '个评1',
        '点评官 1': '个评1',
        'ie 2': '个评2',
        '个评2': '个评2',
        '点评官 2': '个评2',
        'ie 3': '个评3',
        '个评3': '个评3',
        '点评官 3': '个评3',
        'ie 4': '个评4',
        '个评4': '个评4',
        '点评官 4': '个评4',
        
        # Others
        'president': '会长',
        '会长': '会长',
        'free sharing': '自由分享',
        '自由分享': '自由分享',
        'guest sharing': '嘉宾分享',
        '嘉宾分享': '嘉宾分享',
        'workshop': '成长工作坊',
        '成长工作坊': '成长工作坊',
        '后备': '后备人员',
        '后备人员': '后备人员',
    }
    
    # Pattern 1: Role: Name format (e.g., "MM: Guiling/Sibly")
    role_pattern = re.compile(r'^([^:：]+)[:：]\s*(.+)$')
    
    for line in lines:
        line = line.strip()
        # Remove leading numbers/bullets often found in copy-pasted lists (e.g., "1. MM: Name" or "1 MM: Name")
        cleaned_line = re.sub(r'^\d+[\.\)\-]?\s*', '', line)
        
        if not cleaned_line or cleaned_line.startswith('#') or cleaned_line.startswith('欢迎') or cleaned_line.startswith('Welcome'):
            continue
        
        # Match "Role: Name" pattern
        match = role_pattern.match(cleaned_line)
        if match:
            role_key = match.group(1).strip().lower()
            members_str = match.group(2).strip()
            
            # Skip if no members or empty/vacant
            vacant_markers = ['【空缺', '【空位', '【待定', '【后续', '空缺', '空位', 'tbd', 'vacant', 'open']
            if not members_str or any(m in members_str.lower() for m in vacant_markers):
                continue
            
            # Map role key to standard role name
            standard_role = role_mapping.get(role_key)
            
            if not standard_role:
                # Try matching each space-separated token in role_key
                for token in role_key.split():
                    if token in role_mapping:
                        standard_role = role_mapping[token]
                        break
            
            if not standard_role:
                # Try longest substring match from role_mapping keys
                best_match = None
                best_len = 0
                for key, value in role_mapping.items():
                    if key in role_key and len(key) > best_len:
                        best_match = value
                        best_len = len(key)
                if best_match:
                    standard_role = best_match
            
            if not standard_role:
                # Try to find partial match using word boundaries
                for key, value in role_mapping.items():
                    if re.search(r'\b' + re.escape(key) + r'\b', role_key):
                        standard_role = value
                        break
            
            if standard_role:
                members = [m.strip() for m in members_str.split('/') if m.strip()]
                for member in members:
                    is_guest = bool(re.search(r'[（(]\s*guest\s*[）)]', member, re.IGNORECASE))
                    if not is_guest:
                        is_guest = bool(re.search(r'[（(]\s*嘉宾\s*[）)]', member))
                    member = re.sub(r'[（()]\s*嘉宾\s*[）()]*', '', member)
                    member = re.sub(r'[（()]\s*guest\s*[）()]*', '', member, flags=re.IGNORECASE)
                    member = member.strip()
                    if member and not any(m in member.lower() for m in vacant_markers):
                        registrations.append((standard_role, member, is_guest))
    
    return meeting_info, registrations

@app.route('/meeting/create', methods=['GET', 'POST'])
def create_meeting():
    if request.method == 'POST':
        meeting_id = request.form['meeting_id']
        theme = request.form['theme']
        english_theme = request.form.get('english_theme', '')
        time = request.form['time']
        time_en = request.form.get('time_en', '')
        address = request.form.get('address', '')
        address_en = request.form.get('address_en', '')
        fee_info = request.form.get('fee_info', '')
        fee_info_en = request.form.get('fee_info_en', '')
        workshop_enabled = request.form.get('workshop_enabled') == 'on'
        workshop_speaker = request.form.get('workshop_speaker', '')
        workshop_speaker_en = request.form.get('workshop_speaker_en', '')
        workshop_zh = request.form.get('workshop_zh', '')
        workshop_en = request.form.get('workshop_en', '')
        workshop_duration = request.form.get('workshop_duration', '30')
        
        # If workshop is not enabled, clear the workshop fields
        if not workshop_enabled:
            workshop_speaker = ''
            workshop_speaker_en = ''
            workshop_zh = ''
            workshop_en = ''
            workshop_duration = '30'
        
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO meetings (meeting_id, theme, english_theme, time, time_en, address, address_en, fee_info, fee_info_en, workshop_speaker, workshop_speaker_en, workshop_zh, workshop_en, workshop_duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (meeting_id, theme, english_theme, time, time_en, address, address_en, fee_info, fee_info_en, workshop_speaker, workshop_speaker_en, workshop_zh, workshop_en, workshop_duration)
            )
            meeting_db_id = conn.execute('SELECT id FROM meetings WHERE meeting_id = ?', (meeting_id,)).fetchone()['id']
            for role in DEFAULT_ROLES:
                conn.execute(
                    "INSERT INTO meeting_roles (meeting_id, role_name) VALUES (?, ?)",
                    (meeting_db_id, role['name_zh'])
                )
            conn.commit()
            flash('会议创建成功！', 'success')
            return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
        except sqlite3.IntegrityError:
            flash('会议编号已存在！', 'danger')
        finally:
            conn.close()
    return render_template('create_meeting.html')

@app.route('/create-from-post', methods=['GET', 'POST'])
def create_from_post():
    """从帖子内容创建会议并自动报名 - 两步流程：预览 → 确认创建"""
    if request.method == 'POST':
        action = request.form.get('action', 'parse')
        
        if action == 'confirm':
            # First try session, fallback to form data
            meeting_info = session.get('preview_meeting_info', {})
            registrations = session.get('preview_registrations', [])
            
            # Also check form as fallback (for test client compatibility)
            if not meeting_info:
                meeting_info = {
                    'meeting_id': request.form.get('meeting_id', ''),
                    'theme': request.form.get('theme', ''),
                    'time': request.form.get('time', ''),
                    'address': request.form.get('address', '')
                }
                try:
                    registration_data = request.form.get('registrations', '')
                    if registration_data:
                        import ast
                        registrations = ast.literal_eval(registration_data)
                except:
                    registrations = []
            
            meeting_id = meeting_info.get('meeting_id', '') or ''
            
            if not meeting_id:
                flash('No meeting ID found! Please parse again.', 'danger')
                return redirect(url_for('create_from_post'))
            
            if not registrations:
                flash('No registrations found! Please parse again.', 'danger')
                return redirect(url_for('create_from_post'))
            
            conn = get_db_connection()
            try:
                existing = conn.execute('SELECT id FROM meetings WHERE meeting_id = ?', 
                                      (meeting_id,)).fetchone()
                if existing:
                    flash(f'会议 {meeting_id} 已存在！', 'danger')
                    return redirect(url_for('create_from_post'))
                
                conn.execute("""
                    INSERT INTO meetings (meeting_id, theme, english_theme, time, time_en, address, address_en, fee_info, fee_info_en)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    meeting_id, 
                    meeting_info.get('theme', '') or '', 
                    '',
                    meeting_info.get('time', '') or '', 
                    '',
                    meeting_info.get('address', '') or '', 
                    '', '', ''
                ))
                
                meeting_db_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
                
                for role in DEFAULT_ROLES:
                    conn.execute(
                        "INSERT INTO meeting_roles (meeting_id, role_name) VALUES (?, ?)",
                        (meeting_db_id, role['name_zh'])
                    )
                
                registered_count = 0
                skipped_roles = []
                for item in registrations:
                    if len(item) == 3:
                        role_name, member_name, is_guest = item
                    else:
                        role_name, member_name = item
                        is_guest = False
                    try:
                        role_exists = conn.execute(
                            "SELECT 1 FROM meeting_roles WHERE meeting_id = ? AND role_name = ?",
                            (meeting_db_id, role_name)
                        ).fetchone()
                        
                        if not role_exists:
                            skipped_roles.append(role_name)
                            continue
                        
                        existing_reg = conn.execute(
                            "SELECT 1 FROM registrations WHERE meeting_id = ? AND role_name = ?",
                            (meeting_db_id, role_name)
                        ).fetchone()
                        
                        if existing_reg:
                            continue
                        
                        existing_member = conn.execute('SELECT * FROM members WHERE name = ?', 
                                                    (member_name,)).fetchone()
                        is_member = 0 if is_guest else 1
                        if not existing_member:
                            conn.execute("INSERT INTO members (name, is_member) VALUES (?, ?)", 
                                        (member_name, is_member))
                        else:
                            conn.execute("UPDATE members SET is_member = ? WHERE name = ?",
                                        (is_member, member_name))
                        
                        conn.execute(
                            "INSERT INTO registrations (meeting_id, role_name, member_name) VALUES (?, ?, ?)",
                            (meeting_db_id, role_name, member_name)
                        )
                        registered_count += 1
                    except Exception as e:
                        pass
                
                conn.commit()
                
                msg = f'Meeting created! {registered_count} roles registered'
                if skipped_roles:
                    msg += f' (skipped: {", ".join(skipped_roles)})'
                flash(msg, 'success')
                return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
            
            except sqlite3.IntegrityError as e:
                flash(f'Create failed: {e}', 'danger')
            finally:
                conn.close()
            
            return redirect(url_for('create_from_post'))
        
        else:
            # Step 1: Parse the post and show preview
            post_text = request.form.get('post_text', '').strip()
            if not post_text:
                flash('请粘贴帖子内容！', 'warning')
                return redirect(url_for('create_from_post'))
            
            meeting_info, registrations = parse_wechat_signup(post_text)
            
            # Store parsed data in session for confirm step
            session['preview_meeting_info'] = meeting_info
            session['preview_registrations'] = registrations
            
            # Build parsing hints
            hints = []
            if not meeting_info.get('meeting_id'):
                hints.append('未识别到会议编号（需含 #数字 格式，如 #982）')
            if not meeting_info.get('time'):
                hints.append('未识别到日期时间（需含 "2026年5月7日" 格式）')
            if not meeting_info.get('address'):
                hints.append('未识别到会议地址（需含 "地址：xxx" 或 "📍 地址：xxx" 格式）')
            if not meeting_info.get('theme'):
                hints.append('未识别到会议主题')
            if not registrations:
                hints.append('未识别到任何角色报名信息（需含 "角色：姓名" 格式）')
            
            return render_template('create_from_post.html',
                preview=True,
                meeting_info=meeting_info,
                registrations=registrations,
                hints=hints,
                post_text=post_text)
    
    return render_template('create_from_post.html', preview=False)

@app.route('/meeting/<int:meeting_db_id>/edit', methods=['GET', 'POST'])
def edit_meeting(meeting_db_id):
    """编辑会议信息"""
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        meeting_id = request.form['meeting_id']
        theme = request.form['theme']
        english_theme = request.form.get('english_theme', '')
        time = request.form['time']
        time_en = request.form.get('time_en', '')
        address = request.form.get('address', '')
        address_en = request.form.get('address_en', '')
        fee_info = request.form.get('fee_info', '')
        fee_info_en = request.form.get('fee_info_en', '')
        workshop_enabled = request.form.get('workshop_enabled') == 'on'
        workshop_speaker = request.form.get('workshop_speaker', '')
        workshop_speaker_en = request.form.get('workshop_speaker_en', '')
        workshop_zh = request.form.get('workshop_zh', '')
        workshop_en = request.form.get('workshop_en', '')
        workshop_duration = request.form.get('workshop_duration', '30')
        
        # If workshop is not enabled, clear the workshop fields
        if not workshop_enabled:
            workshop_speaker = ''
            workshop_speaker_en = ''
            workshop_zh = ''
            workshop_en = ''
            workshop_duration = '30'
        
        conn.execute("""
            UPDATE meetings SET meeting_id = ?, theme = ?, english_theme = ?, time = ?, time_en = ?, address = ?, address_en = ?, fee_info = ?, fee_info_en = ?, workshop_speaker = ?, workshop_speaker_en = ?, workshop_zh = ?, workshop_en = ?, workshop_duration = ?
            WHERE id = ?
        """, (meeting_id, theme, english_theme, time, time_en, address, address_en, fee_info, fee_info_en, workshop_speaker, workshop_speaker_en, workshop_zh, workshop_en, workshop_duration, meeting_db_id))
        conn.commit()
        flash('会议信息已更新！', 'success')
        conn.close()
        return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
    
    conn.close()
    return render_template('edit_meeting.html', meeting=meeting)

@app.route('/meeting/<int:meeting_db_id>/export')
def export_meeting_csv(meeting_db_id):
    """导出会议报名数据为CSV"""
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    # 获取所有报名记录
    registrations = conn.execute("""
        SELECT reg.role_name, reg.member_name, reg.registration_time, m.is_member
        FROM registrations reg
        LEFT JOIN members m ON reg.member_name = m.name
        WHERE reg.meeting_id = ?
        ORDER BY reg.role_name
    """, (meeting_db_id,)).fetchall()
    conn.close()
    
    # 生成CSV
    import csv
    from flask import make_response
    
    meeting_id = meeting['meeting_id']
    meeting_theme = meeting['theme']
    meeting_time = meeting['time']
    meeting_address = meeting['address']
    
    response = make_response()
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={meeting_id}_participants.csv'
    
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 标题行
    writer.writerow(['会议编号', '会议主题', '时间', '地址', '角色', '参会人员', '类型', '报名时间'])
    
    # 数据行
    for reg in registrations:
        member_type = '会员' if reg['is_member'] else '嘉宾'
        writer.writerow([
            meeting_id,
            meeting_theme,
            meeting_time,
            meeting_address or '',
            reg['role_name'],
            reg['member_name'],
            member_type,
            reg['registration_time']
        ])
    
    response.data = output.getvalue()
    return response

@app.route('/export/all')
def export_all_meetings():
    """导出所有会议报名汇总统计CSV"""
    conn = get_db_connection()
    
    # 获取所有会议
    meetings = conn.execute('SELECT * FROM meetings ORDER BY created_at DESC').fetchall()
    
    # 获取所有报名记录
    all_regs = conn.execute("""
        SELECT reg.meeting_id, m.name, m.is_member, GROUP_CONCAT(reg.role_name) as roles
        FROM registrations reg
        LEFT JOIN members m ON reg.member_name = m.name
        GROUP BY reg.meeting_id, reg.member_name
    """).fetchall()
    conn.close()
    
    # 统计每个角色的参会次数
    role_count = {}
    for reg in all_regs:
        if reg['roles']:
            for role in reg['roles'].split(','):
                role = role.strip()
                if role not in role_count:
                    role_count[role] = set()
                if reg['name']:
                    role_count[role].add(reg['name'])
    
    # 生成CSV
    import csv
    from flask import make_response
    
    response = make_response()
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = 'attachment; filename=role_statistics.csv'
    
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 标题行
    writer.writerow(['角色', '参会次数', '参会人员列表'])
    
    # 数据行
    for role in sorted(role_count.keys()):
        members = list(role_count[role])
        writer.writerow([role, len(members), ', '.join(sorted(members))])
    
    response.data = output.getvalue()
    return response

@app.route('/meeting/<int:meeting_db_id>')
def meeting_detail(meeting_db_id):
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    lang = session.get('lang', 'zh')
    
    roles = conn.execute("""SELECT mr.role_name, r.description, reg.member_name, m.is_member, reg.project
        FROM meeting_roles mr
        LEFT JOIN registrations reg ON mr.meeting_id = reg.meeting_id AND mr.role_name = reg.role_name
        LEFT JOIN members m ON reg.member_name = m.name
        LEFT JOIN roles r ON mr.role_name = r.name
        WHERE mr.meeting_id = ?
    """, (meeting_db_id,)).fetchall()
    
    # 获取格式化的角色名、描述和是否会员专属
    roles_with_info = []
    for role in roles:
        role_name = role['role_name']
        display_name = get_role_display_name_lang(role_name, lang)
        role_desc = get_role_description(role_name, lang)
        member_only = is_member_only_role(role_name)
        
        # 检查是否有默认成员设置
        default_member = None
        for r in DEFAULT_ROLES:
            if r['name_zh'] == role_name and 'default_member' in r:
                default_member = r['default_member']
                break
        
        # 如果角色无人报名且有默认成员，则显示默认成员
        member_name = role['member_name']
        is_default_assigned = False
        if not member_name and default_member:
            member_name = default_member
            is_default_assigned = True
        
        # 默认分配的角色（如会长 Bass）默认是会员
        if is_default_assigned:
            is_member_val = True
        else:
            is_member_val = role['is_member']
        
        roles_with_info.append({
            'role_name': role_name,
            'display_name': display_name,
            'description': role_desc,
            'member_name': member_name,
            'is_member': is_member_val,
            'member_only': member_only,
            'is_default_assigned': is_default_assigned,
            'has_registration': role['member_name'] is not None,
            'project': role['project'] or ''
        })
    
    registered_members = conn.execute("""SELECT reg.member_name, m.is_member, GROUP_CONCAT(reg.role_name) as roles
        FROM registrations reg
        LEFT JOIN members m ON reg.member_name = m.name
        WHERE reg.meeting_id = ?
        GROUP BY reg.member_name
    """, (meeting_db_id,)).fetchall()
    
    # 格式化注册人员的角色显示
    formatted_members = []
    for member in registered_members:
        roles_list = member['roles'].split(',') if member['roles'] else []
        formatted_roles = ', '.join([get_role_display_name_lang(r, lang) for r in roles_list])
        formatted_members.append({
            'member_name': member['member_name'],
            'is_member': member['is_member'],
            'roles': formatted_roles
        })
    
    conn.close()
    return render_template('meeting_detail.html', meeting=meeting, roles=roles_with_info, registered_members=formatted_members)

@app.route('/meeting/<int:meeting_db_id>/update_club_name', methods=['POST'])
def update_club_name(meeting_db_id):
    club_name = request.json.get('club_name', '').strip()
    conn = get_db_connection()
    conn.execute('UPDATE meetings SET club_name = ? WHERE id = ?', (club_name, meeting_db_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'club_name': club_name})

@app.route('/meeting/<int:meeting_db_id>/poster')
def generate_agenda_poster(meeting_db_id):
    lang = request.args.get('lang', session.get('lang', 'zh'))
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        conn.close()
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
    reg_dict = {r['role_name']: r['member_name'] for r in regs}
    
    if lang == 'en' and meeting['time_en']:
        current_min = parse_meeting_start_time(meeting['time_en'])
    else:
        current_min = parse_meeting_start_time(meeting['time'])
    
    workshop_speaker = meeting['workshop_speaker'] if meeting['workshop_speaker'] else None
    workshop_zh = meeting['workshop_zh'] if meeting['workshop_zh'] else None
    workshop_en = meeting['workshop_en'] if meeting['workshop_en'] else None
    workshop_duration = int(meeting['workshop_duration']) if meeting['workshop_duration'] else 30
    
    agenda = []
    
    for phase in PHASE_CONFIG:
        phase_key = phase['key']
        templates = PHASE_TEMPLATES.get(phase_key, [])
        
        if phase_key == 'workshop':
            if workshop_speaker:
                if lang == 'en' and workshop_en:
                    workshop_activity = workshop_en
                elif lang == 'zh':
                    workshop_activity = workshop_zh if workshop_zh else ''
                else:
                    workshop_activity = f"{workshop_en if workshop_en else ''} {workshop_zh if workshop_zh else ''}"
                
                speaker_name = meeting['workshop_speaker_en'] if (lang == 'en' and meeting['workshop_speaker_en']) else workshop_speaker

                if workshop_activity:
                    workshop_activity += f" ({speaker_name})"
                else:
                    workshop_activity = f"Workshop ({speaker_name})"
                
                agenda.append({
                    "time": f"{current_min//60:02d}:{current_min%60:02d}",
                    "end_time": f"{(current_min + workshop_duration)//60:02d}:{(current_min + workshop_duration)%60:02d}",
                    "phase": "workshop",
                    "activity": workshop_activity,
                    "duration": workshop_duration,
                    "role": speaker_name
                })
                current_min += workshop_duration
            continue
        
        if phase_key == 'custom':
            custom_acts = conn.execute('SELECT * FROM custom_activities WHERE meeting_id = ? ORDER BY sort_order', (meeting_db_id,)).fetchall()
            for ca in custom_acts:
                act_name = ca['activity_en'] if (lang == 'en' and ca['activity_en']) else (ca['activity_en'] + ' ' + ca['activity_zh'] if lang == 'both' and ca['activity_en'] else ca['activity_zh'])
                role_val = ca['role'] if ca['role'] else '-'
                agenda.append({
                    "time": f"{current_min//60:02d}:{current_min%60:02d}",
                    "end_time": f"{(current_min + ca['duration'])//60:02d}:{(current_min + ca['duration'])%60:02d}",
                    "phase": "custom",
                    "activity": act_name,
                    "duration": ca['duration'],
                    "role": role_val
                })
                current_min += ca['duration']
            continue
        
        for tpl in templates:
            template_role = tpl['role']
            if '(' in template_role and ')' in template_role:
                role_name_for_lookup = template_role.split('(')[0]
            else:
                role_name_for_lookup = template_role
            
            member = get_role_member(reg_dict, role_name_for_lookup)
            if not member and tpl.get('default_member'):
                member = tpl['default_member']
            
            if lang == 'en':
                activity = tpl.get('activity_en', tpl.get('activity_zh', ''))
            else:
                activity = tpl.get('activity_zh', tpl.get('activity_en', ''))
            
            agenda.append({
                "time": f"{current_min//60:02d}:{current_min%60:02d}",
                "end_time": f"{(current_min + tpl.get('duration', 0))//60:02d}:{(current_min + tpl.get('duration', 0))%60:02d}",
                "phase": phase_key,
                "activity": activity,
                "duration": tpl.get('duration', 0),
                "role": member if member else ('TBD' if tpl.get('duration', 0) > 0 else '-')
            })
            current_min += tpl.get('duration', 0)
        
        # Speech: dynamic PS entries
        if phase_key == 'speech':
            ps_projects = {}
            for row in conn.execute('SELECT role_name, project FROM registrations WHERE meeting_id = ? AND (role_name LIKE ? OR role_name LIKE ?)',
                                   (meeting_db_id, '%备稿演讲%', '%PS%')).fetchall():
                ps_projects[row['role_name']] = row['project'] or ''
            for i in range(1, 5):
                ps_member = None
                for role_name, member in reg_dict.items():
                    if f'备稿演讲{i}' in role_name or f'PS{i}' in role_name:
                        ps_member = member
                        break
                if ps_member:
                    tom_member = None
                    for role_name, member in reg_dict.items():
                        if '总主持' in role_name or 'TOM' in role_name:
                            tom_member = member
                            break
                    if lang == 'en':
                        intro = f"Brief introduction ({tom_member or 'TOM'})"
                    elif lang == 'zh':
                        intro = f"演讲介绍（{tom_member or 'TOM'}）"
                    else:
                        intro = f"Brief introduction 演讲介绍（{tom_member or 'TOM'}）"
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "end_time": f"{(current_min + 1)//60:02d}:{(current_min + 1)%60:02d}",
                        "phase": phase_key,
                        "activity": intro,
                        "duration": 1,
                        "role": tom_member or 'TBD'
                    })
                    current_min += 1
                    proj = ps_projects.get(f'备稿演讲{i}', ps_projects.get(f'PS{i}', ''))
                    proj_str = f' {proj}' if proj else ''
                    if lang == 'en':
                        act = f"PS{i} Prepared Speech {i}{proj_str} ({ps_member})"
                    elif lang == 'zh':
                        act = f"PS{i} 备稿演讲{i}{proj_str}（{ps_member}）"
                    else:
                        act = f"PS{i} Prepared Speech 备稿演讲{i}{proj_str}（{ps_member}）"
                    duration = 7 if i < 4 else 15
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "end_time": f"{(current_min + duration)//60:02d}:{(current_min + duration)%60:02d}",
                        "phase": phase_key,
                        "activity": act,
                        "duration": duration,
                        "role": ps_member
                    })
                    current_min += duration
        
        # Evaluation: dynamic IE entries
        if phase_key == 'evaluation':
            for i in range(1, 5):
                ie_member = None
                ps_member = None
                for role_name, member in reg_dict.items():
                    if f'个评{i}' in role_name or f'IE{i}' in role_name:
                        ie_member = member
                    if f'备稿演讲{i}' in role_name or f'PS{i}' in role_name:
                        ps_member = member
                if ie_member:
                    if lang == 'en':
                        act = f"IE{i} Evaluation for {ps_member or 'Speech '+str(i)} ({ie_member})"
                    elif lang == 'zh':
                        act = f"IE{i} 点评{ps_member or '演讲'+str(i)}（{ie_member}）"
                    else:
                        act = f"IE{i} Evaluation 点评{ps_member or '演讲'+str(i)}（{ie_member}）"
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "end_time": f"{(current_min + 3)//60:02d}:{(current_min + 3)%60:02d}",
                        "phase": phase_key,
                        "activity": act,
                        "duration": 3,
                        "role": ie_member
                    })
                    current_min += 3
    
    meeting_manager_name = reg_dict.get('会议经理', '')
    
    conn.close()
    return render_template('agenda_poster.html', meeting=meeting, agenda=agenda, PHASE_CONFIG=PHASE_CONFIG, meeting_manager_name=meeting_manager_name, reg_dict=reg_dict)

@app.route('/meeting/<int:meeting_db_id>/agenda')
def generate_agenda(meeting_db_id):
    # 优先使用 Session 中的语言设置，URL 参数可选覆盖
    lang = request.args.get('lang', session.get('lang', 'zh'))
    
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
    reg_dict = {r['role_name']: r['member_name'] for r in regs}
    
    # 从会议信息中提取开始时间 - 优先使用当前语言的版本
    if lang == 'en' and meeting['time_en']:
        current_min = parse_meeting_start_time(meeting['time_en'])
    elif lang == 'both' and meeting['time_en']:
        # 中英模式：尝试解析英文时间，如果失败则用中文时间
        current_min = parse_meeting_start_time(meeting['time_en'])
        if current_min == 19 * 60 + 30:  # 如果解析失败（返回默认值）
            current_min = parse_meeting_start_time(meeting['time'])
    else:
        current_min = parse_meeting_start_time(meeting['time'])
    
    agenda = []
    
    # 获取工作坊信息
    workshop_speaker = meeting['workshop_speaker'] if meeting['workshop_speaker'] else None
    workshop_speaker_en = meeting['workshop_speaker_en'] if meeting['workshop_speaker_en'] else None
    workshop_zh = meeting['workshop_zh'] if meeting['workshop_zh'] else None
    workshop_en = meeting['workshop_en'] if meeting['workshop_en'] else None
    workshop_duration = int(meeting['workshop_duration']) if meeting['workshop_duration'] else 30
    
    for phase in PHASE_CONFIG:
        phase_key = phase['key']
        templates = PHASE_TEMPLATES.get(phase_key, [])
        
        # 在evaluation之后、closing之前插入workshop阶段
        if phase_key == 'workshop':
            # Show workshop only if speaker is filled (workshop enabled)
            if workshop_speaker:
                # 添加工作坊活动
                if lang == 'en' and workshop_en:
                    workshop_activity = workshop_en
                elif lang == 'zh':
                    workshop_activity = workshop_zh if workshop_zh else ''
                else:  # both
                    workshop_activity = f"{workshop_en if workshop_en else ''} {workshop_zh if workshop_zh else ''}"
                
                # Add speaker name to the activity
                if lang == 'en' and workshop_speaker_en:
                    speaker_name = workshop_speaker_en
                elif lang == 'zh':
                    speaker_name = workshop_speaker if workshop_speaker else ''
                else:  # both
                    speaker_name = workshop_speaker_en if workshop_speaker_en else workshop_speaker
                
                if workshop_activity:
                    workshop_activity += f" ({speaker_name})"
                else:
                    workshop_activity = f"Workshop ({speaker_name})"
                
                agenda.append({
                    "time": f"{current_min//60:02d}:{current_min%60:02d}",
                    "phase": "workshop",
                    "activity": workshop_activity,
                    "duration": workshop_duration,
                    "role": speaker_name
                })
                current_min += workshop_duration
            continue  # 跳过workshop阶段，因为它不是从模板生成的
        
        for tpl in templates:
            # Extract Chinese role name from template (e.g., "时间官(Timer)" -> "时间官")
            template_role = tpl['role']
            if '(' in template_role and ')' in template_role:
                # Format is "中文名(英文缩写)", extract the Chinese part
                role_name_for_lookup = template_role.split('(')[0]
            else:
                role_name_for_lookup = template_role
            member = get_role_member(reg_dict, role_name_for_lookup)
            
            # 处理默认成员逻辑（嘉宾分享、颁奖环节、闭幕词默认为Bass）
            if not member and tpl.get('default_member'):
                member = tpl['default_member']
            
            if lang == 'en':
                activity = tpl['activity_en']
            elif lang == 'zh':
                activity = tpl['activity_zh']
            else:
                activity = f"{tpl['activity_en']} {tpl['activity_zh']}"
            
            if member:
                activity += f" ({member})"
            elif tpl['role'] != '-' and tpl['role'] != 'All':
                activity += " (TBD)"
            
            agenda.append({
                "time": f"{current_min//60:02d}:{current_min%60:02d}",
                "phase": phase_key,
                "activity": activity,
                "duration": tpl['duration'],
                "role": member or ('' if tpl['role'] in ['-', 'All'] else 'TBD')
            })
            current_min += tpl['duration']
        
        # Speech: dynamic PS entries
        if phase_key == 'speech':
            ps_projects = {}
            for row in conn.execute('SELECT role_name, project FROM registrations WHERE meeting_id = ? AND (role_name LIKE ? OR role_name LIKE ?)',
                                   (meeting_db_id, '%备稿演讲%', '%PS%')).fetchall():
                ps_projects[row['role_name']] = row['project'] or ''
            for i in range(1, 5):
                # Find matching PS role in reg_dict - support both formats
                ps_member = None
                for role_name, member in reg_dict.items():
                    if f'备稿演讲{i}' in role_name or f'PS{i}' in role_name:
                        ps_member = member
                        break
                
                if ps_member:
                    # TOM brief introduction
                    tom_member = None
                    for role_name, member in reg_dict.items():
                        if '总主持' in role_name or 'TOM' in role_name:
                            tom_member = member
                            break
                    
                    if lang == 'en':
                        intro = f"Brief introduction ({tom_member or 'TOM'})"
                    elif lang == 'zh':
                        intro = f"演讲介绍（{tom_member or 'TOM'}）"
                    else:
                        intro = f"Brief introduction 演讲介绍（{tom_member or 'TOM'}）"
                    
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "phase": phase_key,
                        "activity": intro,
                        "duration": 1,
                        "role": tom_member or 'TBD'
                    })
                    current_min += 1
                    
                    # PS speech
                    proj = ps_projects.get(f'备稿演讲{i}', ps_projects.get(f'PS{i}', ''))
                    proj_str = f' {proj}' if proj else ''
                    if lang == 'en':
                        act = f"PS{i} Prepared Speech {i}{proj_str} ({ps_member})"
                    elif lang == 'zh':
                        act = f"PS{i} 备稿演讲{i}{proj_str}（{ps_member}）"
                    else:
                        act = f"PS{i} Prepared Speech 备稿演讲{i}{proj_str}（{ps_member}）"
                    
                    duration = 7 if i < 4 else 15  # last speech longer
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "phase": phase_key,
                        "activity": act,
                        "duration": duration,
                        "role": ps_member
                    })
                    current_min += duration
        
        if phase_key == 'custom':
            custom_acts = conn.execute('SELECT * FROM custom_activities WHERE meeting_id = ? ORDER BY sort_order', (meeting_db_id,)).fetchall()
            for ca in custom_acts:
                if lang == 'en':
                    act_name = ca['activity_en'] if ca['activity_en'] else ca['activity_zh']
                elif lang == 'zh':
                    act_name = ca['activity_zh']
                else:
                    act_name = f"{ca['activity_en'] + ' ' if ca['activity_en'] else ''}{ca['activity_zh']}"
                role_val = ca['role'] if ca['role'] else '-'
                if role_val != '-':
                    act_name += f" ({role_val})"
                agenda.append({
                    "time": f"{current_min//60:02d}:{current_min%60:02d}",
                    "phase": "custom",
                    "activity": act_name,
                    "duration": ca['duration'],
                    "role": role_val
                })
                current_min += ca['duration']
            continue
        
        # Evaluation: dynamic IE entries
        if phase_key == 'evaluation':
            for i in range(1, 5):
                # Use the exact name_zh from DEFAULT_ROLES for lookup as stored in DB
                ie_role_key = f'个评{i}'
                ie_role_alt = f'IE{i}'
                ps_role_key = f'备稿演讲{i}'
                ps_role_alt = f'PS{i}'
                
                # Find matching IE role in reg_dict
                ie_member = None
                ps_member = None
                for role_name, member in reg_dict.items():
                    if f'个评{i}' in role_name or f'IE{i}' in role_name:
                        ie_member = member
                    if f'备稿演讲{i}' in role_name or f'PS{i}' in role_name:
                        ps_member = member
                
                if ie_member:
                    if lang == 'en':
                        act = f"IE{i} Evaluation for {ps_member or 'Speech '+str(i)} ({ie_member})"
                    elif lang == 'zh':
                        act = f"IE{i} 点评{ps_member or '演讲'+str(i)}（{ie_member}）"
                    else:
                        act = f"IE{i} Evaluation 点评{ps_member or '演讲'+str(i)}（{ie_member}）"
                    
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "phase": phase_key,
                        "activity": act,
                        "duration": 3,
                        "role": ie_member
                    })
                    current_min += 3
    
    conn.close()
    return render_template('agenda.html', meeting=meeting, agenda=agenda, PHASE_CONFIG=PHASE_CONFIG, lang=lang)

@app.route('/api/meeting/<int:meeting_db_id>/custom_activities', methods=['GET'])
def get_custom_activities(meeting_db_id):
    conn = get_db_connection()
    activities = conn.execute(
        'SELECT id, activity_zh, activity_en, duration, role, sort_order FROM custom_activities WHERE meeting_id = ? ORDER BY sort_order',
        (meeting_db_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(a) for a in activities])

@app.route('/api/meeting/<int:meeting_db_id>/custom_activities', methods=['POST'])
def add_custom_activity(meeting_db_id):
    data = request.get_json()
    conn = get_db_connection()
    max_order = conn.execute('SELECT COALESCE(MAX(sort_order), -1) + 1 as next FROM custom_activities WHERE meeting_id = ?',
                            (meeting_db_id,)).fetchone()['next']
    conn.execute(
        'INSERT INTO custom_activities (meeting_id, activity_zh, activity_en, duration, role, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
        (meeting_db_id, data['activity_zh'], data.get('activity_en', ''), int(data.get('duration', 5)), data.get('role', ''), max_order)
    )
    conn.commit()
    new_id = conn.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/meeting/<int:meeting_db_id>/custom_activities/<int:activity_id>', methods=['PUT'])
def update_custom_activity(meeting_db_id, activity_id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE custom_activities SET activity_zh=?, activity_en=?, duration=?, role=? WHERE id=? AND meeting_id=?',
        (data['activity_zh'], data.get('activity_en', ''), int(data.get('duration', 5)), data.get('role', ''), activity_id, meeting_db_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/meeting/<int:meeting_db_id>/custom_activities/<int:activity_id>', methods=['DELETE'])
def delete_custom_activity(meeting_db_id, activity_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM custom_activities WHERE id=? AND meeting_id=?', (activity_id, meeting_db_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/meeting/<int:meeting_db_id>/custom_activities/reorder', methods=['PUT'])
def reorder_custom_activities(meeting_db_id):
    data = request.get_json()
    conn = get_db_connection()
    for item in data['order']:
        conn.execute('UPDATE custom_activities SET sort_order=? WHERE id=? AND meeting_id=?',
                    (item['sort_order'], item['id'], meeting_db_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/register', methods=['POST'])
def register():
    meeting_db_id = request.form['meeting_db_id']
    role_name = request.form['role_name']
    member_name = request.form['member_name']
    is_member = request.form.get('is_member', '0') == '1'
    project = request.form.get('project', '').strip()
    
    # 检查是否会员专属角色
    if is_member_only_role(role_name) and not is_member:
        flash(f'角色 {role_name} 仅限会员报名，请勾选"会员"后重新提交！', 'danger')
        return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
    
    conn = get_db_connection()
    try:
        existing_member = conn.execute('SELECT * FROM members WHERE name = ?', (member_name,)).fetchone()
        if existing_member:
            if existing_member['is_member'] != is_member:
                conn.execute("UPDATE members SET is_member = ? WHERE name = ?", (is_member, member_name))
        else:
            conn.execute("INSERT INTO members (name, is_member) VALUES (?, ?)", (member_name, is_member))
        
        existing_reg = conn.execute('SELECT * FROM registrations WHERE meeting_id = ? AND role_name = ?', 
                                  (meeting_db_id, role_name)).fetchone()
        
        if existing_reg:
            conn.execute("UPDATE registrations SET member_name = ?, project = ? WHERE meeting_id = ? AND role_name = ?",
                        (member_name, project, meeting_db_id, role_name))
        else:
            conn.execute("INSERT INTO registrations (meeting_id, role_name, member_name, project) VALUES (?, ?, ?, ?)",
                        (meeting_db_id, role_name, member_name, project))
        conn.commit()
        flash(f'成功报名角色 {role_name}！', 'success')
    except Exception as e:
        flash(f'报名失败：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))

@app.route('/api/meeting/<int:meeting_db_id>/roles')
def get_meeting_roles(meeting_db_id):
    conn = get_db_connection()
    roles = conn.execute("""SELECT mr.role_name, reg.member_name, m.is_member
        FROM meeting_roles mr
        LEFT JOIN registrations reg ON mr.meeting_id = reg.meeting_id AND mr.role_name = reg.role_name
        LEFT JOIN members m ON reg.member_name = m.name
        WHERE mr.meeting_id = ?
    """, (meeting_db_id,)).fetchall()
    conn.close()
    return jsonify([dict(role) for role in roles])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)