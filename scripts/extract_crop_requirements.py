"""
Helper script to create crop requirement JSON files.
Run this to generate template files for manual data entry.
"""

import json
from pathlib import Path

# Template structure
CROP_TEMPLATE = {
    "crop_name": "",
    "scientific_name": "",
    "seasonal": False,
    "seasons": None,
    "climate_requirements": {
        "annual_precipitation_mm": {
            "S1": [None, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [None, None]
        },
        "mean_annual_temp_c": {
            "S1": [None, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [None, None]
        }
    },
    "topography_requirements": {
        "slope_pct_level1": {
            "S1": [0, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [">", None]
        }
    },
    "wetness_requirements": {
        "flooding": {
            "S1": [],
            "S2": [],
            "S3": [],
            "N": []
        },
        "drainage": {
            "S1": [],
            "S2": [],
            "S3": [],
            "N": []
        }
    },
    "physical_soil_requirements": {
        "texture": {
            "S1": [],
            "S2": [],
            "S3": [],
            "N": []
        },
        "coarse_fragments_pct": {
            "S1": [None, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [">", None]
        },
        "soil_depth_cm": {
            "S1": [">", None],
            "S2": [None, None],
            "S3": [None, None],
            "N": ["<", None]
        }
    },
    "soil_fertility_requirements": {
        "apparent_cec_cmol_kg_clay": {
            "S1": [">", None],
            "S2": [None, None],
            "S3_minus": ["<", None],
            "S3_plus": ["<", None]
        },
        "base_saturation_pct": {
            "S1": [">", None],
            "S2": [None, None],
            "S3": [None, None],
            "N": ["<", None]
        },
        "ph_h2o": {
            "S1": [None, None],
            "S2": [[None, None], [None, None]],
            "S3": [[None, None], [None, None]],
            "N": [["<", None], [">", None]]
        }
    },
    "salinity_alkalinity_requirements": {
        "ece_ds_m": {
            "S1": [None, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [">", None]
        },
        "esp_pct": {
            "S1": [None, None],
            "S2": [None, None],
            "S3": [None, None],
            "N": [">", None]
        }
    },
    "notes": ""
}

CROPS_TO_EXTRACT = [
    "Arabica Coffee",
    "Robusta Coffee",
    "Banana",
    "Cabbage",
    "Carrots",
    "Cocoa",
    "Maize",
    "Oil Palm",
    "Pineapple",
    "Sorghum",
    "Sugarcane",
    "Sweet Potato",
    "Tomato"
]

def create_template_files():
    """Create template JSON files for each crop."""
    # Get data directory
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    data_dir = project_root / "data" / "crop_requirements"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Creating template files in: {data_dir}\n")
    
    for crop_name in CROPS_TO_EXTRACT:
        filename = crop_name.lower().replace(" ", "_") + ".json"
        filepath = data_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            print(f"⏭  Skipped (already exists): {filename}")
            continue
        
        # Create template with crop name filled in
        template = CROP_TEMPLATE.copy()
        template["crop_name"] = crop_name
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"✓ Created: {filename}")
    
    print(f"\n✅ Template creation complete!")
    print(f"📝 Now fill in the values from the Extension Project PDF (Pages 55-76)")

if __name__ == "__main__":
    create_template_files()