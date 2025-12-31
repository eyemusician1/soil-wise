"""
Check why some crops didn't get requirements
"""

import json
from pathlib import Path

crops_with_zero = ['maize.json', 'oil_palm.json', 'pineapple.json', 
                   'sorghum.json', 'sugarcane.json', 'sweet_potato.json', 
                   'tomato.json']

crop_dir = Path(__file__).parent.parent / "data" / "crop_requirements"

print("Checking crops with 0 requirements...\n")

for crop_file in crops_with_zero:
    file_path = crop_dir / crop_file
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"📄 {crop_file}")
        print(f"   Keys: {list(data.keys())[:5]}...")
        
        # Check requirement categories
        categories = [
            'topography_requirements',
            'wetness_requirements',
            'physical_soil_requirements',
            'soil_fertility_requirements',
            'salinity_alkalinity_requirements'
        ]
        
        for cat in categories:
            if cat in data:
                cat_data = data[cat]
                if isinstance(cat_data, dict):
                    print(f"   ✅ {cat}: {len(cat_data)} params")
                else:
                    print(f"   ⚠️  {cat}: {type(cat_data)}")
            else:
                print(f"   ❌ {cat}: MISSING")
        print()
