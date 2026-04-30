from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'meeting_manager_secret_key'
DB_PATH = 'meeting.db'

DEFAULT_ROLES = [
    '会议经理(MM)', '接待官(SAA)', '总主持(TOM)', '时间官(Timer)', 
    '游戏官(Game Master)', '摄影师(Photographer)', '总点评(GE)',
    'PS1 备稿演讲1', 'PS2 备稿演讲2', 'PS3 备稿演讲3', 'PS4 备稿演讲4',
    'IE1 个评1', 'IE2 个评2', 'IE3 个评3', 'IE4 个评4',
    '哼哈官(Ah-Counter)', '语法官(Grammarian)',
    '即兴主持(TTM)', '即兴点评(TTE)',
    '自由分享(Free Sharing)', '嘉宾分享(Guest Sharing)',
    'President'
]

PHASE_CONFIG = [
    {"key": "init", "name_zh": "签到与开场", "name_en": "Init", "color": "bg-info text-white"},
    {"key": "table_topics", "name_zh": "即兴演讲", "name_en": "Table Topics", "color": "bg-warning"},
    {"key": "speech", "name_zh": "备稿演讲", "name_en": "Prepared Speech", "color": "bg-success text-white"},
    {"key": "break", "name_zh": "中场休息", "name_en": "Break", "color": "bg-secondary text-white"},
    {"key": "evaluation", "name_zh": "点评环节", "name_en": "Evaluation", "color": "bg-primary text-white"},
    {"key": "closing", "name_zh": "闭幕总结", "name_en": "Closing", "color": "bg-dark text-white"},
]

PHASE_TEMPLATES = {
    "init": [
        {"activity_zh": "会员嘉宾签到", "activity_en": "Guest & Members Sign In", "duration": 15, "role": "接待官(SAA)"},
        {"activity_zh": "宣布开会及规则介绍", "activity_en": "Calling for the meeting & rules intro", "duration": 4, "role": "接待官(SAA)"},
        {"activity_zh": "开场致辞及嘉宾介绍", "activity_en": "Opening remarks & Guests Introduction", "duration": 5, "role": "总主持(TOM)"},
        {"activity_zh": "TOM介绍会议角色", "activity_en": "TOM's Introduction of facilitators", "duration": 2, "role": "总主持(TOM)"},
        {"activity_zh": "摄影师介绍", "activity_en": "Introduction of Photographer", "duration": 1, "role": "摄影师(Photographer)"},
        {"activity_zh": "时间官介绍", "activity_en": "Introduction of Timer", "duration": 2, "role": "时间官(Timer)"},
        {"activity_zh": "哼哈官介绍", "activity_en": "Introduction of Ah Counter", "duration": 0, "role": "哼哈官(Ah-Counter)"},
        {"activity_zh": "语法官介绍", "activity_en": "Introduction of Grammarian", "duration": 0, "role": "语法官(Grammarian)"},
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
        {"activity_zh": "最佳投票", "activity_en": "Vote for the Best", "duration": 1, "role": "总主持(TOM)"},
        {"activity_zh": "总点评报告", "activity_en": "General evaluator report", "duration": 7, "role": "总点评(GE)"},
        {"activity_zh": "嘉宾分享", "activity_en": "Guest sharing", "duration": 3, "role": "嘉宾分享(Guest Sharing)"},
        {"activity_zh": "颁奖环节", "activity_en": "Awarding time", "duration": 3, "role": "President"},
        {"activity_zh": "闭幕词", "activity_en": "Closing remarks", "duration": 2, "role": "President"},
        {"activity_zh": "角色预订", "activity_en": "Role booking", "duration": 1, "role": "会议经理(MM)"},
        {"activity_zh": "会议结束", "activity_en": "Meeting Adjourned", "duration": 0, "role": "-"},
    ]
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id TEXT UNIQUE NOT NULL,
            theme TEXT NOT NULL,
            time TEXT NOT NULL,
            address TEXT,
            fee_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
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
        for role in DEFAULT_ROLES:
            try:
                cursor.execute("INSERT INTO roles (name) VALUES (?)", (role,))
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

@app.route('/meeting/create', methods=['GET', 'POST'])
def create_meeting():
    if request.method == 'POST':
        meeting_id = request.form['meeting_id']
        theme = request.form['theme']
        time = request.form['time']
        address = request.form.get('address', '')
        fee_info = request.form.get('fee_info', '')
        
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO meetings (meeting_id, theme, time, address, fee_info) VALUES (?, ?, ?, ?, ?)",
                (meeting_id, theme, time, address, fee_info)
            )
            meeting_db_id = conn.execute('SELECT id FROM meetings WHERE meeting_id = ?', (meeting_id,)).fetchone()['id']
            for role in DEFAULT_ROLES:
                conn.execute(
                    "INSERT INTO meeting_roles (meeting_id, role_name) VALUES (?, ?)",
                    (meeting_db_id, role)
                )
            conn.commit()
            flash('会议创建成功！', 'success')
            return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
        except sqlite3.IntegrityError:
            flash('会议编号已存在！', 'danger')
        finally:
            conn.close()
    return render_template('create_meeting.html')

