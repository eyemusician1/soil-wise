"""
SoilWise Crop Suitability Evaluator - ENHANCED VERSION

Orchestrates the complete evaluation workflow using the Square Root Method
Reference: Khiddir et al. 1986, FAO 1976, Sys et al. 1993
"""

import logging
from typing import Dict, List, Optional, Tuple

from knowledge_base.crop_rules import CropRules
from knowledge_base.rules_engine import RulesEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class SuitabilityEvaluator:
    """
    High-level evaluator that orchestrates crop suitability assessment.

    This class:
    1. Loads crop requirements from the knowledge base
    2. Evaluates soil data against crop requirements
    3. Calculates Land Suitability Index (LSI) using Square Root Method
    4. Identifies limiting factors
    5. Generates comprehensive evaluation reports
    """

    def __init__(self) -> None:
        logger.info("Initializing SuitabilityEvaluator...")
        self.crop_rules = CropRules()
        self.rules_engine = RulesEngine()
        num_crops = len(self.crop_rules.get_crop_names())
        logger.info("✓ SuitabilityEvaluator initialized with %d crops", num_crops)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def evaluate_suitability(
        self,
        soil_data: Dict[str, float],
        crop_name: str,
        season: Optional[str] = None,
    ) -> Dict:
        """
        Evaluate crop suitability for given soil data.

        Args:
            soil_data: Dictionary containing soil and climate parameters.
            crop_name: Name of the crop to evaluate.
            season: Optional season for seasonal crops.

        Returns:
            Dictionary containing comprehensive evaluation results.
            Always includes a 'soil_data' key so UI pages can reuse it.
        """
        logger.info("\n" + "=" * 100)
        logger.info("STARTING SUITABILITY EVALUATION")
        logger.info("=" * 100)
        logger.info("Crop: %s", crop_name)
        logger.info("Season: %s", season if season else "N/A")
        logger.info("Input parameters: %d", len(soil_data))

        # Validate crop exists
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        if not crop_data:
            error_msg = f"Crop '{crop_name}' not found in knowledge base"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("✓ Crop data loaded successfully")

        # Check if crop is seasonal and season is provided
        if crop_data.get("seasonal", False) and not season:
            available_seasons = crop_data.get("seasons", [])
            error_msg = (
                f"{crop_name} is a seasonal crop. "
                f"Please specify season: {', '.join(available_seasons)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log input data
        logger.info("\n" + "-" * 100)
        logger.info("INPUT SOIL/CLIMATE DATA")
        logger.info("-" * 100)
        for key, value in sorted(soil_data.items()):
            logger.info(" %-30s = %s", key, value)
        logger.info("-" * 100)

        # Perform evaluation using rules engine
        evaluation_result = self.rules_engine.evaluate(crop_name, soil_data, season)

        # Enrich result with additional information (and attach soil_data)
        enriched_result = self._enrich_evaluation_result(
            evaluation_result,
            crop_data,
            soil_data,
            crop_name,
            season,
        )

        logger.info("\n" + "=" * 100)
        logger.info("EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 100 + "\n")

        return enriched_result

    def evaluate_multiple_crops(
        self,
        soil_data: Dict[str, float],
        crop_names: Optional[List[str]] = None,
        season: Optional[str] = None,
    ) -> List[Dict]:
        """
        Evaluate suitability for multiple crops.

        Args:
            soil_data: Dictionary containing soil and climate parameters.
            crop_names: List of crop names to evaluate. If None, evaluates all crops.
            season: Optional season for seasonal crops.

        Returns:
            List of evaluation result dictionaries, sorted by LSI (descending).
        """
        if crop_names is None:
            crop_names = self.crop_rules.get_crop_names()

        logger.info("\n" + "=" * 100)
        logger.info("EVALUATING MULTIPLE CROPS")
        logger.info("=" * 100)
        logger.info("Number of crops to evaluate: %d", len(crop_names))
        logger.info("Crops: %s", ", ".join(crop_names))

        results: List[Dict] = []
        success_count = 0
        failure_count = 0

        for i, crop_name in enumerate(crop_names, 1):
            logger.info("\n[%d/%d] Evaluating %s...", i, len(crop_names), crop_name)
            try:
                result = self.evaluate_suitability(soil_data, crop_name, season)
                results.append(result)
                success_count += 1
                logger.info(
                    " ✓ %s: LSI = %.2f, Class = %s",
                    crop_name,
                    result["lsi"],
                    result["full_classification"],
                )
            except Exception as e:
                failure_count += 1
                logger.error(" ✗ Failed to evaluate %s: %s", crop_name, str(e))
                continue

        # Sort by LSI (descending)
        results.sort(key=lambda x: x["lsi"], reverse=True)

        logger.info("\n" + "=" * 100)
        logger.info("MULTIPLE CROP EVALUATION SUMMARY")
        logger.info("=" * 100)
        logger.info("Successfully evaluated: %d/%d", success_count, len(crop_names))
        logger.info("Failed evaluations: %d/%d", failure_count, len(crop_names))

        if results:
            logger.info("\nTop 3 Most Suitable Crops:")
            for i, result in enumerate(results[:3], 1):
                logger.info(
                    " %d. %s: LSI = %.2f, Class = %s",
                    i,
                    result["crop_name"],
                    result["lsi"],
                    result["full_classification"],
                )

        logger.info("=" * 100 + "\n")
        return results

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _enrich_evaluation_result(
        self,
        evaluation_result: Dict,
        crop_data: Dict,
        soil_data: Dict,
        crop_name: str,
        season: Optional[str],
    ) -> Dict:
        """
        Enrich evaluation result with additional information and recommendations.
        Also attaches soil_data and metadata for UI reuse.
        """
        logger.debug("Enriching evaluation result...")

        enriched = evaluation_result.copy()

        # Attach original inputs so UI pages can reuse them
        enriched["soil_data"] = soil_data
        enriched["crop_name"] = enriched.get("crop_name", crop_name)
        if season is not None:
            enriched["season"] = season

        # Add scientific name
        enriched["scientific_name"] = crop_data.get("scientific_name", "N/A")

        # Add detailed limiting factors
        enriched["limiting_factors_detailed"] = self._get_limiting_factors_details(
            evaluation_result.get("parameter_ratings", {}),
            soil_data,
        )

        # Generate recommendations
        enriched["recommendations"] = self._generate_recommendations(
            evaluation_result,
            soil_data,
        )

        # Add interpretation
        enriched["interpretation"] = self._get_interpretation(
            evaluation_result["lsc"],
            evaluation_result["lsi"],
        )

        # Add notes from crop data
        enriched["notes"] = crop_data.get("notes", "")

        logger.debug("Evaluation result enriched successfully")
        return enriched

    def _get_limiting_factors_details(
        self,
        parameter_ratings: Dict[str, Tuple[float, str, str]],
        soil_data: Dict,
    ) -> List[Dict]:
        """
        Get detailed information about limiting factors.
        ✅ If all ratings are perfect (>= 1.0), no limiting factors are returned.
        """
        if not parameter_ratings:
            return []

        # Find minimum rating
        min_rating = min(r[0] for r in parameter_ratings.values())

        # If all ratings are perfect
        if min_rating >= 1.0:
            logger.info(
                "✅ No limiting factors - all parameters are highly suitable (S1)"
            )
            return []

        limiting_details: List[Dict] = []
        threshold = 0.001  # Tolerance for floating-point comparison

        for param_name, (rating, classification, subclass) in parameter_ratings.items():
            if abs(rating - min_rating) < threshold:
                actual_value = soil_data.get(param_name, "N/A")
                limiting_details.append(
                    {
                        "parameter": param_name,
                        "actual_value": actual_value,
                        "rating": rating,
                        "classification": classification,
                        "subclass": subclass,
                        "description": self._get_parameter_description(param_name),
                        "category": self._get_category_name(subclass),
                    }
                )

        logger.info("Identified %d limiting factor(s)", len(limiting_details))
        return limiting_details

    def _get_parameter_description(self, param_name: str) -> str:
        """Get human-readable description of parameter."""
        descriptions = {
            "temperature": "Mean Annual Temperature",
            "rainfall": "Annual Precipitation",
            "humidity": "Relative Humidity",
            "ph": "Soil pH",
            "organic_carbon": "Organic Carbon Content",
            "organic_matter": "Organic Matter Content",
            "nitrogen": "Available Nitrogen",
            "phosphorus": "Available Phosphorus",
            "potassium": "Available Potassium",
            "texture": "Soil Texture",
            "soil_depth": "Soil Depth",
            "drainage": "Drainage Condition",
            "flooding": "Flooding Risk",
            "slope": "Slope Percentage",
            "coarse_fragments": "Coarse Fragments",
            "base_saturation": "Base Saturation",
            "cec": "Cation Exchange Capacity",
            "ec": "Electrical Conductivity",
            "esp": "Exchangeable Sodium Percentage",
            "dry_season": "Dry Season Length",
            "max_temp": "Maximum Temperature",
            "min_temp_coldest": "Minimum Temperature (Coldest Month)",
            "caco3": "Calcium Carbonate Content",
            "gypsum": "Gypsum Content",
            "sum_basic_cations": "Sum of Basic Cations",
        }
        return descriptions.get(param_name, param_name.replace("_", " ").title())

    def _get_category_name(self, subclass: str) -> str:
        """Get category name from subclass code."""
        categories = {
            "c": "Climate",
            "t": "Topography",
            "w": "Wetness",
            "s": "Physical Soil",
            "f": "Soil Fertility",
            "n": "Salinity/Alkalinity",
        }
        return categories.get(subclass, "Unknown")

    def _generate_recommendations(
        self,
        evaluation_result: Dict,
        soil_data: Dict,
    ) -> List[str]:
        """
        Generate agronomic recommendations based on evaluation results.
        ✅ Special handling for S1 with no limiting factors.
        """
        logger.debug("Generating recommendations...")

        recommendations: List[str] = []
        lsc = evaluation_result["lsc"]
        limiting_factors = evaluation_result.get("limiting_factors", "")

        # Special case for perfect suitability
        if lsc == "S1" and not limiting_factors:
            recommendations.append(
                "✓ This crop is highly suitable for the given soil conditions "
                "with no limiting factors. Standard cultivation practices are "
                "recommended for optimal yields."
            )
            logger.info("Generated %d recommendation(s)", len(recommendations))
            return recommendations

        # General suitability recommendation
        if lsc == "S1":
            recommendations.append(
                "✓ This crop is highly suitable for the given soil conditions. "
                "Standard cultivation practices are recommended."
            )
        elif lsc == "S2":
            recommendations.append(
                "⚠ This crop is moderately suitable. Some management interventions "
                "are needed to address limiting factors."
            )
        elif lsc == "S3":
            recommendations.append(
                "⚠ This crop is marginally suitable. Significant management "
                "interventions are required. Consider alternative crops."
            )
        else:  # N
            recommendations.append(
                "✗ This crop is not suitable for the given conditions. "
                "Strongly recommend selecting alternative crops."
            )

        # Specific recommendations based on limiting factor groups
        if "f" in limiting_factors:
            recommendations.extend(self._get_fertility_recommendations(soil_data))
        if "c" in limiting_factors:
            recommendations.append(
                "• Climate conditions are limiting. Consider protected cultivation "
                "or select more climate-adapted varieties."
            )
        if "w" in limiting_factors:
            recommendations.extend(self._get_drainage_recommendations(soil_data))
        if "s" in limiting_factors:
            recommendations.extend(self._get_physical_soil_recommendations(soil_data))
        if "t" in limiting_factors:
            recommendations.append(
                "• Slope is limiting. Implement soil conservation measures "
                "such as terracing or contour farming."
            )
        if "n" in limiting_factors:
            recommendations.append(
                "• Salinity/alkalinity is limiting. Consider leaching, "
                "gypsum application, or salt-tolerant varieties."
            )

        logger.info("Generated %d recommendation(s)", len(recommendations))
        return recommendations

    def _get_fertility_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate fertility-specific recommendations."""
        recommendations: List[str] = []

        ph = soil_data.get("ph")
        if ph is not None:
            if ph < 5.5:
                recommendations.append(
                    f"• Soil is strongly acidic (pH {ph:.2f}). Apply lime to "
                    "raise pH to 6.0–6.5."
                )
            elif ph > 7.5:
                recommendations.append(
                    f"• Soil is alkaline (pH {ph:.2f}). Consider sulfur "
                    "application to lower pH."
                )

        oc = soil_data.get("organic_carbon")
        om = soil_data.get("organic_matter")
        if oc is not None and oc < 1.5:
            recommendations.append(
                f"• Organic carbon is low ({oc:.2f}%). Incorporate compost, "
                "manure, or green manure to improve soil health."
            )
        elif om is not None and om < 2.0:
            recommendations.append(
                f"• Organic matter is low ({om:.2f}%). Incorporate compost, "
                "manure, or green manure to improve soil health."
            )

        return recommendations

    def _get_drainage_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate drainage-specific recommendations."""
        recommendations: List[str] = []

        drainage = soil_data.get("drainage")
        if drainage in ["poor", "poor_not_drainable"]:
            recommendations.append(
                "• Poor drainage detected. Install drainage systems or "
                "raise beds to improve water management."
            )

        flooding = soil_data.get("flooding")
        if flooding and flooding != "Fo":
            recommendations.append(
                "• Flooding risk present. Implement flood protection measures "
                "or select flood-tolerant varieties."
            )

        return recommendations

    def _get_physical_soil_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate physical soil recommendations."""
        recommendations: List[str] = []

        texture = soil_data.get("texture")
        if texture in ["S", "LS", "fS"]:
            recommendations.append(
                "• Sandy texture limits water retention. Increase irrigation "
                "frequency and add organic matter to improve water-holding capacity."
            )
        elif texture in ["C", "SiC", "Cm"]:
            recommendations.append(
                "• Heavy clay texture limits drainage and root penetration. "
                "Add organic matter and practice deep tillage to improve structure."
            )

        depth = soil_data.get("soil_depth")
        if depth is not None and depth < 50:
            recommendations.append(
                f"• Shallow soil depth ({depth} cm) limits root growth. "
                "Consider raised beds or select shallow-rooted crops."
            )

        return recommendations

    def _get_interpretation(self, lsc: str, lsi: float) -> str:
        """Get interpretation text for the suitability classification."""
        interpretations = {
            "S1": (
                f"Highly Suitable (LSI: {lsi:.2f}). "
                "Land has no significant limitations for sustained application "
                "of the given use. Expected yields are high with minimal inputs."
            ),
            "S2": (
                f"Moderately Suitable (LSI: {lsi:.2f}). "
                "Land has limitations that reduce productivity or require "
                "increased inputs. Expected yields are moderate with proper "
                "management."
            ),
            "S3": (
                f"Marginally Suitable (LSI: {lsi:.2f}). "
                "Land has severe limitations that reduce productivity or "
                "require intensive management. Expected yields are low even "
                "with inputs."
            ),
            "N": (
                f"Not Suitable (LSI: {lsi:.2f}). "
                "Land has limitations so severe that they preclude successful "
                "sustained use. Cultivation is not recommended."
            ),
        }
        return interpretations.get(lsc, f"Classification: {lsc}, LSI: {lsi:.2f}")

    # Convenience methods for other components (e.g., Knowledge Base page)

    def get_available_crops(self) -> List[str]:
        """Get list of all available crops in the knowledge base."""
        return self.crop_rules.get_crop_names()

    def get_crop_info(self, crop_name: str) -> Optional[Dict]:
        """Get basic information about a crop."""
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        return {
            "name": crop_data.get("crop_name"),
            "scientific_name": crop_data.get("scientific_name"),
            "seasonal": crop_data.get("seasonal", False),
            "seasons": crop_data.get("seasons", []),
            "notes": crop_data.get("notes", ""),
        }


if __name__ == "__main__":
    # Optional CLI/demo left as in your original file (trim or remove for production)
    pass
