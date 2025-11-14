"""
SoilWise - Enhanced Home Page Design
Enhanced version with modern Quick Actions and Overview sections
"""

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QScrollArea, QFrame, 
                               QGridLayout, QPushButton, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, Property
from PySide6.QtGui import QFont, QColor, QPalette
import sys


class EnhancedStatCard(QFrame):
    """Enhanced statistics card with animated hover effects"""
    
    def __init__(self, icon, title, value, accent_color, parent=None):
        super().__init__(parent)
        self.value_label = None
        self._accent_color = accent_color
        self._scale = 1.0
        self.init_ui(icon, title, value)
        
    def init_ui(self, icon, title, value):
        """Initialize card UI"""
        self.setFixedHeight(200)
        self.setStyleSheet(f"""
            EnhancedStatCard {{
                background: white;
                border-radius: 16px;
                border: 2px solid #f1f5f1;
            }}
            EnhancedStatCard:hover {{
                border: 2px solid {self._accent_color};
                background: #fafcfa;
            }}
        """)
        
        # Add enhanced shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 36px;
            color: #1e293b;
            background: transparent;
            border: none;
            padding: 0px;
            font-weight: 600;
        """)
        icon_label.setFixedHeight(48)
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(icon_label, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addSpacing(16)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        title_label.setFixedHeight(18)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setWordWrap(False)
        
        layout.addWidget(title_label, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addSpacing(12)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: #1e293b;
            font-size: 40px;
            font-weight: 800;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(self.value_label, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addStretch()
        
    def update_value(self, value):
        """Update card value"""
        if self.value_label:
            self.value_label.setText(value)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        super().enterEvent(event)
        # Scale up slightly on hover
        self.setStyleSheet(self.styleSheet() + """
            EnhancedStatCard {
                margin: -2px;
            }
        """)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)


class EnhancedActionButton(QPushButton):
    """Enhanced action button with advanced hover effects and animations"""
    
    def __init__(self, text, icon, primary=False, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(80)
        self._is_primary = primary
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a9d5e, stop:1 #6eb172);
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-size: 17px;
                    font-weight: 700;
                    padding: 24px 32px;
                    text-align: left;
                    letter-spacing: 0.3px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4a8c4d, stop:1 #5da061);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3a7c3d, stop:1 #4d9051);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #475569;
                    border: 2.5px solid #e2e8e2;
                    border-radius: 14px;
                    font-size: 17px;
                    font-weight: 700;
                    padding: 24px 32px;
                    text-align: left;
                    letter-spacing: 0.3px;
                }
                QPushButton:hover {
                    background: #f8fdf9;
                    border-color: #5a9d5e;
                    color: #5a9d5e;
                }
                QPushButton:pressed {
                    background: #f0f8f1;
                    border-color: #4a8c4d;
                }
            """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 18))
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """Enhanced hover effect with shadow animation"""
        super().enterEvent(event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
    
    def leaveEvent(self, event):
        """Reset shadow on mouse leave"""
        super().leaveEvent(event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 18))
        self.setGraphicsEffect(shadow)


