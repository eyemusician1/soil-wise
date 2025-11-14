"""
SoilWise/main.py
Application entry point
"""

import sys
from PySide6.QtWidgets import QApplication
from SoilWise.ui.main_window import MainWindow
from SoilWise.utils.logger import setup_logger
from SoilWise.config.constants import APP_NAME, APP_VERSION

# Setup main logger
logger = setup_logger(__name__, 'soilwise.log')


def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("=" * 60)
    
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        logger.info("QApplication created")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        logger.info("Main window displayed")
        
        # Start event loop
        logger.info("Starting event loop")
        exit_code = app.exec()
        
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())