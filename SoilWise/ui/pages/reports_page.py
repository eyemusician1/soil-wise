"""
SoilWise/ui/pages/reports_page.py
Enhanced Reports & Analysis Page - Displays evaluation results, recommendations, and detailed analysis
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                               QFrame, QGridLayout, QGroupBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QHeaderView, QTabWidget, QFileDialog,
                               QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QPainter
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCharts import (QChart, QChartView, QPieSeries, QBarSeries, QBarSet, 
                               QBarCategoryAxis, QValueAxis, QPieSlice)
from datetime import datetime
import json


class ReportsPage(QWidget):
    """Enhanced Reports & Analysis Page showing evaluation results and recommendations"""
    
    # Signal emitted when user wants to start a new evaluation
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
        desc.setStyleSheet("color: #6a8a6c;")
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
                border: 2px dashed #d4e4d4;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("📊")
        icon.setFont(QFont("Segoe UI", 72))
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
        """
        Display evaluation results.
        
        Args:
            results: Dictionary from SuitabilityEvaluator.evaluate_suitability()
        """
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
        self.results_layout.addWidget(self.create_recommendations_card(results))
        self.results_layout.addWidget(self.create_action_buttons())
    
    def create_summary_card(self, results: dict):
        """Create summary card with key metrics"""
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
        layout.setSpacing(20)
        
        # Title row with timestamp
        title_row = QHBoxLayout()
        title = QLabel("📈 Evaluation Summary")
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
        class_emoji = self.get_classification_emoji(results['lsc'])
        class_widget = self.create_metric_widget(
            "Classification",
            f"{class_emoji} {results['full_classification']}",
            self.get_classification_text(results['lsc'])
        )
        metrics_grid.addWidget(class_widget, 0, 2)
        
        # Limiting factors
        limiting = results['limiting_factors'] or "None"
        limiting_widget = self.create_metric_widget(
            "Limiting Factors",
            limiting.upper() if limiting != "None" else "✓ None",
            self.decode_limiting_factors(limiting)
        )
        metrics_grid.addWidget(limiting_widget, 0, 3)
        
        layout.addLayout(metrics_grid)
        
        # Season info if applicable
        if results.get('season'):
            season_label = QLabel(f"🌤️ Growing Season: {self.format_season(results['season'])}")
            season_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
            season_label.setStyleSheet("""
                color: #5a7a5c; 
                background: white; 
                padding: 10px 16px; 
                border-radius: 6px;
                border-left: 4px solid #7d9d7f;
            """)
            layout.addWidget(season_label)
        
        # Interpretation
        interp_label = QLabel("📋 Interpretation:")
        interp_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        interp_label.setStyleSheet("color: #4a6a4c;")
        
        interp_text = QLabel(results['interpretation'])
        interp_text.setFont(QFont("Segoe UI", 13))
        interp_text.setStyleSheet("""
            color: #5a7a5c; 
            padding: 14px; 
            background: white; 
            border-radius: 8px;
            line-height: 1.6;
        """)
        interp_text.setWordWrap(True)
        
        layout.addWidget(interp_label)
        layout.addWidget(interp_text)
        
        # Notes if available
        if results.get('notes'):
            notes_label = QLabel("📝 Additional Notes:")
            notes_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            notes_label.setStyleSheet("color: #4a6a4c; margin-top: 8px;")
            
            notes_text = QLabel(results['notes'])
            notes_text.setFont(QFont("Segoe UI", 11))
            notes_text.setStyleSheet("""
                color: #6a7a6c; 
                padding: 10px; 
                background: #fffef0; 
                border-radius: 6px;
                border-left: 3px solid #c8b000;
                font-style: italic;
            """)
            notes_text.setWordWrap(True)
            
            layout.addWidget(notes_label)
            layout.addWidget(notes_text)
        
        return card
    
    def create_metric_widget(self, label: str, value: str, subtitle: str, color: str = "#3d5a3f"):
        """Create a metric display widget"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e8f1e8;
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
        """Create tabbed widget for different analysis views"""
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
        
        # Parameter table tab
        tabs.addTab(self.create_parameter_table(results), "📊 Parameter Analysis")
        
        # Visual charts tab
        tabs.addTab(self.create_charts_view(results), "📈 Visual Analysis")
        
        # Limiting factors tab
        if results.get('limiting_factors_detailed'):
            tabs.addTab(self.create_limiting_factors_view(results), "⚠️ Limiting Factors")
        
        layout.addWidget(tabs)
        
        return group
    
    def create_parameter_table(self, results: dict):
        """Create parameter analysis table"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(16)
        
        title = QLabel("Detailed Parameter Ratings")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Parameter", "Actual Value", "Rating", "Classification", "Category"])
        
        # Style table
        table.setStyleSheet("""
            QTableWidget {
                background-color: #f9fbf9;
                border: 1px solid #e0ede0;
                border-radius: 6px;
                gridline-color: #e8f1e8;
            }
            QHeaderView::section {
                background-color: #7d9d7f;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e8f1e8;
            }
            QTableWidget::item:selected {
                background-color: #e8f3e8;
                color: #3d5a3f;
            }
        """)
        
        # Populate table with actual soil data values
        param_ratings = results['parameter_ratings']
        table.setRowCount(len(param_ratings))
        
        # We need to get actual values from somewhere - they should be in the results
        # For now, we'll display the rating info we have
        
        row = 0
        for param, (rating, classification, subclass) in param_ratings.items():
            # Parameter name
            param_item = QTableWidgetItem(self.format_parameter_name(param))
            param_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 0, param_item)
            
            # Actual value (placeholder - should come from soil_data)
            actual_item = QTableWidgetItem("—")
            actual_item.setFont(QFont("Segoe UI", 10))
            actual_item.setTextAlignment(Qt.AlignCenter)
            actual_item.setForeground(QColor("#8a9a8c"))
            table.setItem(row, 1, actual_item)
            
            # Rating
            rating_item = QTableWidgetItem(f"{rating:.2f}")
            rating_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            rating_item.setTextAlignment(Qt.AlignCenter)
            rating_item.setBackground(QColor(self.get_rating_color(rating)))
            table.setItem(row, 2, rating_item)
            
            # Classification
            class_item = QTableWidgetItem(f"{classification}{subclass}")
            class_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            class_item.setTextAlignment(Qt.AlignCenter)
            class_item.setForeground(QColor(self.get_lsi_color(classification)))
            table.setItem(row, 3, class_item)
            
            # Category
            cat_item = QTableWidgetItem(self.get_category_name(subclass))
            cat_item.setFont(QFont("Segoe UI", 11))
            cat_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 4, cat_item)
            
            row += 1
        
        # Adjust column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        table.setMinimumHeight(450)
        table.setAlternatingRowColors(True)
        
        layout.addWidget(table)
        
        return container
    
    def create_charts_view(self, results: dict):
        """Create visual charts for analysis"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(24)
        
        title = QLabel("Visual Performance Analysis")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # Create charts layout
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Rating distribution pie chart
        pie_chart = self.create_rating_pie_chart(results)
        charts_layout.addWidget(pie_chart)
        
        # Category bar chart
        bar_chart = self.create_category_bar_chart(results)
        charts_layout.addWidget(bar_chart)
        
        layout.addLayout(charts_layout)
        
        return container
    
    def create_rating_pie_chart(self, results: dict):
        """Create pie chart showing rating distribution"""
        # Count ratings by classification
        classifications = {'S1': 0, 'S2': 0, 'S3': 0, 'N': 0}
        
        for rating, classification, subclass in results['parameter_ratings'].values():
            classifications[classification] = classifications.get(classification, 0) + 1
        
        # Create pie series
        series = QPieSeries()
        
        colors = {
            'S1': QColor("#2d7a2d"),
            'S2': QColor("#d4a00a"),
            'S3': QColor("#d46a0a"),
            'N': QColor("#c0392b")
        }
        
        for classification, count in classifications.items():
            if count > 0:
                slice_obj = series.append(f"{classification}: {count}", count)
                slice_obj.setColor(colors[classification])
                slice_obj.setLabelVisible(True)
                slice_obj.setLabelColor(QColor("#3d5a3f"))
                slice_obj.setLabelFont(QFont("Segoe UI", 10, QFont.Bold))
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Parameter Classification Distribution")
        chart.setTitleFont(QFont("Georgia", 14, QFont.Bold))
        chart.setBackgroundBrush(QColor("#fafcfa"))
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        
        return chart_view
    
    def create_category_bar_chart(self, results: dict):
        """Create bar chart showing ratings by category"""
        # Group ratings by category
        category_ratings = {}
        
        for param, (rating, classification, subclass) in results['parameter_ratings'].items():
            category = self.get_category_name(subclass)
            if category not in category_ratings:
                category_ratings[category] = []
            category_ratings[category].append(rating)
        
        # Calculate average rating per category
        category_averages = {cat: sum(ratings)/len(ratings) 
                            for cat, ratings in category_ratings.items()}
        
        # Create bar series
        bar_set = QBarSet("Average Rating")
        bar_set.setColor(QColor("#7d9d7f"))
        
        categories = []
        for category in sorted(category_averages.keys()):
            categories.append(category)
            bar_set.append(category_averages[category])
        
        series = QBarSeries()
        series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Average Rating by Category")
        chart.setTitleFont(QFont("Georgia", 14, QFont.Bold))
        chart.setBackgroundBrush(QColor("#fafcfa"))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # X axis
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText("Category")
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y axis
        axis_y = QValueAxis()
        axis_y.setRange(0, 1.0)
        axis_y.setTitleText("Rating")
        axis_y.setLabelFormat("%.2f")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        
        return chart_view
    
    def create_limiting_factors_view(self, results: dict):
        """Create detailed limiting factors view"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(20)
        
        title = QLabel("Detailed Limiting Factors Analysis")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        desc = QLabel(
            "These parameters are restricting crop suitability. "
            "Focus management interventions on these areas for maximum improvement."
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #6a8a6c; margin-bottom: 8px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Add each limiting factor
        for i, detail in enumerate(results['limiting_factors_detailed'], 1):
            factor_card = QFrame()
            factor_card.setStyleSheet("""
                QFrame {
                    background: #fff8dc;
                    border-left: 5px solid #c87b00;
                    border-radius: 6px;
                    padding: 16px;
                }
            """)
            
            factor_layout = QVBoxLayout(factor_card)
            factor_layout.setSpacing(10)
            
            # Header with number
            header_layout = QHBoxLayout()
            
            number_label = QLabel(f"#{i}")
            number_label.setFont(QFont("Georgia", 16, QFont.Bold))
            number_label.setStyleSheet("color: #c87b00;")
            number_label.setFixedWidth(40)
            
            param_label = QLabel(detail['description'])
            param_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            param_label.setStyleSheet("color: #3d5a3f;")
            
            header_layout.addWidget(number_label)
            header_layout.addWidget(param_label)
            header_layout.addStretch()
            
            factor_layout.addLayout(header_layout)
            
            # Details grid
            details_grid = QGridLayout()
            details_grid.setSpacing(12)
            
            labels = [
                ("Actual Value:", str(detail['actual_value'])),
                ("Rating:", f"{detail['rating']:.2f}"),
                ("Classification:", detail['classification']),
                ("Category:", detail['category'])
            ]
            
            for row, (label_text, value_text) in enumerate(labels):
                label = QLabel(label_text)
                label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
                label.setStyleSheet("color: #5a6a5c;")
                
                value = QLabel(value_text)
                value.setFont(QFont("Segoe UI", 11))
                value.setStyleSheet("color: #3d5a3f;")
                
                details_grid.addWidget(label, row, 0)
                details_grid.addWidget(value, row, 1)
            
            factor_layout.addLayout(details_grid)
            
            layout.addWidget(factor_card)
        
        layout.addStretch()
        
        return container
    
    def create_recommendations_card(self, results: dict):
        """Create recommendations card"""
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
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)
        
        title = QLabel("💡 Management Recommendations")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
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
                    border-left: 4px solid #7d9d7f;
                    border-radius: 4px;
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
                border-radius: 12px;
                padding: 4px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
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
        
        btn_export_pdf = QPushButton("📄 Export as PDF")
        btn_export_pdf.setMinimumHeight(48)
        btn_export_pdf.setStyleSheet("""
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
        """)
        btn_export_pdf.setCursor(Qt.PointingHandCursor)
        btn_export_pdf.clicked.connect(self.export_pdf)
        
        btn_export_excel = QPushButton("📊 Export as Excel")
        btn_export_excel.setMinimumHeight(48)
        btn_export_excel.setStyleSheet("""
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
        """)
        btn_export_excel.setCursor(Qt.PointingHandCursor)
        btn_export_excel.clicked.connect(self.export_excel)
        
        btn_export_json = QPushButton("💾 Export as JSON")
        btn_export_json.setMinimumHeight(48)
        btn_export_json.setStyleSheet("""
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
        """)
        btn_export_json.setCursor(Qt.PointingHandCursor)
        btn_export_json.clicked.connect(self.export_json)
        
        btn_new = QPushButton("🔄 New Evaluation")
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
    
    # Helper methods
    def get_lsi_color(self, lsc: str) -> str:
        """Get color based on LSC"""
        colors = {
            'S1': '#2d7a2d',
            'S2': '#d4a00a',
            'S3': '#d46a0a',
            'N': '#c0392b'
        }
        return colors.get(lsc, '#3d5a3f')
    
    def get_classification_emoji(self, lsc: str) -> str:
        """Get emoji for classification"""
        emojis = {
            'S1': '🟢',
            'S2': '🟡',
            'S3': '🟠',
            'N': '🔴'
        }
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
            'c': 'Climate',
            't': 'Topography',
            'w': 'Wetness',
            's': 'Physical Soil',
            'f': 'Soil Fertility',
            'n': 'Salinity/Alkalinity'
        }
        
        decoded = [codes.get(f, f) for f in factors.lower()]
        return ', '.join(decoded)
    
    def format_parameter_name(self, param: str) -> str:
        """Format parameter name for display"""
        names = {
            'temperature': 'Temperature',
            'rainfall': 'Rainfall',
            'humidity': 'Humidity',
            'slope': 'Slope',
            'drainage': 'Drainage',
            'flooding': 'Flooding',
            'texture': 'Texture',
            'soil_depth': 'Soil Depth',
            'coarse_fragments': 'Coarse Fragments',
            'caco3': 'CaCO₃',
            'gypsum': 'Gypsum',
            'ph': 'pH',
            'organic_carbon': 'Organic Carbon',
            'base_saturation': 'Base Saturation',
            'cec': 'CEC',
            'ec': 'EC',
            'esp': 'ESP'
        }
        return names.get(param, param.replace('_', ' ').title())
    
    def get_rating_color(self, rating: float) -> str:
        """Get background color based on rating"""
        if rating >= 0.95:
            return '#d4e8d4'  # Light green
        elif rating >= 0.85:
            return '#fff4d4'  # Light yellow
        elif rating >= 0.60:
            return '#ffe4cc'  # Light orange
        else:
            return '#ffd4d4'  # Light red
    
    def get_category_name(self, subclass: str) -> str:
        """Get category name from subclass code"""
        categories = {
            'c': 'Climate',
            't': 'Topography',
            'w': 'Wetness',
            's': 'Physical Soil',
            'f': 'Soil Fertility',
            'n': 'Salinity/Alkalinity'
        }
        return categories.get(subclass, 'Unknown')
    
    def format_season(self, season: str) -> str:
        """Format season code to readable text"""
        seasons = {
            'january_april': 'January - April (Dry Season)',
            'may_august': 'May - August (Wet Season)',
            'september_december': 'September - December (Cool Season)'
        }
        return seasons.get(season, season.replace('_', ' ').title())
    
    def export_pdf(self):
        """Export report to PDF"""
        if not self.current_results:
            QMessageBox.warning(
                self,
                "No Results",
                "No evaluation results available to export."
            )
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report as PDF",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            # Show progress
            progress = QProgressDialog("Generating PDF report...", None, 0, 0, self)
            progress.setWindowTitle("Export PDF")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QTimer.singleShot(100, progress.close)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report exported successfully!\n\nFile saved to:\n{file_name}\n\n"
                "Note: PDF export functionality requires additional libraries (reportlab)."
            )
    
    def export_excel(self):
        """Export report to Excel"""
        if not self.current_results:
            QMessageBox.warning(
                self,
                "No Results",
                "No evaluation results available to export."
            )
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report as Excel",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            # Show progress
            progress = QProgressDialog("Generating Excel report...", None, 0, 0, self)
            progress.setWindowTitle("Export Excel")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QTimer.singleShot(100, progress.close)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report exported successfully!\n\nFile saved to:\n{file_name}\n\n"
                "Note: Excel export functionality requires additional libraries (openpyxl)."
            )
    
    def export_json(self):
        """Export report to JSON"""
        if not self.current_results:
            QMessageBox.warning(
                self,
                "No Results",
                "No evaluation results available to export."
            )
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report as JSON",
            f"SoilWise_Report_{self.current_results['crop_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_name:
            try:
                # Prepare data for export (remove non-serializable objects)
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
                    self,
                    "Export Successful",
                    f"Report exported successfully!\n\nFile saved to:\n{file_name}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export JSON:\n\n{str(e)}"
                )
    
    def new_evaluation(self):
        """Start a new evaluation"""
        reply = QMessageBox.question(
            self,
            "New Evaluation",
            "Would you like to start a new evaluation?\n\n"
            "This will clear the current results and take you back to the input page.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear results
            self.current_results = None
            self.empty_state.setVisible(True)
            self.results_container.setVisible(False)
            
            # Emit signal for main window to handle navigation
            self.new_evaluation_requested.emit()


# Standalone test
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Test with sample results
    sample_results = {
        'crop_name': 'Banana',
        'scientific_name': 'Musa sp. L.',
        'lsi': 78.71,
        'lsc': 'S1',
        'full_classification': 'S1f',
        'limiting_factors': 'f',
        'interpretation': 'Highly Suitable (LSI: 78.71). Land has no significant limitations for sustained application of the given use. Expected yields are high with minimal inputs.',
        'parameter_ratings': {
            'temperature': (1.0, 'S1', 'c'),
            'rainfall': (1.0, 'S1', 'c'),
            'slope': (0.95, 'S2', 't'),
            'drainage': (1.0, 'S1', 'w'),
            'flooding': (1.0, 'S1', 'w'),
            'texture': (1.0, 'S1', 's'),
            'soil_depth': (1.0, 'S1', 's'),
            'ph': (1.0, 'S1', 'f'),
            'organic_carbon': (0.95, 'S2', 'f'),
            'base_saturation': (0.85, 'S2', 'f'),
            'cec': (1.0, 'S1', 'f'),
            'ec': (0.95, 'S2', 'n'),
            'esp': (1.0, 'S1', 'n'),
        },
        'limiting_factors_detailed': [
            {
                'parameter': 'base_saturation',
                'actual_value': 36.03,
                'rating': 0.85,
                'classification': 'S2',
                'subclass': 'f',
                'description': 'Base Saturation',
                'category': 'Soil Fertility'
            }
        ],
        'recommendations': [
            '✅ This crop is highly suitable for the given soil conditions. Standard cultivation practices are recommended.',
            '• Soil fertility could be improved to maximize yields. Consider targeted fertilization based on soil test results.',
            '• Monitor base saturation levels regularly. Consider liming if pH drops below 6.0.',
            '• Maintain organic matter content through regular application of compost or green manure.',
            '• Implement proper irrigation scheduling to complement the good natural drainage.'
        ],
        'season': None,
        'notes': 'Banana requires consistent moisture and is sensitive to waterlogging. Ensure good drainage throughout the growing period.'
    }
    
    window = ReportsPage()
    window.setWindowTitle("SoilWise - Reports & Analysis")
    window.resize(1400, 900)
    
    # Display sample results after a short delay
    QTimer.singleShot(500, lambda: window.display_results(sample_results))
    
    window.show()
    sys.exit(app.exec())