@app.route('/meeting/<int:meeting_db_id>')
def meeting_detail(meeting_db_id):
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    roles = conn.execute("""SELECT mr.role_name, r.description, reg.member_name, m.is_member
        FROM meeting_roles mr
        LEFT JOIN registrations reg ON mr.meeting_id = reg.meeting_id AND mr.role_name = reg.role_name
        LEFT JOIN members m ON reg.member_name = m.name
        LEFT JOIN roles r ON mr.role_name = r.name
        WHERE mr.meeting_id = ?
    """, (meeting_db_id,)).fetchall()
    
    registered_members = conn.execute("""SELECT reg.member_name, m.is_member, GROUP_CONCAT(reg.role_name) as roles
        FROM registrations reg
        LEFT JOIN members m ON reg.member_name = m.name
        WHERE reg.meeting_id = ?
        GROUP BY reg.member_name
    """, (meeting_db_id,)).fetchall()
    
    conn.close()
    return render_template('meeting_detail.html', meeting=meeting, roles=roles, registered_members=registered_members)

@app.route('/meeting/<int:meeting_db_id>/agenda')
def generate_agenda(meeting_db_id):
    lang = request.args.get('lang', 'both')
    
    conn = get_db_connection()
    meeting = conn.execute('SELECT * FROM meetings WHERE id = ?', (meeting_db_id,)).fetchone()
    if not meeting:
        flash('会议不存在！', 'danger')
        return redirect(url_for('index'))
    
    regs = conn.execute('SELECT role_name, member_name FROM registrations WHERE meeting_id = ?', (meeting_db_id,)).fetchall()
    reg_dict = {r['role_name']: r['member_name'] for r in regs}
    
    current_min = 19 * 60  # 19:00
    agenda = []
    
    for phase in PHASE_CONFIG:
        phase_key = phase['key']
        templates = PHASE_TEMPLATES.get(phase_key, [])
        
        for tpl in templates:
            member = get_role_member(reg_dict, tpl['role'])
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
            for i in range(1, 5):
                ps_role = f'PS{i} 备稿演讲{i}'
                ie_role = f'IE{i} 个评{i}'
                if ps_role in reg_dict:
                    member = reg_dict[ps_role]
                    # TOM brief introduction
                    tom_member = get_role_member(reg_dict, '总主持(TOM)')
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
                    if lang == 'en':
                        act = f"PS{i} Prepared Speech {i} ({member})"
                    elif lang == 'zh':
                        act = f"PS{i} 备稿演讲{i}（{member}）"
                    else:
                        act = f"PS{i} Prepared Speech 备稿演讲{i}（{member}）"
                    
                    duration = 7 if i < 4 else 15  # last speech longer
                    agenda.append({
                        "time": f"{current_min//60:02d}:{current_min%60:02d}",
                        "phase": phase_key,
                        "activity": act,
                        "duration": duration,
                        "role": member
                    })
                    current_min += duration
        
        # Evaluation: dynamic IE entries
        if phase_key == 'evaluation':
            for i in range(1, 5):
                ie_role = f'IE{i} 个评{i}'
                ps_role = f'PS{i} 备稿演讲{i}'
                if ie_role in reg_dict:
                    ie_member = reg_dict[ie_role]
                    ps_member = reg_dict.get(ps_role, f'Speech {i}')
                    
                    if lang == 'en':
                        act = f"IE{i} Evaluation for {ps_member} ({ie_member})"
                    elif lang == 'zh':
                        act = f"IE{i} 点评{ps_member}（{ie_member}）"
                    else:
                        act = f"IE{i} Evaluation 点评{ps_member}（{ie_member}）"
                    
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

@app.route('/register', methods=['POST'])
def register():
    meeting_db_id = request.form['meeting_db_id']
    role_name = request.form['role_name']
    member_name = request.form['member_name']
    is_member = request.form.get('is_member', '0') == '1'
    
    conn = get_db_connection()
    try:
        existing_member = conn.execute('SELECT * FROM members WHERE name = ?', (member_name,)).fetchone()
        if not existing_member:
            conn.execute("INSERT INTO members (name, is_member) VALUES (?, ?)", (member_name, is_member))
        
        existing_reg = conn.execute('SELECT * FROM registrations WHERE meeting_id = ? AND role_name = ?', 
                                  (meeting_db_id, role_name)).fetchone()
        
        if existing_reg:
            flash(f'角色 {role_name} 已被 {existing_reg["member_name"]} 报名！', 'danger')
            return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
        
        user_regs = conn.execute('SELECT * FROM registrations WHERE meeting_id = ? AND member_name = ?', 
                                (meeting_db_id, member_name)).fetchall()
        
        if user_regs:
            flash(f'您已在本次会议报名了 {user_regs[0]["role_name"]}，请勿重复报名！', 'warning')
            return redirect(url_for('meeting_detail', meeting_db_id=meeting_db_id))
        
        conn.execute("INSERT INTO registrations (meeting_id, role_name, member_name) VALUES (?, ?, ?)",
                    (meeting_db_id, role_name, member_name))
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
    app.run(host='0.0.0.0', port=8082, debug=True)