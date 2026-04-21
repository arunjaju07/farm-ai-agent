import sqlite3

conn = sqlite3.connect('farm.db')
cursor = conn.cursor()

# Create zones table
cursor.execute('''
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    area_acres REAL,
    location_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations (id)
)
''')

conn.commit()
conn.close()

print("✅ Zones table created successfully!")