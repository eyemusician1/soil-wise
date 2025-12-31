"""
SoilWise/ui/pages/evaluation_history_page.py
Evaluation History Page - View and manage past crop evaluations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QLineEdit, 
                               QComboBox, QPushButton, QHeaderView, QFrame,
                               QMessageBox, QFileDialog, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime
import json
import csv
import os
from database.db_manager import get_database


class EvaluationHistoryPage(QWidget):
    """Evaluation History page with search and filtering"""
    
    # Signals
    view_report_requested = Signal(dict)  # When user wants to view a report
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.evaluation_data = []  # Store all evaluations
        self.filtered_data = []    # Store filtered results
        self.init_ui()
        # Initialize database
        try:
            self.db = get_database()
            print("Database connected in Evaluation History Page")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.db = None
        self.load_history()
        

    
    def init_ui(self):
        """Initialize the page UI"""
        self.setStyleSheet("background-color: #fafcfa;")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(28)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Title and subtitle
        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        
        title = QLabel("Evaluation History")
        title.setFont(QFont("Georgia", 28, QFont.Bold))
        title.setStyleSheet("color: #1e293b; background: transparent;")
        
        subtitle = QLabel("View and manage your past crop suitability evaluations")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; background: transparent;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        # Export button
        btn_export = QPushButton("Export to CSV")
        btn_export.setFixedHeight(40)
        btn_export.setFixedWidth(140)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("""
            QPushButton {
                background: #7d9d7f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #8ab08c;
            }
            QPushButton:pressed {
                background: #6b8a6d;
            }
        """)
        btn_export.clicked.connect(self.export_to_csv)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(btn_export)
        
        layout.addLayout(header_layout)
        
        # Statistics section
        stats_layout = self.create_statistics_section()
        layout.addLayout(stats_layout)
        
        # Search and filter section
        filter_card = self.create_filter_section()
        layout.addWidget(filter_card)
        
        # Table section
        table_card = self.create_table_section()
        layout.addWidget(table_card, 1)
    
    def create_statistics_section(self):
        """Create modern statistics cards matching Home page style"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
       
        stats = [
            ("Total Evaluations", "0", "#5a9d5e", "="),    # List icon style
            ("Average LSI", "0.0", "#7fbc83", "~"),         # Wave/average symbol
            ("Most Evaluated", "None", "#6eb172", "★")     # Star symbol
        ]
        
        for label, value, color, icon_text in stats:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 12px;
                    border: none;
                }}
            """)
            
            # Add shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 8))
            card.setGraphicsEffect(shadow)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(24, 20, 24, 20)
            card_layout.setSpacing(12)
            
            # Header with icon and label
            header_layout = QHBoxLayout()
            header_layout.setSpacing(12)
            
            # Icon circle - STYLED LIKE HOME PAGE
            icon_container = QFrame()
            icon_container.setFixedSize(48, 48)
            icon_container.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {color}40, 
                        stop:0.5 {color}25, 
                        stop:1 {color}10);
                    border-radius: 24px;
                    border: 2.5px solid {color}35;
                }}
            """)
            
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel(icon_text)
            icon_label.setStyleSheet(f"""
                color: {color};
                font-size: 22px;
                font-weight: 800;
                background: transparent;
                border: none;
                padding: 0px;
            """)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                color: #475569; 
                font-size: 13px; 
                font-weight: 700;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                background: transparent;
            """)
            
            header_layout.addWidget(icon_container)
            header_layout.addWidget(label_widget)
            header_layout.addStretch()
            
            # Value
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Georgia", 32, QFont.Bold))
            value_widget.setStyleSheet(f"""
                color: {color}; 
                background: transparent; 
                margin-top: 8px;
                letter-spacing: -1px;
            """)
            
            # Store reference for updating
            if label == "Total Evaluations":
                self.stat_total = value_widget
            elif label == "Average LSI":
                self.stat_avg_lsi = value_widget
            elif label == "Most Evaluated":
                self.stat_most_crop = value_widget
            
            card_layout.addLayout(header_layout)
            card_layout.addWidget(value_widget)
            
            layout.addWidget(card)
        
        return layout

    def create_filter_section(self):
        """Create search and filter controls"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8f0e9;
                border-radius: 12px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 6))
        card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 13px; background: transparent;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by crop name...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #fafcfa;
                border: 1px solid #d4e4d4;
                border-radius: 6px;
                padding: 0px 14px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border: 2px solid #7d9d7f;
                background: white;
                padding: 0px 13px;
            }
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Classification filter
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 13px; background: transparent;")
        
        self.classification_filter = QComboBox()
        self.classification_filter.addItems([
            "All Classifications",
            "S1 - Highly Suitable",
            "S2 - Moderately Suitable", 
            "S3 - Marginally Suitable",
            "N1 - Currently Not Suitable",
            "N2 - Permanently Not Suitable"
        ])
        self.classification_filter.setFixedHeight(38)
        self.classification_filter.setStyleSheet("""
            QComboBox {
                background: #fafcfa;
                border: 1px solid #d4e4d4;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                color: #1e293b;
                min-width: 220px;
            }
            QComboBox:hover {
                border: 1px solid #7d9d7f;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        self.classification_filter.currentTextChanged.connect(self.apply_filters)
        
        # Clear button
        btn_clear = QPushButton("Clear")
        btn_clear.setFixedHeight(38)
        btn_clear.setFixedWidth(90)
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 0px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
                border-color: #94a3b8;
            }
        """)
        btn_clear.clicked.connect(self.clear_filters)
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input, 2)
        layout.addWidget(filter_label)
        layout.addWidget(self.classification_filter, 1)
        layout.addWidget(btn_clear)
        
        return card
    
    def create_table_section(self):
        """Create table for evaluation history"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8f0e9;
                border-radius: 12px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 6))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date & Time", "Crop Name", "LSI Score", "Classification", 
            "Limiting Factors", "Actions", "ID"
        ])
        
        # Hide ID column (used internally)
        self.table.setColumnHidden(6, True)
        
        # Table styling - FIXED SELECTION COLORS
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                gridline-color: #f1f5f9;
                font-size: 13px;
                border-radius: 12px;
            }
            QTableWidget::item {
                padding: 14px 16px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background: #f0f9f1;
                color: #1e293b;
            }
            QTableWidget::item:hover {
                background: #f8faf8;
            }
            QHeaderView::section {
                background: #fafcfa;
                color: #475569;
                padding: 16px 16px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }
        """)
        
        # Table properties
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(False)  # We'll handle this manually
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Crop Name
        header.setSectionResizeMode(2, QHeaderView.Fixed)             # LSI
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Classification
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Limiting Factors
        header.setSectionResizeMode(5, QHeaderView.Fixed)             # Actions
        
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(5, 180)
        
        layout.addWidget(self.table)
        
        return card
    
    def load_history(self):
        """Load evaluation history from database"""
        if not self.db:
            print("Database not available - using sample data")
            self.create_sample_data()
            return
        
        try:
            # Load from database
            db_evaluations = self.db.get_evaluation_history(limit=100)
            
            print(f"Loaded {len(db_evaluations)} evaluations from database")
            
            # Convert to internal format
            self.evaluation_data = []
            for eval_data in db_evaluations:
                formatted = {
                    'id': f"eval_{eval_data['evaluation_id']}",
                    'date': eval_data.get('created_at', '')[:19].replace('T', ' '),
                    'crop_name': eval_data.get('crop_id', '').replace('_', ' ').title(),
                    'lsi': eval_data.get('lsi', 0),
                    'lsc': eval_data.get('lsc', 'N/A'),
                    'classification': eval_data.get('full_classification', 'N/A'),
                    'limiting_factors': eval_data.get('limiting_factors', ''),
                    'location': eval_data.get('location', 'N/A')
                }
                self.evaluation_data.append(formatted)
            
            self.filtered_data = self.evaluation_data.copy()
            self.populate_table()
            self.update_statistics()
            
        except Exception as e:
            print(f"Error loading from database: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to sample data
            self.create_sample_data()

    
    def create_sample_data(self):
        """Create sample evaluation data"""
        self.evaluation_data = [
            {
                "id": "eval_001",
                "date": "2025-12-26 14:30:00",
                "crop_name": "Cabbage",
                "lsi": 78.5,
                "lsc": "S2",
                "classification": "S2 - Moderately Suitable",
                "limiting_factors": "t"
            },
            {
                "id": "eval_002",
                "date": "2025-12-25 10:15:00",
                "crop_name": "Banana",
                "lsi": 92.3,
                "lsc": "S1",
                "classification": "S1 - Highly Suitable",
                "limiting_factors": ""
            },
            {
                "id": "eval_003",
                "date": "2025-12-24 16:45:00",
                "crop_name": "Arabica Coffee",
                "lsi": 45.2,
                "lsc": "N1",
                "classification": "N1 - Currently Not Suitable",
                "limiting_factors": "w, t"
            }
        ]
        self.filtered_data = self.evaluation_data.copy()
        self.populate_table()
        self.update_statistics()
    
    def populate_table(self):
        """Populate table with filtered data"""
        self.table.setRowCount(0)
        
        for row_idx, eval_data in enumerate(self.filtered_data):
            self.table.insertRow(row_idx)
            
            # Date & Time
            date_item = QTableWidgetItem(eval_data['date'])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            date_item.setForeground(QColor("#475569"))
            self.table.setItem(row_idx, 0, date_item)
            
            # Crop Name
            crop_item = QTableWidgetItem(eval_data['crop_name'])
            crop_item.setFlags(crop_item.flags() & ~Qt.ItemIsEditable)
            crop_item.setFont(QFont("Georgia", 13, QFont.DemiBold))
            crop_item.setForeground(QColor("#1e293b"))
            self.table.setItem(row_idx, 1, crop_item)
            
            # LSI Score
            lsi_item = QTableWidgetItem(f"{eval_data['lsi']:.1f}")
            lsi_item.setFlags(lsi_item.flags() & ~Qt.ItemIsEditable)
            lsi_item.setTextAlignment(Qt.AlignCenter)
            lsi_item.setFont(QFont("Georgia", 14, QFont.Bold))
            
            # Color code LSI
            lsi_value = eval_data['lsi']
            if lsi_value >= 80:
                lsi_item.setForeground(QColor("#16a34a"))
            elif lsi_value >= 60:
                lsi_item.setForeground(QColor("#ca8a04"))
            else:
                lsi_item.setForeground(QColor("#dc2626"))
            
            self.table.setItem(row_idx, 2, lsi_item)
            
            # Classification
            class_item = QTableWidgetItem(eval_data['classification'])
            class_item.setFlags(class_item.flags() & ~Qt.ItemIsEditable)
            class_item.setForeground(QColor("#475569"))
            self.table.setItem(row_idx, 3, class_item)
            
            # Limiting Factors
            factors = eval_data.get('limiting_factors', '')
            factors_text = factors.upper() if factors else "None"
            factors_item = QTableWidgetItem(factors_text)
            factors_item.setFlags(factors_item.flags() & ~Qt.ItemIsEditable)
            factors_item.setForeground(QColor("#64748b"))
            self.table.setItem(row_idx, 4, factors_item)
            
            # Actions - Create widget with buttons
            actions_widget = self.create_action_buttons(eval_data)
            self.table.setCellWidget(row_idx, 5, actions_widget)
            
            # ID (hidden)
            id_item = QTableWidgetItem(eval_data['id'])
            self.table.setItem(row_idx, 6, id_item)
            
            # Set row height
            self.table.setRowHeight(row_idx, 70)
    
    def create_action_buttons(self, eval_data):
        """Create action buttons for each row - IMPROVED STYLING"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")  # Ensure transparent background
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # View button - Professional green matching SoilWise theme
        btn_view = QPushButton("View")
        btn_view.setFixedSize(70, 32)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setStyleSheet("""
            QPushButton {
                background: #7d9d7f;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #8ab08c;
            }
            QPushButton:pressed {
                background: #6b8a6d;
            }
        """)
        btn_view.clicked.connect(lambda: self.view_evaluation(eval_data))
        
        # Delete button - Professional red/gray
        btn_delete = QPushButton("Delete")
        btn_delete.setFixedSize(70, 32)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background: white;
                color: #dc2626;
                border: 1px solid #fca5a5;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #fef2f2;
                border-color: #dc2626;
            }
            QPushButton:pressed {
                background: #fee2e2;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_evaluation(eval_data))
        
        layout.addWidget(btn_view)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget

    
    def apply_filters(self):
        """Apply search and filter to data"""
        search_text = self.search_input.text().lower()
        classification = self.classification_filter.currentText()
        
        self.filtered_data = []
        
        for eval_data in self.evaluation_data:
            # Apply search filter
            if search_text and search_text not in eval_data['crop_name'].lower():
                continue
            
            # Apply classification filter
            if classification != "All Classifications":
                if not eval_data['classification'].startswith(classification[:2]):
                    continue
            
            self.filtered_data.append(eval_data)
        
        self.populate_table()
        self.update_statistics()
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.classification_filter.setCurrentIndex(0)
    
    def update_statistics(self):
        """Update statistics display - ALWAYS use ALL data, not filtered"""
        
        # === STATISTICS ARE BASED ON ALL DATA ===
        if not self.evaluation_data:
            self.stat_total.setText("0")
            self.stat_avg_lsi.setText("0.0")
            self.stat_most_crop.setText("None")
            return
        
        # Total evaluations - FROM ALL DATA
        total = len(self.evaluation_data)
        self.stat_total.setText(str(total))
        
        # Average LSI - FROM ALL DATA
        avg_lsi = sum(e['lsi'] for e in self.evaluation_data) / total
        self.stat_avg_lsi.setText(f"{avg_lsi:.1f}")
        
        # Most evaluated crop - FROM ALL DATA
        crop_counts = {}
        for eval_data in self.evaluation_data:
            crop = eval_data['crop_name']
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
        
        if crop_counts:
            most_crop = max(crop_counts, key=crop_counts.get)
            self.stat_most_crop.setText(most_crop)
        else:
            self.stat_most_crop.setText("None")

    
    def view_evaluation(self, eval_data):
        """View evaluation details"""
        # TODO: Navigate to reports page with this evaluation
        print(f"View evaluation: {eval_data['id']}")
        self.view_report_requested.emit(eval_data)
    
    def delete_evaluation(self, eval_data):
        """Delete an evaluation"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the evaluation for {eval_data['crop_name']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from data
            self.evaluation_data = [e for e in self.evaluation_data if e['id'] != eval_data['id']]
            self.filtered_data = [e for e in self.filtered_data if e['id'] != eval_data['id']]
            
            # Refresh table
            self.populate_table()
            self.update_statistics()
            
            QMessageBox.information(self, "Deleted", "Evaluation deleted successfully.")
    
    def export_to_csv(self):
        """Export filtered data to CSV"""
        if not self.filtered_data:
            QMessageBox.warning(self, "No Data", "No evaluations to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"evaluation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date & Time', 'Crop Name', 'LSI Score', 
                               'Classification', 'Limiting Factors'])
                
                for eval_data in self.filtered_data:
                    writer.writerow([
                        eval_data['date'],
                        eval_data['crop_name'],
                        eval_data['lsi'],
                        eval_data['classification'],
                        eval_data.get('limiting_factors', '')
                    ])
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Data exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Could not export data:\n{str(e)}")
    
    def add_evaluation(self, eval_data):
        """Add a new evaluation to history"""
        # Add timestamp if not present
        if 'date' not in eval_data:
            eval_data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate ID if not present
        if 'id' not in eval_data:
            eval_data['id'] = f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Add to data
        self.evaluation_data.insert(0, eval_data)
        self.apply_filters()  # Refresh with current filters
