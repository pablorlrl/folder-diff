import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QLabel,
    QDialog, QTextEdit, QDialogButtonBox
)


class FileCompareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File/Folder Bitwise Compare")
        self.resize(600, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # First path selector
        self.path1_edit = QLineEdit()
        btn1_file = QPushButton("File...")
        btn1_folder = QPushButton("Folder...")
        btn1_file.clicked.connect(lambda: self.browse_file(self.path1_edit))
        btn1_folder.clicked.connect(lambda: self.browse_folder(self.path1_edit))
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Path 1:"))
        h1.addWidget(self.path1_edit)
        h1.addWidget(btn1_file)
        h1.addWidget(btn1_folder)

        # Second path selector
        self.path2_edit = QLineEdit()
        btn2_file = QPushButton("File...")
        btn2_folder = QPushButton("Folder...")
        btn2_file.clicked.connect(lambda: self.browse_file(self.path2_edit))
        btn2_folder.clicked.connect(lambda: self.browse_folder(self.path2_edit))
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Path 2:"))
        h2.addWidget(self.path2_edit)
        h2.addWidget(btn2_file)
        h2.addWidget(btn2_folder)

        # Compare button
        compare_btn = QPushButton("Compare")
        compare_btn.clicked.connect(self.compare_paths)

        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addWidget(compare_btn)
        self.setLayout(layout)

    # -----------------------
    # Browsing
    # -----------------------
    def browse_file(self, target_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            target_edit.setText(file_path)

    def browse_folder(self, target_edit):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            target_edit.setText(folder_path)

    # -----------------------
    # Main comparison logic
    # -----------------------
    def compare_paths(self):
        path1 = self.path1_edit.text().strip()
        path2 = self.path2_edit.text().strip()

        if not path1 or not path2:
            QMessageBox.warning(self, "Warning", "Please select both paths first.")
            return

        try:
            if os.path.isfile(path1) and os.path.isfile(path2):
                self.compare_files_ui(path1, path2)

            elif os.path.isdir(path1) and os.path.isdir(path2):
                self.compare_folders_ui(path1, path2)

            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Both paths must be either files or folders."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error:\n{e}")

    # -----------------------
    # Scrollable dialog
    # -----------------------
    def show_scrollable_result(self, title, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        text_edit.setMaximumHeight(500)
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    # -----------------------
    # File compare
    # -----------------------
    def compare_files_ui(self, file1, file2):
        same = self.compare_bitwise(file1, file2)
        if same:
            QMessageBox.information(self, "Result", "Files are IDENTICAL.")
        else:
            QMessageBox.information(self, "Result", "Files DIFFER.")

    def compare_bitwise(self, file1, file2):
        """Compare two files byte-by-byte."""
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            while True:
                b1 = f1.read(4096)
                b2 = f2.read(4096)
                if b1 != b2:
                    return False
                if not b1:
                    return True

    # -----------------------
    # Folder compare
    # -----------------------
    def compare_folders_ui(self, folder1, folder2):
        result = self.compare_folders(folder1, folder2)
        msg = []

        if result["missing_in_2"]:
            msg.append("Files missing in folder 2:")
            msg.extend("  " + f for f in result["missing_in_2"])
            msg.append("")

        if result["missing_in_1"]:
            msg.append("Files missing in folder 1:")
            msg.extend("  " + f for f in result["missing_in_1"])
            msg.append("")

        if result["different"]:
            msg.append("Files that differ:")
            msg.extend("  " + f for f in result["different"])
            msg.append("")

        if not msg:
            msg = ["Folders are IDENTICAL."]

        self.show_scrollable_result("Folder Compare Result", "\n".join(msg))

    def get_all_files(self, folder):
        """Return all file paths relative to folder."""
        file_list = []
        for root, _, files in os.walk(folder):
            for f in files:
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, folder)
                file_list.append(rel_path.replace("\\", "/"))
        return file_list

    def compare_folders(self, folder1, folder2):
        """Compare all files inside two folders recursively."""
        files1 = self.get_all_files(folder1)
        files2 = self.get_all_files(folder2)

        set1 = set(files1)
        set2 = set(files2)

        missing_in_2 = sorted(list(set1 - set2))
        missing_in_1 = sorted(list(set2 - set1))

        different = []

        common_files = set1 & set2
        for rel in sorted(common_files):
            f1 = os.path.join(folder1, rel)
            f2 = os.path.join(folder2, rel)
            if not self.compare_bitwise(f1, f2):
                different.append(rel)

        return {
            "missing_in_2": missing_in_2,
            "missing_in_1": missing_in_1,
            "different": different
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCompareApp()
    window.show()
    sys.exit(app.exec())
