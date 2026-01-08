"""

Rules Engine for SoilWise - CORRECTED & VERIFIED WITH SEASONAL SUPPORT

Implements the Square Root Method for crop suitability evaluation

FORMULA: LSI = Rmin × √(product of ALL ratings) × 100

"""

import math
import logging
from typing import Dict, List, Tuple, Optional
from knowledge_base.crop_rules import CropRules

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    CORRECTED FORMULA: LSI = Rmin × √(product of ALL ratings) × 100
    SEASONAL SUPPORT: Handles crops with different requirements per season
    """
    
    def __init__(self):
        self.crop_rules = CropRules()
        logger.info("="*80)
        logger.info("RulesEngine initialized - CORRECTED FORMULA VERSION + SEASONAL SUPPORT")
        logger.info("Formula: LSI = Rmin × √(product of ALL ratings) × 100")
        logger.info("="*80)
    
    def get_parameter_rating(
        self,
        crop_name: str,
        category: str,
        parameter: str,
        value: float,
        season: Optional[str] = None
    ) -> Tuple[float, str, str]:
        """Get rating for a specific parameter value."""
        
        # Special handling for slope
        if parameter == "slope_pct":
            return self._get_slope_rating(crop_name, value)
        
        # ✅ FIXED: Pass season parameter to get_parameter_requirement
        requirements = self.crop_rules.get_parameter_requirement(
            crop_name, category, parameter, season=season
        )
        
        if not requirements:
            logger.warning(
                f"⚠️  No requirements for {parameter} in {category}. "
                f"Defaulting to S1 (1.0)"
            )
            return (1.0, "S1", self._get_subclass_code(category))
        
        subclass = self._get_subclass_code(category)
        
        # Check each classification level
        for classification_key, spec in requirements.items():
            if "range" in spec:
                min_val, max_val = spec["range"]
                if min_val is None:
                    min_val = float('-inf')
                if max_val is None:
                    max_val = float('inf')
                
                if min_val <= value <= max_val:
                    rating = spec["rating"]
                    classification = self._get_classification_from_key(classification_key)
                    logger.debug(
                        f"  ✓ {parameter} = {value} → {classification} "
                        f"(rating: {rating:.4f}, range: [{min_val}, {max_val}])"
                    )
                    return (rating, classification, subclass)
            
            elif "values" in spec:
                value_str = str(value)
                if value_str in spec["values"]:
                    rating = spec["rating"]
                    classification = self._get_classification_from_key(classification_key)
                    logger.debug(
                        f"  ✓ {parameter} = '{value_str}' → {classification} "
                        f"(rating: {rating:.4f})"
                    )
                    return (rating, classification, subclass)
        
        logger.warning(
            f"  ✗ No match for {parameter} = {value}. Defaulting to S1 (1.0)"
        )
        return (1.0, "S1", subclass)

    def _get_slope_rating(self, crop_name: str, slope_value: float) -> Tuple[float, str, str]:
            """Special handler for slope parameter - supports both level-based and direct structures."""
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
            
            # FIX: Try direct structure first (for Oil Palm, Banana, etc.)
            # Check if slope_reqs has direct classification keys (S1_0, S2, etc.)
            has_direct_structure = any(key.startswith(('S1', 'S2', 'S3', 'N')) for key in slope_reqs.keys())
            
            if has_direct_structure:
                logger.debug(f"Using DIRECT slope structure for {crop_name}")
                for classification_key, spec in slope_reqs.items():
                    if "range" not in spec:
                        continue
                    
                    min_val, max_val = spec["range"]
                    if min_val is None:
                        min_val = float('-inf')
                    if max_val is None:
                        max_val = float('inf')
                    
                    if min_val <= slope_value <= max_val:
                        rating = spec["rating"]
                        classification = self._get_classification_from_key(classification_key)
                        logger.debug(
                            f"  ✓ slope = {slope_value}% → {classification} "
                            f"(rating: {rating:.4f}, range: [{min_val}, {max_val}])"
                        )
                        return (rating, classification, "t")
            
            # ✅ FALLBACK: Try level-based structure (for Coffee crops)
            else:
                logger.debug(f"Using LEVEL-BASED slope structure for {crop_name}")
                level1 = slope_reqs.get('level1', {})
                
                if not level1:
                    logger.warning(f"No level1 found in slope requirements for {crop_name}")
                    return (0.25, "N", "t")
                
                for classification_key, spec in level1.items():
                    if "range" not in spec:
                        continue
                    
                    min_val, max_val = spec["range"]
                    if min_val is None:
                        min_val = float('-inf')
                    if max_val is None:
                        max_val = float('inf')
                    
                    if min_val <= slope_value <= max_val:
                        rating = spec["rating"]
                        classification = self._get_classification_from_key(classification_key)
                        logger.debug(
                            f"  ✓ slope = {slope_value}% → {classification} "
                            f"(rating: {rating:.4f})"
                        )
                        return (rating, classification, "t")
            
            # No match found
            logger.warning(f"No matching slope range found for {slope_value}%")
            return (0.25, "N", "t")

    
    def _get_classification_from_key(self, key: str) -> str:
        """Extract classification from key."""
        if key.startswith("S1"):
            return "S1"
        elif key.startswith("S2"):
            return "S2"
        elif key.startswith("S3"):
            return "S3"
        elif key.startswith("N"):
            return "N"
        else:
            return key
    
    def _get_subclass_code(self, category: str) -> str:
        """Get subclass code based on category."""
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
        Calculate LSI using CORRECTED formula.
        FORMULA: LSI = Rmin × √(product of ALL ratings) × 100
        
        Example with Arabica Coffee:
        ratings = [0.95, 0.60, 0.85, 0.95, 1.0, 1.0, 0.25, ...]
        Rmin = 0.25
        Product = 0.95 × 0.60 × ... × 0.25 = 0.088272
        √Product = 0.297106
        LSI = 0.25 × 0.297106 × 100 = 7.43 ✓
        """
        logger.info("\n" + "="*80)
        logger.info("CALCULATING LSI - CORRECTED FORMULA")
        logger.info("="*80)
        logger.info(f"Input ratings: {ratings}")
        logger.info(f"Number of parameters: {len(ratings)}")
        
        if not ratings:
            logger.error("❌ No ratings provided!")
            return 0.0
        
        # Step 1: Find Rmin
        rmin = min(ratings)
        logger.info(f"\n📍 Step 1: Find Rmin")
        logger.info(f"   Rmin = {rmin:.4f}")
        
        # Step 2: Calculate product of ALL ratings
        logger.info(f"\n📍 Step 2: Calculate product of ALL ratings")
        logger.info(f"   Including Rmin in the product calculation")
        
        # Show all non-1.0 ratings being multiplied
        non_one = [r for r in ratings if r != 1.0]
        logger.info(f"   Non-1.0 ratings: {non_one}")
        
        product = math.prod(ratings)
        logger.info(f"   Product = {product:.10f}")
        
        # Step 3: Square root
        sqrt_product = math.sqrt(product)
        logger.info(f"\n📍 Step 3: Calculate square root")
        logger.info(f"   √({product:.10f}) = {sqrt_product:.10f}")
        
        # Step 4: Calculate LSI
        logger.info(f"\n📍 Step 4: Calculate LSI")
        logger.info(f"   Formula: LSI = Rmin × √(product) × 100")
        logger.info(f"   LSI = {rmin:.4f} × {sqrt_product:.10f} × 100")
        
        lsi = rmin * sqrt_product * 100
        lsi_rounded = round(lsi, 2)
        
        logger.info(f"   LSI = {lsi:.10f}")
        logger.info(f"   LSI (rounded) = {lsi_rounded}")
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ FINAL LSI = {lsi_rounded}")
        logger.info("="*80 + "\n")
        
        return lsi_rounded
    
    def classify_lsi(self, lsi: float) -> str:
        """Classify LSI into suitability class."""
        if lsi >= 75:
            classification = "S1"
        elif lsi >= 50:
            classification = "S2"
        elif lsi >= 25:
            classification = "S3"
        else:
            classification = "N"
        
        logger.info(f"📊 Classification: LSI {lsi:.2f} → {classification}")
        return classification
    
    def identify_limiting_factors(
        self,
        parameter_ratings: Dict[str, Tuple[float, str, str]]
    ) -> str:
        """Identify limiting factors."""
        logger.info("\n" + "="*80)
        logger.info("IDENTIFYING LIMITING FACTORS")
        logger.info("="*80)
        
        if not parameter_ratings:
            return ""
        
        min_rating = min(r[0] for r in parameter_ratings.values())
        logger.info(f"Minimum rating (Rmin): {min_rating:.4f}")
        
        limiting_subclasses = set()
        threshold = 0.001
        
        logger.info(f"\nParameters with rating = {min_rating:.4f}:")
        for param_name, (rating, classification, subclass) in parameter_ratings.items():
            if abs(rating - min_rating) < threshold and subclass:
                limiting_subclasses.add(subclass)
                logger.info(
                    f"  🔴 {param_name}: {rating:.4f} ({classification}, subclass: {subclass})"
                )
        
        limiting_codes = "".join(sorted(limiting_subclasses))
        logger.info(f"\n⚠️  Limiting factors: {limiting_codes if limiting_codes else 'None'}")
        logger.info("="*80 + "\n")
        
        return limiting_codes
    
    def evaluate(
        self,
        crop_name: str,
        soil_data: Dict[str, float],
        season: Optional[str] = None
    ) -> Dict:
        """Evaluate crop suitability."""
        logger.info("\n" + "="*100)
        logger.info(f"🌱 EVALUATING: {crop_name}")
        if season:
            logger.info(f"🗓️  SEASON: {season}")
        logger.info("="*100)
        logger.info(f"Input parameters: {len(soil_data)}")
        
        parameter_ratings = {}
        
        parameter_mapping = {
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
        
        ratings_list = []
        
        logger.info("\n" + "-"*100)
        logger.info("PARAMETER EVALUATION")
        logger.info("-"*100)
        
        for soil_key, value in soil_data.items():
            if soil_key in parameter_mapping:
                category, parameter = parameter_mapping[soil_key]
                try:
                    # ✅ FIXED: Pass season to get_parameter_rating
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
                    logger.error(f"❌ Error evaluating {soil_key}: {e}", exc_info=True)
                    continue
            else:
                logger.debug(f"⚠️  {soil_key} not mapped")
        
        logger.info("-"*100)
        logger.info(f"✅ Evaluated {len(ratings_list)} parameters successfully")
        logger.info(f"📋 Ratings list: {ratings_list}")
        
        if not ratings_list:
            logger.error("❌ No parameters evaluated!")
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
        
        # Classify
        lsc = self.classify_lsi(lsi)
        
        # Limiting factors
        limiting_factors = self.identify_limiting_factors(parameter_ratings)
        
        full_classification = f"{lsc}{limiting_factors}" if limiting_factors else lsc
        
        logger.info("\n" + "="*100)
        logger.info("📊 FINAL RESULTS")
        logger.info("="*100)
        logger.info(f"Crop: {crop_name}")
        if season:
            logger.info(f"Season: {season}")
        logger.info(f"LSI: {lsi:.2f}")
        logger.info(f"Classification: {full_classification}")
        logger.info("="*100 + "\n")
        
        return {
            "crop_name": crop_name,
            "lsi": lsi,
            "lsc": lsc,
            "full_classification": full_classification,
            "limiting_factors": limiting_factors,
            "parameter_ratings": parameter_ratings,
            "season": season
        }
