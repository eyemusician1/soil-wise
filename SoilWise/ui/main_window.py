"""
SoilWise/ui/main_window.py
Main application window - FIXED with Reports Page Integration
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QFrame, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from SoilWise.ui.widgets.collapsible_sidebar import CollapsibleSidebar, NavButton
from SoilWise.ui.pages.home_page import HomePage
from SoilWise.ui.pages.input_page import InputPage
from SoilWise.ui.pages.reports_page import ReportsPage  # ADD THIS IMPORT
from SoilWise.config.constants import APP_NAME, APP_VERSION, LOCATION
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__, 'main_window.log')


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1400, 900)
        
        # Apply theme
        self.apply_theme()
        
        # Initialize pages
        self.pages = {}
        
        # Initialize UI
        self.init_ui()
        
        logger.info("MainWindow initialized")
    
    def apply_theme(self):
        """Apply Fluent Design theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7f5;
            }
            QWidget {
                background-color: #f5f7f5;
                color: #3a4a3a;
                font-family: 'Georgia', 'Palatino', 'Garamond', 'Times New Roman', serif;
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
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
        
        # Set initial page
        self.change_page(0)
    
    def create_sidebar(self):
        """Create sidebar with navigation"""
        sidebar = CollapsibleSidebar()
        
        # Navigation buttons - Using black Unicode symbols instead of colored emojis
        self.nav_buttons = []
        
        # Home - using house symbol
        self.btn_home = NavButton("⌂", "Home")
        self.btn_home.set_active(True)
        self.btn_home.clicked.connect(lambda: self.change_page(0))
        sidebar.add_nav_button(self.btn_home)
        self.nav_buttons.append(self.btn_home)
        
        # Soil Data Input - using square/grid symbol
        self.btn_input = NavButton("▦", "Soil Data Input")
        self.btn_input.clicked.connect(lambda: self.change_page(1))
        sidebar.add_nav_button(self.btn_input)
        self.nav_buttons.append(self.btn_input)
        
        # Crop Evaluation - using plant/seedling symbol
        self.btn_evaluation = NavButton("⚘", "Crop Evaluation")
        self.btn_evaluation.clicked.connect(lambda: self.change_page(2))
        sidebar.add_nav_button(self.btn_evaluation)
        self.nav_buttons.append(self.btn_evaluation)
        
        # Reports - using chart symbol
        self.btn_reports = NavButton("◱", "Reports")
        self.btn_reports.clicked.connect(lambda: self.change_page(3))
        sidebar.add_nav_button(self.btn_reports)
        self.nav_buttons.append(self.btn_reports)
        
        # Knowledge Base - using book symbol
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
        title_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e5e8e5;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(32, 0, 24, 0)
        
        # Page title
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
        self.pages['home'] = home_page
        self.pages_stack.addWidget(home_page)
        
        # Input page
        input_page = InputPage()
        input_page.data_saved.connect(self.on_data_saved)
        # CRITICAL: Connect evaluation_complete signal
        input_page.evaluation_complete.connect(self.on_evaluation_complete)
        self.pages['input'] = input_page
        self.pages_stack.addWidget(input_page)
        
        # Placeholder for Crop Evaluation
        self.pages_stack.addWidget(self.create_placeholder_page("Select crops to evaluate"))
        
        # REPLACE PLACEHOLDER WITH ACTUAL REPORTS PAGE
        reports_page = ReportsPage()
        # Connect new evaluation signal to go back to input
        reports_page.new_evaluation_requested.connect(self.on_new_evaluation_requested)
        self.pages['reports'] = reports_page
        self.pages_stack.addWidget(reports_page)
        
        # Knowledge Base placeholder
        self.pages_stack.addWidget(self.create_placeholder_page("Browse crop requirements"))
        
        logger.info("All pages created")
    
    def create_placeholder_page(self, description):
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
    
    def on_evaluation_complete(self, results: dict):
        """
        Handle evaluation completion from Input Page.
        
        Args:
            results: Evaluation results dictionary from SuitabilityEvaluator
        """
        logger.info(f"📊 Evaluation complete for {results['crop_name']}")
        logger.info(f"   LSI: {results['lsi']:.2f}, Classification: {results['full_classification']}")
        
        # Pass results to reports page
        self.pages['reports'].display_results(results)
        
        # Navigate to reports page (index 3)
        self.change_page(3)
        
        logger.info("✅ Navigated to Reports page with results")
    
    def on_new_evaluation_requested(self):
        """
        Handle new evaluation request from Reports Page.
        User clicked "New Evaluation" button on reports page.
        """
        logger.info("🔄 New evaluation requested, navigating to Input page")
        
        # Navigate back to input page (index 1)
        self.change_page(1)
        
        # Optionally clear the form
        # self.pages['input'].clear_form()
    
    def change_page(self, index):
        """Change current page"""
        logger.info(f"Changing to page index: {index}")
        
        self.pages_stack.setCurrentIndex(index)
        
        # Update navigation buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        
        # Update title
        titles = ["Home", "Soil Data Input", "Crop Evaluation", 
                 "Reports & Analysis", "Knowledge Base"]
        self.page_title.setText(titles[index])
        
        # Refresh home page if navigating to it
        if index == 0 and 'home' in self.pages:
            self.pages['home'].refresh()
    
    def on_data_saved(self, soil_id):
        """Handle data saved event"""
        logger.info(f"Data saved event received: soil_id={soil_id}")
        # Refresh home page statistics
        if 'home' in self.pages:
            self.pages['home'].update_statistics()