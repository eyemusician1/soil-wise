"""
Universal migration script that handles both JSON formats
"""

import json
from pathlib import Path
from database.db_manager import get_database


def parse_category_format(crop_data, crop_id):
    """Parse format with topography_requirements, wetness_requirements, etc."""
    parsed = []
    
    categories = [
        'topography_requirements',
        'wetness_requirements',
        'physical_soil_requirements',
        'soil_fertility_requirements',
        'salinity_alkalinity_requirements'
    ]
    
    is_seasonal = crop_data.get('seasonal', False)
    seasons = crop_data.get('seasons', [])
    
    if is_seasonal and seasons:
        # Seasonal crop
        for season in seasons:
            for category in categories:
                category_data = crop_data.get(category, {})
                
                if isinstance(category_data, dict) and season in category_data:
                    # Data nested by season
                    season_data = category_data[season]
                else:
                    # Data same for all seasons
                    season_data = category_data
                
                parsed.extend(parse_requirement_params(season_data, crop_id, season))
    else:
        # Non-seasonal
        for category in categories:
            category_data = crop_data.get(category, {})
            parsed.extend(parse_requirement_params(category_data, crop_id, None))
    
    return parsed


def parse_requirements_format(crop_data, crop_id):
    """Parse format with single 'requirements' key"""
    parsed = []
    requirements = crop_data.get('requirements', {})
    
    is_seasonal = crop_data.get('seasonal', False)
    seasons = crop_data.get('seasons', [])
    
    if is_seasonal and seasons:
        # Check if requirements are nested by season
        for param_name, param_data in requirements.items():
            if isinstance(param_data, dict):
                # Check if it has season keys
                has_seasons = any(s in param_data for s in seasons)
                
                if has_seasons:
                    # Seasonal structure
                    for season in seasons:
                        if season in param_data:
                            req = extract_requirement(crop_id, param_name, param_data[season], season)
                            if req:
                                parsed.append(req)
                else:
                    # Same for all seasons - duplicate for each
                    for season in seasons:
                        req = extract_requirement(crop_id, param_name, param_data, season)
                        if req:
                            parsed.append(req)
    else:
        # Non-seasonal
        for param_name, param_data in requirements.items():
            if isinstance(param_data, dict):
                req = extract_requirement(crop_id, param_name, param_data, None)
                if req:
                    parsed.append(req)
    
    return parsed


def parse_requirement_params(category_data, crop_id, season):
    """Parse individual parameters in a category"""
    parsed = []
    
    if not isinstance(category_data, dict):
        return parsed
    
    for param_name, param_data in category_data.items():
        if isinstance(param_data, dict):
            req = extract_requirement(crop_id, param_name, param_data, season)
            if req:
                parsed.append(req)
    
    return parsed


def extract_requirement(crop_id, param_name, data, season):
    """Extract S1, S2, S3 from parameter data"""
    if not isinstance(data, dict):
        return None
    
    s1 = data.get('s1', data.get('S1', {}))
    s2 = data.get('s2', data.get('S2', {}))
    s3 = data.get('s3', data.get('S3', {}))
    
    if not isinstance(s1, dict):
        s1 = {}
    if not isinstance(s2, dict):
        s2 = {}
    if not isinstance(s3, dict):
        s3 = {}
    
    return {
        'crop_id': crop_id,
        'parameter': param_name,
        's1_min': s1.get('min'),
        's1_max': s1.get('max'),
        's2_min': s2.get('min'),
        's2_max': s2.get('max'),
        's3_min': s3.get('min'),
        's3_max': s3.get('max'),
        'unit': data.get('unit', ''),
        'season': season,
        'notes': data.get('notes', '')
    }


def migrate_crop(json_file, db):
    """Migrate a crop file (handles both formats)"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        crop_data = json.load(f)
    
    crop_name = crop_data.get('crop_name', json_file.stem.replace('_', ' ').title())
    crop_id = crop_name.lower().replace(' ', '_')
    
    is_seasonal = crop_data.get('seasonal', False)
    seasons = crop_data.get('seasons', [])
    
    print(f"\n📄 {crop_name}")
    print(f"   Seasonal: {is_seasonal}")
    
    # Add crop
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
    
    # Detect format and parse
    has_categories = any(k in crop_data for k in [
        'topography_requirements', 'wetness_requirements', 
        'physical_soil_requirements', 'soil_fertility_requirements',
        'salinity_alkalinity_requirements'
    ])
    
    if has_categories:
        print(f"   📋 Format: Category-based")
        parsed_reqs = parse_category_format(crop_data, crop_id)
    else:
        print(f"   📋 Format: Requirements-based")
        parsed_reqs = parse_requirements_format(crop_data, crop_id)
    
    # Add requirements to database
    req_count = 0
    for req in parsed_reqs:
        try:
            db.add_crop_requirement(req)
            req_count += 1
        except Exception:
            pass  # Ignore duplicates
    
    print(f"   ✅ Added {req_count} requirements")
    return req_count


def migrate_all():
    """Main migration function"""
    
    crop_dir = Path(__file__).parent.parent / "data" / "crop_requirements"
    
    print("=" * 70)
    print("🌱 UNIVERSAL SOILWISE MIGRATION")
    print("=" * 70)
    print(f"📂 Directory: {crop_dir}\n")
    
    if not crop_dir.exists():
        print("❌ Directory not found!")
        return
    
    db = get_database()
    json_files = sorted(crop_dir.glob("*.json"))
    
    print(f"Found {len(json_files)} crop files\n")
    
    total_reqs = 0
    success = 0
    
    for json_file in json_files:
        try:
            req_count = migrate_crop(json_file, db)
            total_reqs += req_count
            success += 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    stats = db.get_stats()
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print(f"📊 Migrated: {success}/{len(json_files)}")
    print(f"📊 Total crops: {stats['total_crops']}")
    print(f"📊 Total requirements: {total_reqs}")
    print(f"💾 Database: {db.db_path}")
    print("=" * 70)


if __name__ == "__main__":
    migrate_all()
