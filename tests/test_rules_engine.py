"""
Test the Rules Engine calculations
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_base.rules_engine import RulesEngine


def test_basic_calculation():
    """Test basic LSI calculation"""
    print("\n" + "="*70)
    print("TEST: Basic LSI Calculation (Square Root Method)")
    print("="*70)
    
    engine = RulesEngine()
    
    # Test case 1: All S1 ratings
    print("\n📊 Test Case 1: All S1 ratings (perfect conditions)")
    ratings = [1.0, 1.0, 1.0, 1.0]
    lsi = engine.calculate_lsi(ratings)
    print(f"Ratings: {ratings}")
    print(f"Expected LSI: 100")
    print(f"Calculated LSI: {lsi}")
    assert lsi == 100, f"Expected 100, got {lsi}"
    print("✅ PASSED")
    
    # Test case 2: Mixed ratings
    print("\n📊 Test Case 2: Mixed ratings")
    ratings = [0.85, 0.95, 1.0, 0.85]
    lsi = engine.calculate_lsi(ratings)
    print(f"Ratings: {ratings}")
    print(f"Rmin = {min(ratings)}")
    print(f"Others = {[r for r in ratings if r != min(ratings)]}")
    print(f"Calculated LSI: {lsi}")
    classification = engine.classify_lsi(lsi)
    print(f"Classification: {classification}")
    assert 50 <= lsi <= 100, f"LSI should be between 50-100 for these ratings"
    print("✅ PASSED")
    
    # Test case 3: Low rating (Not Suitable)
    print("\n📊 Test Case 3: Low rating (Not Suitable)")
    ratings = [0.25, 0.85, 1.0]
    lsi = engine.calculate_lsi(ratings)
    print(f"Ratings: {ratings}")
    print(f"Calculated LSI: {lsi}")
    classification = engine.classify_lsi(lsi)
    print(f"Classification: {classification}")
    assert classification == "N", f"Should be N, got {classification}"
    print("✅ PASSED")


def test_banana_evaluation():
    """Test full banana evaluation"""
    print("\n" + "="*70)
    print("TEST: Full Banana Evaluation")
    print("="*70)
    
    engine = RulesEngine()
    
    # Excellent conditions (should be S1)
    print("\n🍌 Test: Excellent Conditions")
    soil_data = {
        "temperature": 25.0,
        "rainfall": 2000.0,
        "ph": 6.2,
        "organic_matter": 3.0,
        "texture": "L",
        "soil_depth": 120,
        "drainage": "good",
        "flooding": "Fo",
    }
    
    result = engine.evaluate("Banana", soil_data)
    
    print(f"LSI: {result['lsi']}")
    print(f"Classification: {result['full_classification']}")
    print(f"Expected: S1 (75-100)")
    
    assert result['lsc'] == "S1", f"Expected S1, got {result['lsc']}"
    print("✅ PASSED")
    
    # Poor pH (should show limiting factor)
    print("\n🍌 Test: Poor pH (acidic)")
    soil_data['ph'] = 4.8
    result = engine.evaluate("Banana", soil_data)
    
    print(f"LSI: {result['lsi']}")
    print(f"Classification: {result['full_classification']}")
    print(f"Limiting Factors: {result['limiting_factors']}")
    
    assert "f" in result['limiting_factors'], "Should show fertility limitation"
    print("✅ PASSED")


if __name__ == "__main__":
    test_basic_calculation()
    test_banana_evaluation()
    print("\n" + "="*70)
    print("🎉 ALL RULES ENGINE TESTS PASSED!")
    print("="*70)