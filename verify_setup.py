"""Quick verification that everything is set up correctly"""

from pathlib import Path
import json

def verify_setup():
    print("🔍 Verifying SoilWise setup...\n")
    
    # Check directory structure
    data_dir = Path("data/crop_requirements")
    
    if not data_dir.exists():
        print("❌ ERROR: data/crop_requirements directory not found!")
        print(f"   Expected at: {data_dir.absolute()}")
        return False
    
    print(f"✓ Found data directory: {data_dir.absolute()}")
    
    # Check for banana.json
    banana_file = data_dir / "banana.json"
    if not banana_file.exists():
        print("❌ ERROR: banana.json not found!")
        return False
    
    print(f"✓ Found banana.json")
    
    # Try to load it
    try:
        with open(banana_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Successfully loaded banana.json")
        print(f"  Crop name: {data.get('crop_name')}")
        print(f"  Scientific name: {data.get('scientific_name')}")
    except Exception as e:
        print(f"❌ ERROR loading banana.json: {e}")
        return False
    
    # Try to import CropRules
    try:
        from knowledge_base.crop_rules import CropRules
        print(f"✓ Successfully imported CropRules")
        
        # Try to instantiate
        rules = CropRules()
        crops = rules.get_crop_names()
        print(f"✓ Loaded {len(crops)} crops: {', '.join(crops)}")
        
    except Exception as e:
        print(f"❌ ERROR with CropRules: {e}")
        return False
    
    print("\n✅ Setup verification complete! Everything looks good.")
    return True

if __name__ == "__main__":
    verify_setup()