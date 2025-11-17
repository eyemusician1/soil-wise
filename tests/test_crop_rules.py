"""
Test suite for CropRules class
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_base.crop_rules import CropRules

def test_crop_loading():
    """Test that crop requirements are loaded correctly."""
    print("🧪 Testing CropRules loading...")
    
    rules = CropRules()
    
    # Check crops loaded
    crops = rules.get_crop_names()
    print(f"✓ Loaded {len(crops)} crops: {', '.join(crops)}")
    
    assert len(crops) > 0, "No crops were loaded!"
    print("✓ Test passed: Crops loaded successfully\n")

def test_banana_requirements():
    """Test accessing Banana requirements."""
    print("🧪 Testing Banana requirements access...")
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    
    assert banana is not None, "Banana requirements not found!"
    assert banana['crop_name'] == "Banana"
    print(f"✓ Crop Name: {banana['crop_name']}")
    print(f"✓ Scientific Name: {banana.get('scientific_name', 'N/A')}")
    
    # Test climate requirements
    climate = rules.get_climate_requirements("Banana")
    assert climate is not None
    print(f"✓ Climate requirements accessible")
    
    # Test specific parameter
    precip = climate.get('annual_precipitation_mm')
    print(f"✓ Annual Precipitation: {precip}")
    
    print("✓ Test passed: Banana requirements accessible\n")

def test_parameter_access():
    """Test accessing specific parameters."""
    print("🧪 Testing parameter access...")
    
    rules = CropRules()
    
    # Get pH requirement for Banana
    ph_req = rules.get_parameter_requirement(
        "Banana", 
        "soil_fertility_requirements", 
        "ph_h2o"
    )
    
    assert ph_req is not None
    print(f"✓ Banana pH requirements: {ph_req}")
    print("✓ Test passed: Parameter access working\n")

if __name__ == "__main__":
    test_crop_loading()
    test_banana_requirements()
    test_parameter_access()
    print("✅ All tests passed!")