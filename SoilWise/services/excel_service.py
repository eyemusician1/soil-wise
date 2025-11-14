"""
SoilWise/services/excel_service.py
Excel import/export operations
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from SoilWise.models.soil_data import SoilData
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__, 'excel_service.log')


class ExcelService:
    """Service for Excel file operations"""
    
    COLUMN_MAPPING = {
        'Barangay': 'barangay',
        'Site_Name': 'site_name',
        'pH': 'ph',
        'Organic_Matter': 'organic_matter',
        'Nitrogen': 'nitrogen',
        'Phosphorus': 'phosphorus',
        'Potassium': 'potassium',
        'Texture': 'texture',
        'Temperature': 'temperature',
        'Rainfall': 'rainfall',
        'Humidity': 'humidity'
    }
    
    @staticmethod
    def import_soil_data(file_path: str) -> Optional[SoilData]:
        """
        Import soil data from Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            SoilData object or None if import fails
        """
        logger.info(f"Importing soil data from: {file_path}")
        
        try:
            # Validate file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            logger.debug(f"Read {len(df)} rows from Excel")
            
            if df.empty:
                logger.warning("Excel file is empty")
                raise ValueError("Excel file is empty")
            
            # Get first row
            row = df.iloc[0]
            
            # Map Excel columns to SoilData fields
            data = {}
            for excel_col, model_field in ExcelService.COLUMN_MAPPING.items():
                if excel_col in df.columns:
                    value = row[excel_col]
                    # Convert to appropriate type
                    if model_field in ['ph', 'organic_matter', 'nitrogen', 'phosphorus', 
                                      'potassium', 'temperature', 'rainfall', 'humidity']:
                        data[model_field] = float(value)
                    else:
                        data[model_field] = str(value)
                else:
                    logger.warning(f"Column '{excel_col}' not found in Excel file")
            
            # Create SoilData object
            soil_data = SoilData.from_dict(data)
            
            # Validate
            is_valid, error_msg = soil_data.validate()
            if not is_valid:
                logger.error(f"Validation failed: {error_msg}")
                raise ValueError(f"Validation failed: {error_msg}")
            
            logger.info(f"Successfully imported soil data: {soil_data}")
            return soil_data
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}", exc_info=True)
            raise
        except ValueError as e:
            logger.error(f"Value error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Failed to import Excel file: {str(e)}", exc_info=True)
            raise Exception(f"Failed to import Excel file: {str(e)}")
    
    @staticmethod
    def export_soil_data(soil_data: SoilData, file_path: str) -> bool:
        """
        Export soil data to Excel file
        
        Args:
            soil_data: SoilData object to export
            file_path: Path where to save Excel file
            
        Returns:
            True if export successful
        """
        logger.info(f"Exporting soil data to: {file_path}")
        
        try:
            # Convert SoilData to dictionary
            data_dict = soil_data.to_dict()
            
            # Prepare data for Excel (reverse mapping)
            excel_data = {}
            reverse_mapping = {v: k for k, v in ExcelService.COLUMN_MAPPING.items()}
            
            for model_field, excel_col in reverse_mapping.items():
                if model_field in data_dict and model_field not in ['id', 'created_at', 'updated_at']:
                    excel_data[excel_col] = [data_dict[model_field]]
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Export to Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            logger.info(f"Successfully exported soil data to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export Excel file: {str(e)}", exc_info=True)
            raise Exception(f"Failed to export Excel file: {str(e)}")
    
    @staticmethod
    def create_template(file_path: str) -> bool:
        """
        Create Excel template with sample data
        
        Args:
            file_path: Path where to save template
            
        Returns:
            True if template created successfully
        """
        logger.info(f"Creating Excel template: {file_path}")
        
        try:
            # Template data with sample values
            template_data = {
                'Barangay': ['Barangay 1'],
                'Site_Name': ['Sample Farm'],
                'pH': [6.5],
                'Organic_Matter': [3.5],
                'Nitrogen': [45.0],
                'Phosphorus': [22.0],
                'Potassium': [180.0],
                'Texture': ['Loam'],
                'Temperature': [27.0],
                'Rainfall': [2000.0],
                'Humidity': [75.0]
            }
            
            # Create DataFrame
            df = pd.DataFrame(template_data)
            
            # Export to Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            logger.info(f"Successfully created template: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create template: {str(e)}")
    
    @staticmethod
    def validate_excel_file(file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate Excel file structure
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"Validating Excel file: {file_path}")
        
        try:
            # Check file exists
            if not Path(file_path).exists():
                return False, "File not found"
            
            # Check file extension
            if not file_path.endswith(('.xlsx', '.xls')):
                return False, "Invalid file format. Use .xlsx or .xls"
            
            # Try to read file
            df = pd.read_excel(file_path)
            
            # Check if empty
            if df.empty:
                return False, "Excel file is empty"
            
            # Check for required columns
            required_columns = list(ExcelService.COLUMN_MAPPING.keys())
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing columns: {', '.join(missing_columns)}"
            
            logger.info("Excel file validation passed")
            return True, None
            
        except Exception as e:
            logger.error(f"Excel validation failed: {str(e)}", exc_info=True)
            return False, f"Validation error: {str(e)}"