"""
SoilWise/ui/pages/input_page_new.py
Enhanced Soil data input page with modern agricultural design
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                               QFrame, QGridLayout, QLineEdit, QComboBox, QGroupBox,
                               QDoubleSpinBox, QMessageBox, QFileDialog, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from SoilWise.ui.widgets.fluent_button import FluentButton
from SoilWise.ui.widgets.fluent_card import FluentCard
from SoilWise.config.constants import SOIL_RANGES, CLIMATE_RANGES, SOIL_TEXTURES, BARANGAYS
from SoilWise.models.soil_data import SoilData
from SoilWise.services.excel_service import ExcelService
from SoilWise.services.data_service import DataService
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__)


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
    """Enhanced Soil data input page"""
    
    data_saved = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.excel_service = ExcelService()
        self.data_service = DataService()
        self.init_ui()
        logger.info("Enhanced InputPage initialized")
    
    def init_ui(self):
        """Initialize enhanced user interface"""
        # Set background color
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
        
        # Location group
        layout.addWidget(self.create_location_group())
        
        # Soil properties group
        layout.addWidget(self.create_soil_group())
        
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
        
        desc = QLabel("Enter soil properties and climate characteristics from Piagapo, Lanao del Sur")
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
        
        # Add shadow effect
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
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
    
    def create_location_group(self):
        """Create enhanced location information group"""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 24px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        # Add shadow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
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
        
        # Barangay
        barangay_label = QLabel("Barangay:")
        barangay_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        barangay_label.setStyleSheet("color: #4a6a4c;")
        grid.addWidget(barangay_label, 0, 0)
        
        self.barangay_input = QComboBox()
        self.barangay_input.addItems(BARANGAYS)
        self.barangay_input.setMinimumHeight(44)
        self.barangay_input.setStyleSheet("""
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
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """)
        grid.addWidget(self.barangay_input, 0, 1)
        
        # Site Name
        site_label = QLabel("Site Name:")
        site_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        site_label.setStyleSheet("color: #4a6a4c;")
        grid.addWidget(site_label, 1, 0)
        
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
        grid.addWidget(self.site_input, 1, 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group
    
    def create_soil_group(self):
        """Create enhanced soil properties group"""
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
        
        # Add shadow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        group.setGraphicsEffect(shadow)
        
        title_label = QLabel("◉  Soil Properties")
        title_label.setFont(QFont("Georgia", 16, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        
        # Store spinboxes
        self.soil_inputs = {}
        
        properties = [
            ("pH Level:", "ph"),
            ("Organic Matter (%):", "organic_matter"),
            ("Nitrogen (ppm):", "nitrogen"),
            ("Phosphorus (ppm):", "phosphorus"),
            ("Potassium (ppm):", "potassium"),
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
        
        for i, (label_text, key) in enumerate(properties):
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
            label.setStyleSheet("color: #4a6a4c;")
            grid.addWidget(label, i, 0)
            
            min_val, max_val, default = SOIL_RANGES[key]
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setSingleStep(0.1 if max_val <= 14 else 1.0)
            spinbox.setMinimumHeight(44)
            spinbox.setStyleSheet(spinbox_style)
            
            self.soil_inputs[key] = spinbox
            grid.addWidget(spinbox, i, 1)
        
        # Soil Texture
        texture_label = QLabel("Soil Texture:")
        texture_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        texture_label.setStyleSheet("color: #4a6a4c;")
        grid.addWidget(texture_label, len(properties), 0)
        
        self.texture_input = QComboBox()
        self.texture_input.addItems(SOIL_TEXTURES)
        self.texture_input.setMinimumHeight(44)
        self.texture_input.setStyleSheet("""
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
            }
        """)
        grid.addWidget(self.texture_input, len(properties), 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group
    
    def create_climate_group(self):
        """Create enhanced climate characteristics group"""
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
        
        # Add shadow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
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
        
        # Store climate inputs
        self.climate_inputs = {}
        
        properties = [
            ("Average Temperature (°C):", "temperature"),
            ("Annual Rainfall (mm):", "rainfall"),
            ("Humidity (%):", "humidity"),
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
        
        for i, (label_text, key) in enumerate(properties):
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
            label.setStyleSheet("color: #4a6a4c;")
            grid.addWidget(label, i, 0)
            
            min_val, max_val, default = CLIMATE_RANGES[key]
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setMinimumHeight(44)
            spinbox.setStyleSheet(spinbox_style)
            
            self.climate_inputs[key] = spinbox
            grid.addWidget(spinbox, i, 1)
        
        layout.addLayout(grid)
        group.setLayout(layout)
        
        return group
    
    def create_action_buttons(self):
        """Create enhanced action buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.addStretch()
        
        btn_clear = EnhancedButton("Clear Form", "↻")
        btn_clear.setMinimumWidth(160)
        btn_clear.clicked.connect(self.clear_form)
        
        btn_save = EnhancedButton("Save Data", "◈", primary=True)
        btn_save.setMinimumWidth(160)
        btn_save.setMinimumHeight(52)
        btn_save.clicked.connect(self.save_soil_data)
        
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
        
        # Add shadow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
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

    
    def get_form_data(self) -> SoilData:
        """Get data from form fields"""
        return SoilData(
            barangay=self.barangay_input.currentText(),
            site_name=self.site_input.text().strip(),
            ph=self.soil_inputs['ph'].value(),
            organic_matter=self.soil_inputs['organic_matter'].value(),
            nitrogen=self.soil_inputs['nitrogen'].value(),
            phosphorus=self.soil_inputs['phosphorus'].value(),
            potassium=self.soil_inputs['potassium'].value(),
            texture=self.texture_input.currentText(),
            temperature=self.climate_inputs['temperature'].value(),
            rainfall=self.climate_inputs['rainfall'].value(),
            humidity=self.climate_inputs['humidity'].value()
        )
    
    def set_form_data(self, soil_data: SoilData):
        """Set form fields from SoilData"""
        logger.info(f"Setting form data: {soil_data}")
        
        index = self.barangay_input.findText(soil_data.barangay)
        if index >= 0:
            self.barangay_input.setCurrentIndex(index)
        
        self.site_input.setText(soil_data.site_name)
        
        self.soil_inputs['ph'].setValue(soil_data.ph)
        self.soil_inputs['organic_matter'].setValue(soil_data.organic_matter)
        self.soil_inputs['nitrogen'].setValue(soil_data.nitrogen)
        self.soil_inputs['phosphorus'].setValue(soil_data.phosphorus)
        self.soil_inputs['potassium'].setValue(soil_data.potassium)
        
        index = self.texture_input.findText(soil_data.texture)
        if index >= 0:
            self.texture_input.setCurrentIndex(index)
        
        self.climate_inputs['temperature'].setValue(soil_data.temperature)
        self.climate_inputs['rainfall'].setValue(soil_data.rainfall)
        self.climate_inputs['humidity'].setValue(soil_data.humidity)
    
    def clear_form(self):
        """Clear all form inputs"""
        logger.info("Clearing form")
        
        reply = QMessageBox.question(
            self,
            "Clear Form",
            "Are you sure you want to clear all input fields?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.barangay_input.setCurrentIndex(0)
            self.site_input.clear()
            
            for key, spinbox in self.soil_inputs.items():
                _, _, default = SOIL_RANGES[key]
                spinbox.setValue(default)
            
            self.texture_input.setCurrentIndex(0)
            
            for key, spinbox in self.climate_inputs.items():
                _, _, default = CLIMATE_RANGES[key]
                spinbox.setValue(default)
            
            logger.info("Form cleared")
    
    def save_soil_data(self):
        """Save soil data to database"""
        logger.info("Saving soil data")
        
        try:
            soil_data = self.get_form_data()
            
            is_valid, error_msg = soil_data.validate()
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error_msg)
                return
            
            soil_id = self.data_service.save_soil_data(soil_data)
            
            QMessageBox.information(
                self,
                "Success",
                f"Soil data saved successfully!\n\nRecord ID: {soil_id}\n\n"
                "You can now run the analysis to evaluate crop suitability."
            )
            
            self.data_saved.emit(soil_id)
            logger.info(f"Soil data saved with ID: {soil_id}")
            
        except Exception as e:
            logger.error(f"Failed to save soil data: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save soil data:\n{str(e)}")
    
    def import_excel(self):
        """Import soil data from Excel"""
        logger.info("Starting Excel import")
        
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_name:
            try:
                soil_data = self.excel_service.import_soil_data(file_name)
                self.set_form_data(soil_data)
                
                QMessageBox.information(self, "Success", "Data imported successfully!")
                logger.info(f"Excel import successful from: {file_name}")
                
            except Exception as e:
                logger.error(f"Excel import failed: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to import Excel file:\n{str(e)}")
    
    def export_excel(self):
        """Export current form data to Excel"""
        logger.info("Starting Excel export")
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Excel File",
            "soilwise_data.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            try:
                soil_data = self.get_form_data()
                self.excel_service.export_soil_data(soil_data, file_name)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Data exported successfully to:\n{file_name}"
                )
                logger.info(f"Excel export successful to: {file_name}")
                
            except Exception as e:
                logger.error(f"Excel export failed: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to export Excel file:\n{str(e)}")
    
    def download_template(self):
        """Download Excel template"""
        logger.info("Downloading Excel template")
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template",
            "soilwise_template.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            try:
                self.excel_service.create_template(file_name)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template downloaded successfully!\n\nFile saved to:\n{file_name}\n\n"
                    "Fill in your data and import it back using 'Import Excel' button."
                )
                logger.info(f"Template created: {file_name}")
                
            except Exception as e:
                logger.error(f"Template creation failed: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to create template:\n{str(e)}")
    
    def run_analysis(self):
        """Run crop suitability analysis"""
        logger.info("Running analysis")
        
        if self.barangay_input.currentIndex() == 0:
            QMessageBox.warning(
                self,
                "No Data",
                "Please enter or import soil data before running analysis!"
            )
            return
        
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
        logger.info("Analysis initiated")
