import re, sys
sys.stdout.reconfigure(encoding='utf-8')
# Test the regex on the actual text
text = 'Doris Huang（嘉宾）'
print('Input:', repr(text))

is_guest = bool(re.search(r'[（(]\s*guest\s*[）)]', text, re.IGNORECASE))
print('Match (guest):', is_guest)

is_guest2 = bool(re.search(r'[（(]\s*嘉宾\s*[）)]', text))
print('Match (嘉宾):', is_guest2)

cleaned = re.sub(r'[（(]\s*嘉宾\s*[）)]', '', text)
cleaned = re.sub(r'[（(]\s*guest\s*[）)]', '', cleaned, flags=re.IGNORECASE)
print('Cleaned:', repr(cleaned))

# Try full-width parentheses
is_guest3 = '（' in text and '嘉宾' in text
print('Full-width check:', is_guest3)

cleaned2 = re.sub(r'[（()]\s*嘉宾\s*[）()]*', '', text)
print('Full-width clean:', repr(cleaned2))