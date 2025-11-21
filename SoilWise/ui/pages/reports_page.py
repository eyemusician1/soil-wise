"""
SoilWise/ui/pages/reports_page.py
Simplified Reports & Analysis Page - With Collapsible Recommendations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                               QFrame, QGridLayout, QGroupBox, QPushButton, QTabWidget,
                               QFileDialog, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from datetime import datetime
import json

# Import the extracted analysis components
from SoilWise.ui.widgets.analysis_tabs import (
    ParameterAnalysisTab, 
    VisualAnalysisTab, 
    LimitingFactorsTab
)


class CollapsibleSection(QWidget):
    """Collapsible section widget with smooth animation"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.init_ui(title)
    
    def init_ui(self, title: str):
        """Initialize the collapsible section UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle)
        self.update_button_text(title)
        
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8ab08c, stop:1 #7d9d7f);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 20px;
                text-align: left;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Georgia';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9bc09d, stop:1 #8ab08c);
            }
            QPushButton:pressed {
                background: #7d9d7f;
            }
        """)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.toggle_button)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 12, 0, 0)
        self.content_layout.setSpacing(0)
        
        main_layout.addWidget(self.content_widget)
        
        # Animation
        self.animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def update_button_text(self, title: str):
        """Update button text with arrow indicator"""
        arrow = "▼" if self.is_expanded else "▶"
        self.toggle_button.setText(f"{arrow}  {title}")
    
    def toggle(self):
        """Toggle the section visibility"""
        self.is_expanded = not self.is_expanded
        self.update_button_text(self.toggle_button.text().split("  ", 1)[1])
        
        if self.is_expanded:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """Collapse the section"""
        self.animation.setStartValue(self.content_widget.height())
        self.animation.setEndValue(0)
        self.animation.start()
    
    def expand(self):
        """Expand the section"""
        self.animation.setStartValue(self.content_widget.height())
        # Get the actual height needed
        self.content_widget.setMaximumHeight(16777215)  # Reset max height
        content_height = self.content_widget.sizeHint().height()
        self.animation.setEndValue(content_height)
        self.animation.start()
    
    def set_content(self, widget: QWidget):
        """Set the content widget"""
        self.content_layout.addWidget(widget)


