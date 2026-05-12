import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('meeting.db')

# Fix meeting 23 - all should be Member (is_member=1) except Doris who is already Member
# Doris Huang (id=37) stays as is_member=1
# All others in meeting 23 should be is_member=1

# First, let's see what names are in meeting 23 that should be members
guest_names = ['Christina Fang', 'Coco Chen', 'Scott Peng', 'Mei', 'Tony', 
               'Alex Lee', 'Ken Luo', 'Lavender Li', 'Rocky Jiang', 
               'Joyce Chen', 'Rebecca Fu', 'Dom Zhu']

for name in guest_names:
    conn.execute("UPDATE members SET is_member = 1 WHERE name = ?", (name,))

conn.commit()

# Verify
print("Updated members:")
for name in guest_names + ['Doris Huang']:
    row = conn.execute("SELECT id, name, is_member FROM members WHERE name = ?", (name,)).fetchone()
    if row:
        tag = 'Member' if row[2] else 'Guest'
        print(f"  {row[1]} -> {tag}")

conn.close()
print("\nDone! All meeting 23 members should now show as Member.")