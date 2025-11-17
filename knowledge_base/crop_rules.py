import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class CropRules:
    """
    Manages loading and accessing crop requirement rules from JSON files.
    """
    
    def __init__(self):
        self.crop_requirements: Dict[str, Dict[str, Any]] = {}
        self._load_all_crops()
    
    def _get_data_dir(self) -> Path:
        """Get the data/crop_requirements directory path."""
        # Get the project root (assuming this file is in SoilWise/knowledge_base/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        data_dir = project_root / "data" / "crop_requirements"
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Crop requirements directory not found: {data_dir}")
        
        return data_dir
    
    def _load_all_crops(self):
        """Load all crop requirement JSON files from the data directory."""
        data_dir = self._get_data_dir()
        
        # Find all JSON files (excluding SCHEMA.md and __init__.py)
        json_files = list(data_dir.glob("*.json"))
        
        if not json_files:
            print(f"Warning: No crop requirement files found in {data_dir}")
            return
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    crop_data = json.load(f)
                    crop_name = crop_data.get('crop_name')
                    
                    if crop_name:
                        self.crop_requirements[crop_name] = crop_data
                        print(f"✓ Loaded crop requirements: {crop_name}")
                    else:
                        print(f"⚠ Warning: {json_file.name} missing 'crop_name' field")
                        
            except json.JSONDecodeError as e:
                print(f"✗ Error loading {json_file.name}: {e}")
            except Exception as e:
                print(f"✗ Unexpected error loading {json_file.name}: {e}")
    
    def get_crop_names(self) -> List[str]:
        """Get list of all available crop names."""
        return sorted(self.crop_requirements.keys())
    
    def get_crop_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete requirement data for a specific crop.
        
        Args:
            crop_name: Name of the crop (e.g., "Banana", "Arabica Coffee")
        
        Returns:
            Dictionary containing all crop requirements, or None if crop not found
        """
        return self.crop_requirements.get(crop_name)
    
    def get_climate_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Get climate requirements for a specific crop."""
        crop_data = self.get_crop_requirements(crop_name)
        return crop_data.get('climate_requirements') if crop_data else None
    
    def get_soil_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Get physical soil requirements for a specific crop."""
        crop_data = self.get_crop_requirements(crop_name)
        return crop_data.get('physical_soil_requirements') if crop_data else None
    
    def get_fertility_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Get soil fertility requirements for a specific crop."""
        crop_data = self.get_crop_requirements(crop_name)
        return crop_data.get('soil_fertility_requirements') if crop_data else None
    
    def is_seasonal(self, crop_name: str) -> bool:
        """Check if a crop has seasonal variations in requirements."""
        crop_data = self.get_crop_requirements(crop_name)
        return crop_data.get('seasonal', False) if crop_data else False
    
    def get_parameter_requirement(
        self, 
        crop_name: str, 
        category: str, 
        parameter: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific parameter requirement for a crop.
        
        Args:
            crop_name: Name of the crop
            category: Category name (e.g., 'climate_requirements', 'soil_fertility_requirements')
            parameter: Parameter name (e.g., 'ph_h2o', 'soil_depth_cm')
        
        Returns:
            Dictionary with S1, S2, S3, N classifications, or None
        """
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        
        category_data = crop_data.get(category)
        if not category_data:
            return None
        
        return category_data.get(parameter)
    
    def __repr__(self):
        return f"CropRules(loaded_crops={len(self.crop_requirements)})"


# Example usage for testing
if __name__ == "__main__":
    # Test the crop rules loader
    rules = CropRules()
    
    print(f"\n📋 Loaded {len(rules.crop_requirements)} crops:")
    for crop in rules.get_crop_names():
        print(f"  • {crop}")
    
    # Test getting banana requirements
    print("\n🍌 Testing Banana requirements:")
    banana_climate = rules.get_climate_requirements("Banana")
    if banana_climate:
        print(f"  Annual Precipitation: {banana_climate.get('annual_precipitation_mm')}")
        print(f"  Mean Annual Temp: {banana_climate.get('mean_annual_temp_c')}")
    
    # Test specific parameter
    ph_req = rules.get_parameter_requirement("Banana", "soil_fertility_requirements", "ph_h2o")
    print(f"\n  pH Requirements: {ph_req}")