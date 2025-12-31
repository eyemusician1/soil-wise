"""
Migration script to convert JSON crop requirements to SQLite database
Run this once to populate the database from existing JSON files
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager, get_database


def migrate_crop_from_json(json_path: Path, db: 'DatabaseManager'):
    """Migrate a single crop from JSON to database"""
    
    print(f"\n📄 Processing: {json_path.name}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        crop_data = json.load(f)
    
    # Extract crop info
    crop_name = crop_data.get('crop_name', json_path.stem)
    crop_id = crop_name.lower().replace(' ', '_')
    
    # Determine if seasonal
    seasonal_crops = {'cabbage', 'carrots', 'maize', 'sorghum', 'sugarcane', 'sweet_potato', 'tomato'}
    is_seasonal = 1 if crop_id in seasonal_crops else 0
    
    # Add crop to database
    try:
        db.add_crop({
            'crop_id': crop_id,
            'crop_name': crop_name,
            'display_name': crop_data.get('display_name', crop_name),
            'category': crop_data.get('category', 'Unknown'),
            'is_seasonal': is_seasonal,
            'validation_status': 'draft',  # Mark as draft initially
            'description': crop_data.get('description', ''),
            'notes': f"Migrated from {json_path.name}"
        })
        print(f"  ✅ Added crop: {crop_name}")
    except Exception as e:
        print(f"  ⚠️  Crop already exists or error: {e}")
    
    # Migrate requirements
    requirements = crop_data.get('requirements', {})
    req_count = 0
    
    for param_name, param_data in requirements.items():
        # Handle both seasonal and non-seasonal requirements
        if isinstance(param_data, dict) and 'january_april' in param_data:
            # Seasonal crop - process each season
            for season, season_data in param_data.items():
                try:
                    db.add_crop_requirement({
                        'crop_id': crop_id,
                        'parameter': param_name,
                        's1_min': season_data.get('s1', {}).get('min'),
                        's1_max': season_data.get('s1', {}).get('max'),
                        's2_min': season_data.get('s2', {}).get('min'),
                        's2_max': season_data.get('s2', {}).get('max'),
                        's3_min': season_data.get('s3', {}).get('min'),
                        's3_max': season_data.get('s3', {}).get('max'),
                        'unit': season_data.get('unit', ''),
                        'season': season,
                        'notes': season_data.get('notes', '')
                    })
                    req_count += 1
                except Exception as e:
                    print(f"  ⚠️  Error adding {param_name} ({season}): {e}")
        else:
            # Non-seasonal crop
            try:
                db.add_crop_requirement({
                    'crop_id': crop_id,
                    'parameter': param_name,
                    's1_min': param_data.get('s1', {}).get('min'),
                    's1_max': param_data.get('s1', {}).get('max'),
                    's2_min': param_data.get('s2', {}).get('min'),
                    's2_max': param_data.get('s2', {}).get('max'),
                    's3_min': param_data.get('s3', {}).get('min'),
                    's3_max': param_data.get('s3', {}).get('max'),
                    'unit': param_data.get('unit', ''),
                    'season': None,
                    'notes': param_data.get('notes', '')
                })
                req_count += 1
            except Exception as e:
                print(f"  ⚠️  Error adding {param_name}: {e}")
    
    print(f"  ✅ Added {req_count} requirements")
    return True


def migrate_all_crops():
    """Migrate all crop JSON files to database"""
    
    print("=" * 70)
    print("🌱 SOILWISE - JSON TO DATABASE MIGRATION")
    print("=" * 70)
    
    # Get database instance
    db = get_database()
    
    # Find crop requirements directory - FIXED PATH
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / "data" / "crop_requirements",  # SoilWise/data/crop_requirements
        Path.cwd() / "data" / "crop_requirements",  # Current directory
        Path.cwd() / "SoilWise" / "data" / "crop_requirements",  # If running from parent
    ]
    
    crop_dir = None
    for path in possible_paths:
        if path.exists():
            crop_dir = path
            break
    
    if crop_dir is None:
        print(f"❌ Error: Crop requirements directory not found!")
        print(f"   Searched in:")
        for path in possible_paths:
            print(f"   - {path}")
        print(f"\n💡 Current directory: {Path.cwd()}")
        print(f"💡 Script location: {Path(__file__).parent}")
        return False
    
    # Get all JSON files
    json_files = list(crop_dir.glob("*.json"))
    
    if not json_files:
        print(f"❌ Error: No JSON files found in {crop_dir}")
        return False
    
    print(f"\n📂 Found {len(json_files)} crop files in: {crop_dir}")
    print(f"📂 Database location: {db.db_path}")
    
    # Migrate each crop
    success_count = 0
    for json_file in sorted(json_files):
        try:
            if migrate_crop_from_json(json_file, db):
                success_count += 1
        except Exception as e:
            print(f"  ❌ Failed to migrate {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Show statistics
    print("\n" + "=" * 70)
    print("📊 MIGRATION SUMMARY")
    print("=" * 70)
    
    stats = db.get_stats()
    print(f"✅ Successfully migrated: {success_count}/{len(json_files)} crops")
    print(f"📈 Database Stats:")
    print(f"   - Total crops: {stats['total_crops']}")
    print(f"   - Validated crops: {stats['validated_crops']}")
    print(f"   - Soil inputs: {stats['soil_inputs']}")
    print(f"   - Evaluations: {stats['evaluations']}")
    print(f"   - Comparisons: {stats['comparisons']}")
    
    print("\n✅ Migration complete!")
    print(f"💾 Database saved to: {db.db_path}")
    
    return True



if __name__ == "__main__":
    migrate_all_crops()
