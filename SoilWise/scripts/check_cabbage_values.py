"""
Check what exact values Cabbage expects
"""

import json
from pathlib import Path

crop_dir = Path(__file__).parent.parent / "data" / "crop_requirements"
cabbage_file = crop_dir / "cabbage.json"

with open(cabbage_file, 'r') as f:
    data = json.load(f)

print("=" * 70)
print("🥬 CABBAGE REQUIREMENTS - january_april")
print("=" * 70)

# Check physical requirements
print("\n📋 Physical Soil Requirements:")
phys = data.get('physical_soil_requirements', {})
for param, values in phys.items():
    print(f"\n  {param}:")
    if isinstance(values, dict):
        for key, val in values.items():
            print(f"    {key}: {val}")

# Check wetness requirements
print("\n💧 Wetness Requirements:")
wet = data.get('wetness_requirements', {})
for param, values in wet.items():
    print(f"\n  {param}:")
    if isinstance(values, dict):
        for key, val in values.items():
            print(f"    {key}: {val}")

# Check climate
print("\n🌤️ Climate Requirements:")
climate = data.get('climate_requirements', {})
if 'january_april' in climate:
    print("  (Seasonal structure detected)")
    for param, values in climate['january_april'].items():
        print(f"\n  {param}:")
        if isinstance(values, dict):
            for key, val in values.items():
                print(f"    {key}: {val}")

print("\n" + "=" * 70)
