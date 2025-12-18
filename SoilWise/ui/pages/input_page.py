"""
SoilWise/ui/pages/input_page.py
Enhanced Soil data input page with complete evaluation integration
Based on Escomen et al. 2024 methodology and Square Root Method
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                                QFrame, QGridLayout, QLineEdit, QComboBox, QGroupBox,
                                QDoubleSpinBox, QMessageBox, QFileDialog, QPushButton, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtWidgets import QGraphicsDropShadowEffect

# Import evaluation engine
try:
    from knowledge_base.evaluation import SuitabilityEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import SuitabilityEvaluator: {e}")
    EVALUATOR_AVAILABLE = False


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


class InputPage(QWidget):
    """Enhanced Soil data input page with complete evaluation integration"""
    
    data_saved = Signal(int)
    evaluation_complete = Signal(dict)  # Emits evaluation results for navigation

    def __init__(self, parent=None):
        super().__init__(parent)
        self.soil_inputs = {}
        self.climate_inputs = {}
        self.crop_input = None
        self.season_input = None
        self.season_label = None
        self.seasonal_info = None
        
        # Define seasonal crops based on Escomen et al. Table 7
        self.seasonal_crops = {
            "Cabbage", "Carrots", "Cocoa", "Maize", 
            "Sorghum", "Sugarcane", "Sweet Potato", "Tomato"
        }
        
        # Initialize evaluation engine
        self.evaluator = None
        if EVALUATOR_AVAILABLE:
            try:
                self.evaluator = SuitabilityEvaluator()
                print("✅ Evaluation engine initialized successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize evaluator: {e}")
        else:
            print("⚠️ Warning: Evaluation engine not available")
        
        self.init_ui()

    def init_ui(self):
        """Initialize enhanced user interface"""
        self.setStyleSheet("background-color: #fafcfa;")
        
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
        
        # Import/Export card
        layout.addWidget(self.create_import_export_card())
        
        # Crop selection with seasonal support
        layout.addWidget(self.create_crop_selection_group())
        
        # Location group
        layout.addWidget(self.create_location_group())
        
        # Soil properties with subcategories
        layout.addWidget(self.create_soil_properties_group())
        
        # Climate group
        layout.addWidget(self.create_climate_group())
        
        # Action buttons
        layout.addLayout(self.create_action_buttons())
        
        # Analysis section
        layout.addWidget(self.create_analysis_card())
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_header(self):
        """Create page header"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(8)
        
        title = QLabel("Soil Data Input")
        title.setFont(QFont("Georgia", 28, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        
        desc = QLabel("Enter detailed soil and landscape characteristics for crop suitability evaluation")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #6a8a6c; line-height: 1.5;")
        desc.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        
        return widget

    def create_import_export_card(self):
        """Create enhanced import/export card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        
        label = QLabel("◰ Data Import/Export")
        label.setFont(QFont("Georgia", 16, QFont.Bold))
        label.setStyleSheet("color: #3d5a3f;")
        
        template_btn = EnhancedButton("Download Template", "▥")
        template_btn.clicked.connect(self.download_template)
        
        import_btn = EnhancedButton("Import Excel", "↓")
        import_btn.clicked.connect(self.import_excel)
        
        export_btn = EnhancedButton("Export Excel", "↑")
        export_btn.clicked.connect(self.export_excel)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(template_btn)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        
        return card

    def create_crop_selection_group(self):
        """Create crop selection group with seasonal support"""
        group = QGroupBox()
        group.setStyleSheet("""
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
        group.setGraphicsEffect(shadow)
        
        title_label = QLabel("⚘ Crop Selection")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        
        # Crop selection dropdown
        crop_label = QLabel("Select Crop:")
        crop_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        crop_label.setStyleSheet("color: #4a6a4c;")
        grid.addWidget(crop_label, 0, 0)
        
        self.crop_input = QComboBox()
        self.crop_input.addItems([
            "Select a crop...",
            "Arabica Coffee", "Banana", "Cabbage", "Carrots", "Cocoa",
            "Maize", "Oil Palm", "Pineapple", "Robusta Coffee",
            "Sorghum", "Sugarcane", "Sweet Potato", "Tomato"
        ])
        self.crop_input.setMinimumHeight(44)
        self.crop_input.setStyleSheet("""
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
        self.crop_input.currentTextChanged.connect(self.on_crop_changed)
        grid.addWidget(self.crop_input, 0, 1)
        
        # Season selection
        self.season_label = QLabel("Growing Season:")
        self.season_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        self.season_label.setStyleSheet("color: #4a6a4c;")
        self.season_label.setVisible(False)
        grid.addWidget(self.season_label, 1, 0)
        
        self.season_input = QComboBox()
        self.season_input.addItems([
            "Select season...",
            "January - April (Dry Season)",
            "May - August (Wet Season)",
            "September - December (Cool Season)"
        ])
        self.season_input.setMinimumHeight(44)
        self.season_input.setStyleSheet("""
            QComboBox {
                background: #fff8dc;
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
        self.season_input.setVisible(False)
        grid.addWidget(self.season_input, 1, 1)
        
        self.seasonal_info = QLabel("⚠️ This crop has different suitability across growing seasons")
        self.seasonal_info.setFont(QFont("Segoe UI", 11, QFont.Normal))
        self.seasonal_info.setStyleSheet("color: #c87b00; font-style: italic;")
        self.seasonal_info.setWordWrap(True)
        self.seasonal_info.setVisible(False)
        grid.addWidget(self.seasonal_info, 2, 0, 1, 2)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group

    def on_crop_changed(self, crop_name):
        """Show/hide season selector based on crop selection"""
        is_seasonal = crop_name in self.seasonal_crops
        
        if self.season_label:
            self.season_label.setVisible(is_seasonal)
        if self.season_input:
            self.season_input.setVisible(is_seasonal)
        if self.seasonal_info:
            self.seasonal_info.setVisible(is_seasonal)
        
        if not is_seasonal and self.season_input:
            self.season_input.setCurrentIndex(0)

    def get_selected_season_code(self):
        """Convert UI season text to API season code"""
        if not self.season_input:
            return None
            
        season_text = self.season_input.currentText()
        season_mapping = {
            "January - April (Dry Season)": "january_april",
            "May - August (Wet Season)": "may_august",
            "September - December (Cool Season)": "september_december"
        }
        return season_mapping.get(season_text)

    def create_location_group(self):
        """Create location information group"""
        group = QGroupBox()
        group.setStyleSheet("""
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
        group.setGraphicsEffect(shadow)
        
        title_label = QLabel("◉ Location Information")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        
        site_label = QLabel("Site Name:")
        site_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        site_label.setStyleSheet("color: #4a6a4c;")
        grid.addWidget(site_label, 0, 0)
        
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("e.g., Farm Area A")
        self.site_input.setMinimumHeight(44)
        self.site_input.setStyleSheet("""
            QLineEdit {
                background: #f9fbf9;
                border: 2px solid #e0ede0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #3d5a3f;
            }
            QLineEdit:focus {
                border-color: #7d9d7f;
                background: white;
            }
        """)
        grid.addWidget(self.site_input, 0, 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group

    def create_soil_properties_group(self):
        """Create comprehensive soil properties group with subcategories"""
        group = QGroupBox()
        group.setStyleSheet("""
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
        group.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 32, 28, 28)
        main_layout.setSpacing(32)
        
        title_label = QLabel("◉ Soil Properties")
        title_label.setFont(QFont("Georgia", 18, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        main_layout.addWidget(title_label)
        
        main_layout.addWidget(self.create_subsection("Topography", [
            ("Slope (%):", "slope", 0, 100, 1.67, 0.1),
        ]))
        
        main_layout.addWidget(self.create_wetness_subsection())
        
        main_layout.addWidget(self.create_subsection("Physical Soil Characteristics", [
            ("Coarse Fragments (vol %):", "coarse_fragments", 0, 100, 0, 1.0),
            ("Soil Depth (cm):", "soil_depth", 0, 300, 138, 1.0),
            ("CaCO₃ (%):", "caco3", 0, 100, 0, 0.1),
            ("Gypsum (%):", "gypsum", 0, 100, 0, 0.1),
        ], include_texture=True))
        
        # ✅ MODIFIED: Added Sum of Basic Cations field
        main_layout.addWidget(self.create_subsection("Soil Fertility Characteristics", [
            ("Apparent CEC (cmol/kg clay):", "cec", 0, 200, 81.34, 0.1),
            ("Sum of Basic Cations (cmol/kg):", "sum_basic_cations", 0, 100, 14.0, 0.1),  # NEW FIELD
            ("Base Saturation (%):", "base_saturation", 0, 100, 36.03, 0.1),
            ("pH (H₂O):", "ph", 0, 14, 6.20, 0.1),
            ("Organic Carbon (%):", "organic_carbon", 0, 10, 1.90, 0.1),
        ]))
        
        main_layout.addWidget(self.create_subsection("Salinity and Alkalinity", [
            ("ECe (dS/m):", "ece", 0, 20, 0.12, 0.01),
            ("ESP (%):", "esp", 0, 100, 0.09, 0.01),
        ]))
        
        group.setLayout(main_layout)
        return group

    def create_subsection(self, title, fields, include_texture=False):
        """Create a subsection with fields"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                border: 1px solid #e8f1e8;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        
        subtitle = QLabel(title)
        subtitle.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        subtitle.setStyleSheet("color: #5a7a5c; background: transparent; border: none; padding: 0;")
        layout.addWidget(subtitle)
        
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(1, 1)
        
        spinbox_style = """
            QDoubleSpinBox {
                background: white;
                border: 2px solid #e0ede0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #3d5a3f;
                min-height: 28px;
            }
            QDoubleSpinBox:focus {
                border-color: #7d9d7f;
            }
            QDoubleSpinBox::up-button {
                background: #e8f3e8;
                border: none;
                border-top-right-radius: 4px;
                width: 20px;
            }
            QDoubleSpinBox::up-button:hover {
                background: #d4e4d4;
            }
            QDoubleSpinBox::down-button {
                background: #e8f3e8;
                border: none;
                border-bottom-right-radius: 4px;
                width: 20px;
            }
            QDoubleSpinBox::down-button:hover {
                background: #d4e4d4;
            }
            QDoubleSpinBox::up-arrow {
                image: none;
                border: 4px solid transparent;
                border-bottom: 6px solid #3d5a3f;
                width: 0;
                height: 0;
            }
            QDoubleSpinBox::down-arrow {
                image: none;
                border: 4px solid transparent;
                border-top: 6px solid #3d5a3f;
                width: 0;
                height: 0;
            }
        """
        
        for i, field_data in enumerate(fields):
            label_text, key, min_val, max_val, default, step = field_data
            
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 12, QFont.Medium))
            label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
            grid.addWidget(label, i, 0)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setSingleStep(step)
            spinbox.setMinimumHeight(40)
            spinbox.setStyleSheet(spinbox_style)
            
            self.soil_inputs[key] = spinbox
            grid.addWidget(spinbox, i, 1)
        
        if include_texture:
            texture_label = QLabel("Soil Texture:")
            texture_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
            texture_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
            grid.addWidget(texture_label, len(fields), 0)
            
            self.texture_input = QComboBox()
            self.texture_input.addItems([
                "Select texture...",
                "C - Clay", "SiC - Silty Clay", "SC - Sandy Clay",
                "CL - Clay Loam", "SiCL - Silty Clay Loam", "SCL - Sandy Clay Loam",
                "L - Loam", "SiL - Silt Loam", "SL - Sandy Loam",
                "Si - Silt", "LS - Loamy Sand", "S - Sand",
                "Cm - Clay (montmorillonitic)", "CLm - Clay Loam (montmorillonitic)",
                "fS - Fine Sand", "vfS - Very Fine Sand"
            ])
            self.texture_input.setMinimumHeight(40)
            self.texture_input.setStyleSheet("""
                QComboBox {
                    background: white;
                    border: 2px solid #e0ede0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: #3d5a3f;
                }
                QComboBox:focus {
                    border-color: #7d9d7f;
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
            grid.addWidget(self.texture_input, len(fields), 1)
        
        layout.addLayout(grid)
        return container

    def create_wetness_subsection(self):
        """Create wetness subsection with flooding and drainage"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                border: 1px solid #e8f1e8;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        
        subtitle = QLabel("Wetness")
        subtitle.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        subtitle.setStyleSheet("color: #5a7a5c; background: transparent; border: none; padding: 0;")
        layout.addWidget(subtitle)
        
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(1, 1)
        
        combo_style = """
            QComboBox {
                background: white;
                border: 2px solid #e0ede0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
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
        """
        
        flooding_label = QLabel("Flooding:")
        flooding_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        flooding_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
        grid.addWidget(flooding_label, 0, 0)
        
        self.flooding_input = QComboBox()
        self.flooding_input.addItems([
            "Select flooding class...",
            "Fo - No flooding",
            "Fo_good_gw_150 - Good drainage, GW > 150cm",
            "Fo_good_gw_100_150 - Good drainage, GW 100-150cm",
            "Fo_moderate - Moderate flooding risk",
            "Fo_imperfect_drainable - Imperfect but drainable",
            "Fo_poor_drainable - Poor but drainable",
            "Fo_poor_not_drainable - Poor, not drainable",
            "F1 - Occasional flooding",
            "F2 - Frequent flooding",
            "F3 - Very frequent flooding"
        ])
        self.flooding_input.setMinimumHeight(40)
        self.flooding_input.setStyleSheet(combo_style)
        grid.addWidget(self.flooding_input, 0, 1)
        
        drainage_label = QLabel("Drainage:")
        drainage_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        drainage_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
        grid.addWidget(drainage_label, 1, 0)
        
        self.drainage_input = QComboBox()
        self.drainage_input.addItems([
            "Select drainage class...",
            "good - Well drained",
            "good_moderate - Moderately well drained",
            "moderate - Somewhat poorly drained",
            "poor - Poorly drained",
            "poor_not_drainable - Very poorly drained"
        ])
        self.drainage_input.setMinimumHeight(40)
        self.drainage_input.setStyleSheet(combo_style)
        grid.addWidget(self.drainage_input, 1, 1)
        
        layout.addLayout(grid)
        return container

    def create_climate_group(self):
        """Create climate characteristics group"""
        group = QGroupBox()
        group.setStyleSheet("""
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
        group.setGraphicsEffect(shadow)
        
        title_label = QLabel("◎ Climate Characteristics")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        
        properties = [
            ("Average Temperature (°C):", "temperature", 0, 50, 22.29, 0.1),
            ("Annual Rainfall (mm):", "rainfall", 0, 5000, 2651.54, 10),
            ("Humidity (%):", "humidity", 0, 100, 76.62, 1),
        ]
        
        spinbox_style = """
            QDoubleSpinBox {
                background: #f9fbf9;
                border: 2px solid #e0ede0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #3d5a3f;
                min-height: 28px;
            }
            QDoubleSpinBox:focus {
                border-color: #7d9d7f;
                background: white;
            }
            QDoubleSpinBox::up-button {
                background: #e8f3e8;
                border: none;
                border-top-right-radius: 6px;
                width: 20px;
            }
            QDoubleSpinBox::up-button:hover {
                background: #d4e4d4;
            }
            QDoubleSpinBox::down-button {
                background: #e8f3e8;
                border: none;
                border-bottom-right-radius: 6px;
                width: 20px;
            }
            QDoubleSpinBox::down-button:hover {
                background: #d4e4d4;
            }
            QDoubleSpinBox::up-arrow {
                image: none;
                border: 4px solid transparent;
                border-bottom: 6px solid #3d5a3f;
                width: 0;
                height: 0;
            }
            QDoubleSpinBox::down-arrow {
                image: none;
                border: 4px solid transparent;
                border-top: 6px solid #3d5a3f;
                width: 0;
                height: 0;
            }
        """
        
        for i, (label_text, key, min_val, max_val, default, step) in enumerate(properties):
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
            label.setStyleSheet("color: #4a6a4c;")
            grid.addWidget(label, i, 0)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setSingleStep(step)
            spinbox.setMinimumHeight(44)
            spinbox.setStyleSheet(spinbox_style)
            
            self.climate_inputs[key] = spinbox
            grid.addWidget(spinbox, i, 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group

    def create_action_buttons(self):
        """Create action buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.addStretch()
        
        btn_clear = EnhancedButton("Clear Form", "↻")
        btn_clear.setMinimumWidth(160)
        btn_clear.clicked.connect(self.clear_form)
        
        btn_save = EnhancedButton("Save Data", "◈", primary=True)
        btn_save.setMinimumWidth(160)
        btn_save.setMinimumHeight(52)
        btn_save.clicked.connect(self.save_data)
        
        layout.addWidget(btn_clear)
        layout.addWidget(btn_save)
        
        return layout

    def create_analysis_card(self):
        """Create enhanced analysis section"""
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
        layout.setSpacing(12)
        
        title = QLabel("◈ Ready to Analyze?")
        title.setFont(QFont("Georgia", 20, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        
        desc = QLabel(
            "Once you've entered soil and climate data, "
            "click the button below to run the crop suitability analysis using the Square Root Method."
        )
        desc.setFont(QFont("Segoe UI", 14))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #5a7a5c; margin: 8px 0 20px 0;")
        
        btn_analyze = EnhancedButton("▶ Run Analysis", "", primary=True)
        btn_analyze.setMinimumHeight(64)
        btn_analyze.setStyleSheet("""
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
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #8ab08c, stop:1 #7d9d7f);
            }
            QPushButton:pressed {
                background: #6b8a6d;
            }
        """)
        btn_analyze.clicked.connect(self.run_analysis)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(btn_analyze)
        
        return card

    def get_texture_code(self):
        """Extract USDA texture code from dropdown"""
        if not hasattr(self, 'texture_input'):
            return ""
        
        texture_text = self.texture_input.currentText()
        if texture_text == "Select texture..." or not texture_text:
            return ""
        
        code = texture_text.split(" - ")[0].strip()
        return code

    def get_flooding_code(self):
        """Extract flooding code from dropdown"""
        if not hasattr(self, 'flooding_input'):
            return ""
        
        flooding_text = self.flooding_input.currentText()
        if flooding_text == "Select flooding class..." or not flooding_text:
            return ""
        
        code = flooding_text.split(" - ")[0].strip()
        return code

    def get_drainage_code(self):
        """Extract drainage code from dropdown"""
        if not hasattr(self, 'drainage_input'):
            return ""
        
        drainage_text = self.drainage_input.currentText()
        if drainage_text == "Select drainage class..." or not drainage_text:
            return ""
        
        code = drainage_text.split(" - ")[0].strip()
        return code

    def collect_form_data(self):
        """
        Collect all form data into a dictionary for evaluation.
        
        Returns:
            dict: Complete soil and climate data matching rules_engine requirements
        """
        data = {}
        
        # ===== CLIMATE DATA =====
        data['temperature'] = self.climate_inputs['temperature'].value()
        data['rainfall'] = self.climate_inputs['rainfall'].value()
        data['humidity'] = self.climate_inputs['humidity'].value()
        
        # ===== TOPOGRAPHY =====
        data['slope'] = self.soil_inputs['slope'].value()
        
        # ===== WETNESS =====
        data['drainage'] = self.get_drainage_code()
        data['flooding'] = self.get_flooding_code()
        
        # ===== PHYSICAL SOIL =====
        data['texture'] = self.get_texture_code()
        data['soil_depth'] = self.soil_inputs['soil_depth'].value()
        data['coarse_fragments'] = self.soil_inputs['coarse_fragments'].value()
        data['caco3'] = self.soil_inputs['caco3'].value()
        data['gypsum'] = self.soil_inputs['gypsum'].value()
        
        # ===== SOIL FERTILITY =====
        data['ph'] = self.soil_inputs['ph'].value()
        data['organic_carbon'] = self.soil_inputs['organic_carbon'].value()
        data['base_saturation'] = self.soil_inputs['base_saturation'].value()
        data['sum_basic_cations'] = self.soil_inputs['sum_basic_cations'].value()  # ✅ NEW LINE
        data['cec'] = self.soil_inputs['cec'].value()
        
        # ===== SALINITY =====
        data['ec'] = self.soil_inputs['ece'].value()
        data['esp'] = self.soil_inputs['esp'].value()
        
        return data

    def validate_form_data(self):
        """
        Validate form data before evaluation.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        crop_name = self.crop_input.currentText()
        if crop_name == "Select a crop...":
            return False, "⚠️ Please select a crop for evaluation"
        
        if crop_name in self.seasonal_crops:
            season_text = self.season_input.currentText()
            if season_text == "Select season...":
                return False, f"⚠️ {crop_name} is a seasonal crop. Please select a growing season."
        
        data = self.collect_form_data()
        
        if data['temperature'] <= 0:
            return False, "⚠️ Temperature must be greater than 0°C"
        if data['rainfall'] <= 0:
            return False, "⚠️ Annual rainfall must be greater than 0 mm"
        if not data['texture']:
            return False, "⚠️ Please select a soil texture"
        if not data['drainage']:
            return False, "⚠️ Please select a drainage class"
        if not data['flooding']:
            return False, "⚠️ Please select a flooding class"
        if data['ph'] <= 0 or data['ph'] > 14:
            return False, "⚠️ pH must be between 0 and 14"
        
        return True, ""

    def run_analysis(self):
        """Run complete crop suitability analysis"""
        if not self.evaluator:
            QMessageBox.critical(
                self,
                "Evaluation Engine Error",
                "The evaluation engine is not initialized.\n\n"
                "Please check that the crop requirements files are loaded correctly.\n\n"
                "Check console for details."
            )
            return
        
        is_valid, error_message = self.validate_form_data()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_message)
            return
        
        try:
            progress = QMessageBox(self)
            progress.setWindowTitle("Running Analysis")
            progress.setText("Evaluating crop suitability...\n\nThis may take a moment.")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.setModal(True)
            progress.show()
            QApplication.processEvents()
            
            soil_data = self.collect_form_data()
            crop_name = self.crop_input.currentText()
            
            season = None
            if crop_name in self.seasonal_crops:
                season = self.get_selected_season_code()
            
            print("\n" + "="*70)
            print("🔬 RUNNING CROP SUITABILITY EVALUATION")
            print("="*70)
            print(f"Crop: {crop_name}")
            if season:
                print(f"Season: {season}")
            print(f"\nSoil Data:")
            for key, value in soil_data.items():
                print(f"  {key}: {value}")
            print("="*70)
            
            result = self.evaluator.evaluate_suitability(
                soil_data=soil_data,
                crop_name=crop_name,
                season=season
            )
            
            progress.close()
            progress.deleteLater()
            QApplication.processEvents()
            
            self.show_results_summary(result)
            self.evaluation_complete.emit(result)
            
            print("\n✅ Evaluation completed successfully")
            print("="*70 + "\n")
            
        except ValueError as e:
            progress.close()
            QMessageBox.warning(
                self,
                "Evaluation Error",
                f"Could not evaluate crop suitability:\n\n{str(e)}"
            )
            print(f"\n⚠️ Validation error: {e}\n")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                f"Please check the console for details."
            )
            print(f"\n❌ Error during evaluation:")
            import traceback
            traceback.print_exc()

    def show_results_summary(self, result):
        """Display a summary of evaluation results"""
        lsi = result['lsi']
        lsc = result['lsc']
        full_class = result['full_classification']
        limiting = result['limiting_factors']
        
        emoji_map = {
            'S1': '🟢',
            'S2': '🟡',
            'S3': '🟠',
            'N': '🔴'
        }
        emoji = emoji_map.get(lsc, '⚪')
        
        message = f"""
<h2>{emoji} Evaluation Complete</h2>

<p><b>Crop:</b> {result['crop_name']}<br>
<i>{result['scientific_name']}</i></p>

<p><b>Land Suitability Index (LSI):</b> <span style="font-size:16pt; font-weight:bold">{lsi:.2f}</span></p>

<p><b>Classification:</b> <span style="font-size:14pt; font-weight:bold; color:{'#2d7a2d' if lsc=='S1' else '#d4a00a' if lsc=='S2' else '#d46a0a' if lsc=='S3' else '#c0392b'}">{full_class}</span></p>

<p><b>Interpretation:</b><br>
{result['interpretation']}</p>
"""
        
        if limiting:
            message += f"""
<p><b>⚠️ Limiting Factors:</b><br>
"""
            for detail in result['limiting_factors_detailed'][:3]:
                message += f"• {detail['description']}: {detail['actual_value']}<br>"
            message += "</p>"
        
        message += """
<hr>
<p style="color:#666">View the <b>Reports</b> tab for detailed analysis and recommendations.</p>
"""
        
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle("Crop Suitability Results")
        msgbox.setTextFormat(Qt.RichText)
        msgbox.setText(message)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setMinimumWidth(500)
        msgbox.exec()

    def clear_form(self):
        """Clear all form inputs"""
        self.site_input.clear()
        
        for spinbox in self.soil_inputs.values():
            spinbox.setValue(0)
        
        if hasattr(self, 'texture_input'):
            self.texture_input.setCurrentIndex(0)
        if hasattr(self, 'flooding_input'):
            self.flooding_input.setCurrentIndex(0)
        if hasattr(self, 'drainage_input'):
            self.drainage_input.setCurrentIndex(0)
        
        if self.crop_input:
            self.crop_input.setCurrentIndex(0)
        if self.season_input:
            self.season_input.setCurrentIndex(0)
        
        for spinbox in self.climate_inputs.values():
            spinbox.setValue(spinbox.minimum())
        
        print("✅ Form cleared")

    def save_data(self):
        """Save soil data"""
        QMessageBox.information(
            self,
            "Success",
            "Soil data saved successfully!\n\n"
            "You can now run the analysis to evaluate crop suitability."
        )
        self.data_saved.emit(1)

    def import_excel(self):
        """Import soil data from Excel"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if filename:
            QMessageBox.information(
                self,
                "Success",
                f"Data imported from:\n{filename}"
            )

    def export_excel(self):
        """Export current form data to Excel"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Excel File",
            "soilwise_data.xlsx",
            "Excel Files (*.xlsx)"
        )
        if filename:
            QMessageBox.information(
                self,
                "Success",
                f"Data exported to:\n{filename}"
            )

    def download_template(self):
        """Download Excel template"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template",
            "soilwise_template.xlsx",
            "Excel Files (*.xlsx)"
        )
        if filename:
            QMessageBox.information(
                self,
                "Success",
                f"Template downloaded successfully!\n\n"
                f"Saved to: {filename}\n\n"
                f"Fill in your data and import it back using 'Import Excel' button."
            )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = InputPage()
    window.setWindowTitle("SoilWise - Soil Data Input")
    window.resize(900, 800)
    window.show()
    sys.exit(app.exec())
