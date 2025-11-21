"""
Simple Banana Test Script
Run this from your project root: python test_banana_simple.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("🍌 BANANA EVALUATION TEST")
print("="*80)

# Step 1: Import
print("\n📦 Step 1: Importing modules...")
try:
    from knowledge_base.evaluation import SuitabilityEvaluator
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Step 2: Initialize
print("\n🔧 Step 2: Initializing evaluator...")
try:
    evaluator = SuitabilityEvaluator()
    crops = evaluator.get_available_crops()
    print(f"✅ Evaluator initialized")
    print(f"📋 Available crops: {crops}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Prepare test data
print("\n📊 Step 3: Preparing Brgy. Gacap test data...")
test_data = {
    # Climate (from Escomen et al. Tables 2-4)
    'temperature': 22.29,
    'rainfall': 2651.54,
    
    # Topography
    'slope': 1.67,
    
    # Wetness
    'drainage': 'good',
    'flooding': 'Fo',
    
    # Physical Soil (from Table 6)
    'texture': 'CL',
    'soil_depth': 138,
    'coarse_fragments': 0,
    'caco3': 0,
    'gypsum': 0,
    
    # Soil Fertility (Ap horizon)
    'ph': 6.20,
    'organic_carbon': 1.90,
    'base_saturation': 36.03,
    'cec': 81.34,
    
    # Salinity
    'ec': 0.12,
    'esp': 0.09,
}

print("✅ Test data prepared")

# Step 4: Run evaluation
print("\n🔬 Step 4: Running evaluation...")
try:
    result = evaluator.evaluate_suitability(
        soil_data=test_data,
        crop_name="Banana"
    )
    print("✅ Evaluation complete")
except Exception as e:
    print(f"❌ Evaluation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Display results
print("\n" + "="*80)
print("📈 RESULTS")
print("="*80)

print(f"\n🍌 Crop: {result['crop_name']}")
print(f"📊 LSI: {result['lsi']:.2f}")
print(f"🏆 Classification: {result['full_classification']}")
print(f"⚠️  Limiting Factors: {result['limiting_factors'] or 'None'}")

# Classification
if result['lsc'] == 'S1':
    print(f"\n🟢 HIGHLY SUITABLE")
elif result['lsc'] == 'S2':
    print(f"\n🟡 MODERATELY SUITABLE")
elif result['lsc'] == 'S3':
    print(f"\n🟠 MARGINALLY SUITABLE")
else:
    print(f"\n🔴 NOT SUITABLE")

# Parameter details
print(f"\n📋 Parameter Ratings:")
print(f"{'Parameter':<20} {'Value':<12} {'Rating':<8} {'Class'}")
print("-" * 60)

for param, (rating, classification, subclass) in result['parameter_ratings'].items():
    value = test_data.get(param, 'N/A')
    print(f"{param:<20} {str(value):<12} {rating:<8.2f} {classification}{subclass}")

# Comparison with paper
print(f"\n" + "="*80)
print("✅ VALIDATION")
print("="*80)

expected_lsi = 90.25
expected_class = "S1"

print(f"\n📖 Escomen et al. (2024) Table 7:")
print(f"   Expected LSI: {expected_lsi}")
print(f"   Expected Class: {expected_class}")

print(f"\n💻 Your Result:")
print(f"   Calculated LSI: {result['lsi']:.2f}")
print(f"   Calculated Class: {result['lsc']}")

lsi_diff = abs(result['lsi'] - expected_lsi)
class_match = result['lsc'] == expected_class

print(f"\n🎯 Match:")
if lsi_diff < 5.0:
    print(f"   ✅ LSI: PASS (diff: {lsi_diff:.2f})")
else:
    print(f"   ⚠️  LSI: Review needed (diff: {lsi_diff:.2f})")

if class_match:
    print(f"   ✅ Classification: PASS")
else:
    print(f"   ❌ Classification: FAIL (expected {expected_class}, got {result['lsc']})")

print("\n" + "="*80)
if class_match and lsi_diff < 5.0:
    print("🎉 TEST PASSED!")
else:
    print("⚠️  TEST NEEDS REVIEW")
print("="*80 + "\n")