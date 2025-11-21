import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QLabel
)

class FileCompareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Bitwise Compare")
        self.resize(500, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # First file selector
        self.file1_edit = QLineEdit()
        btn1 = QPushButton("Browse...")
        btn1.clicked.connect(lambda: self.browse_file(self.file1_edit))
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("File 1:"))
        h1.addWidget(self.file1_edit)
        h1.addWidget(btn1)

        # Second file selector
        self.file2_edit = QLineEdit()
        btn2 = QPushButton("Browse...")
        btn2.clicked.connect(lambda: self.browse_file(self.file2_edit))
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("File 2:"))
        h2.addWidget(self.file2_edit)
        h2.addWidget(btn2)

        # Compare button
        compare_btn = QPushButton("Compare")
        compare_btn.clicked.connect(self.compare_files)

        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addWidget(compare_btn)

        self.setLayout(layout)

    def browse_file(self, target_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            target_edit.setText(file_path)

    def compare_files(self):
        file1 = self.file1_edit.text().strip()
        file2 = self.file2_edit.text().strip()

        if not file1 or not file2:
            QMessageBox.warning(self, "Warning", "Please select both files first.")
            return

        try:
            same = self.compare_bitwise(file1, file2)
            if same:
                QMessageBox.information(self, "Result", "Files are identical (bitwise match).")
            else:
                QMessageBox.information(self, "Result", "Files differ.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def compare_bitwise(self, file1, file2):
        """Compare two files byte-by-byte"""
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            while True:
                b1 = f1.read(4096)
                b2 = f2.read(4096)
                if b1 != b2:
                    return False
                if not b1:  # both ended
                    break
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCompareApp()
    window.show()
    sys.exit(app.exec())
