"""Application constants and configuration"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
LOG_DIR = BASE_DIR / "logs"
EXPORT_DIR = DATA_DIR / "exports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "soil_samples.db"

# Application settings
APP_NAME = "SoilWise"
APP_VERSION = "1.0.0"
LOCATION = "Piagapo, Lanao del Sur"

# Soil property ranges (min, max, default)
SOIL_RANGES = {
    'ph': (0.0, 14.0, 7.0),
    'organic_matter': (0.0, 100.0, 0.0),
    'nitrogen': (0.0, 1000.0, 0.0),
    'phosphorus': (0.0, 1000.0, 0.0),
    'potassium': (0.0, 1000.0, 0.0),
}

# Climate ranges (min, max, default)
CLIMATE_RANGES = {
    'temperature': (0.0, 50.0, 27.0),
    'rainfall': (0.0, 5000.0, 2000.0),
    'humidity': (0.0, 100.0, 75.0),
}

# Texture options
SOIL_TEXTURES = [
    "Select...",
    "Clay",
    "Clay Loam",
    "Sandy Loam",
    "Loam",
    "Silt Loam",
    "Sand"
]

# Barangays
BARANGAYS = [
    "Select...",
    "Barangay 1",
    "Barangay 2",
    "Barangay 3"
]