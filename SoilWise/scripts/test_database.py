"""
Test database functionality
"""

from database.db_manager import get_database

db = get_database()

# Show statistics
print("\n📊 Database Statistics:")
stats = db.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

# List all crops
print("\n🌱 Available Crops:")
crops = db.get_all_crops()
for crop in crops:
    status = crop['validation_status']
    seasonal = "Seasonal" if crop['is_seasonal'] else "Perennial"
    print(f"   - {crop['crop_name']} ({seasonal}, {status})")

# Test getting requirements for a crop
print("\n📋 Cabbage Requirements:")
reqs = db.get_crop_requirements('cabbage', season='january_april')
for req in reqs[:3]:  # Show first 3
    print(f"   - {req['parameter']}: S1=[{req['s1_min']}-{req['s1_max']}]")
