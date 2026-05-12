import sys, os
os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, '.')

from app import PHASE_TEMPLATES

out_lines = []
for phase_key, templates in PHASE_TEMPLATES.items():
    for tpl in templates:
        role = tpl.get('role', '')
        if '时间官' in role or 'Timer' in role:
            out_lines.append(f"Phase {phase_key}: role='{role}'")
            out_lines.append(f"  Length: {len(role)}")
            out_lines.append(f"  Contains '(' : {'(' in role}")
            out_lines.append(f"  Contains ')' : {')' in role}")
            if '(' in role and ')' in role:
                try:
                    open_idx = role.index('(')
                    close_idx = role.index(')')
                    chinese = role[:open_idx]
                    abbrev = role[open_idx+1:close_idx]
                    out_lines.append(f"  Chinese part: '{chinese}' (len={len(chinese)})")
                    out_lines.append(f"  Abbrev part: '{abbrev}' (len={len(abbrev)})")
                except Exception as e:
                    out_lines.append(f"  Error extracting: {e}")
            out_lines.append("")

with open('C:/Users/v-jaggerzhang/Downloads/opencodeProj/meeting_manager/phase_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print("Written to phase_check.txt")