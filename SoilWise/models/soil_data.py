"""
SoilWise/models/soil_data.py
Data models for soil and climate information
"""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class SoilData:
    """Soil properties data model"""
    
    # Location
    barangay: str
    site_name: str
    
    # Soil properties
    ph: float
    organic_matter: float
    nitrogen: float
    phosphorus: float
    potassium: float
    texture: str
    
    # Climate
    temperature: float
    rainfall: float
    humidity: float
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate data after initialization"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
            
        logger.debug(f"SoilData created for {self.barangay} - {self.site_name}")
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        # Remove None values
        cleaned_data = {k: v for k, v in data.items() if v is not None}
        return cls(**cleaned_data)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate soil data
        Returns: (is_valid, error_message)
        """
        # Check required fields
        if not self.barangay or self.barangay == "Select...":
            return False, "Barangay is required"
        
        if not self.site_name or not self.site_name.strip():
            return False, "Site name is required"
        
        if not self.texture or self.texture == "Select...":
            return False, "Soil texture is required"
        
        # Validate ranges
        validations = [
            (0 <= self.ph <= 14, "pH must be between 0 and 14"),
            (0 <= self.organic_matter <= 100, "Organic matter must be between 0 and 100%"),
            (0 <= self.nitrogen <= 1000, "Nitrogen must be between 0 and 1000 ppm"),
            (0 <= self.phosphorus <= 1000, "Phosphorus must be between 0 and 1000 ppm"),
            (0 <= self.potassium <= 1000, "Potassium must be between 0 and 1000 ppm"),
            (0 <= self.temperature <= 50, "Temperature must be between 0 and 50°C"),
            (0 <= self.rainfall <= 5000, "Rainfall must be between 0 and 5000 mm"),
            (0 <= self.humidity <= 100, "Humidity must be between 0 and 100%"),
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                logger.warning(f"Validation failed: {error_msg}")
                return False, error_msg
        
        logger.info(f"SoilData validation passed for {self.site_name}")
        return True, None
    
    def __str__(self):
        """String representation"""
        return f"SoilData({self.barangay} - {self.site_name})"


@dataclass
class EvaluationResult:
    """Crop evaluation result model"""
    
    soil_data_id: int
    crop_name: str
    suitability_class: str  # S1, S2, S3, N
    suitability_score: float
    limiting_factors: list[str]
    recommendations: list[str]
    
    # Metadata
    id: Optional[int] = None
    evaluated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps"""
        if self.evaluated_at is None:
            self.evaluated_at = datetime.now()
        
        logger.debug(f"EvaluationResult created: {self.crop_name} = {self.suitability_class}")
    
    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime to string
        if self.evaluated_at:
            data['evaluated_at'] = self.evaluated_at.isoformat()
        return data
    
    def get_suitability_description(self) -> str:
        """Get human-readable suitability description"""
        descriptions = {
            'S1': 'Highly Suitable',
            'S2': 'Moderately Suitable',
            'S3': 'Marginally Suitable',
            'N': 'Not Suitable'
        }
        return descriptions.get(self.suitability_class, 'Unknown')
    
    def __str__(self):
        """String representation"""
        return f"EvaluationResult({self.crop_name}: {self.suitability_class})"