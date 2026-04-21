import requests

# Sample tasks based on your farm requirements
tasks = [
    {
        "title": "Release Water - 8 Acre",
        "description": "Release water to 8 Acre section",
        "task_type": "daily",
        "location_id": 1,  # 8 Acre
        "assigned_to": 1,  # Arun (admin for now)
        "created_by": 1
    },
    {
        "title": "Check Water Flow - NGP Section",
        "description": "Inspect water flow and pressure",
        "task_type": "daily",
        "location_id": 6,  # NGP Section
        "assigned_to": 1,
        "created_by": 1
    },
    {
        "title": "Apply DAP Fertilizer",
        "description": "Apply DAP to 15 Acre section",
        "task_type": "interval",
        "interval_days": 30,
        "location_id": 3,  # 15 Acre
        "assigned_to": 1,
        "created_by": 1
    },
    {
        "title": "Check Leakage - 3 Acre (Ramanjapur)",
        "description": "Inspect pipes for any leakage",
        "task_type": "manual",
        "location_id": 2,  # 3 Acre Ramanjapur
        "assigned_to": 1,
        "created_by": 1
    },
    {
        "title": "Clean Solar Panels",
        "description": "Clean all solar panels at pump house",
        "task_type": "interval",
        "interval_days": 15,
        "location_id": 1,
        "assigned_to": 1,
        "created_by": 1
    }
]

url = "http://localhost:8000/tasks/create"

for task in tasks:
    response = requests.post(url, json=task)
    print(f"Added: {task['title']} - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Task ID: {response.json()['task_id']}")
    else:
        print(f"  ✗ Error: {response.text}")
    print()