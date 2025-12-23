try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class ReviewablesDialog(QDialog):
    """Dialog to show available reviewables for versions."""

    def __init__(self, all_versions_data, parent=None):
        super().__init__(parent)
        self.all_versions_data = all_versions_data
        self.setWindowTitle("Available Reviewables")
        self.setMinimumSize(700, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel("Reviewables status for all versions in playlist:")
        layout.addWidget(info_label)

        # Tree widget to show versions and their reviewables
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Version", "Status / Reviewable File"])
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

        # Populate tree with ALL versions
        for version_info in self.all_versions_data:
            row_data = version_info['row_data']
            reviewables = version_info.get('reviewables', [])

            # Create version item
            version_name = f"{row_data.get('product', 'N/A')} - {row_data.get('versions', ['N/A'])[0]}"
            version_item = QTreeWidgetItem([version_name, ""])

            if reviewables:
                # Add reviewable children
                for reviewable in reviewables:
                    filename = reviewable.get('filename', reviewable.get('fileId', 'Unknown'))
                    reviewable_item = QTreeWidgetItem(["", filename])
                    version_item.addChild(reviewable_item)
                # Green color for versions with reviewables
                version_item.setForeground(0, QColor(0, 150, 0))
            else:
                # Show "No reviewables available" message
                no_reviewable_item = QTreeWidgetItem(["", "⚠ No reviewables available"])
                no_reviewable_item.setForeground(1, QColor(200, 100, 0))
                version_item.addChild(no_reviewable_item)
                # Gray color for versions without reviewables
                version_item.setForeground(0, QColor(150, 150, 150))

            self.tree.addTopLevelItem(version_item)
            version_item.setExpanded(True)

        self.tree.resizeColumnToContents(0)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


def show_reviewables_dialog(all_versions_data, parent=None):
    """Show reviewables dialog and return True if user accepts."""
    dialog = ReviewablesDialog(all_versions_data, parent)
    return dialog.exec_() == QDialog.Accepted if hasattr(QDialog, 'Accepted') else dialog.exec() == QDialog.Accepted
