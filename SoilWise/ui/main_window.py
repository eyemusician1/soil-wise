"""
SoilWise/ui/main_window.py

Main application window - WITH CROP EVALUATION PAGE INTEGRATION
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from SoilWise.ui.widgets.collapsible_sidebar import CollapsibleSidebar, NavButton
from SoilWise.ui.pages.home_page import HomePage
from SoilWise.ui.pages.input_page import InputPage
from SoilWise.ui.pages.crop_evaluation_page import CropEvaluationPage
from SoilWise.ui.pages.reports_page import ReportsPage
from SoilWise.config.constants import APP_NAME, APP_VERSION, LOCATION
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__, "main_window.log")


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1400, 900)

        # Apply theme
        self.apply_theme()

        # Page registry
        self.pages: dict[str, QWidget] = {}

        # Initialize UI
        self.init_ui()

        logger.info("MainWindow initialized")

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

        # Sidebar
        self.sidebar = self.create_sidebar()
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
        """Create sidebar with navigation"""
        sidebar = CollapsibleSidebar()

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

        # Knowledge Base
        self.btn_knowledge = NavButton("◧", "Knowledge Base")
        self.btn_knowledge.clicked.connect(lambda: self.change_page(4))
        sidebar.add_nav_button(self.btn_knowledge)
        self.nav_buttons.append(self.btn_knowledge)

        # Footer
        footer = QLabel(f"v{APP_VERSION}\n{LOCATION}")
        footer.setStyleSheet("color: #a8b5a8; font-size: 11px; padding: 24px;")
        footer.setAlignment(Qt.AlignCenter)
        sidebar.add_footer(footer)

        return sidebar

    def create_title_bar(self):
        """Create title bar"""
        title_bar = QFrame()
        title_bar.setFixedHeight(80)
        title_bar.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e5e8e5;
            }
            """
        )

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(32, 0, 24, 0)

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

        # When "Update Soil Data" is confirmed, go back to Soil Data Input (index 1)
        crop_evaluation_page.navigate_to_input.connect(
            lambda: self.change_page(1)
        )

        # Multi-crop comparison completion (logged for now)
        crop_evaluation_page.comparison_complete.connect(
            self.on_comparison_complete
        )

        self.pages["crop_evaluation"] = crop_evaluation_page
        self.pages_stack.addWidget(crop_evaluation_page)
        logger.info("Crop Evaluation page created")

        # Reports page
        reports_page = ReportsPage()
        reports_page.new_evaluation_requested.connect(
            self.on_new_evaluation_requested
        )
        self.pages["reports"] = reports_page
        self.pages_stack.addWidget(reports_page)

        # Knowledge Base placeholder
        self.pages_stack.addWidget(
            self.create_placeholder_page("Browse crop requirements")
        )

        logger.info("All pages created")

    def create_placeholder_page(self, description: str) -> QWidget:
        """Create placeholder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)

        desc = QLabel(description)
        desc.setStyleSheet("color: #6a7a6a; font-size: 14px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        from SoilWise.ui.widgets.fluent_card import FluentCard

        card = FluentCard()
        card.setMinimumHeight(200)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        placeholder = QLabel("Coming soon...")
        placeholder.setStyleSheet("color: #a8b5a8; font-size: 16px;")
        placeholder.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(card)
        layout.addStretch()

        return page

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------
    def on_evaluation_complete(self, results: dict):
        """
        Handle evaluation completion from Input Page.

        results: Evaluation results dict from SuitabilityEvaluator
                 including 'soil_data', 'crop_name', 'lsi', etc.
        """
        # NOTE: emojis in logger caused UnicodeEncodeError on cp1252.
        # Keep messages ASCII-only.
        crop_name = results.get("crop_name", "<unknown>")
        logger.info(f"Evaluation complete for {crop_name}")
        logger.info(
            " LSI: %.2f, Classification: %s",
            results.get("lsi", 0.0),
            results.get("full_classification", ""),
        )

        # Pass soil data to Crop Evaluation page so Step 1 can use it
        if "soil_data" in results and "crop_evaluation" in self.pages:
            soil_data = results["soil_data"]
            self.pages["crop_evaluation"].set_last_soil_data(
                soil_data, crop_name
            )
            logger.info(
                "Passed soil data to Crop Evaluation page (Last crop: %s)",
                crop_name,
            )

        # Send results to Reports page and navigate there
        if "reports" in self.pages:
            self.pages["reports"].display_results(results)
        self.change_page(3)
        logger.info("Navigated to Reports page with results")

    def on_comparison_complete(self, results: list):
        """
        Handle comparison completion from Crop Evaluation Page.

        results: list of evaluation result dicts for multiple crops.
        """
        logger.info("Multi-crop comparison complete for %d crops", len(results))
        for i, result in enumerate(results[:3], 1):
            logger.info(
                " %d. %s: LSI=%.2f, %s",
                i,
                result.get("crop_name", ""),
                result.get("lsi", 0.0),
                result.get("full_classification", ""),
            )
        logger.info("Comparison completed successfully")

    def on_new_evaluation_requested(self):
        """Handle 'New Evaluation' from Reports page."""
        logger.info("New evaluation requested, navigating to Input page")
        self.change_page(1)
        # Optionally clear input form:
        # if "input" in self.pages:
        #     self.pages["input"].clear_form()

    def change_page(self, index: int):
        """Change current page by index"""
        logger.info("Changing to page index: %d", index)
        self.pages_stack.setCurrentIndex(index)

        # Update nav buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

        # Update title
        titles = [
            "Home",
            "Soil Data Input",
            "Crop Evaluation",
            "Reports & Analysis",
            "Knowledge Base",
        ]
        if 0 <= index < len(titles):
            self.page_title.setText(titles[index])

        # Refresh home when going back
        if index == 0 and "home" in self.pages:
            self.pages["home"].refresh()

    def on_data_saved(self, soil_id: str):
        """Handle data saved event from Input Page"""
        logger.info("Data saved event received: soil_id=%s", soil_id)
        if "home" in self.pages:
            self.pages["home"].update_statistics()
