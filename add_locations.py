import requests
import json

locations = [
    # Ramanjapur
    {"name": "8 Acre", "area_acres": 8.0, "region": "Ramanjapur"},
    {"name": "3 Acre", "area_acres": 3.0, "region": "Ramanjapur"},
    
    # Maharashtra
    {"name": "7 Acre", "area_acres": 7.0, "region": "Maharashtra"},
    {"name": "15 Acre", "area_acres": 15.0, "region": "Maharashtra"},
    {"name": "6 Acre", "area_acres": 6.0, "region": "Maharashtra"},
    {"name": "3 Acre", "area_acres": 3.0, "region": "Maharashtra"},
    {"name": "NGP Section", "area_acres": 0.0, "region": "Maharashtra"},  # Area unknown
    {"name": "9 Acre", "area_acres": 9.0, "region": "Maharashtra"},
    {"name": "3 Acre Kua", "area_acres": 3.0, "region": "Maharashtra"},
]

url = "http://localhost:8000/locations/add"

for loc in locations:
    response = requests.post(url, json=loc)
    print(f"Added: {loc['name']} - {response.status_code}")
    if response.status_code == 200:
        print(f"  Response: {response.json()}")
    else:
        print(f"  Error: {response.text}")
    print()