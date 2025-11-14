from PySide6.QtWidgets import QWidget, QFormLayout

class InputForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # TODO: Implement input form UI
        self.layout = QFormLayout()
        self.setLayout(self.layout)