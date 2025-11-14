"""
SoilWise/ui/widgets/collapsible_sidebar.py
Collapsible sidebar with animation - Fixed Version
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QCursor

class NavButton(QPushButton):
    """Simple navigation button for sidebar"""
    
    def __init__(self, icon_text, full_text, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.full_text = full_text
        self.is_collapsed = False
        self.is_active = False
        
        self.setMinimumHeight(44)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.update_appearance()
        
    def set_collapsed(self, collapsed):
        """Update button for collapsed/expanded state"""
        self.is_collapsed = collapsed
        self.update_appearance()
        
    def set_active(self, active):
        """Set button active state"""
        self.is_active = active
        self.update_appearance()
        
    def update_appearance(self):
        """Update button text and style"""
        if self.is_collapsed:
            self.setText(self.icon_text)
            self.setToolTip(self.full_text)  # Show tooltip when collapsed
        else:
            self.setText(f"{self.icon_text}  {self.full_text}")
            self.setToolTip("")  # Remove tooltip when expanded
            
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e8f0e8;
                    color: #2d4a2d;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #d9e8d9;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #5a7a5a;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 400;
                }
                QPushButton:hover {
                    background-color: #f5f8f5;
                }
            """)


class CollapsibleSidebar(QFrame):
    """Collapsible sidebar with smooth animation - Fixed"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded_width = 260
        self.collapsed_width = 70
        self.is_expanded = True  # Start expanded
        
        self.setFixedWidth(self.expanded_width)
        self.setStyleSheet("""
            QFrame {
                background-color: #fafbfa;
                border-right: 2px solid #e8f0e8;
            }
        """)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header
        self.create_header()
        
        # Navigation area
        self.nav_widget = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(16, 24, 16, 0)
        self.nav_layout.setSpacing(6)
        
        self.main_layout.addWidget(self.nav_widget)
        
        # Setup animations
        self.setup_animations()
        
    def create_header(self):
        """Create header with toggle button and title"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #fafbfa; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 20, 16, 20)
        
        # Toggle button (☰ hamburger menu)
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5a7a5a;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8f0e8;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        self.title_container = QWidget()
        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(12, 0, 0, 0)
        title_layout.setSpacing(0)
        
        self.title = QLabel("SoilWise")
        self.title.setFont(QFont("Georgia", 18))
        self.title.setStyleSheet("color: #5a7a5a; font-weight: 600;")
        
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        
        header_layout.addWidget(self.toggle_btn)
        header_layout.addWidget(self.title_container)
        
        self.main_layout.addWidget(header)
        
    def setup_animations(self):
        """Setup width animations"""
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.animation2 = QPropertyAnimation(self, b"maximumWidth")
        self.animation2.setDuration(300)
        self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
        
    def add_nav_button(self, button):
        """Add navigation button to sidebar"""
        if isinstance(button, NavButton):
            button.set_collapsed(not self.is_expanded)  # Set initial state
            self.nav_layout.addWidget(button)
        
    def add_footer(self, footer):
        """Add footer widget to sidebar"""
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(footer)
        
    def toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed state"""
        if self.is_expanded:
            # Collapse
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation2.setStartValue(self.expanded_width)
            self.animation2.setEndValue(self.collapsed_width)
            self.is_expanded = False
            self.title.hide()
            self.title_container.setVisible(False)
        else:
            # Expand
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation2.setStartValue(self.collapsed_width)
            self.animation2.setEndValue(self.expanded_width)
            self.is_expanded = True
            self.title.show()
            self.title_container.setVisible(True)
        
        self.animation.start()
        self.animation2.start()
        
        # Update all nav buttons
        self.update_nav_buttons()
        
    def update_nav_buttons(self):
        """Update collapsed state of all navigation buttons"""
        for i in range(self.nav_layout.count()):
            widget = self.nav_layout.itemAt(i).widget()
            if isinstance(widget, NavButton):
                widget.set_collapsed(not self.is_expanded)


# Example usage for testing
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    sidebar = CollapsibleSidebar()
    
    # Add navigation items
    nav_items = [
        ("🏠", "Home"),
        ("📊", "Soil Data Input"),
        ("🌱", "Crop Evaluation"),
        ("📋", "Reports"),
        ("📚", "Knowledge Base"),
    ]
    
    for icon, text in nav_items:
        btn = NavButton(icon, text)
        sidebar.add_nav_button(btn)
    
    # Set first button as active
    first_btn = sidebar.nav_layout.itemAt(0).widget()
    if first_btn:
        first_btn.set_active(True)
    
    window.setCentralWidget(sidebar)
    window.setGeometry(100, 100, 300, 600)
    window.show()
    
    sys.exit(app.exec())