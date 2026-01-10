"""
Database Manager for SoilWise
Handles all SQLite database operations
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional, Any


class DatabaseManager:
    """Centralized database management for SoilWise"""

    def __init__(self, db_path: str = None):
        """
        Initialize database manager

        Args:
            db_path: Path to database file. If None, uses default location.
        """
        if db_path is None:
            # Default: user's Documents/SoilWise/soilwise.db
            user_docs = Path.home() / "Documents" / "SoilWise"
            user_docs.mkdir(parents=True, exist_ok=True)
            self.db_path = user_docs / "soilwise.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.init_database()
        print(f"✅ Database initialized: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Create all database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # ===== CROPS TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crops (
                    crop_id TEXT PRIMARY KEY,
                    crop_name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    category TEXT,
                    is_seasonal INTEGER DEFAULT 0,
                    validation_status TEXT DEFAULT 'draft',
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)

            # ===== CROP REQUIREMENTS TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crop_requirements (
                    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_id TEXT NOT NULL,
                    parameter TEXT NOT NULL,
                    s1_min REAL,
                    s1_max REAL,
                    s2_min REAL,
                    s2_max REAL,
                    s3_min REAL,
                    s3_max REAL,
                    unit TEXT,
                    season TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE CASCADE,
                    UNIQUE(crop_id, parameter, season)
                )
            """)

            # ===== SOIL DATA INPUTS TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS soil_data_inputs (
                    input_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT,
                    ph REAL,
                    temperature REAL,
                    precipitation REAL,
                    texture TEXT,
                    drainage TEXT,
                    flooding TEXT,
                    soil_depth TEXT,
                    gravel_content TEXT,
                    erosion TEXT,
                    slope_percent REAL,
                    electrical_conductivity REAL,
                    organic_carbon REAL,
                    cec REAL,
                    base_saturation REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)

            # ===== EVALUATION RESULTS TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_id INTEGER,
                    crop_id TEXT NOT NULL,
                    season TEXT,
                    lsi REAL NOT NULL,
                    lsc TEXT NOT NULL,
                    full_classification TEXT NOT NULL,
                    limiting_factors TEXT,
                    recommendation TEXT,
                    evaluation_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (input_id) REFERENCES soil_data_inputs(input_id) ON DELETE CASCADE,
                    FOREIGN KEY (crop_id) REFERENCES crops(crop_id)
                )
            """)

            # ===== COMPARISON HISTORY TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comparison_history (
                    comparison_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_id INTEGER,
                    season TEXT,
                    crop_ids TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (input_id) REFERENCES soil_data_inputs(input_id) ON DELETE SET NULL
                )
            """)

            # ===== USER PREFERENCES TABLE =====
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    pref_key TEXT PRIMARY KEY,
                    pref_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_crop_requirements_crop
                ON crop_requirements(crop_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evaluation_results_crop
                ON evaluation_results(crop_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evaluation_results_input
                ON evaluation_results(input_id)
            """)

            conn.commit()
            print("✅ Database schema created/verified")

    # ========== CROP OPERATIONS ==========

    def add_crop(self, crop_data: Dict) -> str:
        """Add a new crop"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO crops (crop_id, crop_name, display_name, category,
                                   is_seasonal, validation_status, description, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crop_data.get('crop_id'),
                crop_data.get('crop_name'),
                crop_data.get('display_name'),
                crop_data.get('category'),
                crop_data.get('is_seasonal', 0),
                crop_data.get('validation_status', 'draft'),
                crop_data.get('description'),
                crop_data.get('notes')
            ))
            return crop_data.get('crop_id')

    def get_all_crops(self, validated_only: bool = False) -> List[Dict]:
        """Get all crops"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if validated_only:
                cursor.execute("""
                    SELECT * FROM crops WHERE validation_status = 'validated'
                    ORDER BY crop_name
                """)
            else:
                cursor.execute("SELECT * FROM crops ORDER BY crop_name")
            return [dict(row) for row in cursor.fetchall()]

    def get_crop(self, crop_id: str) -> Optional[Dict]:
        """Get a specific crop"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM crops WHERE crop_id = ?", (crop_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ========== CROP REQUIREMENTS OPERATIONS ==========

    def add_crop_requirement(self, requirement_data: Dict) -> int:
        """Add a crop requirement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO crop_requirements
                (crop_id, parameter, s1_min, s1_max, s2_min, s2_max, s3_min, s3_max,
                 unit, season, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                requirement_data.get('crop_id'),
                requirement_data.get('parameter'),
                requirement_data.get('s1_min'),
                requirement_data.get('s1_max'),
                requirement_data.get('s2_min'),
                requirement_data.get('s2_max'),
                requirement_data.get('s3_min'),
                requirement_data.get('s3_max'),
                requirement_data.get('unit'),
                requirement_data.get('season'),
                requirement_data.get('notes')
            ))
            return cursor.lastrowid

    def get_crop_requirements(self, crop_id: str, season: str = None) -> List[Dict]:
        """Get all requirements for a crop"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if season:
                cursor.execute("""
                    SELECT * FROM crop_requirements
                    WHERE crop_id = ? AND (season = ? OR season IS NULL)
                """, (crop_id, season))
            else:
                cursor.execute("""
                    SELECT * FROM crop_requirements WHERE crop_id = ?
                """, (crop_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== SOIL DATA OPERATIONS ==========

    def save_soil_input(self, soil_data: Dict) -> int:
        """Save soil data input"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO soil_data_inputs
                (location, ph, temperature, precipitation, texture, drainage,
                 flooding, soil_depth, gravel_content, erosion, slope_percent,
                 electrical_conductivity, organic_carbon, cec, base_saturation, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                soil_data.get('location'),
                soil_data.get('ph'),
                soil_data.get('temperature'),
                soil_data.get('precipitation'),
                soil_data.get('texture'),
                soil_data.get('drainage'),
                soil_data.get('flooding'),
                soil_data.get('soil_depth'),
                soil_data.get('gravel_content'),
                soil_data.get('erosion'),
                soil_data.get('slope_percent'),
                soil_data.get('electrical_conductivity'),
                soil_data.get('organic_carbon'),
                soil_data.get('cec'),
                soil_data.get('base_saturation'),
                soil_data.get('notes')
            ))
            return cursor.lastrowid

    def get_soil_input(self, input_id: int) -> Optional[Dict]:
        """Get a specific soil input"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM soil_data_inputs WHERE input_id = ?", (input_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_recent_soil_inputs(self, limit: int = 10) -> List[Dict]:
        """Get recent soil inputs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM soil_data_inputs
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== EVALUATION RESULTS OPERATIONS ==========

    def save_evaluation_result(self, evaluation_data: Dict) -> int:
        """Save evaluation result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluation_results
                (input_id, crop_id, season, lsi, lsc, full_classification,
                 limiting_factors, recommendation, evaluation_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evaluation_data.get('input_id'),
                evaluation_data.get('crop_id'),
                evaluation_data.get('season'),
                evaluation_data.get('lsi'),
                evaluation_data.get('lsc'),
                evaluation_data.get('full_classification'),
                evaluation_data.get('limiting_factors'),
                evaluation_data.get('recommendation'),
                json.dumps(evaluation_data.get('full_result', {}))
            ))
            return cursor.lastrowid

    def get_evaluation_history(self, crop_id: str = None, limit: int = 50) -> List[Dict]:
        """Get evaluation history (legacy method, still usable)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if crop_id:
                cursor.execute("""
                    SELECT e.*, s.location, s.ph, s.temperature
                    FROM evaluation_results e
                    LEFT JOIN soil_data_inputs s ON e.input_id = s.input_id
                    WHERE e.crop_id = ?
                    ORDER BY e.created_at DESC LIMIT ?
                """, (crop_id, limit))
            else:
                cursor.execute("""
                    SELECT e.*, s.location, s.ph, s.temperature
                    FROM evaluation_results e
                    LEFT JOIN soil_data_inputs s ON e.input_id = s.input_id
                    ORDER BY e.created_at DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # ------- NEW OPTIMIZED METHODS FOR HISTORY PAGE -------

    def get_evaluation_stats_fast(self) -> Dict:
        """Fast aggregate stats for evaluation history (used by Evaluation History page)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {
                "total_evaluations": 0,
                "avg_lsi": 0.0,
                "most_evaluated_crop": None,
            }

            # Total evaluations
            cursor.execute("SELECT COUNT(*) AS cnt FROM evaluation_results")
            row = cursor.fetchone()
            stats["total_evaluations"] = row["cnt"] if row else 0

            if stats["total_evaluations"] == 0:
                return stats

            # Average LSI
            cursor.execute("SELECT AVG(lsi) AS avg_lsi FROM evaluation_results")
            row = cursor.fetchone()
            stats["avg_lsi"] = float(row["avg_lsi"]) if row and row["avg_lsi"] is not None else 0.0

            # Most evaluated crop
            cursor.execute("""
                SELECT crop_id, COUNT(*) AS cnt
                FROM evaluation_results
                GROUP BY crop_id
                ORDER BY cnt DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                stats["most_evaluated_crop"] = row["crop_id"]

            return stats

    def get_evaluation_page(
        self,
        page: int = 0,
        page_size: int = 25,
        crop_id: str = None,
    ) -> List[Dict]:
        """
        Get a single page of evaluation history (for paging in UI).

        Args:
            page: zero-based page index (0 = first page).
            page_size: number of records per page.
            crop_id: optional filter by crop_id.
        """
        offset = page * page_size
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if crop_id:
                cursor.execute("""
                    SELECT e.*, s.location, s.ph, s.temperature
                    FROM evaluation_results e
                    LEFT JOIN soil_data_inputs s ON e.input_id = s.input_id
                    WHERE e.crop_id = ?
                    ORDER BY e.created_at DESC
                    LIMIT ? OFFSET ?
                """, (crop_id, page_size, offset))
            else:
                cursor.execute("""
                    SELECT e.*, s.location, s.ph, s.temperature
                    FROM evaluation_results e
                    LEFT JOIN soil_data_inputs s ON e.input_id = s.input_id
                    ORDER BY e.created_at DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))

            return [dict(row) for row in cursor.fetchall()]

    # ========== COMPARISON HISTORY OPERATIONS ==========

    def save_comparison(self, comparison_data: Dict) -> int:
        """Save comparison history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO comparison_history
                (input_id, season, crop_ids, results_json, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                comparison_data.get('input_id'),
                comparison_data.get('season'),
                json.dumps(comparison_data.get('crop_ids', [])),
                json.dumps(comparison_data.get('results', [])),
                comparison_data.get('notes')
            ))
            return cursor.lastrowid

    def get_comparison_history(self, limit: int = 20) -> List[Dict]:
        """Get comparison history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM comparison_history
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            results = []
            for row in cursor.fetchall():
                record = dict(row)
                record['crop_ids'] = json.loads(record['crop_ids'])
                record['results'] = json.loads(record['results_json'])
                results.append(record)
            return results

    # ========== USER PREFERENCES ==========

    def set_preference(self, key: str, value: Any):
        """Set user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (pref_key, pref_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pref_value FROM user_preferences WHERE pref_key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row['pref_value'])
            return default

    # ========== UTILITY OPERATIONS ==========

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM crops")
            stats['total_crops'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM crops WHERE validation_status = 'validated'")
            stats['validated_crops'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM soil_data_inputs")
            stats['soil_inputs'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM evaluation_results")
            stats['evaluations'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM comparison_history")
            stats['comparisons'] = cursor.fetchone()['count']

            return stats

    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        if backup_path is None:
            backup_dir = self.db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"soilwise_backup_{timestamp}.db"

        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return str(backup_path)


# Singleton instance
_db_instance = None


def get_database() -> DatabaseManager:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
