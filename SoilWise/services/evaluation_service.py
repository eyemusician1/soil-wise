"""
Evaluation Service
Connects the UI to the Knowledge Base System
"""

from typing import Dict, List, Optional
from knowledge_base.evaluation import SuitabilityEvaluator
from models.soil_data import SoilData


class EvaluationService:
    """Service for running crop suitability evaluations"""
    
    def __init__(self):
        self.evaluator = SuitabilityEvaluator()
    
    def evaluate_single_crop(
        self,
        crop_name: str,
        soil_data: SoilData,
        season: Optional[str] = None
    ) -> Dict:
        """
        Evaluate suitability for a single crop.
        
        Args:
            crop_name: Name of the crop
            soil_data: SoilData object from input_page
            season: Optional season
        
        Returns:
            Evaluation result dictionary
        """
        # Convert SoilData to dictionary format expected by evaluator
        soil_dict = {
            "temperature": soil_data.temperature,
            "rainfall": soil_data.rainfall,
            "humidity": soil_data.humidity,
            "ph": soil_data.ph,
            "organic_matter": soil_data.organic_matter,
            "texture": soil_data.texture,
            # Add more mappings as needed
        }
        
        return self.evaluator.evaluate_suitability(soil_dict, crop_name, season)
    
    def evaluate_all_crops(
        self,
        soil_data: SoilData
    ) -> List[Dict]:
        """
        Evaluate suitability for all available crops.
        
        Args:
            soil_data: SoilData object
        
        Returns:
            List of evaluation results for all crops
        """
        crop_names = self.evaluator.crop_rules.get_crop_names()
        results = []
        
        for crop_name in crop_names:
            try:
                result = self.evaluate_single_crop(crop_name, soil_data)
                results.append(result)
            except Exception as e:
                print(f"Error evaluating {crop_name}: {e}")
        
        return results