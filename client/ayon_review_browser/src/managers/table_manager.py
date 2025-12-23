try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    # Try relative imports first (when imported as part of package)
    from ..models.table_models import ComboBoxDelegate
    from ...api.rv import RVOperations
    from ...api.ayon.version_service import VersionService
    from ...api.ayon.file_service import FileService
    from ...utils.rv_media_dialog import show_rv_media_selection_dialog
    from ...utils.reviewables_dialog import show_reviewables_dialog
    from ...utils.download_progress_dialog import DownloadProgressDialog
except ImportError:
    # Fall back to absolute imports (when run directly)
    from src.models.table_models import ComboBoxDelegate
    from api.rv import RVOperations
    from api.ayon.version_service import VersionService
    from api.ayon.file_service import FileService
    from utils.rv_media_dialog import show_rv_media_selection_dialog
    from utils.reviewables_dialog import show_reviewables_dialog
    from utils.download_progress_dialog import DownloadProgressDialog


def exec_menu(menu, pos):
    """Exec menu safely across PySide2/PySide6"""
    if hasattr(menu, "exec"):  # PySide6
        return menu.exec(pos)
    elif hasattr(menu, "exec_"):  # PySide2
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

        # Connect selection changes to activity panel
        self.setup_activity_panel_connections()

    def setup_activity_panel_connections(self):
        """Setup connections for activity panel updates."""
        # Connect table selection changes to activity panel updates
        self.main_window.tableView_review_versions.selectionModel().selectionChanged.connect(
            self._on_table_selection_changed
        )
        self.main_window.tableView_list_versions.selectionModel().selectionChanged.connect(
            self._on_table_selection_changed
        )

    def _on_table_selection_changed(self):
        """Handle table selection changes for activity panel updates."""
        # Only update if table events are enabled
        if not self.main_window.activity_manager.table_events_enabled:
            return

        # Determine active table based on current tab
        current_tab = self.main_window.tabWidget.currentIndex()
        if current_tab == 0:  # Review tab
            table_view = self.main_window.tableView_review_versions
        elif current_tab == 1:  # List tab
            table_view = self.main_window.tableView_list_versions
        else:
            return

        selected_rows = [index.row() for index in table_view.selectionModel().selectedRows()]
        if selected_rows:
            model = table_view.model()
            row_data = model._data[selected_rows[0]]
            version_id = row_data.get('version_id', '')
            # Update activity panel via RV manager
            if hasattr(self.main_window, 'rv_manager'):
                self.main_window.rv_manager.on_rv_version_changed(version_id, row_data)

    def handle_activity_panel_attach(self):
        """Handle activity panel attachment to browser."""
        # Set browser mode and clear RV activity panel
        self.main_window.activity_manager.set_transition_mode()
        rv_ops = self.main_window.rv_manager.get_rv_ops()
        if rv_ops:
            rv_ops.clear_activity_panel()
        # Switch to browser mode and trigger table selection update
        self.main_window.activity_manager.set_browser_mode()
        self._on_table_selection_changed()

    def handle_activity_panel_detach(self):
        """Handle activity panel detachment to RV."""
        # Set transition mode then RV mode
        self.main_window.activity_manager.set_transition_mode()
        self.main_window.activity_manager.set_rv_mode()
        # Sync activity panel with current RV ViewNode
        rv_ops = self.main_window.rv_manager.get_rv_ops()
        if rv_ops:
            rv_ops.sync_with_current_view()

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

        # Setup context menu for review table rows
        self.main_window.tableView_review_versions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_window.tableView_review_versions.customContextMenuRequested.connect(
            lambda pos: self.show_row_menu(pos, self.main_window.tableView_review_versions)
        )

        # Setup context menu for list table rows
        self.main_window.tableView_list_versions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_window.tableView_list_versions.customContextMenuRequested.connect(
            lambda pos: self.show_row_menu(pos, self.main_window.tableView_list_versions)
        )

        # Setup context menu for playlist listView
        self.main_window.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_window.listView.customContextMenuRequested.connect(
            lambda pos: self.show_row_menu(pos, self.main_window.listView)
        )

    def _setup_table_context_menu(self, table_view):
        """Setup context menu for a single table."""
        # Header context menu
        header = table_view.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(
            lambda pos: self.show_column_menu(pos, table_view)
        )

        # Row context menu
        table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        table_view.customContextMenuRequested.connect(
            lambda pos: self.show_row_menu(pos, table_view)
        )

    def show_row_menu(self, position, view):
        """Show context menu for table rows or playlist items."""
        index = view.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self.main_window)

        # Check if RV session has sources loaded
        has_rv_session = self._has_rv_session()

        # Check if this is playlist view
        is_playlist = view == self.main_window.listView

        if has_rv_session:
            if is_playlist:
                add_action = menu.addAction("Add playlist to current session")
                add_action.triggered.connect(
                    lambda: self.open_playlist_in_rv(clear_session=False)
                )

                replace_action = menu.addAction("Replace current session with playlist")
                replace_action.triggered.connect(
                    lambda: self.open_playlist_in_rv(clear_session=True)
                )

                menu.addSeparator()
                local_review_action = menu.addAction("Local Review Session")
                local_review_action.triggered.connect(
                    self.handle_local_review_session
                )
            else:
                add_action = menu.addAction("Add to current session")
                add_action.triggered.connect(
                    lambda: self.open_in_rv(view, index.row(), clear_session=False)
                )

                replace_action = menu.addAction("Replace current session")
                replace_action.triggered.connect(
                    lambda: self.open_in_rv(view, index.row(), clear_session=True)
                )
        else:
            if is_playlist:
                open_rv_action = menu.addAction("Open playlist in RV")
                open_rv_action.triggered.connect(
                    self.open_playlist_in_rv
                )

                menu.addSeparator()
                local_review_action = menu.addAction("Local Review Session")
                local_review_action.triggered.connect(
                    self.handle_local_review_session
                )
            else:
                open_rv_action = menu.addAction("Open In RV")
                open_rv_action.triggered.connect(
                    lambda: self.open_in_rv(view, index.row())
                )

        exec_menu(menu, view.mapToGlobal(position))

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

    def _has_rv_session(self):
        """Check if RV has an active session with sources."""
        try:
            rv_ops = self.main_window.rv_manager.get_rv_ops()
            return rv_ops and len(rv_ops.source_mapping) > 0
        except:
            return False

    def _has_rv_file_loaded(self):
        """Check if any .rv file is currently loaded in the session."""
        try:
            rv_ops = self.main_window.rv_manager.get_rv_ops()
            if not rv_ops or not rv_ops.source_mapping:
                return False
            
            # Check if any loaded source is a .rv file
            for source_info in rv_ops.source_mapping.values():
                path = source_info.get('path', '')
                if path.lower().endswith('.rv'):
                    return True
            return False
        except:
            return False

    def open_in_rv(self, table_view, clicked_row=None, clear_session=True):
        """Open selected media in RV with selection dialog."""
        # Validate if trying to add to session with existing .rv file
        if not clear_session and self._has_rv_file_loaded():
            QMessageBox.warning(
                self.main_window,
                "Cannot Add to Session",
                "A .rv file is already loaded in the current session.\n\n"
                "You cannot add media to a session with a .rv file.\n"
                "Please use 'Replace current session' instead."
            )
            return

        model = table_view.model()
        selection_model = table_view.selectionModel()
        selected_rows = [index.row() for index in selection_model.selectedRows()]

        if not selected_rows and clicked_row is not None:
            selected_rows = [clicked_row]

        if not selected_rows:
            return

        # Collect media data for dialog
        media_data_list = []
        for row in selected_rows:
            row_data = model._data[row]
            version_id = row_data.get('version_id', '')
            media_data_list.append({
                'version_id': version_id,
                'row_data': row_data
            })

        if not media_data_list:
            QMessageBox.warning(self.main_window, "Warning", "No valid media data found.")
            return

        # Show selection dialog
        try:
            result = show_rv_media_selection_dialog(media_data_list, self.main_window)
            if result and result[0]:  # Check if we got valid results
                selected_media, load_mode = result

                # Use RV manager for loading
                rv_ops = self.main_window.rv_manager.get_rv_ops()
                if not rv_ops:
                    from ...api.rv import RVOperations
                    rv_ops = RVOperations()
                    self.main_window.rv_manager._rv_ops = rv_ops
                    rv_ops.set_version_change_callback(self.main_window.rv_manager.on_rv_version_changed)
                success = rv_ops.load_media_with_versions(selected_media, clear_session=clear_session)

                if success:
                    # Bring activity panel to RV
                    if self.main_window.activityCommentDock.parent() == self.main_window:
                        self.main_window.detach_dock()
                        self.main_window.activity_ui.modeToggleButton.setText("SWITCH TO BROWSER")
                        # Handle detach transition
                        self.handle_activity_panel_detach()
                    print(f"Successfully loaded {len(selected_media)} media file(s) into RV")
                else:
                    QMessageBox.warning(self.main_window, "Error", "Failed to load media into RV")

        except ImportError:
            QMessageBox.warning(self.main_window, "Error", "RV module not available")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error loading media: {str(e)}")

    def handle_local_review_session(self):
        """Handle Local Review Session for playlist."""
        # Switch to Lists tab
        self.main_window.tabWidget.setCurrentIndex(1)
        list_table = self.main_window.tableView_list_versions
        model = list_table.model()

        if not model or model.rowCount() == 0:
            QMessageBox.warning(self.main_window, "Warning", "No items in playlist.")
            return

        # Get project name
        project_name = self.main_window.filter_controller.get_current_project()
        if not project_name:
            QMessageBox.warning(self.main_window, "Warning", "No project selected.")
            return

        # Collect ALL rows and check for reviewables
        version_service = VersionService()
        all_versions_data = []
        reviewables_data = []

        for row in range(model.rowCount()):
            row_data = model._data[row]
            version_id = row_data.get('version_id', '')
            has_reviewables = row_data.get('hasReviewables', False)

            version_info = {
                'version_id': version_id,
                'row_data': row_data,
                'reviewables': []
            }

            if has_reviewables:
                reviewables = version_service.get_version_reviewables(project_name, version_id)
                if reviewables:
                    version_info['reviewables'] = reviewables
                    reviewables_data.append(version_info)

            all_versions_data.append(version_info)

        if not reviewables_data:
            QMessageBox.information(self.main_window, "Info", "No reviewables found in this playlist.")
            return

        # Show reviewables dialog with ALL versions
        if not show_reviewables_dialog(all_versions_data, self.main_window):
            return

        # Download only versions with reviewables
        total_files = sum(len(v['reviewables']) for v in reviewables_data)
        progress_dialog = DownloadProgressDialog(total_files, self.main_window)
        progress_dialog.show()

        current_file = 0
        version_temp_paths = {}

        for version_info in reviewables_data:
            version_id = version_info['version_id']
            reviewables = version_info['reviewables']
            temp_paths = []

            for reviewable in reviewables:
                file_id = reviewable.get('fileId', '')
                filename = reviewable.get('filename', file_id)

                current_file += 1
                progress_dialog.update_progress(filename, current_file, total_files)

                temp_path = FileService.download_file(project_name, file_id, filename)
                if temp_path:
                    temp_paths.append(temp_path)

            version_temp_paths[version_id] = temp_paths

        progress_dialog.set_complete()
        progress_dialog.close()

        # Build media_data_list ONLY for versions with downloaded reviewables
        media_data_list = []
        for version_info in reviewables_data:
            row_data = version_info['row_data'].copy()
            version_id = row_data.get('version_id', '')

            if version_id in version_temp_paths and version_temp_paths[version_id]:
                # Replace representations with downloaded temp paths
                row_data['representations'] = [{'path': path} for path in version_temp_paths[version_id]]

                media_data_list.append({
                    'version_id': version_id,
                    'row_data': row_data
                })

        # Show confirmation and start session
        reply = QMessageBox.question(
            self.main_window,
            "Start Session",
            f"Downloaded {len(media_data_list)} version(s) with reviewables. Start RV session?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._load_local_review_to_rv(media_data_list)

    def _load_local_review_to_rv(self, media_data_list):
        """Load local review session media into RV."""
        try:
            # Show selection dialog
            result = show_rv_media_selection_dialog(media_data_list, self.main_window)
            if result and result[0]:
                selected_media, load_mode = result

                # Use RV manager for loading
                rv_ops = self.main_window.rv_manager.get_rv_ops()
                if not rv_ops:
                    from ...api.rv import RVOperations
                    rv_ops = RVOperations()
                    self.main_window.rv_manager._rv_ops = rv_ops
                    rv_ops.set_version_change_callback(self.main_window.rv_manager.on_rv_version_changed)

                success = rv_ops.load_media_with_versions(selected_media, clear_session=True)

                if success:
                    # Bring activity panel to RV
                    if self.main_window.activityCommentDock.parent() == self.main_window:
                        self.main_window.detach_dock()
                        self.main_window.activity_ui.modeToggleButton.setText("SWITCH TO BROWSER")
                        self.handle_activity_panel_detach()
                    print(f"Successfully loaded {len(selected_media)} local review file(s) into RV")
                else:
                    QMessageBox.warning(self.main_window, "Error", "Failed to load media into RV")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error loading local review: {str(e)}")

    def open_playlist_in_rv(self, clear_session=True):
        """Open all items in current playlist in RV by selecting all list items."""
        # Validate if trying to add to session with existing .rv file
        if not clear_session and self._has_rv_file_loaded():
            QMessageBox.warning(
                self.main_window,
                "Cannot Add to Session",
                "A .rv file is already loaded in the current session.\n\n"
                "You cannot add media to a session with a .rv file.\n"
                "Please use 'Replace current session with playlist' instead."
            )
            return

        # Switch to Lists tab if not already there
        self.main_window.tabWidget.setCurrentIndex(1)

        # Select all items in the list table
        list_table = self.main_window.tableView_list_versions
        list_table.selectAll()

        # Trigger the existing open_in_rv method with all selected items
        self.open_in_rv(list_table, clear_session=clear_session)

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
