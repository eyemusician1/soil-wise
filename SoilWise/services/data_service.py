"""
SoilWise/services/data_service.py
Database operations for soil data
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from SoilWise.models.soil_data import SoilData, EvaluationResult
from SoilWise.config.constants import DATABASE_PATH
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__, 'data_service.log')


class DataService:
    """Service for database operations"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db_path = DATABASE_PATH
        self.init_database()
        logger.info(f"DataService initialized with database: {self.db_path}")
    
    def init_database(self):
        """Create database tables if they don't exist"""
        logger.info("Initializing database tables")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Soil data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS soil_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        barangay TEXT NOT NULL,
                        site_name TEXT NOT NULL,
                        ph REAL NOT NULL,
                        organic_matter REAL NOT NULL,
                        nitrogen REAL NOT NULL,
                        phosphorus REAL NOT NULL,
                        potassium REAL NOT NULL,
                        texture TEXT NOT NULL,
                        temperature REAL NOT NULL,
                        rainfall REAL NOT NULL,
                        humidity REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Evaluation results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS evaluation_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        soil_data_id INTEGER NOT NULL,
                        crop_name TEXT NOT NULL,
                        suitability_class TEXT NOT NULL,
                        suitability_score REAL NOT NULL,
                        limiting_factors TEXT,
                        recommendations TEXT,
                        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (soil_data_id) REFERENCES soil_data(id)
                    )
                """)
                
                conn.commit()
                logger.info("Database tables initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            raise
    
    def save_soil_data(self, soil_data: SoilData) -> int:
        """
        Save soil data to database
        
        Args:
            soil_data: SoilData object to save
            
        Returns:
            ID of saved record
        """
        logger.info(f"Saving soil data: {soil_data}")
        
        try:
            # Validate before saving
            is_valid, error_msg = soil_data.validate()
            if not is_valid:
                logger.error(f"Validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO soil_data (
                        barangay, site_name, ph, organic_matter, nitrogen,
                        phosphorus, potassium, texture, temperature, rainfall, humidity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    soil_data.barangay,
                    soil_data.site_name,
                    soil_data.ph,
                    soil_data.organic_matter,
                    soil_data.nitrogen,
                    soil_data.phosphorus,
                    soil_data.potassium,
                    soil_data.texture,
                    soil_data.temperature,
                    soil_data.rainfall,
                    soil_data.humidity
                ))
                
                conn.commit()
                soil_id = cursor.lastrowid
                
                logger.info(f"Soil data saved successfully with ID: {soil_id}")
                return soil_id
                
        except sqlite3.Error as e:
            logger.error(f"Failed to save soil data: {str(e)}", exc_info=True)
            raise Exception(f"Failed to save soil data: {str(e)}")
    
    def get_soil_data(self, soil_id: int) -> Optional[SoilData]:
        """
        Retrieve soil data by ID
        
        Args:
            soil_id: ID of soil data record
            
        Returns:
            SoilData object or None if not found
        """
        logger.info(f"Retrieving soil data with ID: {soil_id}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM soil_data WHERE id = ?", (soil_id,))
                row = cursor.fetchone()
                
                if row:
                    data = dict(row)
                    soil_data = SoilData.from_dict(data)
                    logger.info(f"Retrieved soil data: {soil_data}")
                    return soil_data
                else:
                    logger.warning(f"Soil data not found with ID: {soil_id}")
                    return None
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve soil data: {str(e)}", exc_info=True)
            raise Exception(f"Failed to retrieve soil data: {str(e)}")
    
    def get_all_soil_data(self) -> List[SoilData]:
        """
        Retrieve all soil data records
        
        Returns:
            List of SoilData objects
        """
        logger.info("Retrieving all soil data")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM soil_data ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                soil_data_list = []
                for row in rows:
                    data = dict(row)
                    soil_data_list.append(SoilData.from_dict(data))
                
                logger.info(f"Retrieved {len(soil_data_list)} soil data records")
                return soil_data_list
                
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve all soil data: {str(e)}", exc_info=True)
            raise Exception(f"Failed to retrieve all soil data: {str(e)}")
    
    def update_soil_data(self, soil_data: SoilData) -> bool:
        """
        Update existing soil data
        
        Args:
            soil_data: SoilData object with updated values
            
        Returns:
            True if update successful
        """
        logger.info(f"Updating soil data ID: {soil_data.id}")
        
        try:
            # Validate before updating
            is_valid, error_msg = soil_data.validate()
            if not is_valid:
                logger.error(f"Validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE soil_data SET
                        barangay = ?, site_name = ?, ph = ?, organic_matter = ?,
                        nitrogen = ?, phosphorus = ?, potassium = ?, texture = ?,
                        temperature = ?, rainfall = ?, humidity = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    soil_data.barangay,
                    soil_data.site_name,
                    soil_data.ph,
                    soil_data.organic_matter,
                    soil_data.nitrogen,
                    soil_data.phosphorus,
                    soil_data.potassium,
                    soil_data.texture,
                    soil_data.temperature,
                    soil_data.rainfall,
                    soil_data.humidity,
                    datetime.now(),
                    soil_data.id
                ))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Soil data updated successfully: {soil_data.id}")
                    return True
                else:
                    logger.warning(f"No soil data found with ID: {soil_data.id}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to update soil data: {str(e)}", exc_info=True)
            raise Exception(f"Failed to update soil data: {str(e)}")
    
    def delete_soil_data(self, soil_id: int) -> bool:
        """
        Delete soil data by ID
        
        Args:
            soil_id: ID of soil data to delete
            
        Returns:
            True if deletion successful
        """
        logger.info(f"Deleting soil data ID: {soil_id}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete associated evaluation results first
                cursor.execute("DELETE FROM evaluation_results WHERE soil_data_id = ?", (soil_id,))
                
                # Delete soil data
                cursor.execute("DELETE FROM soil_data WHERE id = ?", (soil_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Soil data deleted successfully: {soil_id}")
                    return True
                else:
                    logger.warning(f"No soil data found with ID: {soil_id}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to delete soil data: {str(e)}", exc_info=True)
            raise Exception(f"Failed to delete soil data: {str(e)}")
    
    def get_statistics(self) -> dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        logger.info("Retrieving database statistics")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count soil samples
                cursor.execute("SELECT COUNT(*) FROM soil_data")
                soil_count = cursor.fetchone()[0]
                
                # Count evaluation results
                cursor.execute("SELECT COUNT(*) FROM evaluation_results")
                eval_count = cursor.fetchone()[0]
                
                # Count unique crops evaluated
                cursor.execute("SELECT COUNT(DISTINCT crop_name) FROM evaluation_results")
                crop_count = cursor.fetchone()[0]
                
                stats = {
                    'soil_samples': soil_count,
                    'evaluations': eval_count,
                    'crops_evaluated': crop_count
                }
                
                logger.info(f"Statistics retrieved: {stats}")
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve statistics: {str(e)}", exc_info=True)
            return {'soil_samples': 0, 'evaluations': 0, 'crops_evaluated': 0}