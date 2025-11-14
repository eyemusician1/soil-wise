from PySide6.QtWidgets import QWidget, QVBoxLayout

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # TODO: Implement results view UI
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)