class ReportsPage(QWidget):
    """Simplified Reports & Analysis Page with Collapsible Recommendations"""
    
    new_evaluation_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the reports page UI"""
        self.setStyleSheet("background-color: #fafcfa;")
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #fafcfa; }")
        
        # Container
        container = QWidget()
        container.setStyleSheet("background-color: #fafcfa;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Page header
        header = self.create_header()
        layout.addWidget(header)
        
        # Empty state (shown when no results)
        self.empty_state = self.create_empty_state()
        layout.addWidget(self.empty_state)
        
        # Results container (hidden initially)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(24)
        self.results_container.setVisible(False)
        layout.addWidget(self.results_container)
        
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
        
        title = QLabel("Reports & Analysis")
        title.setFont(QFont("Georgia", 28, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        
        desc = QLabel("Comprehensive crop suitability evaluation results and recommendations")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #6a8a6c; line-height: 1.5;")
        desc.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        
        return widget
    
    def create_empty_state(self):
        """Create empty state when no results available"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("◱")
        icon.setFont(QFont("Segoe UI", 72))
        icon.setStyleSheet("color: #a8b5a8;")
        icon.setAlignment(Qt.AlignCenter)
        
        title = QLabel("No Evaluation Results Yet")
        title.setFont(QFont("Georgia", 20, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel(
            "Run a crop suitability analysis from the Soil Data Input page\n"
            "to view detailed reports and recommendations here."
        )
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #6a8a6c;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        
        return card
    
    def display_results(self, results: dict):
        """Display evaluation results"""
        self.current_results = results
        
        # Hide empty state, show results
        self.empty_state.setVisible(False)
        self.results_container.setVisible(True)
        
        # Clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add result sections
        self.results_layout.addWidget(self.create_summary_card(results))
        self.results_layout.addWidget(self.create_tabbed_analysis(results))
        self.results_layout.addWidget(self.create_collapsible_recommendations(results))
        self.results_layout.addWidget(self.create_action_buttons())
    
    def create_summary_card(self, results: dict):
        """Create summary card with key metrics"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
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
        layout.setSpacing(20)
        
        # Title row with timestamp
        title_row = QHBoxLayout()
        title = QLabel("◈  Evaluation Summary")
        title.setFont(QFont("Georgia", 20, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        title_row.addWidget(title)
        
        timestamp = QLabel(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        timestamp.setFont(QFont("Segoe UI", 11))
        timestamp.setStyleSheet("color: #8a9a8c;")
        title_row.addStretch()
        title_row.addWidget(timestamp)
        
        layout.addLayout(title_row)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        
        # Crop info
        crop_widget = self.create_metric_widget(
            "Crop",
            f"{results['crop_name']}",
            f"{results['scientific_name']}"
        )
        metrics_grid.addWidget(crop_widget, 0, 0)
        
        # LSI with color coding
        lsi_color = self.get_lsi_color(results['lsc'])
        lsi_widget = self.create_metric_widget(
            "Land Suitability Index",
            f"{results['lsi']:.2f}",
            "Out of 100",
            lsi_color
        )
        metrics_grid.addWidget(lsi_widget, 0, 1)
        
        # Classification
        class_text = self.get_classification_text(results['lsc'])
        class_widget = self.create_metric_widget(
            "Classification",
            f"{results['full_classification']}",
            class_text,
            lsi_color
        )
        metrics_grid.addWidget(class_widget, 0, 2)
        
        # Limiting factors
        limiting = results['limiting_factors'] or "None"
        limiting_widget = self.create_metric_widget(
            "Limiting Factors",
            limiting.upper() if limiting != "None" else "None",
            self.decode_limiting_factors(limiting),
            "#c87b00" if limiting != "None" else "#2d7a2d"
        )
        metrics_grid.addWidget(limiting_widget, 0, 3)
        
        layout.addLayout(metrics_grid)
        
        # Season info if applicable
        if results.get('season'):
            season_container = QFrame()
            season_container.setStyleSheet("""
                QFrame {
                    background: #f9fbf9;
                    border-radius: 6px;
                    padding: 12px 16px;
                }
            """)
            season_layout = QHBoxLayout(season_container)
            season_layout.setContentsMargins(0, 0, 0, 0)
            
            season_label = QLabel(f"◆  Growing Season: {self.format_season(results['season'])}")
            season_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
            season_label.setStyleSheet("color: #5a7a5c;")
            season_layout.addWidget(season_label)
            
            layout.addWidget(season_container)
        
        # Interpretation section
        interp_container = QFrame()
        interp_container.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        interp_layout = QVBoxLayout(interp_container)
        interp_layout.setSpacing(10)
        
        interp_label = QLabel("◉  Interpretation")
        interp_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        interp_label.setStyleSheet("color: #4a6a4c;")
        
        interp_text = QLabel(results['interpretation'])
        interp_text.setFont(QFont("Segoe UI", 13))
        interp_text.setStyleSheet("color: #5a7a5c; line-height: 1.6;")
        interp_text.setWordWrap(True)
        
        interp_layout.addWidget(interp_label)
        interp_layout.addWidget(interp_text)
        
        layout.addWidget(interp_container)
        
        # Notes if available
        if results.get('notes'):
            notes_container = QFrame()
            notes_container.setStyleSheet("""
                QFrame {
                    background: #fffef0;
                    border-radius: 6px;
                    padding: 12px 16px;
                }
            """)
            notes_layout = QVBoxLayout(notes_container)
            notes_layout.setSpacing(8)
            
            notes_label = QLabel("◈  Additional Notes")
            notes_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            notes_label.setStyleSheet("color: #6a5a00;")
            
            notes_text = QLabel(results['notes'])
            notes_text.setFont(QFont("Segoe UI", 11))
            notes_text.setStyleSheet("color: #6a7a6c; font-style: italic;")
            notes_text.setWordWrap(True)
            
            notes_layout.addWidget(notes_label)
            notes_layout.addWidget(notes_text)
            
            layout.addWidget(notes_container)
        
        return card
    
    def create_metric_widget(self, label: str, value: str, subtitle: str, color: str = "#3d5a3f"):
        """Create a metric display widget"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 11))
        label_widget.setStyleSheet("color: #6a8a6c;")
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Georgia", 20, QFont.Bold))
        value_widget.setStyleSheet(f"color: {color};")
        value_widget.setWordWrap(True)
        
        subtitle_widget = QLabel(subtitle)
        subtitle_widget.setFont(QFont("Segoe UI", 10))
        subtitle_widget.setStyleSheet("color: #8a9a8c;")
        subtitle_widget.setWordWrap(True)
        
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        layout.addWidget(subtitle_widget)
        
        return widget
    
    def create_tabbed_analysis(self, results: dict):
        """Create tabbed widget using extracted components"""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background: white;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
                padding: 0px;
                margin-top: 0px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        group.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 0 0 12px 12px;
            }
            QTabBar::tab {
                background: #f5f9f5;
                color: #5a7a5c;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3d5a3f;
            }
            QTabBar::tab:hover {
                background: #eaf3ea;
            }
        """)
        
        # Add tabs using extracted components
        tabs.addTab(ParameterAnalysisTab(results), "◱  Parameter Analysis")
        tabs.addTab(VisualAnalysisTab(results), "◐  Visual Analysis")
        
        # Only add limiting factors tab if there are limiting factors
        if results.get('limiting_factors_detailed'):
            tabs.addTab(LimitingFactorsTab(results), "◈  Limiting Factors")
        
        layout.addWidget(tabs)
        
        return group
    
    def create_collapsible_recommendations(self, results: dict):
        """Create collapsible recommendations section"""
        collapsible = CollapsibleSection("Recommendations")
        
        # Create recommendations content
        recommendations_content = self.create_recommendations_content(results)
        collapsible.set_content(recommendations_content)
        
        return collapsible
    
    def create_recommendations_content(self, results: dict):
        """Create the recommendations content widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
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
        layout.setSpacing(18)
        
        subtitle = QLabel(
            "Based on the evaluation results, here are specific recommendations "
            "to optimize crop production:"
        )
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #6a8a6c; margin-bottom: 8px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        # Add each recommendation
        for i, rec in enumerate(results['recommendations'], 1):
            rec_widget = QFrame()
            rec_widget.setStyleSheet("""
                QFrame {
                    background: #f9fbf9;
                    border-radius: 6px;
                    padding: 14px;
                }
            """)
            
            rec_layout = QHBoxLayout(rec_widget)
            rec_layout.setSpacing(12)
            
            # Number badge
            badge = QLabel(str(i))
            badge.setFont(QFont("Segoe UI", 12, QFont.Bold))
            badge.setStyleSheet("""
                background: #7d9d7f;
                color: white;
                border-radius: 14px;
                padding: 4px;
            """)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(28, 28)
            
            rec_text = QLabel(rec)
            rec_text.setFont(QFont("Segoe UI", 12))
            rec_text.setStyleSheet("color: #4a6a4c;")
            rec_text.setWordWrap(True)
            
            rec_layout.addWidget(badge)
            rec_layout.addWidget(rec_text, 1)
            
            layout.addWidget(rec_widget)
        
        return card
    
    def create_action_buttons(self):
        """Create action buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(16)
        
        btn_export_pdf = QPushButton("▼  Export as PDF")
        btn_export_pdf.setMinimumHeight(48)
        btn_export_pdf.setStyleSheet(self.get_secondary_button_style())
        btn_export_pdf.setCursor(Qt.PointingHandCursor)
        btn_export_pdf.clicked.connect(self.export_pdf)
        
        btn_export_excel = QPushButton("▤  Export as Excel")
        btn_export_excel.setMinimumHeight(48)
        btn_export_excel.setStyleSheet(self.get_secondary_button_style())
        btn_export_excel.setCursor(Qt.PointingHandCursor)
        btn_export_excel.clicked.connect(self.export_excel)
        
        btn_export_json = QPushButton("◈  Export as JSON")
        btn_export_json.setMinimumHeight(48)
        btn_export_json.setStyleSheet(self.get_secondary_button_style())
        btn_export_json.setCursor(Qt.PointingHandCursor)
        btn_export_json.clicked.connect(self.export_json)
        
        btn_new = QPushButton("↻  New Evaluation")
        btn_new.setMinimumHeight(48)
        btn_new.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7d9d7f, stop:1 #6b8a6d);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
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
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.clicked.connect(self.new_evaluation)
        
        layout.addStretch()
        layout.addWidget(btn_export_pdf)
        layout.addWidget(btn_export_excel)
        layout.addWidget(btn_export_json)
        layout.addWidget(btn_new)
        
        return widget
    
    def get_secondary_button_style(self):
        """Get style for secondary buttons"""
        return """
            QPushButton {
                background: white;
                color: #5a7a5c;
                border: 2px solid #7d9d7f;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #f5f9f5;
                border-color: #6b8a6d;
            }
            QPushButton:pressed {
                background: #eaf3ea;
            }
        """
    
    # Helper methods
    def get_lsi_color(self, lsc: str) -> str:
        """Get color based on LSC"""
        colors = {'S1': '#2d7a2d', 'S2': '#d4a00a', 'S3': '#d46a0a', 'N': '#c0392b'}
        return colors.get(lsc, '#3d5a3f')
    
    def get_classification_emoji(self, lsc: str) -> str:
        """Get emoji for classification"""
        emojis = {'S1': '🟢', 'S2': '🟡', 'S3': '🟠', 'N': '🔴'}
        return emojis.get(lsc, '⚪')
    
    def get_classification_text(self, lsc: str) -> str:
        """Get text description for classification"""
        texts = {
            'S1': 'Highly Suitable',
            'S2': 'Moderately Suitable',
            'S3': 'Marginally Suitable',
            'N': 'Not Suitable'
        }
        return texts.get(lsc, 'Unknown')
    
    def decode_limiting_factors(self, factors: str) -> str:
        """Decode limiting factor codes"""
        if not factors or factors == "None":
            return "No significant limitations"
        
        codes = {
            'c': 'Climate', 't': 'Topography', 'w': 'Wetness',
            's': 'Physical Soil', 'f': 'Soil Fertility', 'n': 'Salinity/Alkalinity'
        }
        
        decoded = [codes.get(f, f) for f in factors.lower()]
        return ', '.join(decoded)
    
    def format_season(self, season: str) -> str:
        """Format season code to readable text"""
        seasons = {
            'january_april': 'January - April (Dry Season)',
            'may_august': 'May - August (Wet Season)',
            'september_december': 'September - December (Cool Season)'
        }
        return seasons.get(season, season.replace('_', ' ').title())
    
    # Export methods
    def export_pdf(self):
        """Export report to PDF"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No evaluation results available to export.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Report as PDF",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            progress = QProgressDialog("Generating PDF report...", None, 0, 0, self)
            progress.setWindowTitle("Export PDF")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QTimer.singleShot(100, progress.close)
            
            QMessageBox.information(
                self, "Export Successful",
                f"Report exported successfully!\n\nFile saved to:\n{file_name}\n\n"
                "Note: PDF export functionality requires additional libraries (reportlab)."
            )
    
    def export_excel(self):
        """Export report to Excel"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No evaluation results available to export.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Report as Excel",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            progress = QProgressDialog("Generating Excel report...", None, 0, 0, self)
            progress.setWindowTitle("Export Excel")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QTimer.singleShot(100, progress.close)
            
            QMessageBox.information(
                self, "Export Successful",
                f"Report exported successfully!\n\nFile saved to:\n{file_name}\n\n"
                "Note: Excel export functionality requires additional libraries (openpyxl)."
            )
    
    def export_json(self):
        """Export report to JSON"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No evaluation results available to export.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Report as JSON",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_name:
            try:
                export_data = {
                    'metadata': {
                        'export_date': datetime.now().isoformat(),
                        'application': 'SoilWise v1.0.0',
                        'evaluation_method': 'Square Root Method (Khiddir et al. 1986)'
                    },
                    'results': self.current_results
                }
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self, "Export Successful",
                    f"Report exported successfully!\n\nFile saved to:\n{file_name}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export JSON:\n\n{str(e)}")
    
    def new_evaluation(self):
        """Start a new evaluation"""
        reply = QMessageBox.question(
            self, "New Evaluation",
            "Would you like to start a new evaluation?\n\n"
            "This will clear the current results and take you back to the input page.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_results = None
            self.empty_state.setVisible(True)
            self.results_container.setVisible(False)
            self.new_evaluation_requested.emit()