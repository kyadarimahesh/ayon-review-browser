import base64

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from .version_comparison_dialog import VersionComparisonDialog
from .representation_manager import RepresentationManager
from .activity_worker import ActivityWorker
from .rv_comparison_manager import RVComparisonManager


class ActivityPanelManager(QObject):
    activities_loaded = Signal(str, int)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.activity_ui.textBrowser_activity_panel.setOpenExternalLinks(False)
        self.main_window.activity_ui.textBrowser_activity_panel.anchorClicked.connect(self._handle_anchor_click)
        self.activity_update_timer = QTimer()
        self.activity_update_timer.setSingleShot(True)
        self.activity_update_timer.timeout.connect(self.update_activity_panel)

        self.worker = None
        self.current_fetch_version = 0
        self.activities_loaded.connect(self._update_ui)
        self.current_row_data = None
        self.available_statuses = []
        self.image_cache = {}
        self.saved_content = ""  # Store QTextBrowser content when preview opens
        self.saved_scroll_position = 0  # Store scroll position when preview opens

        # Activity panel state management
        self.panel_mode = 'BROWSER_MODE'  # BROWSER_MODE, RV_MODE, TRANSITION
        self.rv_events_enabled = False
        self.table_events_enabled = True

        # Initialize managers
        self.comparison_dialog = VersionComparisonDialog(main_window)
        self.representation_manager = RepresentationManager(main_window)
        self.rv_comparison_manager = RVComparisonManager(main_window)

        # Connect status combo box change
        self.main_window.activity_ui.statusComboBox.currentTextChanged.connect(self.on_status_changed)

        # Connect version combo box change
        self.main_window.activity_ui.versionComboBox.currentTextChanged.connect(
            self.on_version_changed_from_activity_panel)

        # Auto-scroll will be handled manually after content updates

    def setup_debounced_updates(self):
        """Setup debounced activity panel updates."""
        # Connect selection change signals with debouncing
        self.main_window.tableView_review_versions.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.main_window.tableView_list_versions.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )

    def _on_selection_changed(self):
        """Handle selection change with debouncing."""
        self.activity_update_timer.start(300)

    def update_activity_panel(self):
        """Update activity panel for current selection (debounced)."""
        # Only process table events in BROWSER_MODE
        if self.panel_mode != 'BROWSER_MODE' or not self.table_events_enabled:
            return

        current_tab = self.main_window.tabWidget.currentIndex()
        table_view = self.main_window.tableView_review_versions if current_tab == 0 else self.main_window.tableView_list_versions

        selection_model = table_view.selectionModel()
        current_index = selection_model.currentIndex()

        if current_index.isValid():
            model = table_view.model()
            row_data = model._data[current_index.row()]
            self.fetch_and_display_activities(row_data)
        else:
            pass

    def on_version_changed(self, row_data, new_version):
        """Handle version change from table combo box."""
        if self.panel_mode != 'BROWSER_MODE' or not self.table_events_enabled:
            return

        # Find the version data for the new version
        all_product_versions = row_data.get('all_product_versions', [])
        if all_product_versions:
            # Find matching version data
            selected_version_data = None
            for version in all_product_versions:
                version_name = f"v{version.get('version', 1):03d}"
                if version_name == new_version:
                    selected_version_data = version
                    break

            if selected_version_data:
                # Update row data with new version information
                updated_data = self._update_row_data_with_version(row_data, selected_version_data)

                # Update the table model
                self._update_current_table_row(updated_data)

                # Update activity panel
                self.fetch_and_display_activities(updated_data)
                return

        # Fallback: just update current_version and refresh activities
        updated_data = row_data.copy()
        updated_data['current_version'] = new_version
        self.fetch_and_display_activities(updated_data)

    def on_version_changed_from_activity_panel(self, new_version):
        """Handle version change from activity panel version dropdown."""
        if not self.current_row_data or not new_version:
            return

        current_version = self.current_row_data.get('current_version', 'unknown')
        if current_version == new_version:
            return

        # Find the version data for the new version
        all_product_versions = self.current_row_data.get('all_product_versions', [])
        if not all_product_versions:
            return

        # Find the version that matches the selected version name
        selected_version_data = None
        for version in all_product_versions:
            version_name = f"v{version.get('version', 1):03d}"
            if version_name == new_version:
                selected_version_data = version
                break

        if not selected_version_data:
            return

        # Update row data with new version information
        updated_row_data = self._update_row_data_with_version(self.current_row_data, selected_version_data)

        # In RV_MODE, ask about comparison
        if self.panel_mode == 'RV_MODE':
            should_compare = self.comparison_dialog.ask_comparison_preference(current_version, new_version)

            # If dialog was closed (None returned), revert to previous version
            if should_compare is None:
                self.main_window.activity_ui.versionComboBox.blockSignals(True)
                self.main_window.activity_ui.versionComboBox.setCurrentText(current_version)
                self.main_window.activity_ui.versionComboBox.blockSignals(False)
                return

            if should_compare:
                self.rv_comparison_manager.create_comparison_stack(self.current_row_data, updated_row_data)
                return

        # Replace mode: update table and activity panel
        self._update_current_table_row(updated_row_data)
        self.fetch_and_display_activities(updated_row_data, from_panel=True)

        # Try to maintain the same representation type
        if self.panel_mode == 'RV_MODE' and self.current_row_data.get('current_representation_path'):
            from pathlib import Path
            old_ext = Path(self.current_row_data['current_representation_path']).suffix.lower()

            new_representations = updated_row_data.get('representations', [])
            for rep in new_representations:
                rep_path = rep.get('path', '')
                if rep_path and Path(rep_path).suffix.lower() == old_ext:
                    self.representation_manager.on_representation_clicked([rep], updated_row_data, self.panel_mode)
                    break

    def fetch_and_display_activities(self, row_data, from_rv=False, from_comment=False, from_panel=False):
        """Fetch and display activities for given row data (async)."""
        # Event filtering based on panel mode and source
        if from_rv and (self.panel_mode != 'RV_MODE' or not self.rv_events_enabled):
            return
        if not from_rv and not from_comment and not from_panel and (
                self.panel_mode != 'BROWSER_MODE' or not self.table_events_enabled):
            return
        if from_comment or from_panel:  # Comments and panel changes always allowed
            pass

        # Update version details panel
        self.update_version_details(row_data)

        version_id = row_data.get('version_id', '')
        self.current_fetch_version += 1
        fetch_id = self.current_fetch_version

        # Skip loading message - skeleton will show immediately

        # Fetch in background thread
        if self.worker:
            self.worker.quit()
            self.worker.wait()

        # Get status colors for activity display
        status_colors = self.main_window.data_service.get_status_colors_dict()

        # Cancel previous worker
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.quit()
            self.worker.wait(100)

        # Extract task_id and path from row_data
        task_id = row_data.get('task_id')
        path = row_data.get('path')
        
        self.worker = ActivityWorker(self.main_window.data_service, version_id, task_id, path, 
                                     fetch_id, status_colors, self)
        self.worker.text_ready.connect(self.activities_loaded.emit)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.image_ready.connect(self.update_image)
        self.worker.start()

    def _update_ui(self, activities_html, fetch_id):
        """Update UI with loaded activities (runs in main thread)."""
        # Ignore if newer fetch was initiated
        if fetch_id != self.current_fetch_version:
            return

        if activities_html and activities_html != "<div style='font-family: Arial, sans-serif; color: #333;'>\n</div>":
            self.main_window.activity_ui.textBrowser_activity_panel.setHtml(activities_html)
        else:
            self.main_window.activity_ui.textBrowser_activity_panel.setHtml("<p>No activity records found</p>")

        # Initial scroll after content is set
        self._scroll_to_bottom()

    def fetch_and_display_activities_after_comment(self, row_data):
        """Special callback for comment updates that bypasses RV lock."""
        self.fetch_and_display_activities(row_data, from_comment=True)

    def set_browser_mode(self):
        """Switch to browser mode - listen to table events only."""
        self.panel_mode = 'BROWSER_MODE'
        self.table_events_enabled = True
        self.rv_events_enabled = False
        pass

    def set_rv_mode(self):
        """Switch to RV mode - listen to RV events only."""
        self.panel_mode = 'RV_MODE'
        self.table_events_enabled = False
        self.rv_events_enabled = True
        pass

    def set_transition_mode(self):
        """Temporarily disable all events during transitions."""
        self.panel_mode = 'TRANSITION'
        self.table_events_enabled = False
        self.rv_events_enabled = False
        pass

    def set_available_statuses(self, statuses):
        """Set available statuses for the status combo box."""
        self.available_statuses = statuses

    def update_version_details(self, row_data):
        """Update version details panel with current row data."""
        if not row_data:
            return
        self.current_row_data = row_data

        # Update Path
        path = row_data.get('path', 'N/A')
        self.main_window.activity_ui.pathLabel_value.setText(path)

        # Update Version combo box
        versions = row_data.get('versions', [])
        current_version = row_data.get('current_version', '')

        self.main_window.activity_ui.versionComboBox.blockSignals(True)
        self.main_window.activity_ui.versionComboBox.clear()
        if versions:
            self.main_window.activity_ui.versionComboBox.addItems(versions)
            if current_version in versions:
                self.main_window.activity_ui.versionComboBox.setCurrentText(current_version)
        self.main_window.activity_ui.versionComboBox.blockSignals(False)

        # Update Status combo box with all available statuses
        current_status = row_data.get('version_status', 'N/A')
        self.main_window.activity_ui.statusComboBox.blockSignals(True)
        self.main_window.activity_ui.statusComboBox.clear()

        if self.available_statuses:
            combo_index = 0
            for status_item in self.available_statuses:
                if status_item.get('value') != 'All':
                    status_name = status_item.get('value', '')
                    self.main_window.activity_ui.statusComboBox.addItem(status_name)

                    # Apply color if available
                    color = status_item.get('color')
                    if color:
                        self.main_window.activity_ui.statusComboBox.setItemData(combo_index, QColor(color),
                                                                                Qt.ForegroundRole)

                    combo_index += 1

            # Set current status
            if current_status != 'N/A':
                index = self.main_window.activity_ui.statusComboBox.findText(current_status)
                if index >= 0:
                    self.main_window.activity_ui.statusComboBox.setCurrentIndex(index)
                    # Update combo box color for current selection
                    self._update_combo_box_color(current_status)
        else:
            self.main_window.activity_ui.statusComboBox.addItem(current_status)

        self.main_window.activity_ui.statusComboBox.blockSignals(False)

        # Update Author
        author = row_data.get('author', 'N/A')
        self.main_window.activity_ui.authorLineEdit.setText(author)

        # Update Representations Tab
        self.representation_manager.update_representations_tab(row_data, self.panel_mode)


    def _update_table_models_status(self, version_id, new_status):
        """Update table models with new status."""
        # Update review model
        if hasattr(self.main_window, 'review_model'):
            self._update_model_status(self.main_window.review_model, version_id, new_status)

        # Update list model
        if hasattr(self.main_window, 'list_model'):
            self._update_model_status(self.main_window.list_model, version_id, new_status)

    def _update_model_status(self, model, version_id, new_status):
        """Update a specific model's status for the given version."""
        for i, row_data in enumerate(model._data):
            if row_data.get('version_id') == version_id:
                row_data['version_status'] = new_status
                # Emit data changed signal to refresh the view
                model.dataChanged.emit(
                    model.index(i, 0),
                    model.index(i, model.columnCount() - 1)
                )
                break

    def _handle_anchor_click(self, url):
        """Handle image preview clicks."""
        url_str = url.toString()
        if url_str.startswith("preview:"):
            parts = url_str.split(":", 2)
            if len(parts) >= 3:
                file_id, filename = parts[1], parts[2]
                if file_id in self.image_cache:
                    self._show_image_preview(self.image_cache[file_id], filename)

    def _show_image_preview(self, image_data, filename):
        """Show image preview dialog."""
        # Save current QTextBrowser content and scroll position
        text_browser = self.main_window.activity_ui.textBrowser_activity_panel
        self.saved_content = text_browser.toHtml()
        self.saved_scroll_position = text_browser.verticalScrollBar().value()

        # Block table selection events while dialog is open
        self.table_events_enabled = False

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"Preview - {filename}")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap()
        try:
            if pixmap.loadFromData(base64.b64decode(image_data)):
                scaled = pixmap.scaled(750, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
            else:
                label.setText("Failed to load image")
        except Exception as e:
            label.setText(f"Error loading image: {e}")

        layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        # Show dialog without affecting the activity panel
        dialog.exec_()

        # Restore QTextBrowser content and scroll position after dialog closes
        text_browser = self.main_window.activity_ui.textBrowser_activity_panel
        text_browser.setHtml(self.saved_content)
        text_browser.verticalScrollBar().setValue(self.saved_scroll_position)

        # Re-enable table selection events after dialog closes
        self.table_events_enabled = True

    def update_image(self, data):
        """Replace loading placeholder with actual image and cache for preview."""
        if isinstance(data, dict):
            file_id = data.get('file_id', 'unknown')
            img_data = data.get('img_data')

            if img_data:
                self.image_cache[file_id] = img_data
        else:
            # Handle tuple format (file_id, img_tag, img_data)
            if len(data) >= 3:
                file_id, img_tag, img_data = data
                if img_data:
                    self.image_cache[file_id] = img_data
            elif len(data) == 2:
                file_id, img_tag = data
                img_data = None
            else:
                return

        # Update the UI to replace loading placeholder
        def update_ui():
            try:
                current_html = self.main_window.activity_ui.textBrowser_activity_panel.toHtml()
                loading_id = f'loading_{file_id}'

                if loading_id not in current_html:
                    return

                # Extract img_tag if we have tuple data
                if isinstance(data, (list, tuple)) and len(data) >= 2:
                    img_html = data[1]  # This is the img_tag
                else:
                    return

                import re
                # Qt converts: <div id="loading_X">Loading...</div>
                # To: <a name="loading_X"></a><span>L</span><span>oading...</span>

                # Pattern to match Qt's converted HTML structure
                pattern = f'<a name="{loading_id}"></a>.*?oading.*?</span>'
                match = re.search(pattern, current_html, flags=re.DOTALL)

                if match:
                    updated_html = current_html.replace(match.group(0), img_html)
                    self.main_window.activity_ui.textBrowser_activity_panel.setHtml(updated_html)
                    # Scroll after each image update
                    self._scroll_to_bottom()

            except Exception as e:
                import traceback
                traceback.print_exc()

        QTimer.singleShot(0, update_ui)

    def on_status_changed(self, new_status):
        """Handle status change from combo box."""
        if not self.current_row_data or not new_status:
            return

        version_id = self.current_row_data.get('version_id', '')
        project_name = self.main_window.filter_controller.get_current_project()

        if not version_id or not project_name:
            return

        # Update status via API
        from api.ayon.version_service import VersionService
        version_service = VersionService()

        success = version_service.update_version_status(project_name, version_id, new_status)

        if success:
            # Update current row data
            self.current_row_data['version_status'] = new_status

            # Update combo box color
            self._update_combo_box_color(new_status)

            # Update table models
            self._update_table_models_status(version_id, new_status)

            # Refresh activity panel to show status change
            self.fetch_and_display_activities(self.current_row_data, from_comment=True)
        else:
            # Revert combo box if update failed
            old_status = self.current_row_data.get('version_status', '')
            self.main_window.activity_ui.statusComboBox.blockSignals(True)
            index = self.main_window.activity_ui.statusComboBox.findText(old_status)
            if index >= 0:
                self.main_window.activity_ui.statusComboBox.setCurrentIndex(index)
            self.main_window.activity_ui.statusComboBox.blockSignals(False)

    def _update_combo_box_color(self, status_name):
        """Update combo box color based on selected status - Linux compatible."""
        status_color = None
        for status_item in self.available_statuses:
            if status_item.get('value') == status_name:
                status_color = status_item.get('color')
                break

        if status_color:
            # Use QPalette instead of stylesheet for Linux compatibility
            palette = self.main_window.activity_ui.statusComboBox.palette()
            palette.setColor(QPalette.ButtonText, QColor(status_color))
            self.main_window.activity_ui.statusComboBox.setPalette(palette)

    def _scroll_to_bottom(self):
        """Scroll activity panel to bottom."""
        scrollbar = self.main_window.activity_ui.textBrowser_activity_panel.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _update_row_data_with_version(self, original_row_data, version_data):
        """Update row data with new version information."""
        updated_data = original_row_data.copy()

        # Update version-specific fields
        updated_data['version_id'] = version_data.get('id', '')
        updated_data['current_version'] = f"v{version_data.get('version', 1):03d}"
        updated_data['version_status'] = version_data.get('status', 'N/A')
        updated_data['author'] = version_data.get('author', 'N/A')
        updated_data['created_at'] = version_data.get('createdAt', 'N/A')
        updated_data['path'] = version_data.get('path', 'N/A')
        updated_data['hasReviewables'] = version_data.get('hasReviewables', False)

        # Update representations
        try:
            representations = [
                node["node"]["attrib"]
                for node in version_data.get("representations", {}).get("edges", [])
                if node and node.get("node") and node["node"].get("attrib")
            ]
            updated_data['representations'] = representations
        except (KeyError, TypeError):
            updated_data['representations'] = []

        # Update thumbnail
        if version_data.get('thumbnailId'):
            project_name = self.main_window.filter_controller.get_current_project()
            thumbnail_data = self.main_window.data_service.api.get_version_thumbnail_data(
                project_name, version_data['id']
            )
            updated_data['thumbnail_data'] = thumbnail_data
        else:
            updated_data['thumbnail_data'] = None

        return updated_data

    def _update_current_table_row(self, updated_row_data):
        """Update the currently selected table row with new data."""
        current_tab = self.main_window.tabWidget.currentIndex()
        table_view = self.main_window.tableView_review_versions if current_tab == 0 else self.main_window.tableView_list_versions

        selection_model = table_view.selectionModel()
        current_index = selection_model.currentIndex()

        if current_index.isValid():
            model = table_view.model()
            row = current_index.row()
            model._data[row] = updated_row_data
            model.dataChanged.emit(model.index(row, 0), model.index(row, model.columnCount() - 1))
            self.current_row_data = updated_row_data

    def update_progress(self, loaded_count, total_count):
        """Update loading progress."""
        pass

