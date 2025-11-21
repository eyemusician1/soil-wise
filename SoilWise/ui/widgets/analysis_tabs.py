"""
SoilWise/ui/widgets/analysis_tabs.py
Enhanced analysis tab components for the Reports page - DESIGN ONLY UPDATE
Contains: Parameter Analysis, Visual Analysis, and Limiting Factors views
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import (QChart, QChartView, QPieSeries, QBarSeries, 
                               QBarSet, QBarCategoryAxis, QValueAxis)


class ParameterAnalysisTab(QWidget):
    """Parameter Analysis Table Tab - Enhanced Design"""
    
    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.init_ui()
    
    def init_ui(self):
        """Initialize parameter analysis UI with enhanced styling"""
        # Main scroll area for better content handling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(20)
        
        # Enhanced header with legend
        header_layout = QHBoxLayout()
        
        title = QLabel("Detailed Parameter Ratings")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add color legend
        legend = self.create_legend()
        header_layout.addWidget(legend)
        
        layout.addLayout(header_layout)
        
        # Description text
        desc = QLabel(
            "Each parameter is evaluated against crop-specific requirements. "
            "Ratings closer to 1.0 indicate optimal conditions."
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #6a8a6c; margin-bottom: 8px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create enhanced table
        table = self.create_table()
        layout.addWidget(table)
        
        # Add summary statistics
        summary = self.create_summary_stats()
        layout.addWidget(summary)
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_legend(self):
        """Create color legend for rating ranges"""
        legend = QFrame()
        legend.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                padding: 12px 16px;
            }
        """)
        
        layout = QHBoxLayout(legend)
        layout.setSpacing(16)
        
        legend_items = [
            ("Excellent", "#d4e8d4", "≥0.95"),
            ("Good", "#fff4d4", "≥0.85"),
            ("Fair", "#ffe4cc", "≥0.60"),
            ("Poor", "#ffd4d4", "<0.60")
        ]
        
        for label_text, color, range_text in legend_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(6)
            
            color_box = QLabel()
            color_box.setFixedSize(20, 20)
            color_box.setStyleSheet(f"""
                background: {color};
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            """)
            
            text = QLabel(f"{label_text} ({range_text})")
            text.setFont(QFont("Segoe UI", 10))
            text.setStyleSheet("color: #5a7a5c;")
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(text)
            
            layout.addLayout(item_layout)
        
        return legend
    
    def create_table(self):
        """Create parameter analysis table with enhanced styling"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Parameter", "Actual Value", "Rating", "Classification", "Category"
        ])
        
        # Enhanced table styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0ede0;
                border-radius: 8px;
                gridline-color: #e8f1e8;
                selection-background-color: #e8f3e8;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8ab08c, stop:1 #7d9d7f);
                color: white;
                padding: 14px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e8f3e8;
                color: #3d5a3f;
            }
        """)
        
        # Populate table - UNCHANGED LOGIC
        param_ratings = self.results['parameter_ratings']
        table.setRowCount(len(param_ratings))
        
        row = 0
        for param, (rating, classification, subclass) in param_ratings.items():
            # Parameter name with enhanced font
            param_item = QTableWidgetItem(self.format_parameter_name(param))
            param_item.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
            param_item.setForeground(QColor("#3d5a3f"))
            table.setItem(row, 0, param_item)
            
            # Actual value (placeholder - should come from soil_data)
            actual_item = QTableWidgetItem("—")
            actual_item.setFont(QFont("Segoe UI", 11))
            actual_item.setTextAlignment(Qt.AlignCenter)
            actual_item.setForeground(QColor("#8a9a8c"))
            table.setItem(row, 1, actual_item)
            
            # Rating with enhanced styling
            rating_item = QTableWidgetItem(f"{rating:.3f}")
            rating_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            rating_item.setTextAlignment(Qt.AlignCenter)
            rating_item.setBackground(QColor(self.get_rating_color(rating)))
            rating_item.setForeground(QColor("#2d3d2f"))
            table.setItem(row, 2, rating_item)
            
            # Classification with color coding
            class_item = QTableWidgetItem(f"{classification}{subclass}")
            class_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            class_item.setTextAlignment(Qt.AlignCenter)
            class_item.setForeground(QColor(self.get_lsi_color(classification)))
            table.setItem(row, 3, class_item)
            
            # Category
            cat_item = QTableWidgetItem(self.get_category_name(subclass))
            cat_item.setFont(QFont("Segoe UI", 11))
            cat_item.setTextAlignment(Qt.AlignCenter)
            cat_item.setForeground(QColor("#4a6a4c"))
            table.setItem(row, 4, cat_item)
            
            row += 1
        
        # Adjust column widths - UNCHANGED
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Enhanced row height
        table.verticalHeader().setDefaultSectionSize(56)
        table.verticalHeader().setVisible(False)
        
        table.setMinimumHeight(500)
        table.setAlternatingRowColors(True)
        
        return table
    
    def create_summary_stats(self):
        """Create summary statistics panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                border: 1px solid #e8f1e8;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        title = QLabel("📊  Statistical Summary")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # Calculate statistics
        param_ratings = self.results['parameter_ratings']
        ratings = [r[0] for r in param_ratings.values()]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        min_rating = min(ratings) if ratings else 0
        max_rating = max(ratings) if ratings else 0
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        stats = [
            ("Average Rating:", f"{avg_rating:.3f}"),
            ("Minimum Rating:", f"{min_rating:.3f}"),
            ("Maximum Rating:", f"{max_rating:.3f}"),
            ("Parameters Evaluated:", f"{len(ratings)}")
        ]
        
        for i, (label, value) in enumerate(stats):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            label_widget.setStyleSheet("color: #5a7a5c;")
            
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Segoe UI", 11))
            value_widget.setStyleSheet("color: #3d5a3f;")
            
            stats_grid.addWidget(label_widget, i // 2, (i % 2) * 2)
            stats_grid.addWidget(value_widget, i // 2, (i % 2) * 2 + 1)
        
        layout.addLayout(stats_grid)
        
        return panel
    
    # Helper methods - UNCHANGED LOGIC
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
    
    def get_lsi_color(self, lsc: str) -> str:
        """Get color based on LSC"""
        colors = {
            'S1': '#2d7a2d',
            'S2': '#d4a00a',
            'S3': '#d46a0a',
            'N': '#c0392b'
        }
        return colors.get(lsc, '#3d5a3f')
    
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


class VisualAnalysisTab(QWidget):
    """Visual Analysis Charts Tab - Enhanced Design"""
    
    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.init_ui()
    
    def init_ui(self):
        """Initialize visual analysis UI with enhanced styling"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(28)
        
        # Enhanced title
        title = QLabel("Visual Performance Analysis")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Graphical representation of parameter ratings and their distribution "
            "across different categories for quick assessment."
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #6a8a6c; margin-bottom: 8px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create charts layout
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(24)
        
        # Pie chart in card
        pie_card = self.create_chart_card(
            "Classification Distribution",
            "Shows how parameters are distributed across suitability classes",
            self.create_rating_pie_chart()
        )
        charts_layout.addWidget(pie_card)
        
        # Bar chart in card
        bar_card = self.create_chart_card(
            "Category Performance",
            "Average rating for each parameter category",
            self.create_category_bar_chart()
        )
        charts_layout.addWidget(bar_card)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_chart_card(self, title: str, description: str, chart_view: QChartView):
        """Create a card container for charts"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 12px;
                border: 1px solid #e8f1e8;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(12)
        
        # Card title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_label.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title_label)
        
        # Card description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #6a8a6c; font-style: italic;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Chart
        layout.addWidget(chart_view)
        
        return card
    
    def create_rating_pie_chart(self):
        """Create pie chart showing rating distribution - UNCHANGED LOGIC"""
        # Count ratings by classification
        classifications = {'S1': 0, 'S2': 0, 'S3': 0, 'N': 0}
        
        for rating, classification, subclass in self.results['parameter_ratings'].values():
            classifications[classification] = classifications.get(classification, 0) + 1
        
        # Create pie series
        series = QPieSeries()
        
        colors = {
            'S1': QColor("#2d7a2d"),
            'S2': QColor("#d4a00a"),
            'S3': QColor("#d46a0a"),
            'N': QColor("#c0392b")
        }
        
        labels = {
            'S1': 'Highly Suitable',
            'S2': 'Moderately Suitable',
            'S3': 'Marginally Suitable',
            'N': 'Not Suitable'
        }
        
        for classification, count in classifications.items():
            if count > 0:
                label = f"{labels[classification]} ({count})"
                slice_obj = series.append(label, count)
                slice_obj.setColor(colors[classification])
                slice_obj.setLabelVisible(True)
                slice_obj.setLabelColor(QColor("#3d5a3f"))
                slice_obj.setLabelFont(QFont("Segoe UI", 11, QFont.Bold))
                
                # Explode dominant slice
                if count == max(classifications.values()):
                    slice_obj.setExploded(True)
                    slice_obj.setExplodeDistanceFactor(0.08)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")  # Title in card header
        chart.setBackgroundBrush(QColor("#f9fbf9"))
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 11))
        chart.legend().setLabelColor(QColor("#3d5a3f"))
        chart.setMargins(QMargins(10, 10, 10, 10))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        
        return chart_view
    
    def create_category_bar_chart(self):
        """Create bar chart showing ratings by category - UNCHANGED LOGIC"""
        # Group ratings by category
        category_ratings = {}
        
        for param, (rating, classification, subclass) in self.results['parameter_ratings'].items():
            category = self.get_category_name(subclass)
            if category not in category_ratings:
                category_ratings[category] = []
            category_ratings[category].append(rating)
        
        # Calculate average rating per category
        category_averages = {cat: sum(ratings)/len(ratings) 
                            for cat, ratings in category_ratings.items()}
        
        # Sort by rating for better visualization
        sorted_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
        
        # Create bar series
        bar_set = QBarSet("Average Rating")
        bar_set.setColor(QColor("#7d9d7f"))
        bar_set.setBorderColor(QColor("#6b8a6d"))
        
        categories = []
        for category, avg_rating in sorted_categories:
            categories.append(category)
            bar_set.append(avg_rating)
        
        series = QBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.7)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")  # Title in card header
        chart.setBackgroundBrush(QColor("#f9fbf9"))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setMargins(QMargins(10, 10, 10, 10))
        
        # X axis
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText("Category")
        axis_x.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))
        axis_x.setLabelsFont(QFont("Segoe UI", 10))
        axis_x.setLabelsColor(QColor("#3d5a3f"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y axis
        axis_y = QValueAxis()
        axis_y.setRange(0, 1.0)
        axis_y.setTitleText("Rating")
        axis_y.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))
        axis_y.setLabelFormat("%.2f")
        axis_y.setLabelsFont(QFont("Segoe UI", 10))
        axis_y.setLabelsColor(QColor("#3d5a3f"))
        axis_y.setGridLineColor(QColor("#e0ede0"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(400)
        
        return chart_view
    
    def get_category_name(self, subclass: str) -> str:
        """Get category name from subclass code - UNCHANGED"""
        categories = {
            'c': 'Climate',
            't': 'Topography',
            'w': 'Wetness',
            's': 'Physical Soil',
            'f': 'Soil Fertility',
            'n': 'Salinity/Alkalinity'
        }
        return categories.get(subclass, 'Unknown')


class LimitingFactorsTab(QWidget):
    """Limiting Factors Detailed View Tab - Enhanced Design"""
    
    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.init_ui()
    
    def init_ui(self):
        """Initialize limiting factors UI with enhanced styling"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(24)
        
        # Enhanced title
        title = QLabel("Detailed Limiting Factors Analysis")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f;")
        layout.addWidget(title)
        
        # Alert banner
        alert = QFrame()
        alert.setStyleSheet("""
            QFrame {
                background: #fff8dc;
                border-left: 5px solid #c87b00;
                border-radius: 8px;
                padding: 16px 20px;
            }
        """)
        alert_layout = QVBoxLayout(alert)
        alert_layout.setSpacing(8)
        
        alert_icon = QLabel("⚠️  Critical Factors")
        alert_icon.setFont(QFont("Segoe UI", 14, QFont.Bold))
        alert_icon.setStyleSheet("color: #c87b00;")
        
        alert_text = QLabel(
            "These parameters are restricting crop suitability. "
            "Focus management interventions on these areas for maximum improvement."
        )
        alert_text.setFont(QFont("Segoe UI", 12))
        alert_text.setStyleSheet("color: #5a6a5c;")
        alert_text.setWordWrap(True)
        
        alert_layout.addWidget(alert_icon)
        alert_layout.addWidget(alert_text)
        layout.addWidget(alert)
        
        # Add each limiting factor - UNCHANGED LOGIC
        limiting_factors = self.results.get('limiting_factors_detailed', [])
        
        if limiting_factors:
            for i, detail in enumerate(limiting_factors, 1):
                factor_card = self.create_limiting_factor_card(i, detail, len(limiting_factors))
                layout.addWidget(factor_card)
        else:
            # Success message when no limiting factors
            no_limits = QFrame()
            no_limits.setStyleSheet("""
                QFrame {
                    background: #e8f3e8;
                    border-left: 5px solid #2d7a2d;
                    border-radius: 8px;
                    padding: 24px;
                }
            """)
            no_limits_layout = QVBoxLayout(no_limits)
            
            success_icon = QLabel("✅  Excellent Conditions")
            success_icon.setFont(QFont("Segoe UI", 16, QFont.Bold))
            success_icon.setStyleSheet("color: #2d7a2d;")
            
            success_text = QLabel(
                "No significant limiting factors detected. All parameters are within suitable ranges for this crop."
            )
            success_text.setFont(QFont("Segoe UI", 13))
            success_text.setStyleSheet("color: #3d5a3f;")
            success_text.setWordWrap(True)
            
            no_limits_layout.addWidget(success_icon)
            no_limits_layout.addWidget(success_text)
            layout.addWidget(no_limits)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_limiting_factor_card(self, number: int, detail: dict, total: int):
        """Create an enhanced card for a limiting factor - MAINTAINS ORIGINAL STRUCTURE"""
        # Determine priority based on position
        priority = "HIGH" if number <= 2 else "MEDIUM" if number <= 4 else "LOW"
        
        border_colors = {
            "HIGH": "#c0392b",
            "MEDIUM": "#d46a0a",
            "LOW": "#c87b00"
        }
        
        bg_colors = {
            "HIGH": "#fff0f0",
            "MEDIUM": "#fff8e8",
            "LOW": "#fff8dc"
        }
        
        factor_card = QFrame()
        factor_card.setStyleSheet(f"""
            QFrame {{
                background: {bg_colors[priority]};
                border-left: 6px solid {border_colors[priority]};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        factor_layout = QVBoxLayout(factor_card)
        factor_layout.setSpacing(16)
        
        # Header with number and priority badge
        header_layout = QHBoxLayout()
        
        number_label = QLabel(f"#{number}")
        number_label.setFont(QFont("Georgia", 18, QFont.Bold))
        number_label.setStyleSheet(f"color: {border_colors[priority]};")
        number_label.setFixedWidth(50)
        
        param_label = QLabel(detail['description'])
        param_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        param_label.setStyleSheet("color: #3d5a3f;")
        
        header_layout.addWidget(number_label)
        header_layout.addWidget(param_label)
        header_layout.addStretch()
        
        # Priority badge
        priority_badge = QLabel(f"{priority} PRIORITY")
        priority_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
        priority_badge.setStyleSheet(f"""
            background: {border_colors[priority]};
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
        """)
        priority_badge.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(priority_badge)
        
        factor_layout.addLayout(header_layout)
        
        # Details in white container - UNCHANGED STRUCTURE
        details_container = QFrame()
        details_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        details_grid = QGridLayout(details_container)
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
        
        factor_layout.addWidget(details_container)
        
        return factor_card