import sqlite3

conn = sqlite3.connect('farm.db')
cursor = conn.cursor()

# Check current user
cursor.execute("SELECT id, name, username FROM users WHERE username = 'arun'")
user = cursor.fetchone()
print(f"User 'arun' has ID: {user[0]}")

# Move all tasks to this user
cursor.execute("UPDATE tasks SET assigned_to = ?", (user[0],))
count = cursor.rowcount
conn.commit()

print(f"✓ Updated {count} tasks to assigned_to = {user[0]}")

# Verify
cursor.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to = ?", (user[0],))
task_count = cursor.fetchone()[0]
print(f"✓ User now has {task_count} tasks")

conn.close()
print("\n✅ Done! Refresh your page and click View Tasks")