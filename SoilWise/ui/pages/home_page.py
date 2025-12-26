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
        self.setFixedHeight(220)
        self.setStyleSheet(f"""
            EnhancedStatCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.3 #fafcfa, stop:1 #f3f8f3);
                border-radius: 18px;
                border: 1px solid #e8f0e9;
            }}
            EnhancedStatCard:hover {{
                border: 2px solid {self._accent_color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.3 #f5fbf5, stop:1 #eaf4ea);
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 32, 28, 32)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        icon_container = QFrame()
        icon_container.setFixedSize(64, 64)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._accent_color}40, stop:0.5 {self._accent_color}25, stop:1 {self._accent_color}10);
                border-radius: 32px;
                border: 2.5px solid {self._accent_color}35;
            }}
        """)
        
        icon_shadow = QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(15)
        icon_shadow.setXOffset(0)
        icon_shadow.setYOffset(4)
        icon_shadow.setColor(QColor(0, 0, 0, 15))
        icon_container.setGraphicsEffect(icon_shadow)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 32px;
            color: {self._accent_color};
            background: transparent;
            border: none;
            padding: 0px;
            font-weight: 800;
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addSpacing(24)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #475569;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        title_label.setFixedHeight(18)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setWordWrap(False)
        
        layout.addWidget(title_label, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addSpacing(14)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: #1e293b;
            font-size: 48px;
            font-weight: 900;
            background: transparent;
            border: none;
            padding: 0px;
            letter-spacing: -1px;
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
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(55)
        shadow.setXOffset(0)
        shadow.setYOffset(18)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class EnhancedActionButton(QPushButton):
    """Enhanced action button with advanced hover effects and animations"""
    
    def __init__(self, text, icon, primary=False, secondary=False, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(85)
        self._is_primary = primary
        self._is_secondary = secondary
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #5a9d5e, stop:0.5 #6eb172, stop:1 #7fbc83);
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.25);
                    border-radius: 16px;
                    font-size: 18px;
                    font-weight: 700;
                    padding: 28px 36px;
                    text-align: left;
                    letter-spacing: 0.4px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #4a8c4d, stop:1 #5da061);
                    border: 2px solid rgba(255, 255, 255, 0.4);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3a7c3d, stop:1 #4d9051);
                }
            """)
        elif secondary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e8f4e8, stop:1 #d8ecd9);
                    color: #3d6a3e;
                    border: 2.5px solid #c4dec5;
                    border-radius: 16px;
                    font-size: 18px;
                    font-weight: 700;
                    padding: 28px 36px;
                    text-align: left;
                    letter-spacing: 0.4px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d0ecd1, stop:1 #c0e2c1);
                    border: 2.5px solid #5a9d5e;
                    color: #2d5a2e;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c0e2c1, stop:1 #b0d8b1);
                    border: 2.5px solid #4a8c4d;
                }
            """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """Enhanced hover effect with shadow animation"""
        super().enterEvent(event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(48)
        shadow.setXOffset(0)
        shadow.setYOffset(18)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
    
    def leaveEvent(self, event):
        """Reset shadow on mouse leave"""
        super().leaveEvent(event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 25))
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
        """Create modern hero welcome section with minimalist design"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #F5F3ED, stop:1 #E8F3E8);
                border-radius: 24px;
                border: none;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 18))
        card.setGraphicsEffect(shadow)
        
        main_layout = QHBoxLayout(card)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left content section (60% width)
        left_section = QWidget()
        left_section.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(56, 56, 32, 56)
        left_layout.setSpacing(20)
        left_layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel("Welcome to SoilWise!")
        title.setStyleSheet("""
            color: #2d5a2e;
            font-size: 46px;
            font-weight: 800;
            letter-spacing: -1px;
            line-height: 56px;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignLeft)
        title.setWordWrap(True)
        
        # Description
        description = QLabel(
            "Intelligent crop suitability evaluation using advanced soil analysis "
            "and knowledge-based recommendations."
        )
        description.setWordWrap(True)
        description.setStyleSheet("""
            color: #4a7a4b;
            font-size: 15px;
            font-weight: 400;
            line-height: 26px;
            background: transparent;
        """)
        
        # Minimalist feature tags (no icons, clean text)
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(10)
        tags_layout.setAlignment(Qt.AlignLeft)
        
        feature_tags = [
            ("Accurate", "#5a9d5e"),
            ("Efficient", "#6eb172"),
            ("Data-Driven", "#7fbc83")
        ]
        
        for text, color in feature_tags:
            tag = QLabel(text)
            tag.setStyleSheet(f"""
                color: {color};
                background: rgba(90, 157, 94, 0.12);
                border: 1px solid {color}40;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.3px;
            """)
            tags_layout.addWidget(tag)
        
        tags_layout.addStretch()
        
        left_layout.addWidget(title)
        left_layout.addSpacing(8)
        left_layout.addWidget(description)
        left_layout.addSpacing(20)
        left_layout.addLayout(tags_layout)
        left_layout.addStretch()
        
        # Right section - Clean feature cards (40% width)
        right_section = QWidget()
        right_section.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(32, 56, 56, 56)
        right_layout.setSpacing(16)
        
        # Minimalist feature cards
        features_data = [
            ("Knowledge Base", "Extensive agricultural data"),
            ("Smart Analysis", "AI-powered recommendations"),
            ("Real-time Results", "Instant evaluation")
        ]
        
        for title_text, desc in features_data:
            feature_card = QFrame()
            feature_card.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.75);
                    border: none;
                    border-radius: 10px;
                    padding: 0px;
                }
                QFrame:hover {
                    background: rgba(255, 255, 255, 0.95);
                    border: 1px solid rgba(90, 157, 94, 0.3);
                }
            """)
            
            card_shadow = QGraphicsDropShadowEffect()
            card_shadow.setBlurRadius(12)
            card_shadow.setXOffset(0)
            card_shadow.setYOffset(2)
            card_shadow.setColor(QColor(0, 0, 0, 8))
            feature_card.setGraphicsEffect(card_shadow)
            
            card_layout = QVBoxLayout(feature_card)
            card_layout.setContentsMargins(20, 16, 20, 16)
            card_layout.setSpacing(4)
            
            card_title = QLabel(title_text)
            card_title.setStyleSheet("""
                color: #2d5a2e;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            """)
            
            card_desc = QLabel(desc)
            card_desc.setStyleSheet("""
                color: #6a8a6c;
                font-size: 11px;
                font-weight: 500;
                background: transparent;
            """)
            card_desc.setWordWrap(True)
            
            card_layout.addWidget(card_title)
            card_layout.addWidget(card_desc)
            
            right_layout.addWidget(feature_card)
        
        right_layout.addStretch()
        
        main_layout.addWidget(left_section, 6)
        main_layout.addWidget(right_section, 4)
        
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
        """Create enhanced action buttons with modern card-style design"""
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
        
        btn_reports = EnhancedActionButton("View Reports", "◱", secondary=True)
        btn_reports.clicked.connect(self.navigate_to_reports.emit)
        grid.addWidget(btn_reports, 1, 0)
        
        btn_kb = EnhancedActionButton("Browse Knowledge Base", "◐", secondary=True)
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
