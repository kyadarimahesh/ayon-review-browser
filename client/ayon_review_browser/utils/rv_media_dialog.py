try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from pathlib import Path


class RepresentationPreferenceDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Representation Preferences")
        layout = QVBoxLayout(self)
        label = QLabel("Reorder your preferred media extensions (top = highest priority).\nDrag and drop or use the Up/Down buttons.")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        self.list_widget.addItems(order)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.list_widget)

        # Up/Down buttons
        btn_layout = QHBoxLayout()
        self.up_btn = QPushButton("Up")
        self.down_btn = QPushButton("Down")
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)

    def move_down(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1 and row != -1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)

    def get_order(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]


class RVMediaSelectionDialog(QDialog):
    def __init__(self, media_data_list, parent=None):
        super().__init__(parent)
        self.media_data_list = media_data_list
        self.selected_media = []
        self.load_representation_preferences()
        self.setup_ui()
        self.populate_table()

    def load_representation_preferences(self):
        settings = QSettings("AYON", "ReviewBrowser1")
        self.rep_order = settings.value("representation_order", [".rv", ".exr", ".mp4", ".jpg", ".png"])
        if isinstance(self.rep_order, str):
            # QSettings may return a string, convert to list
            self.rep_order = eval(self.rep_order)

    def save_representation_preferences(self, order):
        settings = QSettings("AYON", "ReviewBrowser1")
        settings.setValue("representation_order", order)
        self.rep_order = order

    def setup_ui(self):
        self.setWindowTitle("RV Media Selection")
        self.setModal(True)
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Product", "Version", "Representations"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        # Bottom controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        # Preferences button
        self.pref_btn = QToolButton()
        self.pref_btn.setText("Preferences")
        self.pref_btn.clicked.connect(self.open_representation_preferences)
        controls_layout.insertWidget(0, self.pref_btn)

        # Right side buttons
        self.cancel_btn = QPushButton("Cancel")
        self.load_btn = QPushButton("Load into RV")
        self.load_btn.setDefault(True)

        controls_layout.addWidget(self.cancel_btn)
        controls_layout.addWidget(self.load_btn)

        layout.addLayout(controls_layout)

        # Connect signals
        self.cancel_btn.clicked.connect(self.reject)
        self.load_btn.clicked.connect(self.accept_selection)

    def open_representation_preferences(self):
        dialog = RepresentationPreferenceDialog(self.rep_order, self)
        if dialog.exec() == QDialog.Accepted:
            self.save_representation_preferences(dialog.get_order())
            self.populate_table()

    def populate_table(self):
        self.table.setRowCount(len(self.media_data_list))

        for row, media_item in enumerate(self.media_data_list):
            row_data = media_item.get('row_data', {})

            # Product column
            product = row_data.get('product', 'Unknown')
            self.table.setItem(row, 0, QTableWidgetItem(product))

            # Version column (combobox)
            versions = row_data.get('versions', [])
            current_version = row_data.get('current_version', versions[0] if versions else 'v001')

            version_combo = QComboBox()
            version_combo.addItems(versions if versions else [current_version])
            version_combo.setCurrentText(current_version)
            self.table.setCellWidget(row, 1, version_combo)

            # Representations column (checkboxes for multi-selection)
            representations = row_data.get('representations', [])
            rep_widget = self.create_representations_widget(representations)
            self.table.setCellWidget(row, 2, rep_widget)

        self.table.resizeColumnsToContents()

    def create_representations_widget(self, representations):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # Group representations by extension
        rep_by_ext = {}
        for rep in representations:
            path = rep.get('path', '')
            ext = Path(path).suffix.lower()
            if ext not in rep_by_ext:
                rep_by_ext[ext] = []
            rep_by_ext[ext].append(rep)

        checkboxes = []
        # Create checkboxes for each extension (multi-selection allowed)
        for ext, reps in rep_by_ext.items():
            checkbox = QCheckBox(ext)
            checkbox.setProperty('representations', reps)
            layout.addWidget(checkbox)
            checkboxes.append(checkbox)

        # Auto-select one by preference order
        for ext in self.rep_order:
            for cb in checkboxes:
                if cb.text() == ext:
                    cb.setChecked(True)
                    break
            else:
                continue
            break

        layout.addStretch()
        return widget

    def get_selected_representations(self, row):
        rep_widget = self.table.cellWidget(row, 2)
        selected_reps = []

        for i in range(rep_widget.layout().count()):
            item = rep_widget.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QCheckBox):
                checkbox = item.widget()
                if checkbox.isChecked():
                    reps = checkbox.property('representations')
                    selected_reps.extend(reps if reps else [])

        return selected_reps

    def validate_selection(self):
        rv_count = 0
        total_selected_count = 0

        for row in range(self.table.rowCount()):
            selected_reps = self.get_selected_representations(row)
            if not selected_reps:
                continue

            total_selected_count += len(selected_reps)

            # Check for .rv files
            for rep in selected_reps:
                path = rep.get('path', '')
                if path.lower().endswith('.rv'):
                    rv_count += 1

        # Validation 1: only 1 .rv file allowed
        if rv_count > 1:
            QMessageBox.warning(self, "Warning",
                                "Only one .rv file can be selected.\n"
                                "Please select only one .rv representation.")
            return False

        # Validation 2: .rv cannot be mixed with other representations
        if rv_count > 0 and total_selected_count > 1:
            QMessageBox.warning(self, "Warning",
                                ".rv files cannot be loaded with other representations.\n"
                                "Please select only the .rv file or deselect it.")
            return False

        return True

    def accept_selection(self):
        if not self.validate_selection():
            return

        self.selected_media = []

        for row in range(self.table.rowCount()):
            selected_reps = self.get_selected_representations(row)
            if not selected_reps:
                continue

            version_combo = self.table.cellWidget(row, 1)
            selected_version = version_combo.currentText() if version_combo else 'v001'

            media_item = self.media_data_list[row]
            row_data = media_item.get('row_data', {}).copy()
            row_data['current_version'] = selected_version

            # Get ALL representations for this version (not just selected ones)
            all_representations = row_data.get('representations', [])

            for selected_rep in selected_reps:
                self.selected_media.append({
                    'path': selected_rep.get('path'),
                    'version_id': media_item.get('version_id'),
                    'row_data': row_data,
                    'representation': selected_rep,
                    'all_representations': all_representations  # Include all representations
                })

        self.accept()

    def get_selected_media_data(self):
        return self.selected_media


def show_rv_media_selection_dialog(media_data_list, parent=None):
    """Show RV media selection dialog and return selected media data"""
    dialog = RVMediaSelectionDialog(media_data_list, parent)
    if dialog.exec() == QDialog.Accepted:
        selected_media = dialog.get_selected_media_data()
        return selected_media, "individual"
    return None, None