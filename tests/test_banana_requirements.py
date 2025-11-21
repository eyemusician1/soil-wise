"""
Comprehensive test suite for Banana crop requirements
Tests the accuracy of data extracted from COA Extension Project (Pages 57-58)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_base.crop_rules import CropRules

def test_banana_basic_info():
    """Test basic banana information"""
    print("\n" + "="*70)
    print("TEST 1: BASIC INFORMATION")
    print("="*70)
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    
    assert banana is not None, "Banana not found in crop requirements!"
    
    print(f"✓ Crop Name: {banana['crop_name']}")
    assert banana['crop_name'] == "Banana", "Crop name mismatch!"
    
    print(f"✓ Scientific Name: {banana['scientific_name']}")
    assert banana['scientific_name'] == "Musa sp. L.", "Scientific name mismatch!"
    
    print(f"✓ Seasonal: {banana['seasonal']}")
    assert banana['seasonal'] == False, "Banana should not be seasonal!"
    
    print("\n✅ Basic Information Test PASSED\n")


def test_banana_climate_requirements():
    """Test climate requirements accuracy"""
    print("="*70)
    print("TEST 2: CLIMATE REQUIREMENTS (Page 57)")
    print("="*70)
    
    rules = CropRules()
    climate = rules.get_climate_requirements("Banana")
    
    # Test Annual Precipitation
    print("\n📊 Annual Precipitation (mm):")
    precip = climate['annual_precipitation_mm']
    
    print(f"  S1: {precip['S1']['range']} → Rating: {precip['S1']['rating']}")
    assert precip['S1']['range'] == [1800, None], "S1 precipitation range incorrect!"
    assert precip['S1']['rating'] == 1.0, "S1 rating should be 1.0!"
    
    print(f"  S2: {precip['S2']['range']} → Rating: {precip['S2']['rating']}")
    assert precip['S2']['range'] == [1500, 1800], "S2 precipitation range incorrect!"
    assert precip['S2']['rating'] == 0.85, "S2 rating should be 0.85!"
    
    print(f"  S3: {precip['S3']['range']} → Rating: {precip['S3']['rating']}")
    assert precip['S3']['range'] == [1250, 1500], "S3 precipitation range incorrect!"
    assert precip['S3']['rating'] == 0.60, "S3 rating should be 0.60!"
    
    print(f"  N:  {precip['N']['range']} → Rating: {precip['N']['rating']}")
    assert precip['N']['range'] == [None, 1250], "N precipitation range incorrect!"
    assert precip['N']['rating'] == 0.25, "N rating should be 0.25!"
    
    # Test Mean Annual Temperature
    print("\n🌡️ Mean Annual Temperature (°C):")
    temp = climate['mean_annual_temp_c']
    
    print(f"  S1: {temp['S1']['range']} → Rating: {temp['S1']['rating']}")
    assert temp['S1']['range'] == [22, None], "S1 temp range should be [22, None] (>22)!"
    assert temp['S1']['rating'] == 1.0
    
    print(f"  S2: {temp['S2']['range']} → Rating: {temp['S2']['rating']}")
    assert temp['S2']['range'] == [18, 22], "S2 temp range incorrect!"
    assert temp['S2']['rating'] == 0.85
    
    print(f"  S3: {temp['S3']['range']} → Rating: {temp['S3']['rating']}")
    assert temp['S3']['range'] == [16, 18], "S3 temp range incorrect!"
    assert temp['S3']['rating'] == 0.60
    
    print(f"  N:  {temp['N']['range']} → Rating: {temp['N']['rating']}")
    assert temp['N']['range'] == [None, 16], "N temp range should be [None, 16] (<16)!"
    assert temp['N']['rating'] == 0.25
    
    # Test Dry Season
    print("\n🌵 Dry Season (months):")
    dry = climate['dry_season_months']
    
    print(f"  S1: {dry['S1']['range']} → Rating: {dry['S1']['rating']}")
    assert dry['S1']['range'] == [0, 1], "S1 dry season range incorrect!"
    
    print(f"  S2: {dry['S2']['range']} → Rating: {dry['S2']['rating']}")
    assert dry['S2']['range'] == [1, 3], "S2 dry season range incorrect!"
    
    print(f"  S3: {dry['S3']['range']} → Rating: {dry['S3']['rating']}")
    assert dry['S3']['range'] == [3, 4], "S3 dry season range incorrect!"
    
    print(f"  N:  {dry['N']['range']} → Rating: {dry['N']['rating']}")
    assert dry['N']['range'] == [4, 6], "N dry season range incorrect!"
    
    print("\n✅ Climate Requirements Test PASSED\n")


def test_banana_topography_requirements():
    """Test topography (slope) requirements"""
    print("="*70)
    print("TEST 3: TOPOGRAPHY REQUIREMENTS (Page 58)")
    print("="*70)
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    topo = banana['topography_requirements']
    
    print("\n⛰️ Slope Requirements:")
    
    # Level 1 (most detailed classification)
    print("\n  Level 1 (detailed):")
    slope_l1 = topo['slope_pct']['level1']
    print(f"    S1: {slope_l1['S1']['range']}% → Rating: {slope_l1['S1']['rating']}")
    assert slope_l1['S1']['range'] == [0, 1], "Level1 S1 should be 0-1%!"
    
    print(f"    S2: {slope_l1['S2']['range']}% → Rating: {slope_l1['S2']['rating']}")
    assert slope_l1['S2']['range'] == [1, 2], "Level1 S2 should be 1-2%!"
    
    print(f"    S3: {slope_l1['S3']['range']}% → Rating: {slope_l1['S3']['rating']}")
    assert slope_l1['S3']['range'] == [2, 4], "Level1 S3 should be 2-4%!"
    
    print(f"    N:  {slope_l1['N']['range']}% → Rating: {slope_l1['N']['rating']}")
    assert slope_l1['N']['range'] == [6, None], "Level1 N should be >6%!"
    
    # Level 2
    print("\n  Level 2 (moderate):")
    slope_l2 = topo['slope_pct']['level2']
    assert slope_l2['S1']['range'] == [0, 2], "Level2 S1 should be 0-2%!"
    assert slope_l2['S2']['range'] == [2, 4], "Level2 S2 should be 2-4%!"
    assert slope_l2['S3']['range'] == [4, 8], "Level2 S3 should be 4-8%!"
    assert slope_l2['N']['range'] == [16, None], "Level2 N should be >16%!"
    print("    ✓ All level 2 ranges correct")
    
    # Level 3
    print("\n  Level 3 (broad):")
    slope_l3 = topo['slope_pct']['level3']
    assert slope_l3['S1']['range'] == [0, 4], "Level3 S1 should be 0-4%!"
    assert slope_l3['S2']['range'] == [4, 8], "Level3 S2 should be 4-8%!"
    assert slope_l3['S3']['range'] == [8, 16], "Level3 S3 should be 8-16%!"
    assert slope_l3['N']['range'] == [50, None], "Level3 N should be >50%!"
    print("    ✓ All level 3 ranges correct")
    
    print("\n✅ Topography Requirements Test PASSED\n")


def test_banana_wetness_requirements():
    """Test wetness (flooding & drainage) requirements"""
    print("="*70)
    print("TEST 4: WETNESS REQUIREMENTS (Page 58)")
    print("="*70)
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    wetness = banana['wetness_requirements']
    
    print("\n💧 Flooding:")
    flooding = wetness['flooding']
    
    print(f"  S1: {flooding['S1']['values']} → Rating: {flooding['S1']['rating']}")
    assert flooding['S1']['values'] == ["Fo"], "S1 flooding should be ['Fo']!"
    assert flooding['S1']['rating'] == 1.0
    
    print(f"  S2: {flooding['S2']['values']} → Rating: {flooding['S2']['rating']}")
    assert flooding['S2']['values'] == ["Fo"], "S2 flooding should be ['Fo']!"
    
    print(f"  S3: {flooding['S3']['values']} → Rating: {flooding['S3']['rating']}")
    assert flooding['S3']['values'] == ["F1"], "S3 flooding should be ['F1']!"
    
    print(f"  N:  {flooding['N']['values']} → Rating: {flooding['N']['rating']}")
    assert flooding['N']['values'] == ["F2", "F3"], "N flooding should include F2, F3!"
    
    print("\n💦 Drainage:")
    drainage = wetness['drainage']
    
    print(f"  S1: {drainage['S1']['values']} → Rating: {drainage['S1']['rating']}")
    assert drainage['S1']['values'] == ["good"], "S1 drainage should be ['good']!"
    
    print(f"  S2: {drainage['S2']['values']} → Rating: {drainage['S2']['rating']}")
    assert drainage['S2']['values'] == ["moderate"], "S2 drainage should be ['moderate']!"
    
    print(f"  S3: {drainage['S3']['values']} → Rating: {drainage['S3']['rating']}")
    assert drainage['S3']['values'] == ["imperfect"], "S3 drainage incorrect!"
    
    print(f"  N:  {drainage['N']['values']} → Rating: {drainage['N']['rating']}")
    assert "poor_not_drainable" in drainage['N']['values'], "N should include poor_not_drainable!"
    
    print("\n✅ Wetness Requirements Test PASSED\n")


def test_banana_soil_fertility():
    """Test soil fertility requirements (most critical for calculations)"""
    print("="*70)
    print("TEST 5: SOIL FERTILITY REQUIREMENTS (Page 58)")
    print("="*70)
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    fertility = banana['soil_fertility_requirements']
    
    # Test pH (complex case with multiple ranges)
    print("\n🧪 pH (H2O):")
    ph = fertility['ph_h2o']
    
    print(f"  S1: {ph['S1']['range']} → Rating: {ph['S1']['rating']}")
    assert ph['S1']['range'] == [5.8, 6.4], "S1 pH should be 5.8-6.4 (from table: 6.4-5.8)!"
    assert ph['S1']['rating'] == 1.0
    
    print(f"  S2_low: {ph['S2_low']['range']} → Rating: {ph['S2_low']['rating']}")
    assert ph['S2_low']['range'] == [5.6, 5.8], "S2_low pH should be 5.6-5.8!"
    
    print(f"  S2_high: {ph['S2_high']['range']} → Rating: {ph['S2_high']['rating']}")
    assert ph['S2_high']['range'] == [6.4, 7.0], "S2_high pH should be 6.4-7.0!"
    
    print(f"  S3_low: {ph['S3_low']['range']} → Rating: {ph['S3_low']['rating']}")
    assert ph['S3_low']['range'] == [5.2, 5.6], "S3_low pH should be 5.2-5.6!"
    
    print(f"  S3_high: {ph['S3_high']['range']} → Rating: {ph['S3_high']['rating']}")
    assert ph['S3_high']['range'] == [7.0, 7.5], "S3_high pH should be 7.0-7.5!"
    
    # Test Base Saturation
    print("\n📊 Base Saturation (%):")
    bs = fertility['base_saturation_pct']
    
    print(f"  S1: {bs['S1']['range']}% → Rating: {bs['S1']['rating']}")
    assert bs['S1']['range'] == [50, None], "S1 base saturation should be >50%!"
    assert bs['S1']['rating'] == 1.0
    
    print(f"  S2: {bs['S2']['range']}% → Rating: {bs['S2']['rating']}")
    assert bs['S2']['range'] == [35, 50], "S2 base saturation should be 35-50%!"
    assert bs['S2']['rating'] == 0.85
    
    print(f"  S3: {bs['S3']['range']}% → Rating: {bs['S3']['rating']}")
    assert bs['S3']['range'] == [20, 35], "S3 base saturation should be 20-35%!"
    
    print(f"  N:  {bs['N']['range']}% → Rating: {bs['N']['rating']}")
    assert bs['N']['range'] == [None, 20], "N base saturation should be <20%!"
    
    # Test Organic Carbon
    print("\n🌱 Organic Carbon (%):")
    oc = fertility['organic_carbon_pct']
    
    print(f"  S1: {oc['S1']['range']}% → Rating: {oc['S1']['rating']}")
    assert oc['S1']['range'] == [2.4, None], "S1 OC should be >2.4%!"
    
    print(f"  S2: {oc['S2']['range']}% → Rating: {oc['S2']['rating']}")
    assert oc['S2']['range'] == [1.5, 2.4], "S2 OC should be 1.5-2.4%!"
    
    print(f"  S3: {oc['S3']['range']}% → Rating: {oc['S3']['rating']}")
    assert oc['S3']['range'] == [0.8, 1.5], "S3 OC should be 0.8-1.5%!"
    
    print(f"  N:  {oc['N']['range']}% → Rating: {oc['N']['rating']}")
    assert oc['N']['range'] == [None, 0.8], "N OC should be <0.8%!"
    assert oc['N']['rating'] == 0.60, "N OC rating should be 0.60 (not 0.25)!"
    
    print("\n✅ Soil Fertility Requirements Test PASSED\n")


def test_banana_physical_soil():
    """Test physical soil characteristics"""
    print("="*70)
    print("TEST 6: PHYSICAL SOIL CHARACTERISTICS (Page 58)")
    print("="*70)
    
    rules = CropRules()
    banana = rules.get_crop_requirements("Banana")
    physical = banana['physical_soil_requirements']
    
    # Test Soil Depth
    print("\n📏 Soil Depth (cm):")
    depth = physical['soil_depth_cm']
    
    print(f"  S1: {depth['S1']['range']} → Rating: {depth['S1']['rating']}")
    assert depth['S1']['range'] == [100, None], "S1 depth should be >100cm!"
    
    print(f"  S2: {depth['S2']['range']} → Rating: {depth['S2']['rating']}")
    assert depth['S2']['range'] == [75, 100], "S2 depth should be 75-100cm!"
    
    print(f"  S3: {depth['S3']['range']} → Rating: {depth['S3']['rating']}")
    assert depth['S3']['range'] == [50, 75], "S3 depth should be 50-75cm!"
    
    print(f"  N:  {depth['N']['range']} → Rating: {depth['N']['rating']}")
    assert depth['N']['range'] == [None, 25], "N depth should be <25cm!"
    
    # Test Coarse Fragments
    print("\n🪨 Coarse Fragments (%):")
    cf = physical['coarse_fragments_pct']
    
    print(f"  S1: {cf['S1']['range']}% → Rating: {cf['S1']['rating']}")
    assert cf['S1']['range'] == [0, 3], "S1 coarse fragments should be 0-3%!"
    
    print(f"  S2: {cf['S2']['range']}% → Rating: {cf['S2']['rating']}")
    assert cf['S2']['range'] == [3, 15], "S2 coarse fragments should be 3-15%!"
    
    print(f"  S3: {cf['S3']['range']}% → Rating: {cf['S3']['rating']}")
    assert cf['S3']['range'] == [15, 35], "S3 coarse fragments should be 15-35%!"
    
    print(f"  N:  {cf['N']['range']}% → Rating: {cf['N']['rating']}")
    assert cf['N']['range'] == [55, None], "N coarse fragments should be >55%!"
    
    # Test Texture (categorical)
    print("\n🌾 Soil Texture:")
    texture = physical['texture']
    
    print(f"  S1: {texture['S1']['values']}")
    assert "L" in texture['S1']['values'], "S1 should include 'L' (Loam)!"
    assert "CL" in texture['S1']['values'], "S1 should include 'CL' (Clay Loam)!"
    
    print(f"  S2: {texture['S2']['values']}")
    assert "SC" in texture['S2']['values'], "S2 should include 'SC' (Sandy Clay)!"
    
    print(f"  N:  {texture['N']['values']}")
    assert "Cm" in texture['N']['values'], "N should include 'Cm' (Clay, massive)!"
    
    print("\n✅ Physical Soil Characteristics Test PASSED\n")


def run_all_tests():
    """Run all banana requirement tests"""
    print("\n" + "="*70)
    print(" 🍌 BANANA CROP REQUIREMENTS VALIDATION TEST SUITE")
    print(" Reference: COA Extension Project 2024, Pages 57-58")
    print("="*70)
    
    try:
        test_banana_basic_info()
        test_banana_climate_requirements()
        test_banana_topography_requirements()
        test_banana_wetness_requirements()
        test_banana_soil_fertility()
        test_banana_physical_soil()
        
        print("="*70)
        print("🎉 ALL TESTS PASSED! Banana requirements are accurate.")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\n📝 Action Required: Check your banana.json against COA Extension")
        print("   Project PDF pages 57-58 and fix the incorrect values.")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)