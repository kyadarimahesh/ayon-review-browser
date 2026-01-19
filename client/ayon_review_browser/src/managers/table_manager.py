try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from ..models.table_models import ComboBoxDelegate
except ImportError:
    from src.models.table_models import ComboBoxDelegate


def exec_menu(menu, pos):
    """Exec menu safely across PySide2/PySide6"""
    if hasattr(menu, "exec"):
        return menu.exec(pos)
    elif hasattr(menu, "exec_"):
        return menu.exec_(pos)
    else:
        raise AttributeError("QMenu has neither exec nor exec_")


class TableManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def setup_tables(self):
        """Setup table configurations and delegates."""
        # Enable sorting
        self.main_window.tableView_review_versions.setSortingEnabled(True)
        self.main_window.tableView_list_versions.setSortingEnabled(True)

        # Enable multi-row selection
        self.main_window.tableView_review_versions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_window.tableView_list_versions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_window.tableView_review_versions.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.main_window.tableView_list_versions.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Enable column reordering
        self.main_window.tableView_review_versions.horizontalHeader().setSectionsMovable(True)
        self.main_window.tableView_list_versions.horizontalHeader().setSectionsMovable(True)

        # Performance optimizations
        self.main_window.tableView_review_versions.verticalHeader().setDefaultSectionSize(30)
        self.main_window.tableView_list_versions.verticalHeader().setDefaultSectionSize(30)

        # Setup combo box delegates for Version column
        review_version_col = self.main_window.review_model.COLUMNS.index("Version")
        list_version_col = self.main_window.list_model.COLUMNS.index("Version")
        self.main_window.tableView_review_versions.setItemDelegateForColumn(review_version_col, ComboBoxDelegate())
        self.main_window.tableView_list_versions.setItemDelegateForColumn(list_version_col, ComboBoxDelegate())

    def setup_context_menus(self):
        """Setup column and row context menus."""
        # Setup context menu for review table header
        review_header = self.main_window.tableView_review_versions.horizontalHeader()
        review_header.setContextMenuPolicy(Qt.CustomContextMenu)
        review_header.customContextMenuRequested.connect(
            lambda pos: self.show_column_menu(pos, self.main_window.tableView_review_versions)
        )

        # Setup context menu for list table header
        list_header = self.main_window.tableView_list_versions.horizontalHeader()
        list_header.setContextMenuPolicy(Qt.CustomContextMenu)
        list_header.customContextMenuRequested.connect(
            lambda pos: self.show_column_menu(pos, self.main_window.tableView_list_versions)
        )

        # Setup row context menus
        self.main_window.tableView_review_versions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_window.tableView_review_versions.customContextMenuRequested.connect(
            lambda pos: self._show_row_menu(pos, self.main_window.tableView_review_versions)
        )

        self.main_window.tableView_list_versions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_window.tableView_list_versions.customContextMenuRequested.connect(
            lambda pos: self._show_row_menu(pos, self.main_window.tableView_list_versions)
        )

    def _show_row_menu(self, position, table_view):
        """Show context menu for table rows."""
        index = table_view.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self.main_window)
        open_rv_action = menu.addAction("Open in RV")
        open_rv_action.triggered.connect(lambda: self._open_in_rv(table_view))

        exec_menu(menu, table_view.mapToGlobal(position))

    def _open_in_rv(self, table_view):
        """Open selected versions in RV."""
        try:
            import rv.commands as rv_cmd

            # Get selected rows
            selected_rows = [idx.row() for idx in table_view.selectionModel().selectedRows()]
            if not selected_rows:
                QMessageBox.warning(self.main_window, "Warning", "No rows selected")
                return

            model = table_view.model()

            # Clear RV session
            rv_cmd.clearSession()

            # Load each version
            loaded_count = 0
            for row in selected_rows:
                row_data = model._data[row]
                representations = row_data.get('representations', [])

                # Find best representation (prefer exr, then mov/mp4)
                path = None
                for rep in representations:
                    rep_name = rep.get('name', '').lower()
                    if 'exr' in rep_name or 'mov' in rep_name or 'mp4' in rep_name:
                        path = rep.get('path', '')
                        break

                if not path and representations:
                    path = representations[0].get('path', '')

                if path:
                    rv_cmd.addSource(path)
                    loaded_count += 1

            if loaded_count > 0:
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Loaded {loaded_count} version(s) in RV"
                )
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Warning",
                    "No valid representations found"
                )

        except ImportError:
            QMessageBox.warning(
                self.main_window,
                "Error",
                "RV not available. Please run from within RV."
            )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to load in RV: {str(e)}"
            )

    def show_column_menu(self, position, table_view):
        """Show context menu for table columns."""
        header = table_view.horizontalHeader()
        menu = QMenu(self.main_window)

        model = table_view.model()
        for col in range(model.columnCount()):
            column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            action = menu.addAction(column_name)
            action.setCheckable(True)
            action.setChecked(not table_view.isColumnHidden(col))
            action.triggered.connect(
                self._create_column_toggle_handler(col, table_view)
            )

        exec_menu(menu, header.mapToGlobal(position))

    def _create_column_toggle_handler(self, col, table_view):
        """Create a handler for column toggle."""

        def handler(checked):
            self.toggle_column(col, table_view, checked)

        return handler

    def toggle_column(self, column, table_view, visible):
        """Toggle column visibility."""
        if visible:
            table_view.showColumn(column)
        else:
            table_view.hideColumn(column)
        table_view.resizeColumnsToContents()

    def open_persistent_editors(self):
        """Open persistent editors for Version column."""
        review_version_col = self.main_window.review_model.COLUMNS.index("Version")
        list_version_col = self.main_window.list_model.COLUMNS.index("Version")

        # Open persistent editors for review table
        for row in range(self.main_window.review_model.rowCount()):
            index = self.main_window.review_model.index(row, review_version_col)
            self.main_window.tableView_review_versions.openPersistentEditor(index)

        # Open persistent editors for list table
        for row in range(self.main_window.list_model.rowCount()):
            index = self.main_window.list_model.index(row, list_version_col)
            self.main_window.tableView_list_versions.openPersistentEditor(index)
