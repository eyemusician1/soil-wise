import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from SoilWise.ui.main_window import MainWindow
from SoilWise.utils.logger import setup_logger
from SoilWise.config.constants import APP_NAME, APP_VERSION

logger = setup_logger(__name__, 'soilwise.log')

def main():
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        window = MainWindow()
        window.show()
        
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Error: {str(e)}", exc_info=True)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())