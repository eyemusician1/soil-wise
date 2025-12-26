"""
SoilWise/ui/pages/crop_evaluation_page.py

Multi-crop comparison page with enhanced UI - ENHANCED VERSION
Features:
- Compare multiple crops
- Save comparison history
- Export to PDF
- Visual comparison charts
- Update soil data option
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QGroupBox, QCheckBox, QRadioButton,
    QComboBox, QPushButton, QMessageBox, QDialog, QTableWidget,
    QTableWidgetItem, QButtonGroup, QApplication, QHeaderView,
    QFileDialog
)
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

import json
import os
from datetime import datetime
from pathlib import Path


# Import evaluation engine
try:
    from knowledge_base.evaluation import SuitabilityEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import SuitabilityEvaluator: {e}")
    EVALUATOR_AVAILABLE = False

# ✅ EXCEL export support 
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
    print("✅ Excel export available (openpyxl)")
except ImportError:
    EXCEL_AVAILABLE = False
    print("⚠️ Warning: openpyxl not installed. Excel export disabled.")
    print("   Install with: pip install openpyxl")


class EnhancedButton(QPushButton):
    """Enhanced button with modern styling"""
    
    def __init__(self, text, icon="", primary=False, parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}" if icon else text)
        self.primary = primary
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.apply_style()
    
    def apply_style(self):
        """Apply modern agricultural styling"""
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #7d9d7f, stop:1 #6b8a6d);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 15px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #8ab08c, stop:1 #7d9d7f);
                }
                QPushButton:pressed {
                    background: #6b8a6d;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #5a7a5c;
                    border: 2px solid #d4e4d4;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #f5f9f5;
                    border-color: #7d9d7f;
                }
                QPushButton:pressed {
                    background: #eaf3ea;
                }
            """)


