"""
View SoilWise Database Contents
Quick script to browse all tables and data
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import get_database

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def view_database():
    """Display all database contents"""
    db = get_database()

    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  🗄️  SOILWISE DATABASE VIEWER".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    print(f"\n📂 Database Location: {db.db_path}")
    print(f"📊 Database Size: {db.db_path.stat().st_size / 1024:.2f} KB\n")

    # ========== STATISTICS ==========
    print_section("📊 DATABASE STATISTICS")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title():<25} : {value:>6}")

    # ========== CROPS ==========
    print_section("🌾 CROPS")
    crops = db.get_all_crops()

    if crops:
        print(f"\n  Found {len(crops)} crops:\n")
        for i, crop in enumerate(crops, 1):
            seasonal = "🔄 Seasonal" if crop['is_seasonal'] else "📅 Perennial"
            status = crop['validation_status'].upper()
            print(f"  {i:2}. {crop['crop_name']:<20} | {seasonal:<14} | Status: {status}")

            # Show requirement count for this crop
            reqs = db.get_crop_requirements(crop['crop_id'])
            print(f"      └─ {len(reqs)} requirements")
    else:
        print("  ⚠️ No crops found in database")

    # ========== CROP REQUIREMENTS (Sample) ==========
    print_section("📋 CROP REQUIREMENTS (Sample)")

    if crops:
        # Show requirements for first crop as example
        sample_crop = crops[0]
        print(f"\n  Showing requirements for: {sample_crop['crop_name']}\n")

        reqs = db.get_crop_requirements(sample_crop['crop_id'])[:5]  # First 5

        if reqs:
            for req in reqs:
                season = f" ({req['season']})" if req['season'] else ""
                print(f"  • {req['parameter']:<20}{season}")
                print(f"    S1: {req['s1_min']} - {req['s1_max']} {req['unit']}")
                print(f"    S2: {req['s2_min']} - {req['s2_max']} {req['unit']}")
                print(f"    S3: {req['s3_min']} - {req['s3_max']} {req['unit']}")
                print()

            if len(db.get_crop_requirements(sample_crop['crop_id'])) > 5:
                print(f"  ... and {len(db.get_crop_requirements(sample_crop['crop_id'])) - 5} more requirements")
        else:
            print("  No requirements found")

    # ========== SOIL INPUTS ==========
    print_section("🌱 RECENT SOIL DATA INPUTS")

    soil_inputs = db.get_recent_soil_inputs(limit=5)

    if soil_inputs:
        print(f"\n  Found {len(soil_inputs)} recent soil inputs:\n")
        for i, soil in enumerate(soil_inputs, 1):
            location = soil.get('location', 'N/A')
            date = soil['created_at'][:16] if soil.get('created_at') else 'N/A'
            ph = soil.get('ph', 'N/A')
            temp = soil.get('temperature', 'N/A')

            print(f"  {i}. Input ID: {soil['input_id']}")
            print(f"     Location: {location} | Date: {date}")
            print(f"     pH: {ph} | Temperature: {temp}°C\n")
    else:
        print("\n  ⚠️ No soil inputs found")

    # ========== EVALUATION RESULTS ==========
    print_section("🎯 RECENT EVALUATION RESULTS")

    evaluations = db.get_evaluation_history(limit=5)

    if evaluations:
        print(f"\n  Found {len(evaluations)} recent evaluations:\n")
        for i, eval in enumerate(evaluations, 1):
            crop = eval['crop_id'].replace('_', ' ').title()
            lsi = eval['lsi']
            lsc = eval['lsc']
            classification = eval['full_classification']
            date = eval['created_at'][:16] if eval.get('created_at') else 'N/A'

            print(f"  {i}. Evaluation ID: {eval['evaluation_id']}")
            print(f"     Crop: {crop}")
            print(f"     Result: LSI={lsi:.2f}, LSC={lsc}, {classification}")
            print(f"     Date: {date}\n")
    else:
        print("\n  ⚠️ No evaluation results found")

    # ========== COMPARISONS ==========
    print_section("📊 RECENT COMPARISONS")

    comparisons = db.get_comparison_history(limit=3)

    if comparisons:
        print(f"\n  Found {len(comparisons)} recent comparisons:\n")
        for i, comp in enumerate(comparisons, 1):
            crops_compared = ", ".join([c.replace('_', ' ').title() for c in comp['crop_ids'][:3]])
            if len(comp['crop_ids']) > 3:
                crops_compared += f", ... (+{len(comp['crop_ids']) - 3} more)"
            date = comp['created_at'][:16] if comp.get('created_at') else 'N/A'

            print(f"  {i}. Comparison ID: {comp['comparison_id']}")
            print(f"     Crops: {crops_compared}")
            print(f"     Date: {date}\n")
    else:
        print("\n  ⚠️ No comparison history found")

    # ========== FOOTER ==========
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ✅ End of Database Report".ljust(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")

if __name__ == "__main__":
    try:
        view_database()
    except Exception as e:
        print(f"\n❌ Error viewing database: {e}")
        import traceback
        traceback.print_exc()