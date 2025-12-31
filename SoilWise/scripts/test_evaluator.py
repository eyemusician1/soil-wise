"""
Test that the evaluator works with database
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base.evaluation import SuitabilityEvaluator
from database.db_manager import get_database

print("=" * 70)
print("🧪 TESTING DATABASE INTEGRATION")
print("=" * 70)

# Check database
db = get_database()
stats = db.get_stats()
print(f"\n📊 Database has {stats['total_crops']} crops")

# Initialize evaluator with database
print("\n🔄 Loading evaluator with database...")
evaluator = SuitabilityEvaluator(use_database=True)

print(f"\n✅ Evaluator loaded {len(evaluator.crops)} crops")
print("\n📋 Available crops:")
for crop_name in sorted(evaluator.crops.keys()):
    crop_data = evaluator.crops[crop_name]
    is_seasonal = crop_data.get('is_seasonal', False)
    status = "Seasonal" if is_seasonal else "Perennial"
    print(f"   - {crop_name} ({status})")

# Test evaluation
print("\n🧪 Testing evaluation for Cabbage...")

# Test evaluation
print("\n🧪 Testing evaluation for Cabbage...")

# Test evaluation with CORRECT categorical values
print("\n🧪 Testing evaluation for Cabbage...")

test_soil = {
    'ph': 6.5,
    'temperature': 20,  # Better temp for cabbage
    'precipitation': 1200,
    'texture': 'L',  # Loam - S1_0
    'drainage': 'good',  # S1_0
    'flooding': 'Fo',  # S1_0 (no flooding)
    'soil_depth': 100,  # S1_0 (>75cm)
    'gravel_content': 5,  # S1_1 (3-10%)
    'erosion': 'none',
    'slope_percent': 5,
    'electrical_conductivity': 2,
    'organic_carbon': 2.5,
    'cec': 20,
    'base_saturation': 70
}



try:
    result = evaluator.evaluate_suitability(
        soil_data=test_soil,
        crop_name='Cabbage',
        season='january_april'
    )
    
    print(f"\n✅ Evaluation Result:")
    print(f"   Crop: {result['crop_name']}")
    print(f"   LSI: {result['lsi']:.2f}")
    print(f"   Classification: {result['full_classification']}")
    print(f"   LSC: {result['lsc']}")
    
except Exception as e:
    print(f"\n❌ Evaluation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Database integration test complete!")
print("=" * 70)
