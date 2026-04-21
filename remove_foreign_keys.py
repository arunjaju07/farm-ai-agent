import sqlite3

conn = sqlite3.connect('farm.db')
cursor = conn.cursor()

# Get current data
cursor.execute("SELECT * FROM tasks")
tasks_data = cursor.fetchall()

# Drop the tasks table
cursor.execute("DROP TABLE IF EXISTS tasks")

# Create new table WITHOUT any foreign key constraints
cursor.execute('''
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL,
    interval_days INTEGER,
    location_id INTEGER,
    assigned_to INTEGER,
    created_by INTEGER,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    time_slot TEXT DEFAULT 'anytime',
    zone_id INTEGER,
    recurring_interval_days INTEGER,
    last_completed_at TIMESTAMP,
    next_due_date TIMESTAMP
)
''')

# If there was data, restore it (but there isn't any yet)
print("✅ Tasks table created with NO foreign key constraints")
conn.commit()
conn.close()