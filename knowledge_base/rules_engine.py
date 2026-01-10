"""
Rules Engine for SoilWise - Land Suitability Evaluation

Implements the Square Root Method for crop suitability evaluation based on 
FAO Land Evaluation Framework.

FORMULA: LSI = R_min × √(∏ all ratings) × 100

Where:
    - R_min: Minimum rating among all evaluated parameters
    - ∏: Product of all parameter ratings
    - LSI: Land Suitability Index (0-100)

Classification:
    - S1 (Highly Suitable): LSI ≥ 75
    - S2 (Moderately Suitable): 50 ≤ LSI < 75
    - S3 (Marginally Suitable): 25 ≤ LSI < 50
    - N (Not Suitable): LSI < 25

Author: SoilWise Team
Version: 2.0 (with seasonal support)
"""

import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from knowledge_base.crop_rules import CropRules

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Land Suitability Evaluation Engine using the Square Root Method.
    
    Supports both seasonal and non-seasonal crops with comprehensive
    parameter evaluation across climate, topography, wetness, soil physical
    properties, soil fertility, and salinity/alkalinity.
    """
    
    # Classification thresholds
    LSI_THRESHOLDS = {
        'S1': 75.0,
        'S2': 50.0,
        'S3': 25.0,
        'N': 0.0
    }
    
    # Subclass codes for limiting factors
    SUBCLASS_CODES = {
        "climate_requirements": "c",
        "topography_requirements": "t",
        "wetness_requirements": "w",
        "physical_soil_requirements": "s",
        "soil_fertility_requirements": "f",
        "salinity_alkalinity_requirements": "n"
    }
    
    # Parameter mapping from soil data keys to requirement categories
    PARAMETER_MAPPING = {
        "temperature": ("climate_requirements", "mean_annual_temp_c"),
        "rainfall": ("climate_requirements", "annual_precipitation_mm"),
        "humidity": ("climate_requirements", "mean_relative_humidity_driest_month_pct"),
        "slope": ("topography_requirements", "slope_pct"),
        "drainage": ("wetness_requirements", "drainage"),
        "flooding": ("wetness_requirements", "flooding"),
        "texture": ("physical_soil_requirements", "texture"),
        "soil_depth": ("physical_soil_requirements", "soil_depth_cm"),
        "coarse_fragments": ("physical_soil_requirements", "coarse_fragments_pct"),
        "caco3": ("physical_soil_requirements", "caco3_pct"),
        "gypsum": ("physical_soil_requirements", "gypsum_pct"),
        "ph": ("soil_fertility_requirements", "ph_h2o"),
        "organic_carbon": ("soil_fertility_requirements", "organic_carbon_pct"),
        "base_saturation": ("soil_fertility_requirements", "base_saturation_pct"),
        "sum_basic_cations": ("soil_fertility_requirements", "sum_basic_cations_cmol_kg"),
        "cec": ("soil_fertility_requirements", "apparent_cec_cmol_kg_clay"),
        "ec": ("salinity_alkalinity_requirements", "ece_ds_m"),
        "esp": ("salinity_alkalinity_requirements", "esp_pct"),
    }
    
    def __init__(self):
        """Initialize the Rules Engine with crop requirements."""
        self.crop_rules = CropRules()
        logger.info("=" * 80)
        logger.info("RulesEngine initialized - Square Root Method")
        logger.info("Formula: LSI = R_min × √(∏ ratings) × 100")
        logger.info("=" * 80)
    
    def get_parameter_rating(
        self,
        crop_name: str,
        category: str,
        parameter: str,
        value: Any,
        season: Optional[str] = None
    ) -> Tuple[float, str, str]:
        """
        Get the rating for a specific parameter value.
        
        Args:
            crop_name: Name of the crop being evaluated
            category: Requirement category (e.g., 'climate_requirements')
            parameter: Specific parameter name (e.g., 'mean_annual_temp_c')
            value: Parameter value to evaluate
            season: Optional season for seasonal crops
            
        Returns:
            Tuple of (rating, classification, subclass_code)
            Example: (0.85, 'S2', 'c')
        """
        # Special handling for slope parameter
        if parameter == "slope_pct":
            return self._get_slope_rating(crop_name, value)
        
        # Get parameter requirements
        requirements = self.crop_rules.get_parameter_requirement(
            crop_name, category, parameter, season=season
        )
        
        if not requirements:
            logger.warning(
                f"⚠️  No requirements found for {parameter} in {category}. "
                f"Defaulting to S1 (1.0)"
            )
            return (1.0, "S1", self._get_subclass_code(category))
        
        subclass = self._get_subclass_code(category)
        
        # Evaluate parameter against requirements
        for classification_key, spec in requirements.items():
            # Handle range-based requirements (numeric values)
            if "range" in spec:
                if self._value_in_range(value, spec["range"]):
                    rating = spec["rating"]
                    classification = self._extract_classification(classification_key)
                    logger.debug(
                        f"  ✓ {parameter} = {value} → {classification} "
                        f"(rating: {rating:.4f}, range: {spec['range']})"
                    )
                    return (rating, classification, subclass)
            
            # Handle categorical requirements (text values)
            elif "values" in spec:
                if str(value) in spec["values"]:
                    rating = spec["rating"]
                    classification = self._extract_classification(classification_key)
                    logger.debug(
                        f"  ✓ {parameter} = '{value}' → {classification} "
                        f"(rating: {rating:.4f})"
                    )
                    return (rating, classification, subclass)
        
        # No match found - default to S1
        logger.warning(
            f"  ✗ No match for {parameter} = {value}. Defaulting to S1 (1.0)"
        )
        return (1.0, "S1", subclass)
    
    def _value_in_range(self, value: float, range_spec: List[Optional[float]]) -> bool:
        """
        Check if a value falls within a specified range.
        
        Args:
            value: Value to check
            range_spec: [min, max] where None means unbounded
            
        Returns:
            True if value is in range
        """
        min_val, max_val = range_spec
        min_val = float('-inf') if min_val is None else min_val
        max_val = float('inf') if max_val is None else max_val
        return min_val <= value <= max_val
    
    def _get_slope_rating(
        self,
        crop_name: str,
        slope_value: float
    ) -> Tuple[float, str, str]:
        """
        Special handler for slope parameter.
        
        Supports both direct structure (Oil Palm, Banana) and level-based 
        structure (Coffee crops).
        
        Args:
            crop_name: Name of the crop
            slope_value: Slope percentage value
            
        Returns:
            Tuple of (rating, classification, 't')
        """
        logger.debug(f"Evaluating slope = {slope_value}% for {crop_name}")
        
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        if not crop_data:
            logger.warning(f"No crop data found for {crop_name}")
            return (0.25, "N", "t")
        
        topo_reqs = crop_data.get('topography_requirements', {})
        slope_reqs = topo_reqs.get('slope_pct', {})
        
        if not slope_reqs:
            logger.warning(f"No slope requirements found for {crop_name}")
            return (0.25, "N", "t")
        
        # Check structure type: direct vs level-based
        has_direct_structure = any(
            key.startswith(('S1', 'S2', 'S3', 'N')) 
            for key in slope_reqs.keys()
        )
        
        if has_direct_structure:
            # Direct structure (e.g., Oil Palm, Banana)
            logger.debug(f"Using direct slope structure for {crop_name}")
            return self._evaluate_slope_direct(slope_reqs, slope_value)
        else:
            # Level-based structure (e.g., Coffee crops)
            logger.debug(f"Using level-based slope structure for {crop_name}")
            return self._evaluate_slope_level_based(slope_reqs, slope_value)
    
    def _evaluate_slope_direct(
        self,
        slope_reqs: Dict,
        slope_value: float
    ) -> Tuple[float, str, str]:
        """Evaluate slope using direct structure."""
        for classification_key, spec in slope_reqs.items():
            if "range" not in spec:
                continue
            
            if self._value_in_range(slope_value, spec["range"]):
                rating = spec["rating"]
                classification = self._extract_classification(classification_key)
                logger.debug(
                    f"  ✓ slope = {slope_value}% → {classification} "
                    f"(rating: {rating:.4f}, range: {spec['range']})"
                )
                return (rating, classification, "t")
        
        logger.warning(f"No matching slope range found for {slope_value}%")
        return (0.25, "N", "t")
    
    def _evaluate_slope_level_based(
        self,
        slope_reqs: Dict,
        slope_value: float
    ) -> Tuple[float, str, str]:
        """Evaluate slope using level-based structure (uses level1)."""
        level1 = slope_reqs.get('level1', {})
        
        if not level1:
            logger.warning("No level1 found in slope requirements")
            return (0.25, "N", "t")
        
        for classification_key, spec in level1.items():
            if "range" not in spec:
                continue
            
            if self._value_in_range(slope_value, spec["range"]):
                rating = spec["rating"]
                classification = self._extract_classification(classification_key)
                logger.debug(
                    f"  ✓ slope = {slope_value}% → {classification} "
                    f"(rating: {rating:.4f})"
                )
                return (rating, classification, "t")
        
        logger.warning(f"No matching slope range found for {slope_value}%")
        return (0.25, "N", "t")
    
    def _extract_classification(self, key: str) -> str:
        """
        Extract base classification from a classification key.
        
        Args:
            key: Classification key (e.g., 'S1_0', 'S2_high', 'N2_low')
            
        Returns:
            Base classification (e.g., 'S1', 'S2', 'N')
        """
        if key.startswith("S1"):
            return "S1"
        elif key.startswith("S2"):
            return "S2"
        elif key.startswith("S3"):
            return "S3"
        elif key.startswith("N"):
            return "N"
        return key
    
    def _get_subclass_code(self, category: str) -> str:
        """
        Get the subclass code for a requirement category.
        
        Args:
            category: Requirement category name
            
        Returns:
            Single letter subclass code
        """
        return self.SUBCLASS_CODES.get(category, "")
    
    def calculate_lsi(self, ratings: List[float]) -> float:
        """
        Calculate Land Suitability Index using the Square Root Method.
        
        Formula: LSI = R_min × √(∏ ratings) × 100
        
        Args:
            ratings: List of parameter ratings (0.0 to 1.0)
            
        Returns:
            LSI value (0-100)
            
        Example:
            ratings = [0.95, 0.60, 0.85, 0.95, 1.0, 0.25]
            R_min = 0.25
            Product = 0.95 × 0.60 × 0.85 × 0.95 × 1.0 × 0.25 = 0.115
            √Product = 0.339
            LSI = 0.25 × 0.339 × 100 = 8.47
        """
        logger.info("\n" + "=" * 80)
        logger.info("CALCULATING LSI - SQUARE ROOT METHOD")
        logger.info("=" * 80)
        logger.info(f"Input ratings: {ratings}")
        logger.info(f"Number of parameters: {len(ratings)}")
        
        if not ratings:
            logger.error("❌ No ratings provided!")
            return 0.0
        
        # Step 1: Find minimum rating (R_min)
        rmin = min(ratings)
        logger.info(f"\n📍 Step 1: Find R_min")
        logger.info(f"   R_min = {rmin:.4f}")
        
        # Step 2: Calculate product of all ratings
        logger.info(f"\n📍 Step 2: Calculate product of all ratings")
        non_one_ratings = [r for r in ratings if r != 1.0]
        if non_one_ratings:
            logger.info(f"   Non-1.0 ratings: {non_one_ratings}")
        
        product = math.prod(ratings)
        logger.info(f"   Product (∏) = {product:.10f}")
        
        # Step 3: Calculate square root
        sqrt_product = math.sqrt(product)
        logger.info(f"\n📍 Step 3: Calculate square root")
        logger.info(f"   √({product:.10f}) = {sqrt_product:.10f}")
        
        # Step 4: Calculate LSI
        logger.info(f"\n📍 Step 4: Calculate LSI")
        logger.info(f"   Formula: LSI = R_min × √(product) × 100")
        logger.info(f"   LSI = {rmin:.4f} × {sqrt_product:.10f} × 100")
        
        lsi = rmin * sqrt_product * 100
        lsi_rounded = round(lsi, 2)
        
        logger.info(f"   LSI = {lsi:.10f}")
        logger.info(f"   LSI (rounded) = {lsi_rounded}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ FINAL LSI = {lsi_rounded}")
        logger.info("=" * 80 + "\n")
        
        return lsi_rounded
    
    def classify_lsi(self, lsi: float) -> str:
        """
        Classify LSI into a suitability class.
        
        Args:
            lsi: Land Suitability Index (0-100)
            
        Returns:
            Suitability class ('S1', 'S2', 'S3', or 'N')
        """
        if lsi >= self.LSI_THRESHOLDS['S1']:
            classification = "S1"
        elif lsi >= self.LSI_THRESHOLDS['S2']:
            classification = "S2"
        elif lsi >= self.LSI_THRESHOLDS['S3']:
            classification = "S3"
        else:
            classification = "N"
        
        logger.info(f"📊 Classification: LSI {lsi:.2f} → {classification}")
        return classification
    
    def identify_limiting_factors(
        self,
        parameter_ratings: Dict[str, Tuple[float, str, str]]
    ) -> str:
        """
        Identify limiting factors based on minimum ratings.
        
        Limiting factors are those parameters that have the minimum rating
        and thus constrain the land suitability.
        
        Args:
            parameter_ratings: Dict mapping parameter names to 
                             (rating, classification, subclass) tuples
            
        Returns:
            String of limiting factor codes (e.g., 'cf' for climate and fertility)
        """
        logger.info("\n" + "=" * 80)
        logger.info("IDENTIFYING LIMITING FACTORS")
        logger.info("=" * 80)
        
        if not parameter_ratings:
            return ""
        
        min_rating = min(r[0] for r in parameter_ratings.values())
        logger.info(f"Minimum rating (R_min): {min_rating:.4f}")
        
        limiting_subclasses = set()
        tolerance = 0.001  # Tolerance for floating point comparison
        
        logger.info(f"\nParameters with rating ≈ {min_rating:.4f}:")
        for param_name, (rating, classification, subclass) in parameter_ratings.items():
            if abs(rating - min_rating) < tolerance and subclass:
                limiting_subclasses.add(subclass)
                logger.info(
                    f"  🔴 {param_name}: {rating:.4f} "
                    f"({classification}, subclass: {subclass})"
                )
        
        limiting_codes = "".join(sorted(limiting_subclasses))
        logger.info(
            f"\n⚠️  Limiting factors: {limiting_codes if limiting_codes else 'None'}"
        )
        logger.info("=" * 80 + "\n")
        
        return limiting_codes
    
    def evaluate(
        self,
        crop_name: str,
        soil_data: Dict[str, Any],
        season: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate crop suitability for given soil and climate conditions.
        
        Args:
            crop_name: Name of the crop to evaluate
            soil_data: Dictionary of parameter names to values
            season: Optional season for seasonal crops
            
        Returns:
            Dictionary containing:
                - crop_name: Name of evaluated crop
                - lsi: Land Suitability Index (0-100)
                - lsc: Land Suitability Class ('S1', 'S2', 'S3', 'N')
                - full_classification: Class with limiting factors (e.g., 'S2cf')
                - limiting_factors: Limiting factor codes (e.g., 'cf')
                - parameter_ratings: Detailed ratings for each parameter
                - season: Season (if applicable)
        """
        logger.info("\n" + "=" * 100)
        logger.info(f"🌱 EVALUATING: {crop_name}")
        if season:
            logger.info(f"🗓️  SEASON: {season}")
        logger.info("=" * 100)
        logger.info(f"Input parameters: {len(soil_data)}")
        
        parameter_ratings = {}
        ratings_list = []
        
        logger.info("\n" + "-" * 100)
        logger.info("PARAMETER EVALUATION")
        logger.info("-" * 100)
        
        # Evaluate each parameter
        for soil_key, value in soil_data.items():
            if soil_key not in self.PARAMETER_MAPPING:
                logger.debug(f"⚠️  {soil_key} not in parameter mapping")
                continue
            
            category, parameter = self.PARAMETER_MAPPING[soil_key]
            
            try:
                rating, classification, subclass = self.get_parameter_rating(
                    crop_name, category, parameter, value, season
                )
                
                parameter_ratings[soil_key] = (rating, classification, subclass)
                ratings_list.append(rating)
                
                logger.info(
                    f"{soil_key:<25} = {str(value):<15} → {classification:<8} "
                    f"(rating: {rating:.4f}, subclass: {subclass})"
                )
            except Exception as e:
                logger.error(
                    f"❌ Error evaluating {soil_key}: {e}",
                    exc_info=True
                )
                continue
        
        logger.info("-" * 100)
        logger.info(f"✅ Evaluated {len(ratings_list)} parameters successfully")
        
        # Handle case with no valid ratings
        if not ratings_list:
            logger.error("❌ No parameters were successfully evaluated!")
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
        
        # Create full classification with limiting factors
        full_classification = f"{lsc}{limiting_factors}" if limiting_factors else lsc
        
        # Log final results
        logger.info("\n" + "=" * 100)
        logger.info("📊 FINAL RESULTS")
        logger.info("=" * 100)
        logger.info(f"Crop: {crop_name}")
        if season:
            logger.info(f"Season: {season}")
        logger.info(f"LSI: {lsi:.2f}")
        logger.info(f"Classification: {full_classification}")
        logger.info("=" * 100 + "\n")
        
        return {
            "crop_name": crop_name,
            "lsi": lsi,
            "lsc": lsc,
            "full_classification": full_classification,
            "limiting_factors": limiting_factors,
            "parameter_ratings": parameter_ratings,
            "season": season
        }


# Example usage
if __name__ == "__main__":
    engine = RulesEngine()
    
    # Example soil data
    test_soil_data = {
        "temperature": 26.5,
        "rainfall": 2000,
        "humidity": 70,
        "slope": 2.5,
        "drainage": "good",
        "flooding": "Fo",
        "texture": "CL",
        "soil_depth": 150,
        "coarse_fragments": 5,
        "caco3": 1.0,
        "gypsum": 0.5,
        "ph": 6.0,
        "organic_carbon": 2.0,
        "base_saturation": 60,
        "sum_basic_cations": 5.0,
        "cec": 20,
        "ec": 1.5,
        "esp": 3.0
    }
    
    # Evaluate
    result = engine.evaluate("Arabica Coffee", test_soil_data)
    print(f"\nFinal Result: {result['full_classification']} (LSI: {result['lsi']:.2f})")