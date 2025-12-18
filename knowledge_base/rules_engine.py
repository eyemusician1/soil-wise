"""
Rules Engine for SoilWise - WITH DEBUG OUTPUT
Implements the Square Root Method for crop suitability evaluation
Reference: Khiddir et al. 1986, FAO 1976, COA Extension Project 2024
"""

import math
from typing import Dict, List, Tuple, Optional
from knowledge_base.crop_rules import CropRules


class RulesEngine:
    """
    Implements rule-based evaluation for crop suitability using the Square Root Method.
    
    Formula: I = Rmin × √(A/100 × B/100 × C/100 × ...)
    Where:
        I = Land Suitability Index (LSI)
        Rmin = Minimum rating among all parameters
        A, B, C = Other ratings besides the minimum
    """
    
    def __init__(self):
        self.crop_rules = CropRules()
    
    def get_parameter_rating(
        self,
        crop_name: str,
        category: str,
        parameter: str,
        value: float,
        season: Optional[str] = None
    ) -> Tuple[float, str, str]:
        """
        Get rating for a specific parameter value.
        
        Args:
            crop_name: Name of the crop
            category: Category (e.g., 'climate_requirements', 'soil_fertility_requirements')
            parameter: Parameter name (e.g., 'ph_h2o', 'soil_depth_cm')
            value: The actual measured value
            season: Optional season for seasonal crops
        
        Returns:
            Tuple of (rating_decimal, classification, subclass_code)
            Example: (0.85, "S2", "c") for climate limitation
        """
        # Special handling for slope (has nested levels)
        if parameter == "slope_pct":
            return self._get_slope_rating(crop_name, value)
        
        requirements = self.crop_rules.get_parameter_requirement(
            crop_name, category, parameter
        )
        
        if not requirements:
            return (0.25, "N", self._get_subclass_code(category))
        
        # Determine subclass code based on category
        subclass = self._get_subclass_code(category)
        
        # Check each classification level
        for classification_key, spec in requirements.items():
            if "range" in spec:
                # Numeric parameter
                min_val, max_val = spec["range"]
                
                # Handle None values (no limit)
                if min_val is None:
                    min_val = float('-inf')
                if max_val is None:
                    max_val = float('inf')
                
                # Check if value falls in range
                if min_val <= value <= max_val:
                    rating = spec["rating"]
                    classification = self._get_classification_from_key(classification_key)
                    return (rating, classification, subclass)
            
            elif "values" in spec:
                # Categorical parameter (texture, drainage, flooding)
                # Convert value to string for comparison
                value_str = str(value)
                if value_str in spec["values"]:
                    rating = spec["rating"]
                    classification = self._get_classification_from_key(classification_key)
                    return (rating, classification, subclass)
        
        # Default to N if no match found
        return (0.25, "N", subclass)
    
    def _get_slope_rating(self, crop_name: str, slope_value: float) -> Tuple[float, str, str]:
        """
        Special handler for slope parameter which has nested levels.
        Uses level1 (most detailed) by default.
        
        FIXED: Now iterates through all classification keys instead of hardcoded list.
        
        Args:
            crop_name: Name of the crop
            slope_value: Slope percentage
        
        Returns:
            Tuple of (rating, classification, subclass_code)
        """
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        
        if not crop_data:
            return (0.25, "N", "t")
        
        topo_reqs = crop_data.get('topography_requirements', {})
        slope_reqs = topo_reqs.get('slope_pct', {})
        
        # Use level1 (most detailed classification)
        level1 = slope_reqs.get('level1', {})
        
        if not level1:
            return (0.25, "N", "t")
        
        # FIXED: Iterate through all classification keys in level1
        # This handles keys like 'S1_0', 'S1_1', 'S2', 'S3', 'N2', etc.
        for classification_key, spec in level1.items():
            if "range" not in spec:
                continue
            
            min_val, max_val = spec["range"]
            
            # Handle None values
            if min_val is None:
                min_val = float('-inf')
            if max_val is None:
                max_val = float('inf')
            
            # Check if slope falls in range (inclusive)
            if min_val <= slope_value <= max_val:
                rating = spec["rating"]
                classification = self._get_classification_from_key(classification_key)
                return (rating, classification, "t")
        
        # Default to N if no match
        return (0.25, "N", "t")
    
    def _get_classification_from_key(self, key: str) -> str:
        """
        Extract classification (S1, S2, S3, N) from key like 'S2_low' or 'S3_minus'.
        
        Updated to handle new naming conventions like 'S1_0', 'S1_1', 'N2', etc.
        """
        if key.startswith("S1"):
            return "S1"
        elif key.startswith("S2"):
            return "S2"
        elif key.startswith("S3"):
            return "S3"
        elif key.startswith("N"):
            return "N"
        else:
            return key  # Return as-is if no prefix
    
    def _get_subclass_code(self, category: str) -> str:
        """
        Get subclass code based on category.
        
        Mapping:
            climate_requirements → c
            topography_requirements → t
            wetness_requirements → w
            physical_soil_requirements → s
            soil_fertility_requirements → f
            salinity_alkalinity_requirements → n
        """
        mapping = {
            "climate_requirements": "c",
            "topography_requirements": "t",
            "wetness_requirements": "w",
            "physical_soil_requirements": "s",
            "soil_fertility_requirements": "f",
            "salinity_alkalinity_requirements": "n"
        }
        return mapping.get(category, "")
    
    def calculate_lsi(self, ratings: List[float]) -> float:
        """
        Calculate Land Suitability Index using Square Root Method.
        
        Formula: I = Rmin × √(A/100 × B/100 × C/100 × ...)
        Reference: Khiddir et al. 1986, Escomen et al. 2024
        
        Args:
            ratings: List of ratings (as decimals, e.g., [1.0, 0.85, 0.95])
        
        Returns:
            LSI value (0-100)
        
        Examples:
            >>> calculate_lsi([1.0, 1.0, 1.0])
            100.0
            >>> calculate_lsi([0.85, 0.95, 1.0])
            82.85  # 0.85 × √(0.95 × 1.0) × 100
        """
        if not ratings:
            return 0.0
        
        # Find minimum rating
        rmin = min(ratings)
        
        # If all ratings are the same, return directly
        if all(r == rmin for r in ratings):
            return rmin * 100
        
        # CRITICAL FIX: Remove only ONE instance of minimum
        # Create a copy to avoid modifying original
        other_ratings = ratings.copy()
        other_ratings.remove(rmin)  # Removes first occurrence only
        
        if not other_ratings:
            # Only one unique rating
            return rmin * 100
        
        # Calculate product of other ratings (already as decimals)
        product = 1.0
        for rating in other_ratings:
            product *= rating
        
        # Apply square root method
        # Formula: I = Rmin × √(product) × 100
        lsi = rmin * math.sqrt(product) * 100
        
        return round(lsi, 2)
    
    def classify_lsi(self, lsi: float) -> str:
        """
        Classify LSI into suitability class.
        
        Args:
            lsi: Land Suitability Index (0-100)
        
        Returns:
            Classification: S1, S2, S3, or N
        """
        if lsi >= 75:
            return "S1"
        elif lsi >= 50:
            return "S2"
        elif lsi >= 25:
            return "S3"
        else:
            return "N"
    
    def identify_limiting_factors(
        self,
        parameter_ratings: Dict[str, Tuple[float, str, str]]
    ) -> str:
        """
        Identify limiting factors (subclass codes).
        
        FIXED: Changed threshold from 0.1 to 0.001 to only catch exact minimum ratings.
        
        Args:
            parameter_ratings: Dict mapping parameter names to (rating, class, subclass)
        
        Returns:
            Subclass codes string (e.g., "csf" for climate, soil, fertility limitations)
        """
        if not parameter_ratings:
            return ""
        
        # Find parameters with lowest ratings (limiting factors)
        min_rating = min(r[0] for r in parameter_ratings.values())
        
        # Collect subclass codes for parameters with minimum rating
        limiting_subclasses = set()
        for param_name, (rating, classification, subclass) in parameter_ratings.items():
            # FIXED: Only consider exact minimum (within 0.001 for floating point precision)
            # This prevents false positives from the previous 0.1 threshold
            if abs(rating - min_rating) < 0.001 and subclass:
                limiting_subclasses.add(subclass)
        
        # Sort alphabetically for consistency (c, f, n, s, t, w)
        return "".join(sorted(limiting_subclasses))
    
    def evaluate(
        self,
        crop_name: str,
        soil_data: Dict[str, float],
        season: Optional[str] = None
    ) -> Dict:
        """
        Evaluate crop suitability for given soil data.
        
        Args:
            crop_name: Name of the crop to evaluate
            soil_data: Dictionary of soil/climate parameters and their values
            season: Optional season for seasonal crops
        
        Returns:
            Dictionary containing LSI, classification, limiting factors, and details
        """
        parameter_ratings = {}
        
        # Map soil_data keys to crop requirement parameters
        parameter_mapping = {
            # Climate
            "temperature": ("climate_requirements", "mean_annual_temp_c"),
            "rainfall": ("climate_requirements", "annual_precipitation_mm"),
            "humidity": ("climate_requirements", "mean_relative_humidity_driest_month_pct"),
            "dry_season": ("climate_requirements", "dry_season_months"),
            "max_temp": ("climate_requirements", "mean_annual_max_temp_c"),
            "min_temp_coldest": ("climate_requirements", "mean_daily_min_temp_coldest_month_c"),
            "humidity_driest": ("climate_requirements", "mean_relative_humidity_driest_month_pct"),
            "n_over_N": ("climate_requirements", "n_over_N_5_driest_months"),
            
            # Topography
            "slope": ("topography_requirements", "slope_pct"),
            
            # Wetness
            "drainage": ("wetness_requirements", "drainage"),
            "flooding": ("wetness_requirements", "flooding"),
            
            # Physical Soil
            "texture": ("physical_soil_requirements", "texture"),
            "soil_depth": ("physical_soil_requirements", "soil_depth_cm"),
            "coarse_fragments": ("physical_soil_requirements", "coarse_fragments_pct"),
            "caco3": ("physical_soil_requirements", "caco3_pct"),
            "gypsum": ("physical_soil_requirements", "gypsum_pct"),
            
            # Soil Fertility
            "ph": ("soil_fertility_requirements", "ph_h2o"),
            "organic_carbon": ("soil_fertility_requirements", "organic_carbon_pct"),
            "base_saturation": ("soil_fertility_requirements", "base_saturation_pct"),
            "sum_basic_cations": ("soil_fertility_requirements", "sum_basic_cations_cmol_kg"),
            "cec": ("soil_fertility_requirements", "apparent_cec_cmol_kg_clay"),
            
            # Salinity
            "ec": ("salinity_alkalinity_requirements", "ece_ds_m"),
            "esp": ("salinity_alkalinity_requirements", "esp_pct"),
        }
        
        # Calculate rating for each parameter
        ratings_list = []
        
        # DEBUG OUTPUT - START
        print("\n" + "="*80)
        print(f"DEBUG: PARAMETER RATINGS FOR {crop_name}")
        print("="*80)
        
        for soil_key, value in soil_data.items():
            if soil_key in parameter_mapping:
                category, parameter = parameter_mapping[soil_key]
                
                try:
                    rating, classification, subclass = self.get_parameter_rating(
                        crop_name, category, parameter, value, season
                    )
                    
                    parameter_ratings[soil_key] = (rating, classification, subclass)
                    ratings_list.append(rating)
                    
                    # DEBUG: Print each parameter evaluation
                    print(f"{soil_key:20s} = {str(value):15s} → {classification:3s} ({rating:4.2f}) [{subclass}]")
                    
                except Exception as e:
                    print(f"⚠️ ERROR evaluating {soil_key}: {e}")
                    continue
            else:
                # DEBUG: Show parameters that are NOT in mapping
                print(f"{soil_key:20s} = {str(value):15s} → NOT MAPPED")
        
        print("="*80)
        print(f"Ratings list: {ratings_list}")
        print(f"Total parameters evaluated: {len(ratings_list)}")
        if ratings_list:
            print(f"Min rating (Rmin): {min(ratings_list):.2f}")
            print(f"Count of min rating: {ratings_list.count(min(ratings_list))}")
        print("="*80 + "\n")
        # DEBUG OUTPUT - END
        
        if not ratings_list:
            return {
                "crop_name": crop_name,
                "lsi": 0.0,
                "lsc": "N",
                "full_classification": "N",
                "limiting_factors": "",
                "parameter_ratings": {},
                "season": season
            }
        
        # Calculate LSI
        lsi = self.calculate_lsi(ratings_list)
        
        # Classify LSI
        lsc = self.classify_lsi(lsi)
        
        # Identify limiting factors
        limiting_factors = self.identify_limiting_factors(parameter_ratings)
        
        # Combine classification with limiting factors
        full_classification = f"{lsc}{limiting_factors}" if limiting_factors else lsc
        
        return {
            "crop_name": crop_name,
            "lsi": lsi,
            "lsc": lsc,
            "full_classification": full_classification,
            "limiting_factors": limiting_factors,
            "parameter_ratings": parameter_ratings,
            "season": season
        }