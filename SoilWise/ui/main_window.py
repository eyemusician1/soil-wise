"""
SoilWise/ui/main_window.py
Main application window - WITH LOGO BESIDE TEXT
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QIcon
import os

from SoilWise.ui.widgets.collapsible_sidebar import CollapsibleSidebar, NavButton
from SoilWise.ui.pages.home_page import HomePage
from SoilWise.ui.pages.input_page import InputPage
from SoilWise.ui.pages.crop_evaluation_page import CropEvaluationPage
from SoilWise.ui.pages.reports_page import ReportsPage
from SoilWise.ui.pages.evaluation_history_page import EvaluationHistoryPage
from SoilWise.config.constants import APP_NAME, APP_VERSION, LOCATION
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__, "main_window.log")


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        
        # Set window icon (desktop/taskbar)
        self.set_window_icon()

        # Apply theme
        self.apply_theme()

        # Page registry
        self.pages: dict[str, QWidget] = {}

        # Initialize UI
        self.init_ui()

        logger.info("MainWindow initialized")

    # ------------------------------------------------------------------
    # Logo Integration
    # ------------------------------------------------------------------

    def set_window_icon(self):
        """Set application window icon for desktop/taskbar"""
        try:
            logo_path = os.path.join("SoilWise", "assets", "images", "sample2.png")
            if os.path.exists(logo_path):
                icon = QIcon(logo_path)
                self.setWindowIcon(icon)
                logger.info("Window icon set successfully")
            else:
                logger.warning(f"Logo file not found at: {logo_path}")
        except Exception as e:
            logger.error(f"Failed to set window icon: {e}")

    def create_logo_label(self, size: int = 40) -> QLabel:
        """
        Create a QLabel with the SoilWise logo
        
        Args:
            size: Size of the logo in pixels (width and height)
            
        Returns:
            QLabel with the logo
        """
        logo_label = QLabel()
        try:
            logo_path = os.path.join("SoilWise", "assets", "images", "SOILWISE.ico")
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                scaled_pixmap = pixmap.scaled(
                    size, size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setFixedSize(size, size)
            else:
                logo_label.setText("🌱")
                logo_label.setStyleSheet("font-size: 28px;")
                logger.warning("Logo file not found, using emoji fallback")
        except Exception as e:
            logo_label.setText("🌱")
            logo_label.setStyleSheet("font-size: 28px;")
            logger.error(f"Failed to load logo: {e}")
        
        return logo_label

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_theme(self):
        """Apply Fluent Design-like theme"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f7f5;
            }
            QWidget {
                background-color: #f5f7f5;
                color: #3a4a3a;
                font-family: 'Georgia', 'Palatino', 'Garamond',
                             'Times New Roman', serif;
            }
            QLabel {
                color: #3a4a3a;
                background-color: transparent;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #e5e8e5;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: 600;
                color: #7d9d7f;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #d0d8d0;
                border-radius: 6px;
                padding: 10px 12px;
                color: #3a4a3a;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #7d9d7f;
                padding: 9px 11px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #e8ebe8;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0cac0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8b5a8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    # ------------------------------------------------------------------
    # UI wiring
    # ------------------------------------------------------------------

    def init_ui(self):
        """Initialize user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (pass logo to sidebar)
        self.sidebar = self.create_sidebar()
        # Collapse sidebar by default
        if hasattr(self.sidebar, 'is_expanded') and self.sidebar.is_expanded:
            self.sidebar.toggle_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f5f7f5;")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Title bar
        self.title_bar = self.create_title_bar()
        content_layout.addWidget(self.title_bar)

        # Pages stack
        self.pages_stack = QStackedWidget()
        self.create_pages()
        content_layout.addWidget(self.pages_stack)

        main_layout.addWidget(self.content_area)

        # Initial page
        self.change_page(0)

    def create_sidebar(self):
        """Create sidebar with navigation (logo removed)"""
        sidebar = CollapsibleSidebar(logo_widget=None)
        self.nav_buttons: list[NavButton] = []

        # Home
        self.btn_home = NavButton("⌂", "Home")
        self.btn_home.set_active(True)
        self.btn_home.clicked.connect(lambda: self.change_page(0))
        sidebar.add_nav_button(self.btn_home)
        self.nav_buttons.append(self.btn_home)

        # Soil Data Input
        self.btn_input = NavButton("▦", "Soil Data Input")
        self.btn_input.clicked.connect(lambda: self.change_page(1))
        sidebar.add_nav_button(self.btn_input)
        self.nav_buttons.append(self.btn_input)

        # Crop Evaluation
        self.btn_evaluation = NavButton("⚘", "Crop Evaluation")
        self.btn_evaluation.clicked.connect(lambda: self.change_page(2))
        sidebar.add_nav_button(self.btn_evaluation)
        self.nav_buttons.append(self.btn_evaluation)

        # Reports
        self.btn_reports = NavButton("◱", "Reports")
        self.btn_reports.clicked.connect(lambda: self.change_page(3))
        sidebar.add_nav_button(self.btn_reports)
        self.nav_buttons.append(self.btn_reports)

        # Evaluation History
        self.btn_history = NavButton("◷", "Evaluation History")
        self.btn_history.clicked.connect(lambda: self.change_page(4))
        sidebar.add_nav_button(self.btn_history)
        self.nav_buttons.append(self.btn_history)

        # Footer
        footer = QLabel(f"v{APP_VERSION}\n{LOCATION}")
        footer.setStyleSheet("color: #a8b5a8; font-size: 11px; padding: 24px;")
        footer.setAlignment(Qt.AlignCenter)
        sidebar.add_footer(footer)

        return sidebar

    def create_title_bar(self):
        """Create title bar without logo beside text"""
        title_bar = QFrame()
        title_bar.setFixedHeight(80)
        title_bar.setStyleSheet(
            """
            QFrame {
                background-color: none;
                border-bottom: none;
            }
            """
        )

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(32, 0, 24, 0)
        layout.setSpacing(12)

        # Page title (logo removed)
        self.page_title = QLabel("Home")
        self.page_title.setFont(QFont("Georgia", 24))
        self.page_title.setStyleSheet("color: #3a4a3a; font-weight: 500;")
        layout.addWidget(self.page_title)
        
        layout.addStretch()

        return title_bar

    def create_pages(self):
        """Create all pages"""
        # Home page
        home_page = HomePage()
        home_page.navigate_to_input.connect(lambda: self.change_page(1))
        home_page.navigate_to_evaluation.connect(lambda: self.change_page(2))
        home_page.navigate_to_reports.connect(lambda: self.change_page(3))
        home_page.navigate_to_knowledge.connect(lambda: self.change_page(4))
        self.pages["home"] = home_page
        self.pages_stack.addWidget(home_page)

        # Input page
        input_page = InputPage()
        input_page.data_saved.connect(self.on_data_saved)
        input_page.evaluation_complete.connect(self.on_evaluation_complete)
        self.pages["input"] = input_page
        self.pages_stack.addWidget(input_page)

        # Crop Evaluation page
        crop_evaluation_page = CropEvaluationPage()
        crop_evaluation_page.navigate_to_input.connect(
            lambda: self.change_page(1)
        )
        crop_evaluation_page.comparison_complete.connect(
            self.on_comparison_complete
        )
        self.pages["crop_evaluation"] = crop_evaluation_page
        self.pages_stack.addWidget(crop_evaluation_page)
        logger.info("Crop Evaluation page created")

        # Reports page
        placeholder_results = {
            "crop_name": "No crop selected",
            "lsc": "N",
            "lsi": 0.0,
        }
        reports_page = ReportsPage(placeholder_results)
        reports_page.new_evaluation_requested.connect(
            self.on_new_evaluation_requested
        )
        self.pages["reports"] = reports_page
        self.pages_stack.addWidget(reports_page)

        # Evaluation History page
        history_page = EvaluationHistoryPage()
        history_page.view_report_requested.connect(self.on_view_report_from_history)
        self.pages['history'] = history_page
        self.pages_stack.addWidget(history_page)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def on_evaluation_complete(self, results: dict):
        """Handle evaluation completion from Input Page"""
        crop_name = results.get("crop_name", "")
        logger.info(f"Evaluation complete for {crop_name}")
        logger.info(
            "  LSI: %.2f, Classification: %s",
            results.get("lsi", 0.0),
            results.get("full_classification", ""),
        )

        if "soil_data" in results and "crop_evaluation" in self.pages:
            soil_data = results["soil_data"]
            self.pages["crop_evaluation"].set_last_soil_data(
                soil_data, crop_name
            )
            logger.info(
                "Passed soil data to Crop Evaluation page (Last crop: %s)",
                crop_name,
            )

        if "history" in self.pages:
            logger.info("Auto-refreshing Evaluation History page...")
            self.pages["history"].load_history()
            logger.info("Evaluation History refreshed successfully")

        if "reports" in self.pages:
            old_reports = self.pages["reports"]
            index = self.pages_stack.indexOf(old_reports)

            new_reports = ReportsPage(results)
            new_reports.new_evaluation_requested.connect(
                self.on_new_evaluation_requested
            )

            self.pages_stack.removeWidget(old_reports)
            old_reports.deleteLater()

            self.pages["reports"] = new_reports
            self.pages_stack.insertWidget(index, new_reports)

        self.change_page(3)

    def on_comparison_complete(self, results: list):
        """Handle comparison completion from Crop Evaluation Page"""
        logger.info("Multi-crop comparison complete for %d crops", len(results))
        for i, result in enumerate(results[:3], 1):
            logger.info(
                "  %d. %s: LSI=%.2f, %s",
                i,
                result.get("crop_name", ""),
                result.get("lsi", 0.0),
                result.get("full_classification", ""),
            )

        if "history" in self.pages:
            logger.info("Auto-refreshing Evaluation History after comparison...")
            self.pages["history"].load_history()
            logger.info("Evaluation History refreshed successfully")

        logger.info("Comparison completed successfully")

    def on_new_evaluation_requested(self):
        """Handle 'New Evaluation' from Reports page"""
        logger.info("New evaluation requested, navigating to Input page")
        self.change_page(1)

    def change_page(self, index: int):
        """Change current page by index"""
        logger.info("Changing to page index: %d", index)
        self.pages_stack.setCurrentIndex(index)

        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

        titles = [
            "Home",
            "Soil Data Input",
            "Crop Evaluation",
            "View Reports",
            "Evaluation History",
        ]
        if 0 <= index < len(titles):
            self.page_title.setText(titles[index])

        if index == 0 and "home" in self.pages:
            self.pages["home"].refresh()

        if index == 4 and "history" in self.pages:
            logger.info("Refreshing Evaluation History on page load...")
            self.pages["history"].load_history()

    def on_data_saved(self, soil_id: str):
        """Handle data saved event from Input Page"""
        logger.info("Data saved event received: soil_id=%s", soil_id)
        if "home" in self.pages:
            self.pages["home"].update_statistics()

    def on_view_report_from_history(self, eval_data: dict):
        """Handle viewing a report from history"""
        logger.info(f"View report requested for: {eval_data.get('crop_name')}")
        self.change_page(3)