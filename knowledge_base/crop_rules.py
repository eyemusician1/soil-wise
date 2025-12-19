"""

Crop Rules Loader for SoilWise

Manages loading and accessing crop requirement rules from JSON files.

Enhanced with validation, logging, and SEASONAL SUPPORT.

"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CropRules:
    """
    Manages loading and accessing crop requirement rules from JSON files.
    Supports both seasonal and non-seasonal crops.
    """
    
    def __init__(self):
        self.crop_requirements: Dict[str, Dict[str, Any]] = {}
        self._load_all_crops()
        logger.info(f"CropRules initialized with {len(self.crop_requirements)} crops")
    
    def _get_data_dir(self) -> Path:
        """Get the data/crop_requirements directory path."""
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        data_dir = project_root / "data" / "crop_requirements"
        
        if not data_dir.exists():
            logger.error(f"Crop requirements directory not found: {data_dir}")
            raise FileNotFoundError(f"Crop requirements directory not found: {data_dir}")
        
        logger.debug(f"Data directory located: {data_dir}")
        return data_dir
    
    def _validate_crop_data(self, crop_data: Dict[str, Any], filename: str) -> bool:
        """
        Validate crop data structure.
        
        Args:
            crop_data: Crop requirement data
            filename: Name of the source file
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['crop_name']
        recommended_fields = [
            'scientific_name',
            'climate_requirements',
            'physical_soil_requirements',
            'soil_fertility_requirements'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in crop_data:
                logger.warning(f"{filename}: Missing required field '{field}'")
                return False
        
        # Check recommended fields
        for field in recommended_fields:
            if field not in crop_data:
                logger.debug(f"{filename}: Missing recommended field '{field}'")
        
        return True
    
    def _load_all_crops(self):
        """Load all crop requirement JSON files from the data directory."""
        try:
            data_dir = self._get_data_dir()
            json_files = list(data_dir.glob("*.json"))
            
            if not json_files:
                logger.warning(f"No crop requirement files found in {data_dir}")
                return
            
            logger.info(f"Found {len(json_files)} JSON files to load")
            loaded_count = 0
            
            for json_file in json_files:
                try:
                    logger.debug(f"Loading {json_file.name}...")
                    
                    with open(json_file, 'r', encoding='utf-8') as f:
                        crop_data = json.load(f)
                    
                    # Validate crop data
                    if not self._validate_crop_data(crop_data, json_file.name):
                        continue
                    
                    crop_name = crop_data.get('crop_name')
                    
                    # Check for duplicates
                    if crop_name in self.crop_requirements:
                        logger.warning(
                            f"Duplicate crop name '{crop_name}' found in {json_file.name}. "
                            f"Overwriting previous entry."
                        )
                    
                    self.crop_requirements[crop_name] = crop_data
                    loaded_count += 1
                    
                    # Log if seasonal
                    if crop_data.get('seasonal'):
                        seasons = crop_data.get('seasons', {})
                        logger.info(f"✓ Loaded: {crop_name} ({json_file.name}) - SEASONAL with {len(seasons)} seasons")
                    else:
                        logger.info(f"✓ Loaded: {crop_name} ({json_file.name})")
                
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in {json_file.name}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error loading {json_file.name}: {e}", exc_info=True)
            
            logger.info(f"Successfully loaded {loaded_count}/{len(json_files)} crop requirement files")
        
        except Exception as e:
            logger.error(f"Critical error in _load_all_crops: {e}", exc_info=True)
            raise
    
    def get_crop_names(self) -> List[str]:
        """Get list of all available crop names."""
        crop_names = sorted(self.crop_requirements.keys())
        logger.debug(f"Retrieved {len(crop_names)} crop names")
        return crop_names
    
    def get_crop_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete requirement data for a specific crop.
        
        Args:
            crop_name: Name of the crop (e.g., "Banana", "Arabica Coffee")
            
        Returns:
            Dictionary containing all crop requirements, or None if crop not found
        """
        if crop_name not in self.crop_requirements:
            logger.warning(f"Crop '{crop_name}' not found in knowledge base")
            return None
        
        logger.debug(f"Retrieved requirements for '{crop_name}'")
        return self.crop_requirements.get(crop_name)
    
    def is_seasonal(self, crop_name: str) -> bool:
        """Check if a crop has seasonal variations in requirements."""
        crop_data = self.get_crop_requirements(crop_name)
        is_seasonal = crop_data.get('seasonal', False) if crop_data else False
        logger.debug(f"Crop '{crop_name}' seasonal: {is_seasonal}")
        return is_seasonal
    
    def get_seasons(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """
        Get available seasons for a seasonal crop.
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Dictionary of seasons with their names, or None
        """
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data or not crop_data.get('seasonal'):
            return None
        
        seasons = crop_data.get('seasons', {})
        logger.debug(f"Crop '{crop_name}' has {len(seasons)} seasons: {list(seasons.keys())}")
        return seasons
    
    def get_climate_requirements(
        self, 
        crop_name: str, 
        season: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get climate requirements for a specific crop.
        
        Args:
            crop_name: Name of the crop
            season: Season key (e.g., 'january_april') for seasonal crops
            
        Returns:
            Climate requirements dictionary, or None
        """
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        
        # Check if seasonal
        if crop_data.get('seasonal') and season:
            seasons = crop_data.get('seasons', {})
            season_data = seasons.get(season, {})
            climate_reqs = season_data.get('climate_requirements')
            logger.debug(f"Retrieved climate requirements for '{crop_name}' (season: {season})")
        else:
            climate_reqs = crop_data.get('climate_requirements')
            logger.debug(f"Retrieved climate requirements for '{crop_name}'")
        
        return climate_reqs
    
    def get_soil_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Get physical soil requirements for a specific crop."""
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        
        soil_reqs = crop_data.get('physical_soil_requirements')
        logger.debug(f"Retrieved soil requirements for '{crop_name}'")
        return soil_reqs
    
    def get_fertility_requirements(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """Get soil fertility requirements for a specific crop."""
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        
        fertility_reqs = crop_data.get('soil_fertility_requirements')
        logger.debug(f"Retrieved fertility requirements for '{crop_name}'")
        return fertility_reqs
    
    def get_parameter_requirement(
        self,
        crop_name: str,
        category: str,
        parameter: str,
        season: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific parameter requirement for a crop.
        SUPPORTS SEASONAL CROPS!
        
        Args:
            crop_name: Name of the crop
            category: Category name (e.g., 'climate_requirements', 'soil_fertility_requirements')
            parameter: Parameter name (e.g., 'ph_h2o', 'soil_depth_cm')
            season: Season key (e.g., 'january_april') for seasonal crops
            
        Returns:
            Dictionary with S1, S2, S3, N classifications, or None
        """
        crop_data = self.get_crop_requirements(crop_name)
        if not crop_data:
            logger.debug(f"No crop data found for '{crop_name}'")
            return None
        
        # ✅ SEASONAL SUPPORT: Check if crop is seasonal
        if crop_data.get('seasonal'):
            if not season:
                logger.warning(
                    f"Crop '{crop_name}' is seasonal but no season provided. "
                    f"Available seasons: {list(crop_data.get('seasons', {}).keys())}"
                )
                return None
            
            # Navigate to seasonal requirements
            seasons = crop_data.get('seasons', {})
            season_data = seasons.get(season)
            
            if not season_data:
                logger.warning(
                    f"Season '{season}' not found for crop '{crop_name}'. "
                    f"Available: {list(seasons.keys())}"
                )
                return None
            
            # For climate requirements, look inside season data
            if category == 'climate_requirements':
                category_data = season_data.get(category)
                logger.debug(
                    f"Using seasonal {category} for '{crop_name}' (season: {season})"
                )
            else:
                # Non-climate categories are at root level
                category_data = crop_data.get(category)
                logger.debug(
                    f"Using root-level {category} for '{crop_name}' (shared across seasons)"
                )
        else:
            # Non-seasonal crop: simple access
            category_data = crop_data.get(category)
            logger.debug(f"Using non-seasonal {category} for '{crop_name}'")
        
        if not category_data:
            logger.debug(f"Category '{category}' not found for '{crop_name}'")
            return None
        
        param_req = category_data.get(parameter)
        
        if param_req:
            if season:
                logger.debug(
                    f"Retrieved parameter '{parameter}' from category '{category}' "
                    f"for crop '{crop_name}' (season: {season})"
                )
            else:
                logger.debug(
                    f"Retrieved parameter '{parameter}' from category '{category}' "
                    f"for crop '{crop_name}'"
                )
        else:
            logger.debug(
                f"Parameter '{parameter}' not found in category '{category}' "
                f"for crop '{crop_name}'"
            )
        
        return param_req
    
    def __repr__(self):
        return f"CropRules(loaded_crops={len(self.crop_requirements)})"


# Example usage for testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("CROP RULES LOADER - TEST (WITH SEASONAL SUPPORT)")
    print("="*80)
    
    # Test the crop rules loader
    rules = CropRules()
    
    print(f"\n📋 Loaded {len(rules.crop_requirements)} crops:")
    for crop in rules.get_crop_names():
        seasonal_marker = " 🗓️ SEASONAL" if rules.is_seasonal(crop) else ""
        print(f"  • {crop}{seasonal_marker}")
    
    # Test seasonal crop (Cabbage)
    if rules.is_seasonal("Cabbage"):
        print("\n🥬 Testing Cabbage (SEASONAL):")
        seasons = rules.get_seasons("Cabbage")
        print(f"  Available seasons: {list(seasons.keys())}")
        
        # Test getting climate requirements for a specific season
        climate_jan_apr = rules.get_climate_requirements("Cabbage", "january_april")
        if climate_jan_apr:
            print(f"  January-April climate requirements: {list(climate_jan_apr.keys())}")
        
        # Test parameter requirement with season
        temp_req = rules.get_parameter_requirement(
            "Cabbage", 
            "climate_requirements", 
            "mean_annual_temp_c",
            season="january_april"
        )
        print(f"  Temperature requirements (Jan-Apr): {temp_req}")
    
    # Test non-seasonal crop (Banana)
    print("\n🍌 Testing Banana (NON-SEASONAL):")
    banana_climate = rules.get_climate_requirements("Banana")
    if banana_climate:
        print(f"  Annual Precipitation: {banana_climate.get('annual_precipitation_mm')}")
        print(f"  Mean Annual Temp: {banana_climate.get('mean_annual_temp_c')}")
    
    # Test specific parameter
    ph_req = rules.get_parameter_requirement("Banana", "soil_fertility_requirements", "ph_h2o")
    print(f"  pH Requirements: {ph_req}")
    
    print("\n" + "="*80)
