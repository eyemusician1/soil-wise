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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    
    def __init__(self):
        logger.info("Initializing SuitabilityEvaluator...")
        self.crop_rules = CropRules()
        self.rules_engine = RulesEngine()
        num_crops = len(self.crop_rules.get_crop_names())
        logger.info(f"✓ SuitabilityEvaluator initialized with {num_crops} crops")
    
    def evaluate_suitability(
        self,
        soil_data: Dict[str, float],
        crop_name: str,
        season: Optional[str] = None
    ) -> Dict:
        """
        Evaluate crop suitability for given soil data.
        
        Args:
            soil_data: Dictionary containing soil and climate parameters
            crop_name: Name of the crop to evaluate
            season: Optional season for seasonal crops
            
        Returns:
            Dictionary containing comprehensive evaluation results
        """
        logger.info("\n" + "="*100)
        logger.info(f"STARTING SUITABILITY EVALUATION")
        logger.info("="*100)
        logger.info(f"Crop: {crop_name}")
        logger.info(f"Season: {season if season else 'N/A'}")
        logger.info(f"Input parameters: {len(soil_data)}")
        
        # Validate crop exists
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        if not crop_data:
            error_msg = f"Crop '{crop_name}' not found in knowledge base"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✓ Crop data loaded successfully")
        
        # Check if crop is seasonal and season is provided
        if crop_data.get('seasonal', False) and not season:
            available_seasons = crop_data.get('seasons', [])
            error_msg = (
                f"{crop_name} is a seasonal crop. "
                f"Please specify season: {', '.join(available_seasons)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log input data
        logger.info("\n" + "-"*100)
        logger.info("INPUT SOIL/CLIMATE DATA")
        logger.info("-"*100)
        for key, value in sorted(soil_data.items()):
            logger.info(f"  {key:<30} = {value}")
        logger.info("-"*100)
        
        # Perform evaluation using rules engine
        evaluation_result = self.rules_engine.evaluate(crop_name, soil_data, season)
        
        # Enrich result with additional information
        enriched_result = self._enrich_evaluation_result(
            evaluation_result,
            crop_data,
            soil_data
        )
        
        logger.info("\n" + "="*100)
        logger.info("EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("="*100 + "\n")
        
        return enriched_result
    
    def evaluate_multiple_crops(
        self,
        soil_data: Dict[str, float],
        crop_names: Optional[List[str]] = None,
        season: Optional[str] = None
    ) -> List[Dict]:
        """
        Evaluate suitability for multiple crops.
        
        Args:
            soil_data: Dictionary containing soil and climate parameters
            crop_names: List of crop names to evaluate. If None, evaluates all crops.
            season: Optional season for seasonal crops
            
        Returns:
            List of evaluation result dictionaries, sorted by LSI (descending)
        """
        if crop_names is None:
            crop_names = self.crop_rules.get_crop_names()
        
        logger.info("\n" + "="*100)
        logger.info(f"EVALUATING MULTIPLE CROPS")
        logger.info("="*100)
        logger.info(f"Number of crops to evaluate: {len(crop_names)}")
        logger.info(f"Crops: {', '.join(crop_names)}")
        
        results = []
        success_count = 0
        failure_count = 0
        
        for i, crop_name in enumerate(crop_names, 1):
            logger.info(f"\n[{i}/{len(crop_names)}] Evaluating {crop_name}...")
            try:
                result = self.evaluate_suitability(soil_data, crop_name, season)
                results.append(result)
                success_count += 1
                logger.info(f"  ✓ {crop_name}: LSI = {result['lsi']:.2f}, Class = {result['full_classification']}")
            except Exception as e:
                failure_count += 1
                logger.error(f"  ✗ Failed to evaluate {crop_name}: {str(e)}")
                continue
        
        # Sort by LSI (descending)
        results.sort(key=lambda x: x['lsi'], reverse=True)
        
        logger.info("\n" + "="*100)
        logger.info(f"MULTIPLE CROP EVALUATION SUMMARY")
        logger.info("="*100)
        logger.info(f"Successfully evaluated: {success_count}/{len(crop_names)}")
        logger.info(f"Failed evaluations: {failure_count}/{len(crop_names)}")
        
        if results:
            logger.info(f"\nTop 3 Most Suitable Crops:")
            for i, result in enumerate(results[:3], 1):
                logger.info(
                    f"  {i}. {result['crop_name']}: "
                    f"LSI = {result['lsi']:.2f}, "
                    f"Class = {result['full_classification']}"
                )
        
        logger.info("="*100 + "\n")
        
        return results
    
    def _enrich_evaluation_result(
        self,
        evaluation_result: Dict,
        crop_data: Dict,
        soil_data: Dict
    ) -> Dict:
        """
        Enrich evaluation result with additional information and recommendations.
        """
        logger.debug("Enriching evaluation result...")
        
        enriched = evaluation_result.copy()
        
        # Add scientific name
        enriched['scientific_name'] = crop_data.get('scientific_name', 'N/A')
        
        # Add detailed limiting factors
        enriched['limiting_factors_detailed'] = self._get_limiting_factors_details(
            evaluation_result['parameter_ratings'],
            soil_data
        )
        
        # Generate recommendations
        enriched['recommendations'] = self._generate_recommendations(
            evaluation_result,
            soil_data
        )
        
        # Add interpretation
        enriched['interpretation'] = self._get_interpretation(
            evaluation_result['lsc'],
            evaluation_result['lsi']
        )
        
        # Add notes from crop data
        enriched['notes'] = crop_data.get('notes', '')
        
        logger.debug("Evaluation result enriched successfully")
        
        return enriched
    
    def _get_limiting_factors_details(
        self,
        parameter_ratings: Dict[str, Tuple[float, str, str]],
        soil_data: Dict
    ) -> List[Dict]:
        """
        Get detailed information about limiting factors.
        
        ✅ MODIFIED: Added check for perfect score (min_rating == 1.0)
        """
        if not parameter_ratings:
            return []
        
        # Find minimum rating
        min_rating = min(r[0] for r in parameter_ratings.values())
        
        # ✅ NEW: If all ratings are perfect (1.0), no limiting factors
        if min_rating >= 1.0:
            logger.info("✅ No limiting factors - all parameters are highly suitable (S1)")
            return []
        
        limiting_details = []
        threshold = 0.001  # Tolerance for floating-point comparison
        
        for param_name, (rating, classification, subclass) in parameter_ratings.items():
            if abs(rating - min_rating) < threshold:
                actual_value = soil_data.get(param_name, 'N/A')
                
                limiting_details.append({
                    'parameter': param_name,
                    'actual_value': actual_value,
                    'rating': rating,
                    'classification': classification,
                    'subclass': subclass,
                    'description': self._get_parameter_description(param_name),
                    'category': self._get_category_name(subclass)
                })
        
        logger.info(f"Identified {len(limiting_details)} limiting factor(s)")
        
        return limiting_details
    
    def _get_parameter_description(self, param_name: str) -> str:
        """Get human-readable description of parameter"""
        descriptions = {
            'temperature': 'Mean Annual Temperature',
            'rainfall': 'Annual Precipitation',
            'humidity': 'Relative Humidity',
            'ph': 'Soil pH',
            'organic_carbon': 'Organic Carbon Content',
            'organic_matter': 'Organic Matter Content',
            'nitrogen': 'Available Nitrogen',
            'phosphorus': 'Available Phosphorus',
            'potassium': 'Available Potassium',
            'texture': 'Soil Texture',
            'soil_depth': 'Soil Depth',
            'drainage': 'Drainage Condition',
            'flooding': 'Flooding Risk',
            'slope': 'Slope Percentage',
            'coarse_fragments': 'Coarse Fragments',
            'base_saturation': 'Base Saturation',
            'cec': 'Cation Exchange Capacity',
            'ec': 'Electrical Conductivity',
            'esp': 'Exchangeable Sodium Percentage',
            'dry_season': 'Dry Season Length',
            'max_temp': 'Maximum Temperature',
            'min_temp_coldest': 'Minimum Temperature (Coldest Month)',
            'caco3': 'Calcium Carbonate Content',
            'gypsum': 'Gypsum Content',
            'sum_basic_cations': 'Sum of Basic Cations'
        }
        
        return descriptions.get(param_name, param_name.replace('_', ' ').title())
    
    def _get_category_name(self, subclass: str) -> str:
        """Get category name from subclass code"""
        categories = {
            'c': 'Climate',
            't': 'Topography',
            'w': 'Wetness',
            's': 'Physical Soil',
            'f': 'Soil Fertility',
            'n': 'Salinity/Alkalinity'
        }
        
        return categories.get(subclass, 'Unknown')
    
    def _generate_recommendations(
        self,
        evaluation_result: Dict,
        soil_data: Dict
    ) -> List[str]:
        """
        Generate agronomic recommendations based on evaluation results.
        
        ✅ MODIFIED: Added special handling for S1 with no limiting factors
        """
        logger.debug("Generating recommendations...")
        
        recommendations = []
        lsc = evaluation_result['lsc']
        limiting_factors = evaluation_result['limiting_factors']
        
        # ✅ NEW: Special case for perfect suitability
        if lsc == "S1" and not limiting_factors:
            recommendations.append(
                "✓ This crop is highly suitable for the given soil conditions with no limiting factors. "
                "Standard cultivation practices are recommended for optimal yields."
            )
            logger.info(f"Generated {len(recommendations)} recommendation(s)")
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
        
        # Specific recommendations based on limiting factors
        if 'f' in limiting_factors:
            recommendations.extend(self._get_fertility_recommendations(soil_data))
        
        if 'c' in limiting_factors:
            recommendations.append(
                "• Climate conditions are limiting. Consider protected cultivation "
                "or select more climate-adapted varieties."
            )
        
        if 'w' in limiting_factors:
            recommendations.extend(self._get_drainage_recommendations(soil_data))
        
        if 's' in limiting_factors:
            recommendations.extend(self._get_physical_soil_recommendations(soil_data))
        
        if 't' in limiting_factors:
            recommendations.append(
                "• Slope is limiting. Implement soil conservation measures "
                "such as terracing or contour farming."
            )
        
        if 'n' in limiting_factors:
            recommendations.append(
                "• Salinity/alkalinity is limiting. Consider leaching, "
                "gypsum application, or salt-tolerant varieties."
            )
        
        logger.info(f"Generated {len(recommendations)} recommendation(s)")
        
        return recommendations
    
    def _get_fertility_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate fertility-specific recommendations"""
        recommendations = []
        
        ph = soil_data.get('ph')
        if ph:
            if ph < 5.5:
                recommendations.append(
                    f"• Soil is strongly acidic (pH {ph:.2f}). Apply lime to raise pH to 6.0-6.5."
                )
            elif ph > 7.5:
                recommendations.append(
                    f"• Soil is alkaline (pH {ph:.2f}). Consider sulfur application to lower pH."
                )
        
        oc = soil_data.get('organic_carbon')
        om = soil_data.get('organic_matter')
        
        if oc and oc < 1.5:
            recommendations.append(
                f"• Organic carbon is low ({oc:.2f}%). Incorporate compost, manure, or "
                "green manure to improve soil health."
            )
        elif om and om < 2.0:
            recommendations.append(
                f"• Organic matter is low ({om:.2f}%). Incorporate compost, manure, or "
                "green manure to improve soil health."
            )
        
        return recommendations
    
    def _get_drainage_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate drainage-specific recommendations"""
        recommendations = []
        
        drainage = soil_data.get('drainage')
        if drainage in ['poor', 'poor_not_drainable']:
            recommendations.append(
                "• Poor drainage detected. Install drainage systems or "
                "raise beds to improve water management."
            )
        
        flooding = soil_data.get('flooding')
        if flooding and flooding != 'Fo':
            recommendations.append(
                "• Flooding risk present. Implement flood protection measures "
                "or select flood-tolerant varieties."
            )
        
        return recommendations
    
    def _get_physical_soil_recommendations(self, soil_data: Dict) -> List[str]:
        """Generate physical soil recommendations"""
        recommendations = []
        
        texture = soil_data.get('texture')
        if texture in ['S', 'LS', 'fS']:
            recommendations.append(
                "• Sandy texture limits water retention. Increase irrigation frequency "
                "and add organic matter to improve water-holding capacity."
            )
        elif texture in ['C', 'SiC', 'Cm']:
            recommendations.append(
                "• Heavy clay texture limits drainage and root penetration. "
                "Add organic matter and practice deep tillage to improve structure."
            )
        
        depth = soil_data.get('soil_depth')
        if depth and depth < 50:
            recommendations.append(
                f"• Shallow soil depth ({depth}cm) limits root growth. "
                "Consider raised beds or select shallow-rooted crops."
            )
        
        return recommendations
    
    def _get_interpretation(self, lsc: str, lsi: float) -> str:
        """
        Get interpretation text for the suitability classification.
        """
        interpretations = {
            'S1': (
                f"Highly Suitable (LSI: {lsi:.2f}). "
                "Land has no significant limitations for sustained application "
                "of the given use. Expected yields are high with minimal inputs."
            ),
            'S2': (
                f"Moderately Suitable (LSI: {lsi:.2f}). "
                "Land has limitations that reduce productivity or require increased "
                "inputs. Expected yields are moderate with proper management."
            ),
            'S3': (
                f"Marginally Suitable (LSI: {lsi:.2f}). "
                "Land has severe limitations that reduce productivity or require "
                "intensive management. Expected yields are low even with inputs."
            ),
            'N': (
                f"Not Suitable (LSI: {lsi:.2f}). "
                "Land has limitations so severe that they preclude successful "
                "sustained use. Cultivation is not recommended."
            )
        }
        
        return interpretations.get(lsc, f"Classification: {lsc}, LSI: {lsi:.2f}")
    
    def get_available_crops(self) -> List[str]:
        """Get list of all available crops in the knowledge base"""
        return self.crop_rules.get_crop_names()
    
    def get_crop_info(self, crop_name: str) -> Optional[Dict]:
        """
        Get basic information about a crop.
        """
        crop_data = self.crop_rules.get_crop_requirements(crop_name)
        if not crop_data:
            return None
        
        return {
            'name': crop_data.get('crop_name'),
            'scientific_name': crop_data.get('scientific_name'),
            'seasonal': crop_data.get('seasonal', False),
            'seasons': crop_data.get('seasons', []),
            'notes': crop_data.get('notes', '')
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*100)
    print("SOILWISE CROP SUITABILITY EVALUATOR - ENHANCED DEMONSTRATION")
    print("="*100)
    
    # Initialize evaluator
    evaluator = SuitabilityEvaluator()
    
    # Sample soil data (based on Brgy. Gacap research data)
    print("\n📋 Sample Soil Data (Brgy. Gacap, Piagapo, Lanao del Sur):")
    sample_soil_data = {
        # Climate (from research)
        'temperature': 26.4,      # Mean annual temp
        'rainfall': 2651.54,      # Annual precipitation
        'humidity': 76.62,        # Relative humidity
        
        # Soil Properties (from Table 6)
        'ph': 6.20,               # Ap horizon
        'organic_carbon': 3.76,   # Converted from OM
        'texture': 'L',           # Loam
        'soil_depth': 138,        # Full profile depth
        'drainage': 'good',
        'flooding': 'Fo',
        'slope': 1.67,
        
        # Fertility (from Table 6)
        'base_saturation': 36.03,
        'cec': 30.50,
        
        # Salinity (from Table 6)
        'ec': 0.00022,
        'esp': 0.62
    }
    
    for key, value in sample_soil_data.items():
        print(f"  {key}: {value}")
    
    # Evaluate Banana
    print("\n" + "="*100)
    print("🍌 EVALUATING: BANANA")
    print("="*100)
    
    result = evaluator.evaluate_suitability(sample_soil_data, "Banana")
    
    print(f"\n📊 Results:")
    print(f"  Crop: {result['crop_name']} ({result['scientific_name']})")
    print(f"  LSI: {result['lsi']:.2f}")
    print(f"  Classification: {result['full_classification']}")
    print(f"  Interpretation: {result['interpretation']}")
    
    if result['limiting_factors']:
        print(f"\n⚠️ Limiting Factors:")
        for detail in result['limiting_factors_detailed']:
            print(
                f"  • {detail['description']}: {detail['actual_value']} "
                f"(Rating: {detail['rating']:.4f}, {detail['classification']})"
            )
    
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    # Evaluate multiple crops
    print("\n" + "="*100)
    print("📊 EVALUATING ALL CROPS")
    print("="*100)
    
    all_results = evaluator.evaluate_multiple_crops(sample_soil_data)
    
    print(f"\nTop 10 Most Suitable Crops:")
    print(f"{'Rank':<6} {'Crop':<25} {'LSI':<10} {'Classification':<20} {'Limiting'}")
    print("-" * 100)
    
    for i, result in enumerate(all_results[:10], 1):
        print(
            f"{i:<6} {result['crop_name']:<25} {result['lsi']:<10.2f} "
            f"{result['full_classification']:<20} {result['limiting_factors']}"
        )
    
    print("\n" + "="*100)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*100)
