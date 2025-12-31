"""
SoilWise - Main Application Entry Point
Enhanced with database initialization and migration support
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from SoilWise.ui.main_window import MainWindow
from SoilWise.utils.logger import setup_logger
from SoilWise.config.constants import APP_NAME, APP_VERSION

logger = setup_logger(__name__, 'soilwise.log')


def initialize_database():
    """
    Initialize database and check if migration is needed.
    Returns True if successful, False otherwise.
    """
    try:
        from database.db_manager import get_database

        logger.info("Initializing database...")

        # Get database instance (creates tables automatically)
        db = get_database()
        logger.info(f"[OK] Database initialized: {db.db_path}")

        # Check database statistics
        stats = db.get_stats()
        logger.info(f"Database stats: {stats['total_crops']} crops, "
                   f"{stats['evaluations']} evaluations")

        # Check if database needs migration (empty database)
        if stats['total_crops'] == 0:
            logger.warning("Database is empty - crops need to be migrated")

            # Ask user if they want to run migration now
            response = QMessageBox.question(
                None,
                "First Run Setup",
                f"Welcome to {APP_NAME} v{APP_VERSION}!\n\n"
                "Database is empty. Would you like to load crop data now?\n\n"
                "This will populate the database with 13 crop varieties "
                "and their suitability requirements.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes  # Default to Yes
            )

            if response == QMessageBox.Yes:
                logger.info("User chose to migrate - starting migration...")

                try:
                    # Import and run migration
                    from scripts.all_migration import migrate_all

                    # Show progress message
                    progress = QMessageBox(
                        QMessageBox.Information,
                        "Migrating Data",
                        "Loading crop requirements into database...\n\n"
                        "This may take a few moments.",
                        QMessageBox.NoButton,
                        None
                    )
                    progress.setStandardButtons(QMessageBox.NoButton)
                    progress.show()
                    QApplication.processEvents()

                    # Run migration
                    migrate_all()

                    progress.close()

                    # Get updated stats
                    stats = db.get_stats()

                    logger.info(f"✓ Migration completed: {stats['total_crops']} crops loaded")

                    QMessageBox.information(
                        None,
                        "Migration Complete",
                        f"Successfully loaded {stats['total_crops']} crops!\n\n"
                        "SoilWise is ready to use."
                    )

                except Exception as e:
                    logger.error(f"Migration failed: {e}", exc_info=True)

                    response = QMessageBox.warning(
                        None,
                        "Migration Failed",
                        f"Could not migrate crop data:\n{str(e)}\n\n"
                        "You can:\n"
                        "1. Run migration manually later from scripts/\n"
                        "2. Continue without database (uses JSON files)\n\n"
                        "Continue anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )

                    if response == QMessageBox.No:
                        return False
            else:
                logger.info("User skipped migration - will use JSON files")

                QMessageBox.information(
                    None,
                    "Using JSON Mode",
                    "SoilWise will use JSON files for crop requirements.\n\n"
                    "You can migrate to database later by running:\n"
                    "scripts/all_migration.py"
                )
        else:
            logger.info(f"[OK] Database loaded: {stats['total_crops']} crops available")

        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)

        # Ask if user wants to continue without database
        response = QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to initialize database:\n{str(e)}\n\n"
            "Continue using JSON files instead?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if response == QMessageBox.Yes:
            logger.warning("Continuing without database - using JSON mode")
            return True
        else:
            return False


def main():
    """Main application entry point"""
    logger.info("=" * 70)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("=" * 70)

    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # Initialize database
        if not initialize_database():
            logger.error("Database initialization failed - exiting")
            return 1

        # Create and show main window
        logger.info("Creating main window...")
        window = MainWindow()
        window.show()

        logger.info("[OK] Application started successfully")
        logger.info("=" * 70)

        # Run application event loop
        return app.exec()

    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)

        QMessageBox.critical(
            None,
            "Application Error",
            f"A critical error occurred:\n\n{str(e)}\n\n"
            "Please check soilwise.log for details."
        )

        import traceback
        traceback.print_exc()
        return 1

    finally:
        logger.info("Application shutting down")


if __name__ == "__main__":
    sys.exit(main())