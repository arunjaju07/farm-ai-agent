import sqlite3

conn = sqlite3.connect('farm.db')
cursor = conn.cursor()

# Drop old table
cursor.execute('DROP TABLE IF EXISTS tasks')

# Create new table without foreign key constraint
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

conn.commit()
conn.close()
print('✅ Tasks table recreated successfully')