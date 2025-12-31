"""
Debug script to check JSON structure
"""

import json
from pathlib import Path

# Check one crop file
crop_file = Path("../data/crop_requirements/cabbage.json")

print("📄 Checking cabbage.json structure...\n")

with open(crop_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Top-level keys:")
for key in data.keys():
    print(f"  - {key}")

print("\nRequirements structure:")
requirements = data.get('requirements', {})
print(f"  Total parameters: {len(requirements)}")

# Check first requirement
if requirements:
    first_param = list(requirements.keys())[0]
    first_data = requirements[first_param]
    print(f"\n  First parameter: {first_param}")
    print(f"  Data type: {type(first_data)}")
    print(f"  Content preview:")
    print(f"    {str(first_data)[:200]}")
