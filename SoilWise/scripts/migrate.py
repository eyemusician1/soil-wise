"""
Simple script to run database migration
"""

from database.migrate_json_to_db import migrate_all_crops

if __name__ == "__main__":
    print("\n🚀 Starting SoilWise Data Migration...")
    print("This will import all crop data from JSON into SQLite database\n")
    
    try:
        migrate_all_crops()
        print("\n✅ All done! Your database is ready to use.")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
