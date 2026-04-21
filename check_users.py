import sqlite3

conn = sqlite3.connect("farm.db")
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, name, username, role FROM users")
users = cursor.fetchall()

print("=== USERS IN DATABASE ===)")
if users:
    for user in users:
        print(f"ID: {user[0]}, Name: {user[1]}, Username: {user[2]}, Role: {user[3]}")
else:
    print("No users found!")

# Get tasks assignment
print("\n=== TASKS ASSIGNMENT ===")
cursor.execute("SELECT id, title, assigned_to FROM tasks")
tasks = cursor.fetchall()
for task in tasks:
    print(f"Task ID: {task[0]}, Title: {task[1]}, Assigned To User ID: {task[2]}")

# Check if user 'arun' exists
cursor.execute("SELECT id FROM users WHERE username = 'arun'")
arun = cursor.fetchone()
print(f"\nUser 'arun' exists: {arun is not None}")
if arun:
    print(f"  User ID: {arun[0]}")

conn.close()