"""
SoilWise/ui/widgets/collapsible_sidebar.py
Collapsible sidebar with logo beside text
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont


class NavButton(QPushButton):
    """Navigation button with icon and text"""
    
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.button_text = text
        self.is_active = False
        
        # Fixed size for consistent layout
        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Icon label - FIXED ALIGNMENT
        self.icon_label = QLabel(icon)
        self.icon_label.setFixedWidth(64)  # Same as collapsed sidebar width
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                color: #6a8a6c;
                font-size: 20px;
                font-weight: 600;
                background: transparent;
                border: none;
                text-decoration: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Text label
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #6a8a6c;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                border: none;
                text-decoration: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        
        self.update_style()
    
    def set_active(self, active):
        """Set button active state"""
        self.is_active = active
        self.update_style()
    
    def update_style(self):
        """Update button styling - SUBTLE BORDER ACCENT"""
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(125, 157, 127, 0.12);
                    border: none;
                    border-left: 4px solid #7d9d7f;
                    text-align: left;
                }
            """)
            self.icon_label.setStyleSheet("""
                QLabel {
                    color: #3d6a3e;
                    font-size: 20px;
                    font-weight: 700;
                    background: transparent;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #3d6a3e;
                    font-size: 14px;
                    font-weight: 600;
                    background: transparent;
                    padding: 0px;
                    margin: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-left: 4px solid transparent;
                    text-align: left;
                }
                QPushButton:hover {
                    background: rgba(125, 157, 127, 0.1);
                    border-left: 4px solid #c4dec5;
                }
            """)
            self.icon_label.setStyleSheet("""
                QLabel {
                    color: #6a8a6c;
                    font-size: 20px;
                    font-weight: 600;
                    background: transparent;
                    border: none;
                    text-decoration: none;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #6a8a6c;
                    font-size: 14px;
                    font-weight: 500;
                    background: transparent;
                    border: none;
                    text-decoration: none;
                    padding: 0px;
                    margin: 0px;
                }
            """)
    
    def set_text_visible(self, visible):
        """Show/hide text label"""
        self.text_label.setVisible(visible)


class CollapsibleSidebar(QFrame):
    """Collapsible sidebar with smooth animation and logo"""
    
    def __init__(self, logo_widget=None, parent=None):
        super().__init__(parent)
        self.logo_widget = logo_widget
        self.is_expanded = True
        self.expanded_width = 240
        self.collapsed_width = 64  # Width that fits icon perfectly
        
        self.setFixedWidth(self.expanded_width)
        self.setStyleSheet("""
            QFrame {
                background-color: none;
                border-right: none;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with logo and toggle button
        header = self.create_header()
        layout.addWidget(header)
        
        # Navigation buttons container
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 12, 0, 0)
        self.nav_layout.setSpacing(4)
        self.nav_layout.setAlignment(Qt.AlignTop)
        
        layout.addWidget(self.nav_container)
        
        # Footer container
        self.footer_container = QWidget()
        self.footer_layout = QVBoxLayout(self.footer_container)
        self.footer_layout.setContentsMargins(12, 12, 12, 12)
        self.footer_layout.setSpacing(0)
        
        layout.addStretch()
        layout.addWidget(self.footer_container)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.animation2 = QPropertyAnimation(self, b"maximumWidth")
        self.animation2.setDuration(250)
        self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.nav_buttons = []
    
    def create_header(self):
        """Create header with logo, title, and toggle button"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # Logo (if provided)
        if self.logo_widget:
            self.logo_widget.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_widget)
        
        # Title
        self.title_label = QLabel("SoilWise")
        self.title_label.setFont(QFont("Georgia", 18, QFont.Bold))
        self.title_label.setStyleSheet("""
            color: #3d6a3e; 
            background: transparent; 
            border: none;
            text-decoration: none;
        """)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Toggle button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6a8a6c;
                font-size: 20px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(125, 157, 127, 0.15);
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.toggle_btn)
        
        return header
    
    def add_nav_button(self, button):
        """Add navigation button to sidebar"""
        self.nav_layout.addWidget(button)
        self.nav_buttons.append(button)
    
    def add_footer(self, widget):
        """Add footer widget"""
        self.footer_layout.addWidget(widget)
    
    def toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed state"""
        if self.is_expanded:
            # Collapse
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation2.setStartValue(self.expanded_width)
            self.animation2.setEndValue(self.collapsed_width)
            
            # Hide text labels and logo
            for btn in self.nav_buttons:
                btn.set_text_visible(False)
            
            self.title_label.setVisible(False)
            if self.logo_widget:
                self.logo_widget.setVisible(False)
            
        else:
            # Expand
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation2.setStartValue(self.collapsed_width)
            self.animation2.setEndValue(self.expanded_width)
            
            # Show text labels and logo
            for btn in self.nav_buttons:
                btn.set_text_visible(True)
            
            self.title_label.setVisible(True)
            if self.logo_widget:
                self.logo_widget.setVisible(True)
        
        self.animation.start()
        self.animation2.start()
        self.is_expanded = not self.is_expanded