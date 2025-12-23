try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
# Submission Type f(All, WIP, FINAL, PACKAGE), Show, Shot Name, Service, Review Status f(All, Approved(Only Package), Done, Forward, Retake, Reviewed, Submit), Date f, Task Name, Submitter Name, Reviewer Name

REVIEW_HEADER_TO_KEY = {
    "Submission Type": "submission_type",
    "Shot Name": "shot_name",
    "Task Name": "task_name",
    "Service": "task_type",
    "Product": "product",
    "Version": "versions",
    "Review Status": "version_status",
    "Submitter Name": "author",
    "Reviewer Name": "reviewer_name",
    "Date": "submitted_at",
    "Thumbnail": "thumbnail_data",
    "Path": "path"
}

LIST_HEADER_TO_KEY = {
    "Sequence Name": "sequence_name",
    "Shot Name": "shot_name",
    "Task Type": "task_name",
    "Process": "task_type",
    "Product": "product",
    "Version": "versions",
    "Status": "version_status",
    "Author": "author",
    "Created At": "created_at",
    "Thumbnail": "thumbnail_data",
    "Path": "path"
}


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        model = index.model()
        row_data = model._data[index.row()]
        combo.addItems(row_data.get('versions', []))
        combo.currentTextChanged.connect(lambda text: self.commitData.emit(combo))
        return combo

    def setEditorData(self, editor, index):
        model = index.model()
        row_data = model._data[index.row()]
        current_version = row_data.get('current_version', '')
        editor.setCurrentText(current_version)

    def setModelData(self, editor, model, index):
        selected_version = editor.currentText()
        model.setData(index, selected_version, Qt.EditRole)

    def paint(self, painter, option, index):
        # Don't paint anything when persistent editor is open
        # This prevents text overlap like in AYON
        pass

    def sizeHint(self, option, index):
        return QComboBox().sizeHint()


class VersionTableModel(QAbstractTableModel):
    version_changed = Signal(dict, str)
    sorting_started = Signal()  # Signal to clear activity panel on sort

    def __init__(self, data=None, columns=None, header_mapping=None):
        super().__init__()
        self._data = data or []
        self.COLUMNS = columns
        self.header_mapping = header_mapping
        self._table_view = None

    def set_table_view(self, table_view):
        """Set reference to table view for dynamic sizing."""
        self._table_view = table_view
        table_view.setAlternatingRowColors(True)

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self.COLUMNS)

    def data(self, index, role):
        row = self._data[index.row()]
        col_name = self.COLUMNS[index.column()]

        # Highlight rows where version differs from playlist original
        if role == Qt.BackgroundRole:
            current = row.get('current_version', '')
            original = row.get('original_version', '')
            if current and original and current != original:
                return QColor(80, 60, 40)  # Subtle dark orange/amber

        if col_name == "Thumbnail" and role == Qt.DecorationRole:
            thumbnail_data = row.get('thumbnail_data')
            if thumbnail_data:
                pixmap = QPixmap()
                if pixmap.loadFromData(thumbnail_data):
                    # Get current row height from table view
                    size = self._get_thumbnail_size()
                    try:
                        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    except AttributeError:
                        return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            return None

        if role == Qt.DisplayRole and col_name != "Thumbnail":
            field_key = self.header_mapping.get(col_name, col_name.lower().replace(" ", "_"))
            
            # Special handling for Version column - display current_version or first from versions list
            if col_name == "Version":
                display_value = row.get('current_version', '')
                if not display_value:
                    versions = row.get('versions', [])
                    display_value = versions[0] if versions else ''
                return display_value
            
            return str(row.get(field_key, ""))
        return None

    def _get_thumbnail_size(self):
        """Get thumbnail size based on current row height."""
        if hasattr(self, '_table_view') and self._table_view:
            row_height = self._table_view.verticalHeader().defaultSectionSize()
            return max(30, row_height - 4)  # Leave 4px margin
        return 60  # Default size

    def setData(self, index, value, role):
        if role == Qt.EditRole and self.COLUMNS[index.column()] == "Version":
            row = index.row()
            old_version = self._data[row].get('current_version', '')
            if value != old_version:
                self._data[row]['current_version'] = value

                # Update row data from selected version in all_product_versions
                all_versions = self._data[row].get('all_product_versions', [])

                for v in all_versions:
                    if f"v{v.get('version', 1):03d}" == value:
                        from utils.date_utils import standardize_date

                        # Update fields from selected version with standardized date
                        self._data[row]['created_at'] = standardize_date(v.get('createdAt', 'N/A'))
                        self._data[row]['author'] = v.get('author', 'N/A')
                        self._data[row]['version_status'] = v.get('status', 'N/A')
                        self._data[row]['version_id'] = v.get('id', 'N/A')
                        break

                # Emit signals to update UI and notify listeners
                self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))
                self.version_changed.emit(self._data[row], value)
            return True
        return False

    def flags(self, index):
        if self.COLUMNS[index.column()] == "Version":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return None

    def sort(self, column, order):
        self.sorting_started.emit()  # Clear activity panel
        self.layoutAboutToBeChanged.emit()
        col_name = self.COLUMNS[column]
        field_key = self.header_mapping.get(col_name, col_name.lower().replace(" ", "_"))
        reverse = order == Qt.DescendingOrder
        
        # Store persistent model indexes before sort
        persistent_indexes = self.persistentIndexList()
        old_positions = {id(self._data[idx.row()]): idx.row() for idx in persistent_indexes}

        def sort_key(x):
            value = x.get(field_key, "")
            
            # Handle version lists - extract numeric value
            if field_key == "versions" and isinstance(value, list):
                v = value[0] if value else "v000"
                try:
                    return int(v.replace('v', '')) if v.startswith('v') else 0
                except:
                    return 0
            # Handle current_version field (single version string)
            elif field_key == "current_version":
                if not value:
                    versions = x.get('versions', [])
                    value = versions[0] if versions else "v000"
                try:
                    return int(value.replace('v', '')) if value.startswith('v') else 0
                except:
                    return 0
            # Handle date fields
            elif field_key in ["created_at", "submitted_at"]:
                if value == "N/A" or not value:
                    return "0000-00-00"
                return value
            # Case-insensitive string sorting
            return str(value).lower()

        self._data.sort(key=sort_key, reverse=reverse)
        
        # Update persistent indexes after sort
        new_indexes = []
        for idx in persistent_indexes:
            row_id = id(self._data[old_positions.get(id(self._data[idx.row()]), idx.row())])
            new_row = next((i for i, row in enumerate(self._data) if id(row) == row_id), idx.row())
            new_indexes.append(self.index(new_row, idx.column()))
        
        self.changePersistentIndexList(persistent_indexes, new_indexes)
        self.layoutChanged.emit()

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()
        # Signal that persistent editors need to be reopened
        self.layoutChanged.emit()


class ReviewTableModel(VersionTableModel):
    def __init__(self, data=None):
        super().__init__(data, list(REVIEW_HEADER_TO_KEY.keys()), REVIEW_HEADER_TO_KEY)


class ListTableModel(VersionTableModel):
    def __init__(self, data=None):
        super().__init__(data, list(LIST_HEADER_TO_KEY.keys()), LIST_HEADER_TO_KEY)
