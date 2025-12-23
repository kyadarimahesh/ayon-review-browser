try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class DownloadProgressDialog(QDialog):
    """Dialog to show download progress for reviewables."""

    def __init__(self, total_files, parent=None):
        super().__init__(parent)
        self.total_files = total_files
        self.current_file = 0
        self.setWindowTitle("Downloading Reviewables")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Current file label
        self.file_label = QLabel("Preparing download...")
        layout.addWidget(self.file_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_files)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(f"0 / {self.total_files} files downloaded")
        layout.addWidget(self.status_label)

    def update_progress(self, filename, current, total):
        """Update progress for current file download."""
        self.current_file = current
        self.file_label.setText(f"Downloading: {filename}")
        self.progress_bar.setValue(current)
        self.status_label.setText(f"{current} / {total} files downloaded")
        QApplication.processEvents()

    def set_complete(self):
        """Mark download as complete."""
        self.file_label.setText("Download complete!")
        self.status_label.setText(f"All {self.total_files} files downloaded successfully")
        QApplication.processEvents()
