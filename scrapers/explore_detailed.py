import json

with open("data/raw/detailed/NRL_detailed_match_data_2024.json") as f:
    data = json.load(f)

# See top level structure
print(type(data))
print(data.keys() if isinstance(data, dict) else f"List of {len(data)} items")

# Peek at first item
import pprint
if isinstance(data, list):
    pprint.pprint(data[0])
elif isinstance(data, dict):
    first_key = list(data.keys())[0]
    print(f"\nFirst key: {first_key}")
    pprint.pprint(data[first_key] if not isinstance(data[first_key], list) else data[first_key][0])