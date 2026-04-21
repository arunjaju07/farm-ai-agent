import sqlite3

conn = sqlite3.connect('farm.db')
cursor = conn.cursor()

# Check current columns
cursor.execute('PRAGMA table_info(tasks)')
columns = [col[1] for col in cursor.fetchall()]
print('Current columns:', columns)

# Add missing columns
if 'time_slot' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN time_slot TEXT DEFAULT "anytime"')
    print('✓ Added time_slot column')

if 'zone_id' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN zone_id INTEGER NULL')
    print('✓ Added zone_id column')

if 'recurring_interval_days' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN recurring_interval_days INTEGER NULL')
    print('✓ Added recurring_interval_days column')

if 'last_completed_at' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN last_completed_at TIMESTAMP NULL')
    print('✓ Added last_completed_at column')

if 'next_due_date' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN next_due_date TIMESTAMP NULL')
    print('✓ Added next_due_date column')

conn.commit()
conn.close()

print('\n✅ Database fix complete!')