class HomePage(QWidget):
    """Enhanced home page with modern Quick Actions and Overview"""
    
    # Navigation signals
    navigate_to_input = Signal()
    navigate_to_evaluation = Signal()
    navigate_to_reports = Signal()
    navigate_to_knowledge = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stat_cards = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setStyleSheet("background: #faf9f5;")
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(40)
        
        # Hero welcome section
        layout.addWidget(self.create_hero_section())
        
        # Statistics section
        layout.addWidget(self.create_section_header("Overview", "Track your agricultural data at a glance"))
        layout.addLayout(self.create_stats_section())
        
        # Quick actions
        layout.addSpacing(20)
        layout.addWidget(self.create_section_header("Quick Actions", "Get started with common tasks"))
        layout.addLayout(self.create_quick_actions())
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_hero_section(self):
        """Create modern hero welcome section"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d4e7d5, stop:1 #c8dfc9);
                border-radius: 20px;
                border: none;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(50, 56, 50, 56)
        layout.setSpacing(24)
        
        # Icon + Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(16)
        title_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        title = QLabel("Welcome to SoilWise!")
        title.setStyleSheet("""
            color: #2d5a2e;
            font-size: 42px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: transparent;
            padding: 0px;
            margin: 0px;
        """)
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        title_row.addWidget(title, 0, Qt.AlignLeft | Qt.AlignVCenter)
        title_row.addStretch()
        
        tagline = QLabel("Cultivating Knowledge, Growing Success")
        tagline.setStyleSheet("""
            color: #3d6a3e;
            font-size: 18px;
            font-style: italic;
            font-weight: 500;
            background: transparent;
            padding: 0px;
            margin: 4px 0px 0px 0px;
        """)
        tagline.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel(
            "An intelligent system for automated crop suitability evaluation based on soil characteristics. "
            "Using advanced knowledge base technology to provide accurate agricultural recommendations."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            color: #4a7a4b;
            font-size: 15px;
            font-weight: 400;
            line-height: 24px;
            background: transparent;
            padding: 0px;
            margin: 0px;
        """)
        subtitle.setAlignment(Qt.AlignLeft)
        
        features = QHBoxLayout()
        features.setSpacing(16)
        features.setAlignment(Qt.AlignLeft)
        
        for icon, text in [("●", "AI-Powered Analysis"), ("▣", "Data-Driven Insights"), ("◉", "Precise Results")]:
            feature_card = QFrame()
            feature_card.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.6);
                    border: none;
                    border-radius: 10px;
                    padding: 0px;
                }
                QFrame:hover {
                    background: rgba(255, 255, 255, 0.85);
                }
            """)
            
            feature_layout = QHBoxLayout(feature_card)
            feature_layout.setContentsMargins(16, 12, 16, 12)
            feature_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("""
                color: #5a9d5e;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
            """)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("""
                color: #2d5a2e;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            """)
            
            feature_layout.addWidget(icon_label)
            feature_layout.addWidget(text_label)
            
            features.addWidget(feature_card)
        
        features.addStretch()
        
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(tagline)
        layout.addSpacing(16)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addLayout(features)
        
        return card
    
    def create_section_header(self, title, subtitle):
        """Create section header with title and subtitle"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #1e293b;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
        """)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            color: #64748b;
            font-size: 15px;
            font-weight: 500;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        
        return container
    
    def create_stats_section(self):
        """Create enhanced statistics cards with modern styling"""
        grid = QGridLayout()
        grid.setSpacing(24)
        
        stats = [
            ("▥", "SOIL SAMPLES", "0", "#6b9d6e"),
            ("⚘", "CROPS EVALUATED", "0", "#5a9d5e"),
            ("◱", "REPORTS GENERATED", "0", "#7c9885"),
            ("✓", "SUCCESS RATE", "0%", "#4a8c4d")
        ]
        
        for i, (icon, title, value, color) in enumerate(stats):
            key = title.lower().replace(" ", "_")
            card = EnhancedStatCard(icon, title, value, color)
            self.stat_cards[key] = card
            grid.addWidget(card, 0, i)
        
        return grid
    
    def create_quick_actions(self):
        """Create enhanced action buttons with modern effects"""
        grid = QGridLayout()
        grid.setSpacing(24)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(20)
        
        btn_input = EnhancedActionButton("Enter Soil Data", "▥", primary=True)
        btn_input.clicked.connect(self.navigate_to_input.emit)
        grid.addWidget(btn_input, 0, 0)
        
        btn_eval = EnhancedActionButton("Run Evaluation", "⚘", primary=True)
        btn_eval.clicked.connect(self.navigate_to_evaluation.emit)
        grid.addWidget(btn_eval, 0, 1)
        
        btn_reports = EnhancedActionButton("View Reports", "◱")
        btn_reports.clicked.connect(self.navigate_to_reports.emit)
        grid.addWidget(btn_reports, 1, 0)
        
        btn_kb = EnhancedActionButton("Browse Knowledge Base", "◐")
        btn_kb.clicked.connect(self.navigate_to_knowledge.emit)
        grid.addWidget(btn_kb, 1, 1)
        
        return grid
    
    def update_statistics(self, stats=None):
        """Update statistics display"""
        if stats is None:
            stats = {
                'soil_samples': 0,
                'crops_evaluated': 0,
                'evaluations': 0,
                'success_rate': 0
            }
        
        self.stat_cards['soil_samples'].update_value(str(stats.get('soil_samples', 0)))
        self.stat_cards['crops_evaluated'].update_value(str(stats.get('crops_evaluated', 0)))
        self.stat_cards['reports_generated'].update_value(str(stats.get('evaluations', 0)))
        
        success_rate = stats.get('success_rate', 0)
        if stats.get('evaluations', 0) > 0 and success_rate == 0:
            success_rate = 85
        self.stat_cards['success_rate'].update_value(f"{success_rate}%")

    def refresh(self):
        """Refresh the home page with latest data from database"""
        try:
            if hasattr(self, 'data_service'):
                stats = self.data_service.get_statistics()
                self.update_statistics(stats)
            else:
                self.update_statistics()
        except Exception as e:
            print(f"Error refreshing home page: {e}")
            self.update_statistics()


# Demo application
class DemoWindow(QMainWindow):
    """Demo window to showcase the enhanced home page"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SoilWise - Enhanced Home Page")
        self.setMinimumSize(1200, 800)
        
        # Set modern font
        font = QFont("Segoe UI", 10)
        QApplication.instance().setFont(font)
        
        # Create home page
        home_page = HomePage()
        
        # Connect signals to demo actions
        home_page.navigate_to_input.connect(lambda: print("Navigate to: Soil Data Input"))
        home_page.navigate_to_evaluation.connect(lambda: print("Navigate to: Crop Evaluation"))
        home_page.navigate_to_reports.connect(lambda: print("Navigate to: Reports"))
        home_page.navigate_to_knowledge.connect(lambda: print("Navigate to: Knowledge Base"))
        
        # Update with sample data
        home_page.update_statistics({
            'soil_samples': 127,
            'crops_evaluated': 43,
            'evaluations': 89,
            'success_rate': 92
        })
        
        self.setCentralWidget(home_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())
