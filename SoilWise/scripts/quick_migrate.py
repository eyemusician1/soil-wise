"""
Migration script for SoilWise JSON structure
Handles the actual structure with requirement categories
"""

import json
from pathlib import Path
from database.db_manager import get_database


def parse_requirement_category(category_data, crop_id, season=None):
    """Parse a single requirement category (e.g., physical_soil_requirements)"""
    parsed = []
    
    if not isinstance(category_data, dict):
        return parsed
    
    for param_name, param_data in category_data.items():
        if not isinstance(param_data, dict):
            continue
        
        # Extract S1, S2, S3 ranges
        s1 = param_data.get('s1', param_data.get('S1', {}))
        s2 = param_data.get('s2', param_data.get('S2', {}))
        s3 = param_data.get('s3', param_data.get('S3', {}))
        
        if not isinstance(s1, dict):
            s1 = {}
        if not isinstance(s2, dict):
            s2 = {}
        if not isinstance(s3, dict):
            s3 = {}
        
        req = {
            'crop_id': crop_id,
            'parameter': param_name,
            's1_min': s1.get('min'),
            's1_max': s1.get('max'),
            's2_min': s2.get('min'),
            's2_max': s2.get('max'),
            's3_min': s3.get('min'),
            's3_max': s3.get('max'),
            'unit': param_data.get('unit', ''),
            'season': season,
            'notes': param_data.get('notes', '')
        }
        parsed.append(req)
    
    return parsed


def migrate_crop(json_file, db):
    """Migrate a single crop from JSON to database"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        crop_data = json.load(f)
    
    crop_name = crop_data.get('crop_name', json_file.stem.replace('_', ' ').title())
    crop_id = crop_name.lower().replace(' ', '_')
    
    # Check if seasonal
    is_seasonal = crop_data.get('seasonal', False)
    seasons = crop_data.get('seasons', [])
    
    print(f"\n📄 {crop_name}")
    print(f"   Seasonal: {is_seasonal}")
    if is_seasonal:
        print(f"   Seasons: {', '.join(seasons)}")
    
    # Add crop to database
    try:
        db.add_crop({
            'crop_id': crop_id,
            'crop_name': crop_name,
            'display_name': crop_name,
            'category': 'Agricultural Crop',
            'is_seasonal': 1 if is_seasonal else 0,
            'validation_status': 'draft',
            'description': crop_data.get('scientific_name', ''),
            'notes': crop_data.get('notes', '')
        })
        print(f"   ✅ Added crop")
    except Exception as e:
        print(f"   ⚠️  Crop exists")
    
    # Parse all requirement categories
    requirement_categories = [
        'topography_requirements',
        'wetness_requirements',
        'physical_soil_requirements',
        'soil_fertility_requirements',
        'salinity_alkalinity_requirements'
    ]
    
    total_reqs = 0
    
    if is_seasonal and seasons:
        # Process each season separately
        for season in seasons:
            season_reqs = 0
            for category in requirement_categories:
                category_data = crop_data.get(category, {})
                
                # For seasonal crops, check if data is nested by season
                if isinstance(category_data, dict) and season in category_data:
                    # Data is organized by season
                    parsed = parse_requirement_category(category_data[season], crop_id, season)
                else:
                    # Data is same for all seasons
                    parsed = parse_requirement_category(category_data, crop_id, season)
                
                for req in parsed:
                    try:
                        db.add_crop_requirement(req)
                        season_reqs += 1
                    except Exception:
                        pass
            
            print(f"   ✅ {season}: {season_reqs} requirements")
            total_reqs += season_reqs
    else:
        # Non-seasonal crop
        for category in requirement_categories:
            category_data = crop_data.get(category, {})
            parsed = parse_requirement_category(category_data, crop_id, None)
            
            for req in parsed:
                try:
                    db.add_crop_requirement(req)
                    total_reqs += 1
                except Exception:
                    pass
        
        print(f"   ✅ Total requirements: {total_reqs}")
    
    return total_reqs


def quick_migrate():
    """Main migration function"""
    
    # Find crop directory
    crop_dir = Path(__file__).parent.parent / "data" / "crop_requirements"
    
    print("=" * 70)
    print("🌱 SOILWISE DATABASE MIGRATION")
    print("=" * 70)
    print(f"📂 Crop directory: {crop_dir}")
    
    if not crop_dir.exists():
        print(f"❌ Directory not found!")
        return
    
    db = get_database()
    json_files = sorted(crop_dir.glob("*.json"))
    
    print(f"📂 Found {len(json_files)} crop files")
    
    total_requirements = 0
    success_count = 0
    
    for json_file in json_files:
        try:
            req_count = migrate_crop(json_file, db)
            total_requirements += req_count
            success_count += 1
        except Exception as e:
            print(f"\n❌ Error processing {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Show statistics
    stats = db.get_stats()
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print(f"📊 Crops migrated: {success_count}/{len(json_files)}")
    print(f"📊 Total crops in DB: {stats['total_crops']}")
    print(f"📊 Total requirements: {total_requirements}")
    print(f"💾 Database location: {db.db_path}")
    print("=" * 70)
    
    # Backup the database
    print("\n💾 Creating backup...")
    backup_path = db.backup_database()
    print(f"✅ Backup saved: {backup_path}")


if __name__ == "__main__":
    quick_migrate()
