"""
SoilWise/ui/widgets/fluent_button.py
Fluent Design button components
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from SoilWise.utils.logger import setup_logger

logger = setup_logger(__name__)


class FluentButton(QPushButton):
    """Fluent Design button with subtle shadows and hover effects"""
    
    def __init__(self, text, icon="", primary=False, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}" if icon else text)
        self.primary = primary
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(48)
        self.apply_style()
        logger.debug(f"FluentButton created: {text} (primary={primary})")
        
    def apply_style(self):
        """Apply Fluent Design styles"""
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #7d9d7f;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background-color: #6a8a6c;
                }
                QPushButton:pressed {
                    background-color: #5a7a5c;
                }
                QPushButton:disabled {
                    background-color: #c0cac0;
                    color: #e5e8e5;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e8ebe8;
                    color: #4a5a4a;
                    border: 1px solid #d0d8d0;
                    border-radius: 6px;
                    font-size: 14px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background-color: #dde3dd;
                    border-color: #c0cac0;
                }
                QPushButton:pressed {
                    background-color: #d0d8d0;
                }
                QPushButton:disabled {
                    background-color: #f0f2f0;
                    color: #c0cac0;
                    border-color: #e5e8e5;
                }
            """)


class NavButton(QPushButton):
    """Navigation button for sidebar"""
    
    def __init__(self, text, icon="", parent=None):
        super().__init__(parent)
        self.full_text = text
        self.icon = icon
        self.is_collapsed = False
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(44)
        self.update_text()
        self.apply_style()
        logger.debug(f"NavButton created: {text}")
        
    def update_text(self):
        """Update button text based on collapsed state"""
        if self.is_collapsed:
            self.setText(self.icon)
        else:
            self.setText(f"{self.icon}  {self.full_text}" if self.icon else self.full_text)
        
    def set_collapsed(self, collapsed):
        """Set collapsed state"""
        self.is_collapsed = collapsed
        self.update_text()
        logger.debug(f"NavButton collapsed state: {collapsed}")
        
    def apply_style(self):
        """Apply navigation button styles"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5a6a5a;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(125, 157, 127, 0.1);
                color: #3a4a3a;
            }
            QPushButton:checked {
                background-color: rgba(125, 157, 127, 0.15);
                color: #7d9d7f;
                border-left: 3px solid #7d9d7f;
                font-weight: 600;
            }
        """)