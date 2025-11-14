"""
SoilWise/ui/widgets/fluent_card.py
Fluent Design card components
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QFont
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__)


class FluentCard(QFrame):
    """Fluent-style card with subtle shadow"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: none;
            }
        """)
        logger.debug("FluentCard created")


class StatCard(FluentCard):
    """Fluent-style stat card with icon, title, and value"""
    
    def __init__(self, icon, title, value, color="#7d9d7f", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet(f"font-size: 28px;")
        self.icon_label.setFixedSize(32, 32)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #6a7a6a; font-size: 13px; font-weight: 500;")
        
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Georgia", 32))
        self.value_label.setStyleSheet(f"color: {color}; font-weight: 600;")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        logger.debug(f"StatCard created: {title} = {value}")
    
    def update_value(self, value):
        """Update the stat value"""
        self.value_label.setText(str(value))
        logger.debug(f"StatCard updated: {self.title_label.text()} = {value}")