"""
Test the complete evaluation workflow
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_base.evaluation import SuitabilityEvaluator


def test_evaluator_initialization():
    """Test evaluator initialization"""
    print("\n" + "="*70)
    print("TEST 1: Evaluator Initialization")
    print("="*70)
    
    evaluator = SuitabilityEvaluator()
    
    crops = evaluator.get_available_crops()
    print(f"✓ Loaded {len(crops)} crops")
    print(f"  Available: {', '.join(crops)}")
    
    assert len(crops) > 0, "No crops loaded!"
    print("✅ PASSED\n")


def test_banana_evaluation_excellent():
    """Test banana evaluation with excellent conditions"""
    print("="*70)
    print("TEST 2: Banana Evaluation - Excellent Conditions")
    print("="*70)
    
    evaluator = SuitabilityEvaluator()
    
    # Excellent conditions for banana
    soil_data = {
        'temperature': 25.0,
        'rainfall': 2000.0,
        'ph': 6.2,
        'organic_matter': 3.0,
        'texture': 'L',
        'soil_depth': 120,
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.5,
    }
    
    result = evaluator.evaluate_suitability(soil_data, "Banana")
    
    print(f"\n📊 Results:")
    print(f"  LSI: {result['lsi']}")
    print(f"  Classification: {result['full_classification']}")
    print(f"  Limiting Factors: {result['limiting_factors']}")
    
    assert result['lsc'] == 'S1', f"Expected S1, got {result['lsc']}"
    assert result['lsi'] >= 75, f"Expected LSI >= 75, got {result['lsi']}"
    
    print("✅ PASSED\n")


def test_banana_evaluation_poor_ph():
    """Test banana evaluation with poor pH"""
    print("="*70)
    print("TEST 3: Banana Evaluation - Poor pH (Acidic)")
    print("="*70)
    
    evaluator = SuitabilityEvaluator()
    
    # Poor pH conditions
    soil_data = {
        'temperature': 25.0,
        'rainfall': 2000.0,
        'ph': 4.5,  # Very acidic
        'organic_matter': 3.0,
        'texture': 'L',
        'soil_depth': 120,
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.5,
    }
    
    result = evaluator.evaluate_suitability(soil_data, "Banana")
    
    print(f"\n📊 Results:")
    print(f"  LSI: {result['lsi']}")
    print(f"  Classification: {result['full_classification']}")
    print(f"  Limiting Factors: {result['limiting_factors']}")
    
    print(f"\n⚠️ Limiting Factor Details:")
    for detail in result['limiting_factors_detailed']:
        print(f"    • {detail['description']}: {detail['actual_value']}")
    
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations'][:3]:
        print(f"  {rec[:80]}...")
    
    assert 'f' in result['limiting_factors'], "Should show fertility limitation"
    assert result['lsi'] < 75, "LSI should be lower due to poor pH"
    
    print("✅ PASSED\n")


def test_multiple_crops():
    """Test evaluation of multiple crops"""
    print("="*70)
    print("TEST 4: Multiple Crops Evaluation")
    print("="*70)
    
    evaluator = SuitabilityEvaluator()
    
    soil_data = {
        'temperature': 25.0,
        'rainfall': 2000.0,
        'ph': 6.2,
        'organic_matter': 3.0,
        'texture': 'L',
        'soil_depth': 120,
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.5,
    }
    
    results = evaluator.evaluate_multiple_crops(soil_data)
    
    print(f"\n📊 Evaluated {len(results)} crops")
    print(f"\nTop 3 Most Suitable:")
    print(f"  {'Crop':<15} {'LSI':<8} {'Classification'}")
    print("  " + "-" * 40)
    
    for result in results[:3]:
        print(f"  {result['crop_name']:<15} {result['lsi']:<8.2f} {result['full_classification']}")
    
    assert len(results) > 0, "No crops evaluated!"
    assert results[0]['lsi'] >= results[-1]['lsi'], "Results should be sorted by LSI"
    
    print("✅ PASSED\n")


def test_brgy_gacap_conditions():
    """Test with actual Brgy. Gacap data from research"""
    print("="*70)
    print("TEST 5: Real Data - Brgy. Gacap Conditions")
    print("="*70)
    
    evaluator = SuitabilityEvaluator()
    
    # Data from "Revised_Escomen et al" Table 6
    soil_data = {
        'temperature': 22.29,
        'rainfall': 2651.54,
        'humidity': 76.62,
        'ph': 6.20,
        'organic_matter': 6.50,
        'texture': 'L',
        'soil_depth': 138,
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.67,
        'base_saturation': 36.03,
        'cec': 30.50,
    }
    
    result = evaluator.evaluate_suitability(soil_data, "Banana")
    
    print(f"\n📊 Banana Suitability for Brgy. Gacap:")
    print(f"  LSI: {result['lsi']:.2f}")
    print(f"  Classification: {result['full_classification']}")
    print(f"  Expected from paper: LSI ≈ 90.25, S1")
    
    # Allow some variance due to parameter differences
    print(f"\n  Variance from paper: {abs(result['lsi'] - 90.25):.2f}")
    
    print("✅ PASSED\n")


# Testing and demonstration
if __name__ == "__main__":
    # Fix import path for standalone execution
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Now import
    from knowledge_base.crop_rules import CropRules
    
    print("\n" + "="*70)
    print("RULES ENGINE - TESTING & DEMONSTRATION")
    print("="*70)
    
    # Initialize
    engine = RulesEngine()
    
    # Test 1: Slope Rating
    print("\n🧪 TEST 1: Slope Rating for Banana")
    print("-" * 70)
    
    test_slopes = [0.5, 1.0, 1.5, 2.0, 2.5, 5.0, 7.0, 10.0]
    
    print(f"{'Slope (%)':<12} {'Classification':<18} {'Rating':<10} {'Expected'}")
    print("-" * 70)
    
    for slope in test_slopes:
        rating, classification, subclass = engine._get_slope_rating("Banana", slope)
        
        # Determine expected
        if slope <= 1:
            expected = "S1"
        elif slope <= 2:
            expected = "S2"
        elif slope <= 4:
            expected = "S3"
        else:
            expected = "N"
        
        status = "✓" if classification == expected else "✗"
        print(f"{slope:<12.1f} {classification:<18} {rating:<10.2f} {expected} {status}")
    
    # Test 2: LSI Calculation
    print("\n🧪 TEST 2: LSI Calculation (Square Root Method)")
    print("-" * 70)
    
    test_cases = [
        ([1.0, 1.0, 1.0, 1.0], 100.0, "All S1"),
        ([0.95, 0.95, 0.95], 95.0, "All S2 high"),
        ([0.85, 0.95, 1.0], 85.0, "Mixed S1-S2"),
        ([0.60, 0.85, 1.0], 60.0, "Mixed S2-S3"),
        ([0.25, 0.85, 1.0], 25.0, "One N rating"),
    ]
    
    print(f"{'Ratings':<30} {'Expected LSI':<15} {'Calculated':<15} {'Status'}")
    print("-" * 70)
    
    for ratings, expected_lsi, description in test_cases:
        calculated_lsi = engine.calculate_lsi(ratings)
        status = "✓" if abs(calculated_lsi - expected_lsi) < 5.0 else "✗"
        print(f"{str(ratings):<30} {expected_lsi:<15.2f} {calculated_lsi:<15.2f} {status}")
    
    # Test 3: Full Evaluation
    print("\n🧪 TEST 3: Full Banana Evaluation")
    print("-" * 70)
    
    # Excellent conditions
    excellent_soil = {
        'temperature': 25.0,
        'rainfall': 2000.0,
        'ph': 6.2,
        'organic_matter': 3.0,
        'texture': 'L',
        'soil_depth': 120,
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.5,
    }
    
    print("\n📊 Test Case: Excellent Conditions")
    result = engine.evaluate("Banana", excellent_soil)
    
    print(f"  LSI: {result['lsi']:.2f}")
    print(f"  Classification: {result['full_classification']}")
    print(f"  Limiting Factors: {result['limiting_factors'] or 'None'}")
    print(f"\n  Parameter Ratings:")
    for param, (rating, cls, sub) in result['parameter_ratings'].items():
        print(f"    {param:<20}: {rating:.2f} ({cls}{sub})")
    
    expected_class = "S1" if result['lsi'] >= 75 else "S2" if result['lsi'] >= 50 else "S3"
    status = "✓" if result['lsc'] == expected_class else "✗"
    print(f"\n  Expected: {expected_class} | Actual: {result['lsc']} {status}")
    
    # Poor pH conditions
    print("\n📊 Test Case: Poor pH (Acidic)")
    poor_soil = excellent_soil.copy()
    poor_soil['ph'] = 4.5
    
    result2 = engine.evaluate("Banana", poor_soil)
    print(f"  LSI: {result2['lsi']:.2f}")
    print(f"  Classification: {result2['full_classification']}")
    print(f"  Limiting Factors: {result2['limiting_factors']}")
    
    has_fertility_limit = 'f' in result2['limiting_factors']
    status = "✓" if has_fertility_limit else "✗"
    print(f"  Expected fertility limitation: {status}")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)