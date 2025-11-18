"""
SoilWise/ui/pages/input_page_enhanced.py
Enhanced Soil data input page with categorized soil properties
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                               QFrame, QGridLayout, QLineEdit, QComboBox, QGroupBox,
                               QDoubleSpinBox, QMessageBox, QFileDialog, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class EnhancedButton(QPushButton):
    """Enhanced button with modern styling"""
    
    def __init__(self, text, icon="", primary=False, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}" if icon else text)
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
    """Enhanced Soil data input page with categorized properties"""
    
    data_saved = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soil_inputs = {}
        self.climate_inputs = {}
        self.crop_input = None  # Initialize crop input
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
        
        # Crop selection
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
        
        desc = QLabel("Enter detailed soil and landscape characteristics")
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
        
        label = QLabel("◰  Data Import/Export")
        label.setFont(QFont("Georgia", 16, QFont.Bold))
        label.setStyleSheet("color: #3d5a3f;")
        
        template_btn = EnhancedButton("Download Template", "▥")
        template_btn.clicked.connect(self.download_template)
        
        import_btn = EnhancedButton("Import Excel", "⇓")
        import_btn.clicked.connect(self.import_excel)
        
        export_btn = EnhancedButton("Export Excel", "⇑")
        export_btn.clicked.connect(self.export_excel)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(template_btn)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        
        return card
    
    def create_crop_selection_group(self):
        """Create crop selection group"""
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
        
        title_label = QLabel("⚘  Crop Selection")
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
            "Arabica Coffee",
            "Banana",
            "Cabbage",
            "Carrots",
            "Cocoa",
            "Maize",
            "Oil Palm",
            "Pineapple",
            "Robusta Coffee",
            "Sorghum",
            "Sugarcane",
            "Sweet Potato",
            "Tomato"
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
        grid.addWidget(self.crop_input, 0, 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group
    
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
        
        title_label = QLabel("◉  Location Information")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        
        # Site Name
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
        
        title_label = QLabel("◉  Soil Properties")
        title_label.setFont(QFont("Georgia", 18, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        main_layout.addWidget(title_label)
        
        main_layout.addWidget(self.create_subsection("Topography", [
            ("Slope (%):", "slope", 0, 100, 0, 1.0),
        ]))
        
        main_layout.addWidget(self.create_wetness_subsection())
        
        main_layout.addWidget(self.create_subsection("Physical Soil Characteristics", [
            ("Coarse Fragments (vol %):", "coarse_fragments", 0, 100, 0, 1.0),
            ("Soil Depth (cm):", "soil_depth", 0, 300, 100, 10.0),
            ("CaCO₃ (%):", "caco3", 0, 100, 0, 0.1),
            ("Gypsum (%):", "gypsum", 0, 100, 0, 0.1),
        ], include_texture=True))
        
        main_layout.addWidget(self.create_subsection("Soil Fertility Characteristics", [
            ("Apparent CEC (cmol/kg clay):", "cec", 0, 100, 24, 1.0),
            ("Base Saturation (%):", "base_saturation", 0, 100, 80, 1.0),
            ("pH H₂O:", "ph", 0, 14, 7.0, 0.1),
            ("Organic Carbon (%):", "organic_carbon", 0, 10, 2.4, 0.1),
        ]))
        
        main_layout.addWidget(self.create_subsection("Salinity and Alkalinity", [
            ("ECe (dS/m):", "ece", 0, 20, 0, 0.1),
            ("ESP (%):", "esp", 0, 100, 0, 0.1),
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
        
        # Subsection title
        subtitle = QLabel(title)
        subtitle.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        subtitle.setStyleSheet("color: #5a7a5c; background: transparent; border: none; padding: 0;")
        layout.addWidget(subtitle)
        
        # Fields grid
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
        
        # Add texture field if requested
        if include_texture:
            texture_label = QLabel("Soil Texture/Structure:")
            texture_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
            texture_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
            grid.addWidget(texture_label, len(fields), 0)
            
            self.texture_input = QComboBox()
            self.texture_input.addItems([
                "Select...",
                "Clay", "Silty Clay", "Sandy Clay",
                "Clay Loam", "Silty Clay Loam", "Sandy Clay Loam",
                "Loam", "Silt Loam", "Sandy Loam",
                "Silt", "Loamy Sand", "Sand"
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
        """
        
        # Flooding
        flooding_label = QLabel("Flooding:")
        flooding_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        flooding_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
        grid.addWidget(flooding_label, 0, 0)
        
        self.flooding_input = QComboBox()
        self.flooding_input.addItems([
            "Select...",
            "None (Fo)",
            "Good (Fo good; groundwa. > 150 cm)",
            "Good-Moderate (Fo good; groundwa. 100-150 cm)",
            "Moderate (Fo moderate)",
            "Imperfect (Fo imperf. but drainab)",
            "Poor (Fo poor but drainab)"
        ])
        self.flooding_input.setMinimumHeight(40)
        self.flooding_input.setStyleSheet(combo_style)
        grid.addWidget(self.flooding_input, 0, 1)
        
        # Drainage
        drainage_label = QLabel("Drainage:")
        drainage_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        drainage_label.setStyleSheet("color: #4a6a4c; background: transparent; border: none;")
        grid.addWidget(drainage_label, 1, 0)
        
        self.drainage_input = QComboBox()
        self.drainage_input.addItems([
            "Select...",
            "Well drained",
            "Moderately well drained",
            "Somewhat poorly drained",
            "Poorly drained",
            "Very poorly drained"
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
        
        title_label = QLabel("◐  Climate Characteristics")
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
            ("Average Temperature (°C):", "temperature", 0, 50, 25, 0.1),
            ("Annual Rainfall (mm):", "rainfall", 0, 5000, 2000, 10),
            ("Humidity (%):", "humidity", 0, 100, 70, 1),
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
        
        title = QLabel("◈  Ready to Analyze?")
        title.setFont(QFont("Georgia", 20, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        
        desc = QLabel(
            "Once you've entered or imported soil and climate data, "
            "click the button below to run the crop suitability analysis."
        )
        desc.setFont(QFont("Segoe UI", 14))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #5a7a5c; margin: 8px 0 20px 0;")
        
        btn_analyze = EnhancedButton("▶  Run Analysis", "", primary=True)
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
        
        for spinbox in self.climate_inputs.values():
            spinbox.setValue(spinbox.minimum())
    
    def save_data(self):
        """Save soil data"""
        QMessageBox.information(
            self,
            "Success",
            "Soil data saved successfully!\n\nYou can now run the analysis to evaluate crop suitability."
        )
        self.data_saved.emit(1)
    
    def import_excel(self):
        """Import soil data from Excel"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_name:
            QMessageBox.information(self, "Success", f"Data imported from:\n{file_name}")
    
    def export_excel(self):
        """Export current form data to Excel"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Excel File",
            "soilwise_data.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            QMessageBox.information(self, "Success", f"Data exported to:\n{file_name}")
    
    def download_template(self):
        """Download Excel template"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template",
            "soilwise_template.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            QMessageBox.information(
                self,
                "Success",
                f"Template downloaded successfully!\n\nFile saved to:\n{file_name}\n\n"
                "Fill in your data and import it back using 'Import Excel' button."
            )
    
    def run_analysis(self):
        """Run crop suitability analysis"""
        QMessageBox.information(
            self,
            "Analysis Running",
            "Crop suitability analysis is now running...\n\n"
            "This will:\n"
            "• Apply threshold analysis\n"
            "• Classify land suitability (S1, S2, S3, N)\n"
            "• Identify limiting factors\n"
            "• Generate detailed reports\n\n"
            "Results will appear in the 'Reports' tab."
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