class CropEvaluationPage(QWidget):
    """Multi-crop comparison page with enhanced features"""
    
    comparison_complete = Signal(list)  # Emits list of results
    navigate_to_input = Signal()  # NEW: Navigate to input page
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.crop_checkboxes = {}
        self.selected_soil_data = None
        self.saved_data_combo = None
        self.last_soil_data = None
        self.last_crop_name = None
        self.compare_status_label = None
        self.compare_btn = None
        self.last_comparison_results = None  # ✅ NEW: Store last results
        self.soil_data_timestamp = None  # ✅ NEW: Track when data was received
        self.season_card = None

        
        # Define seasonal crops
        self.seasonal_crops = {
            "Cabbage", "Carrots", "Maize", 
            "Sorghum", "Sugarcane", "Sweet Potato", "Tomato"
        }
        
        # ✅ NEW: Create comparison history directory
        self.history_dir = Path("data/comparison_history")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize evaluation engine
        self.evaluator = None
        if EVALUATOR_AVAILABLE:
            try:
                self.evaluator = SuitabilityEvaluator()
                print("✅ Evaluation engine initialized for crop comparison")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize evaluator: {e}")
        else:
            print("⚠️ Warning: Evaluation engine not available")
        
        self.init_ui()
    
    def set_last_soil_data(self, soil_data, crop_name=None):
        """Set the last used soil data from Input page"""
        self.last_soil_data = soil_data
        self.last_crop_name = crop_name
        self.soil_data_timestamp = QDateTime.currentDateTime()  # ✅ NEW: Timestamp
        print(f"✅ Crop Evaluation: Received soil data (Last crop: {crop_name})")
        self.update_saved_data_display()
    
    def update_saved_data_display(self):
        """Update the saved data dropdown with last used data"""
        if not hasattr(self, 'saved_data_combo') or self.saved_data_combo is None:
            return
        
        self.saved_data_combo.clear()
        
        if self.last_soil_data:
            # ✅ ENHANCED: Add timestamp info
            temp = self.last_soil_data.get('temperature', 'N/A')
            ph = self.last_soil_data.get('ph', 'N/A')
            crop_info = f" (Last: {self.last_crop_name})" if self.last_crop_name else ""
            
            # Add time info if available
            time_info = ""
            if self.soil_data_timestamp:
                mins_ago = self.soil_data_timestamp.secsTo(QDateTime.currentDateTime()) // 60
                if mins_ago < 60:
                    time_info = f" - {mins_ago} min ago"
                elif mins_ago < 1440:  # Less than 24 hours
                    time_info = f" - {mins_ago // 60} hrs ago"
            
            label = f"Last Analysis{crop_info} - pH {ph}, Temp {temp}°C{time_info}"
            self.saved_data_combo.addItem(label, self.last_soil_data)
            print(f"✅ Added last soil data to dropdown: {label}")
        else:
            self.saved_data_combo.addItem("No soil data available")
        
        # Update button state
        self.update_compare_button_text()
    
    def init_ui(self):
        """Initialize enhanced user interface"""
        self.setStyleSheet("background-color: #fafcfa;")
        
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #fafcfa; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: #fafcfa;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Page header
        header = self.create_header()
        layout.addWidget(header)
        
        # Step 1: Soil data source
        layout.addWidget(self.create_soil_source_card())
        
        # Step 2: Crop selector
        layout.addWidget(self.create_crop_selector_card())
        
        # Step 3: Season selector
        layout.addWidget(self.create_season_card())
        
        # Compare button
        layout.addWidget(self.create_compare_button())
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.update_season_card_state()

    
    def create_header(self):
        """Create page header"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(8)
        
        title = QLabel("Crop Evaluation")
        title.setFont(QFont("Georgia", 28, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        
        desc = QLabel(
            "Compare suitability of multiple crops for your soil conditions. "
            "Select crops to evaluate and see which ones are best suited for your land."
        )
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #6a8a6c; line-height: 1.5;")
        desc.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        
        return widget
    
    def create_soil_source_card(self):
        """Create soil data source selection card"""
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 24px;
                margin-top: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("◉ Step 1: Select Soil Data Source")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel(
            "Use soil data from a previous analysis on the Soil Data Input page."
        )
        info_label.setFont(QFont("Segoe UI", 12))
        info_label.setStyleSheet("color: #6a8a6c;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Saved data dropdown
        self.saved_data_combo = QComboBox()
        self.saved_data_combo.setMinimumHeight(44)
        self.saved_data_combo.setStyleSheet("""
            QComboBox {
                background: #f9fbf9;
                border: 2px solid #e0ede0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #3d5a3f;
            }
            QComboBox:focus {
                border-color: #7d9d7f;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 5px solid transparent;
                border-top: 6px solid #3d5a3f;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
        """)
        self.saved_data_combo.currentIndexChanged.connect(self.update_compare_button_text)
        self.update_saved_data_display()
        layout.addWidget(self.saved_data_combo)
        
        # ✅ ENHANCEMENT 1: Add "Update Data" button
        update_btn_layout = QHBoxLayout()
        update_data_btn = EnhancedButton("↻ Update Soil Data", "")
        update_data_btn.setToolTip("Navigate to Soil Data Input page to run a new analysis")
        update_data_btn.clicked.connect(self.on_update_data_clicked)
        update_btn_layout.addWidget(update_data_btn)
        update_btn_layout.addStretch()
        layout.addLayout(update_btn_layout)
        
        card.setLayout(layout)
        return card
    
    def on_update_data_clicked(self):
        """Handle update data button click"""
        reply = QMessageBox.question(
            self,
            "Navigate to Soil Data Input?",
            "This will take you to the Soil Data Input page to run a new analysis.\n\n"
            "Your current crop selections will be cleared. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.navigate_to_input.emit()
    
    def create_crop_selector_card(self):
        """Create multi-crop selector card with seasonal labels"""
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 24px;
                margin-top: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("⚘ Step 2: Select Crops to Compare")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel(
            "Select multiple crops to compare their suitability (minimum 2 crops). "
            "Crops marked with ◐ require season selection."
        )
        info_label.setFont(QFont("Segoe UI", 12))
        info_label.setStyleSheet("color: #6a8a6c;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Scrollable crop list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(360)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #f9fbf9;
                border: 2px solid #e0ede0;
                border-radius: 8px;
            }
        """)
        
        crop_widget = QWidget()
        crop_widget.setStyleSheet("background: #f9fbf9;")
        crop_layout = QVBoxLayout(crop_widget)
        crop_layout.setContentsMargins(16, 16, 16, 16)
        crop_layout.setSpacing(8)
        
        # Get available crops
        if self.evaluator:
            crops = self.evaluator.get_available_crops()
        else:
            crops = [
                "Arabica Coffee", "Banana", "Cabbage", "Carrots",
                "Cocoa", "Maize", "Oil Palm", "Pineapple",
                "Robusta Coffee", "Sorghum", "Sugarcane", "Sweet Potato", "Tomato"
            ]
        
        # Create checkboxes with season labels
        for crop in sorted(crops):
            crop_container = QWidget()
            crop_container.setStyleSheet("background: transparent;")
            crop_h_layout = QHBoxLayout(crop_container)
            crop_h_layout.setContentsMargins(0, 0, 0, 0)
            crop_h_layout.setSpacing(8)
            
            checkbox = QCheckBox(f"  {crop}")
            checkbox.setFont(QFont("Segoe UI", 13))
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #3d5a3f;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #d4e4d4;
                    border-radius: 4px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #7d9d7f;
                    border-color: #7d9d7f;
                }
            """)
            checkbox.stateChanged.connect(self.on_crop_selection_changed)
            crop_h_layout.addWidget(checkbox)
            
            
            if crop in self.seasonal_crops:
                season_label = QLabel("◐ Seasonal")
                season_label.setFont(QFont("Segoe UI", 10))
                season_label.setStyleSheet("""
                    color: #c87b00;
                    background: #fff8dc;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-weight: 600;
                """)
                crop_h_layout.addWidget(season_label)
            
            crop_h_layout.addStretch()
            crop_layout.addWidget(crop_container)
            self.crop_checkboxes[crop] = checkbox
        
        crop_layout.addStretch()
        scroll.setWidget(crop_widget)
        layout.addWidget(scroll)
        
        # Helper buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        select_all_btn = EnhancedButton("Select All", " ")
        select_all_btn.clicked.connect(self.select_all_crops)
        
        clear_all_btn = EnhancedButton("Clear All", "")
        clear_all_btn.clicked.connect(self.clear_all_crops)
        
        seasonal_btn = EnhancedButton("Seasonal Crops", "")
        seasonal_btn.clicked.connect(
            lambda: self.select_preset(list(self.seasonal_crops))
        )
        
        perennial_btn = EnhancedButton("Perennial Crops", "")
        perennial_btn.clicked.connect(self.select_perennial_crops)
        
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(clear_all_btn)
        btn_layout.addWidget(seasonal_btn)
        btn_layout.addWidget(perennial_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        card.setLayout(layout)
        return card
    
    
    def select_perennial_crops(self):
        """Select all non-seasonal (perennial) crops"""
        self.clear_all_crops()
        for crop_name, checkbox in self.crop_checkboxes.items():
            if crop_name not in self.seasonal_crops:
                checkbox.setChecked(True)
    
    def create_season_card(self):
        """Create season selection card"""
        card = QGroupBox()
        card.setObjectName("seasonCard")
        card.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 24px;
                margin-top: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("◐ Step 3: Select Growing Season (for seasonal crops only)")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("")
        layout.addWidget(title_label)
        
        # Info label
        info_text = QLabel(
            "This selection applies to all seasonal crops selected above. "
            "Perennial crops are not affected by season."
        )
        info_text.setFont(QFont("Segoe UI", 11))
        info_text.setStyleSheet("color: #6a8a6c; font-style: italic;")
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
        # Season radio buttons
        self.season_group = QButtonGroup(self)
        
        seasons = [
            ("January - April (Dry Season)", "january_april"),
            ("May - August (Wet Season)", "may_august"),
            ("September - December (Cool Season)", "september_december")
        ]
        
        for season_text, season_code in seasons:
            radio = QRadioButton(season_text)
            radio.setFont(QFont("Segoe UI", 13))
            radio.setStyleSheet("")
            radio.setProperty("season_code", season_code)
            self.season_group.addButton(radio)
            layout.addWidget(radio)
        
        # Set first as default
        self.season_group.buttons()[0].setChecked(True)
        
        card.setLayout(layout)
        self.season_card = card
        return card
    
    def update_season_card_state(self):
        """Enable Step 3 only if at least one seasonal crop is selected."""
        if not self.season_card:
            return

        selected = self.get_selected_crops()
        has_seasonal = any(c in self.seasonal_crops for c in selected)

        if not has_seasonal:
            self.season_card.setEnabled(False)
            self.season_card.setStyleSheet("""
            QGroupBox#seasonCard {
                background: transparent;
                border: none;
                padding: 24px;
                margin-top: 12px;
            }
            QGroupBox#seasonCard QLabel {
                color: #b0b0b0;
            }
            QGroupBox#seasonCard QRadioButton {
                color: #b0b0b0;
            }
            """)
        else:
            self.season_card.setEnabled(True)
            self.season_card.setStyleSheet("""
            QGroupBox#seasonCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 24px;
                margin-top: 12px;
            }
            QGroupBox#seasonCard QLabel {
                color: #3d5a3f;
            }
            QGroupBox#seasonCard QRadioButton {
                color: #4a6a4c;
            }
            """)

    
    def create_compare_button(self):
        """Create comparison action button"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #e8f3e8, stop:1 #f0f7f0);
                border-radius: 12px;
                border: none;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        
        # Status label
        self.compare_status_label = QLabel("Select at least 2 crops to compare")
        self.compare_status_label.setFont(QFont("Segoe UI", 14))
        self.compare_status_label.setStyleSheet("color: #6a8a6c;")
        self.compare_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.compare_status_label)
        
        # Compare button
        self.compare_btn = EnhancedButton("Compare Crops", "", primary=True)
        self.compare_btn.setMinimumHeight(64)
        self.compare_btn.setEnabled(False)
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #7d9d7f, stop:1 #6b8a6d);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #8ab08c, stop:1 #7d9d7f);
            }
            QPushButton:pressed {
                background: #6b8a6d;
            }
            QPushButton:disabled {
                background: #d0d0d0;
                color: #888888;
            }
        """)
        self.compare_btn.clicked.connect(self.compare_crops)
        layout.addWidget(self.compare_btn)
        
        return card
    
    def get_selected_crops(self):
        """Get list of selected crop names"""
        selected = []
        for crop_name, checkbox in self.crop_checkboxes.items():
            if checkbox.isChecked():
                selected.append(crop_name)
        return selected
    
    def select_all_crops(self):
        """Select all crop checkboxes"""
        for checkbox in self.crop_checkboxes.values():
            checkbox.setChecked(True)
        self.update_compare_button_text()
        self.update_season_card_state()

    
    def clear_all_crops(self):
        """Clear all crop checkboxes"""
        for checkbox in self.crop_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_preset(self, crop_names):
        """Select specific preset crops"""
        self.clear_all_crops()
        for crop_name in crop_names:
            if crop_name in self.crop_checkboxes:
                self.crop_checkboxes[crop_name].setChecked(True)
                
    def on_crop_selection_changed(self, state):
        self.update_compare_button_text()
        self.update_season_card_state()

    
    def update_compare_button_text(self):
        """Update compare button text based on selection AND data availability"""
        if not hasattr(self, 'compare_status_label') or self.compare_status_label is None:
            return
        if not hasattr(self, 'compare_btn') or self.compare_btn is None:
            return
        
        count = len(self.get_selected_crops())
        has_data = self.last_soil_data is not None
        
        selected_crops = self.get_selected_crops()
        seasonal_count = sum(1 for c in selected_crops if c in self.seasonal_crops)
        perennial_count = count - seasonal_count
        
        if count == 0:
            self.compare_status_label.setText("Select at least 2 crops to compare")
            self.compare_status_label.setStyleSheet("color: #6a8a6c;")
            self.compare_btn.setText("▶ Compare Crops")
            self.compare_btn.setEnabled(False)
        elif count == 1:
            self.compare_status_label.setText(
                "Select at least one more crop for comparison"
            )
            self.compare_status_label.setStyleSheet("color: #6a8a6c;")
            self.compare_btn.setText("▶ Compare Crops")
            self.compare_btn.setEnabled(False)
        elif not has_data:
            self.compare_status_label.setText(
                f"{count} crops selected, but no soil data available. "
                "Please run an analysis on the Soil Data Input page first."
            )
            self.compare_status_label.setStyleSheet("color: #d46a00; font-weight: 600;")
            self.compare_btn.setText("▶ Compare Crops")
            self.compare_btn.setEnabled(False)
        else:
            if seasonal_count > 0 and perennial_count > 0:
                status = f"Ready to compare {count} crops ({seasonal_count} seasonal, {perennial_count} perennial)"
            elif seasonal_count > 0:
                status = f"Ready to compare {seasonal_count} seasonal crops"
            else:
                status = f"Ready to compare {perennial_count} perennial crops"
            
            self.compare_status_label.setText(status)
            self.compare_status_label.setStyleSheet("color: #6a8a6c;")
            self.compare_btn.setText(f"▶ Compare {count} Crops")
            self.compare_btn.setEnabled(True)
    
    def get_selected_season(self):
        """Get selected season code"""
        selected_button = self.season_group.checkedButton()
        if selected_button:
            return selected_button.property("season_code")
        return "january_april"
    
    def compare_crops(self):
        """Run multi-crop comparison"""
        if not self.evaluator:
            QMessageBox.critical(
                self,
                "Evaluation Engine Error",
                "The evaluation engine is not initialized.\n\n"
                "Please check that the crop requirements files are loaded correctly."
            )
            return
        
        selected_crops = self.get_selected_crops()
        
        if len(selected_crops) < 2:
            QMessageBox.warning(
                self,
                "Insufficient Selection",
                "Please select at least 2 crops to compare."
            )
            return
        
        if not self.last_soil_data:
            QMessageBox.warning(
                self,
                "No Soil Data",
                "No soil data is available.\n\n"
                "Please run an analysis on the Soil Data Input page first."
            )
            return
        
        try:
            progress = QMessageBox(self)
            progress.setWindowTitle("Comparing Crops")
            progress.setText("Evaluating multiple crops... this may take a moment.")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.setModal(True)
            progress.show()
            QApplication.processEvents()
            
            season = self.get_selected_season()
            
            print("="*70)
            print("RUNNING MULTI-CROP COMPARISON")
            print("="*70)
            print(f"Selected crops: {', '.join(selected_crops)}")
            print(f"Season: {season}")
            print(f"Soil data available: {self.last_soil_data is not None}")
            
            results = []
            for crop_name in selected_crops:
                crop_season = season if crop_name in self.seasonal_crops else None
                print(f"\nEvaluating: {crop_name}" + (f" ({crop_season})" if crop_season else ""))
                
                result = self.evaluator.evaluate_suitability(
                    soil_data=self.last_soil_data,
                    crop_name=crop_name,
                    season=crop_season
                )
                results.append(result)
            
            progress.close()
            progress.deleteLater()
            
            results.sort(key=lambda x: x['lsi'], reverse=True)
            
            print("\n" + "="*70)
            print("COMPARISON RESULTS")
            print("="*70)
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['crop_name']}: LSI={r['lsi']:.2f}, {r['full_classification']}")
            print("="*70)
            
            # ✅ ENHANCEMENT 2: Save comparison history
            self.last_comparison_results = results
            self.save_comparison_history(results, selected_crops, season)
            
            # Show comparison dialog
            self.show_comparison_results(results)
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Comparison Error",
                f"An error occurred during comparison:\n\n{str(e)}\n\n"
                "Please check the console for details."
            )
            print(f"❌ Error during comparison: {e}")
            import traceback
            traceback.print_exc()
    
    # ✅ ENHANCEMENT 2: Save comparison history
    def save_comparison_history(self, results, selected_crops, season):
        """Save comparison to history file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.history_dir / f"comparison_{timestamp}.json"
            
            history_data = {
                "timestamp": datetime.now().isoformat(),
                "soil_data": self.last_soil_data,
                "season": season,
                "selected_crops": selected_crops,
                "results": results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Comparison history saved: {filename}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save comparison history: {e}")
    
    def show_comparison_results(self, results):
        """Display comparison results in dialog with enhanced features"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Crop Comparison Results")
        dialog.resize(1100, 700)
        dialog.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Title
        title = QLabel("◉ Crop Suitability Comparison")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # ✅ ENHANCEMENT 4: Add visual chart
        chart_view = self.create_comparison_chart(results)
        chart_view.setMaximumHeight(300)
        layout.addWidget(chart_view)
        
        # Results table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Rank", "Crop", "LSI", "Classification", "Limiting Factors"
        ])
        table.setRowCount(len(results))
        
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0ede0;
                border-radius: 8px;
                gridline-color: #e8f1e8;
            }
            QHeaderView::section {
                background: #f9fbf9;
                color: #3d5a3f;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0ede0;
                font-weight: bold;
            }
        """)
        
        for row, result in enumerate(results):
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, rank_item)
            
            table.setItem(row, 1, QTableWidgetItem(result['crop_name']))
            
            lsi_item = QTableWidgetItem(f"{result['lsi']:.2f}")
            lsi_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, lsi_item)
            
            class_item = QTableWidgetItem(result['full_classification'])
            class_item.setTextAlignment(Qt.AlignCenter)
            
            lsc = result['lsc']
            if lsc == 'S1':
                class_item.setBackground(QColor("#7d9d7f"))
            elif lsc == 'S2':
                class_item.setBackground(QColor("#a8c4a8"))
            elif lsc == 'S3':
                class_item.setBackground(QColor("#e6b84d"))
            else:
                class_item.setBackground(QColor("#d46a6a"))
            
            class_item.setForeground(QColor("white"))
            table.setItem(row, 3, class_item)
            
            limiting = result.get('limiting_factors', '')
            table.setItem(row, 4, QTableWidgetItem(limiting if limiting else "-"))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Recommendation
        best_crop = results[0]
        rec_label = QLabel(
            f"◈ Recommendation: {best_crop['crop_name']} is most suitable "
            f"(LSI: {best_crop['lsi']:.2f}, {best_crop['full_classification']})"
        )
        rec_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        rec_label.setStyleSheet("""
            background: #e8f3e8;
            color: #3d5a3f;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #d4e4d4;
        """)
        rec_label.setWordWrap(True)
        layout.addWidget(rec_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        # ✅ ENHANCEMENT 3: Export to PDF button
        if EXCEL_AVAILABLE:
            export_btn = EnhancedButton("Export as Excel", "")
            export_btn.clicked.connect(lambda: self.export_comparison_excel(results, dialog))
            btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        
        close_btn = EnhancedButton("Close", "", primary=True)
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    # ✅ ENHANCEMENT 4: Create visual comparison chart
    def create_comparison_chart(self, results):
        """Create bar chart comparing LSI values"""
        # Create bar set
        bar_set = QBarSet("Land Suitability Index (LSI)")
        bar_set.setColor(QColor("#7d9d7f"))
        
        categories = []
        for result in results:
            bar_set.append(result['lsi'])
            categories.append(result['crop_name'])
        
        # Create series
        series = QBarSeries()
        series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Crop Suitability Comparison")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitleFont(QFont("Georgia", 14, QFont.Bold))
        
        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText("LSI Value")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    # ✅ ENHANCEMENT 3: Export comparison to Excel
def export_comparison_excel(self, results, parent_dialog):
    """Export comparison results to Excel file"""
    if not EXCEL_AVAILABLE:
        QMessageBox.warning(
            parent_dialog,
            "Excel Export Unavailable",
            "openpyxl is not installed.\n\n"
            "Install with: pip install openpyxl"
        )
        return
    
    try:
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"crop_comparison_{timestamp}.xlsx"
        
        filepath, _ = QFileDialog.getSaveFileName(
            parent_dialog,
            "Export Comparison as Excel",
            default_filename,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not filepath:
            return  # User cancelled
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Crop Comparison"
        
        # Define styles
        header_fill = PatternFill(start_color="3d5a3f", end_color="3d5a3f", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        title_font = Font(bold=True, size=14, color="3d5a3f")
        
        border = Border(
            left=Side(style='thin', color='e0ede0'),
            right=Side(style='thin', color='e0ede0'),
            top=Side(style='thin', color='e0ede0'),
            bottom=Side(style='thin', color='e0ede0')
        )
        
        # Classification colors
        class_colors = {
            'S1': 'C6E0B4',  # Light green
            'S2': 'FFE699',  # Light yellow
            'S3': 'F4B084',  # Light orange
            'N': 'FF9999'    # Light red
        }
        
        # Title
        ws['A1'] = "Crop Suitability Comparison Report"
        ws['A1'].font = title_font
        ws.merge_cells('A1:E1')
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        
        # Timestamp and soil info
        row = 3
        ws[f'A{row}'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws[f'A{row}'].font = Font(size=10)
        row += 1
        
        ws[f'A{row}'] = f"Number of crops compared: {len(results)}"
        row += 1
        
        # Soil parameters (compact format)
        if self.last_soil_data:
            ph = self.last_soil_data.get('ph', 'N/A')
            temp = self.last_soil_data.get('temperature', 'N/A')
            ws[f'A{row}'] = f"Soil pH: {ph}, Temperature: {temp}°C"
            row += 1
        
        row += 1  # Blank row
        
        # Table headers
        headers = ["Rank", "Crop", "LSI", "Classification", "Limiting Factors"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border
        
        # Data rows
        for rank, result in enumerate(results, 1):
            row += 1
            
            # Rank
            cell = ws.cell(row=row, column=1, value=rank)
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
            
            # Crop
            cell = ws.cell(row=row, column=2, value=result['crop_name'])
            cell.border = border
            
            # LSI
            cell = ws.cell(row=row, column=3, value=f"{result['lsi']:.2f}")
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
            
            # Classification with color
            lsc = result['lsc']
            class_text = result['full_classification']
            cell = ws.cell(row=row, column=4, value=class_text)
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
            
            if lsc in class_colors:
                cell.fill = PatternFill(start_color=class_colors[lsc], 
                                       end_color=class_colors[lsc], 
                                       fill_type="solid")
            
            # Limiting factors
            limiting = result.get('limiting_factors', '')
            cell = ws.cell(row=row, column=5, value=limiting if limiting else "-")
            cell.border = border
            cell.alignment = Alignment(wrap_text=True)
        
        row += 2  # Blank row
        
        # Recommendation
        best_crop = results[0]
        ws[f'A{row}'] = (
            f"◈ Recommendation: {best_crop['crop_name']} is most suitable "
            f"(LSI: {best_crop['lsi']:.2f}, {best_crop['full_classification']})"
        )
        ws[f'A{row}'].font = Font(bold=True, color="3d5a3f", size=11)
        ws.merge_cells(f'A{row}:E{row}')
        ws[f'A{row}'].alignment = Alignment(wrap_text=True)
        
        # Set column widths
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 25
        ws.column_dimensions['E'].width = 30
        
        # Save file
        wb.save(filepath)
        
        QMessageBox.information(
            parent_dialog,
            "Export Successful",
            f"Comparison report exported to:\n{filepath}"
        )
        
        print(f"✅ Excel export successful: {filepath}")
        
    except Exception as e:
        QMessageBox.critical(
            parent_dialog,
            "Export Error",
            f"Failed to export Excel file:\n\n{str(e)}"
        )
        print(f"❌ Excel export error: {e}")
        import traceback
        traceback.print_exc()
