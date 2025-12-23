import sys
import os

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
    from ...ui.generated.review_browser_ui import Ui_BrowserWidget
    from ...ui.generated.activity_panel_ui import Ui_ActivityPanel
    from ...services.data_service import DataService
    from ..models.table_models import ReviewTableModel, ListTableModel
    from ..controllers.advanced_filter_controller import AdvancedFilterController
    from ..controllers.lists_controller import ListsController
    from ...utils.comment_handler import CommentHandler
    from ..managers.activity_panel_manager import ActivityPanelManager
    from ..managers.table_manager import TableManager
    from ..managers.preferences_manager import PreferencesManager
    from ..managers.rv_integration_manager import RVIntegrationManager
except ImportError:
    # Fall back to absolute imports (when run directly)
    from ui.generated.review_browser_ui import Ui_BrowserWidget
    from ui.generated.activity_panel_ui import Ui_ActivityPanel
    from services.data_service import DataService
    from src.models.table_models import ReviewTableModel, ListTableModel
    from src.controllers.advanced_filter_controller import AdvancedFilterController
    from src.controllers.lists_controller import ListsController
    from utils.comment_handler import CommentHandler
    from src.managers.activity_panel_manager import ActivityPanelManager
    from src.managers.table_manager import TableManager
    from src.managers.preferences_manager import PreferencesManager
    from src.managers.rv_integration_manager import RVIntegrationManager


class ReviewBrowser(QMainWindow, Ui_BrowserWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize activity panel widget
        self.activityCommentDock = QDockWidget(self)
        self.activity_ui = Ui_ActivityPanel()
        self.activity_ui.setupUi(self.activityCommentDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.activityCommentDock)

        # Initialize RV integration manager
        self.rv_manager = RVIntegrationManager(self)
        self.rv_manager.initialize()
        
        # Setup RV event listeners (decoupled integration)
        self._setup_rv_integration()

        # Initialize core components
        self.data_service = DataService()
        self.comment_handler = CommentHandler(self)

        # Data storage
        self.all_versions = []
        self.current_versions = []
        self.playlists = {}

        # Initialize managers
        self.activity_manager = ActivityPanelManager(self)
        self.table_manager = TableManager(self)
        self.preferences_manager = PreferencesManager(self)

        # Setup components
        self._setup_models()
        self._setup_controllers()
        self._load_initial_data()
        self._setup_ui()

        # Load preferences after initialization
        QTimer.singleShot(100, self.preferences_manager.load_preferences)

    def _setup_models(self):
        """Initialize and configure data models."""
        self.review_model = ReviewTableModel()
        self.list_model = ListTableModel()
        self.playlist_model = QStringListModel()

        # Set models to views
        self.tableView_review_versions.setModel(self.review_model)
        self.tableView_list_versions.setModel(self.list_model)
        self.listView.setModel(self.playlist_model)

        # Set table view references for dynamic thumbnail sizing
        self.review_model.set_table_view(self.tableView_review_versions)
        self.list_model.set_table_view(self.tableView_list_versions)

        # Set table view references for dynamic thumbnail sizing
        self.review_model.set_table_view(self.tableView_review_versions)
        self.list_model.set_table_view(self.tableView_list_versions)

        # Configure tables through manager
        self.table_manager.setup_tables()
        self.table_manager.setup_context_menus()

        # Connect signals
        self.review_model.version_changed.connect(self.activity_manager.on_version_changed)
        self.list_model.version_changed.connect(self.activity_manager.on_version_changed)
        self.review_model.sorting_started.connect(self._clear_activity_panel)
        self.list_model.sorting_started.connect(self._clear_activity_panel)

        # Setup activity panel updates
        self.activity_manager.setup_debounced_updates()

        # Initialize persistent editors
        self.table_manager.open_persistent_editors()

    def _setup_controllers(self):
        """Initialize and configure controllers."""
        self.filter_controller = AdvancedFilterController(self.filtersLayout, self.toolButton)
        self.lists_controller = ListsController(self)

        # Connect filter signals
        self.filter_controller.filters_changed.connect(self._on_filters_changed)
        self.filter_controller.project_changed.connect(self.on_project_changed)

        # Connect UI signals
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.listView.selectionModel().currentChanged.connect(self.on_playlist_selected)
        self.activity_ui.pushButton_comment.clicked.connect(self.on_comment_clicked)

        # Connect mode toggle button
        self.activity_ui.modeToggleButton.clicked.connect(self.toggle_activity_mode)

        # Setup preferences menu
        self.preferences_manager.setup_tool_button_menu()

    def _load_initial_data(self):
        """Load initial project data."""
        projects = self.data_service.fetch_projects()
        self.filter_controller.set_projects(projects)

    def _setup_ui(self):
        """Configure UI elements."""
        self.tabWidget.setTabText(0, "📦 Review Submissions")
        self.tabWidget.setTabText(1, "📝 Lists")

        self.activity_ui.pushButton_comment.setStyleSheet("font-size: 12px; color: #ffffff; padding: 3px;")

    def on_project_changed(self, project_name):
        """Handle project selection change."""
        if project_name:
            self._load_project_data(project_name)
            # Update OpenRV host context for Loader
            self._update_openrv_context(project_name)
        else:
            self._clear_project_data()

        self._update_ui_after_project_change(project_name)

        # Save project selection to QSettings
        settings = QSettings("ReviewBrowser1", "UIPreferences1")
        settings.setValue("current_project", project_name or "")

    def _update_openrv_context(self, project_name):
        """Update OpenRV host context to match selected project."""
        try:
            from ayon_core.pipeline.context_tools import registered_host
            from ayon_openrv.api.pipeline import imprint
            import os

            # Update environment variables
            os.environ["AYON_PROJECT_NAME"] = project_name

            # Update OpenRV session context
            context_data = {
                "project_name": project_name,
                "folder_path": "",  # Reset folder/task when changing projects
                "task_name": ""
            }

            # Store in OpenRV root node
            imprint("root", context_data, prefix="ayon.")

            # Update host context if available
            host = registered_host()
            if hasattr(host, 'update_context_data'):
                host.update_context_data(context_data, {})

        except ModuleNotFoundError as e:
            import os
            # Fallback if OpenRV modules not available
            os.environ["AYON_PROJECT_NAME"] = project_name
            os.environ["AYON_FOLDER_PATH"] = ""
            os.environ["AYON_TASK_NAME"] = ""

    def _load_project_data(self, project_name):
        """Load data for selected project."""
        self.data_service.set_project(project_name)
        self.all_versions = self.data_service.fetch_versions()
        self.playlists = self.data_service.fetch_playlists()

    def _clear_project_data(self):
        """Clear project data when no project selected."""
        self.data_service.set_project(None)
        self.all_versions = []
        self.playlists = {}

    def _update_ui_after_project_change(self, project_name):
        """Update UI components after project change."""
        reviewers = self._extract_reviewers() if project_name else []
        playlists_names = list(self.playlists.keys()) if project_name else []

        self.review_model.update_data(self.all_versions)
        # Update the playlist model and notify the lists controller
        self.playlist_model.setStringList(playlists_names)
        if hasattr(self, 'lists_controller'):
            self.lists_controller.update_list_items(playlists_names)

        self.filter_controller.set_reviewers(reviewers)

        # Fetch and set dynamic statuses and task types
        if project_name:
            statuses = self.data_service.fetch_version_statuses(project_name)
            task_types = self.data_service.fetch_task_types(project_name)

            self.filter_controller.review_filter_controller.strategy.set_status_items(statuses)
            self.filter_controller.list_filter_controller.strategy.set_status_items(statuses)
            self.filter_controller.review_filter_controller.strategy.set_task_type_items(task_types)
            self.filter_controller.list_filter_controller.strategy.set_task_type_items(task_types)

            # Set available statuses for activity panel
            self.activity_manager.set_available_statuses(statuses)

            self.filter_controller.filter_manager.refresh_current_strategy()

        self.current_versions = []
        self.activity_ui.textBrowser_activity_panel.clear()
        self.apply_filters()

        if project_name:
            self.tableView_review_versions.resizeColumnsToContents()

    def _extract_reviewers(self):
        """Extract unique reviewers from versions data."""
        return list(set(item.get('reviewer_name', 'N/A') for item in self.all_versions
                        if item.get('reviewer_name', 'N/A') != 'N/A'))

    def on_playlist_selected(self, current, previous):
        """Handle playlist selection change."""
        if current.isValid():
            playlist_name = self.playlist_model.data(current)
            current_project = self.filter_controller.get_current_project()
            playlist_id = self.playlists[playlist_name]
            self.current_versions = self.data_service.fetch_versions_by_playlist(playlist_id, current_project)
            self.apply_filters()

    def on_tab_changed(self):
        """Handle tab change."""
        current_tab = self.tabWidget.currentIndex()
        self.filter_controller.switch_tab(current_tab)
        # Delay apply_filters to allow filter restoration to complete
        QTimer.singleShot(100, self.apply_filters)
        QTimer.singleShot(150, self.table_manager.open_persistent_editors)

    def _on_filters_changed(self, tab_index, filters):
        """Handle filter changes from filter controller."""
        self.apply_filters()

    def apply_filters(self):
        """Apply current filters to data."""
        current_tab = self.tabWidget.currentIndex()

        if current_tab == 0:  # Review tab
            filtered_versions = self.filter_controller.apply_filters(self.all_versions, current_tab)
            self.review_model.update_data(filtered_versions)
            self.tableView_review_versions.resizeColumnsToContents()
        else:  # Lists tab
            filtered_versions = self.filter_controller.apply_filters(self.current_versions, current_tab)
            self.list_model.update_data(filtered_versions)
            self.tableView_list_versions.resizeColumnsToContents()

        QTimer.singleShot(50, self.table_manager.open_persistent_editors)

    def on_comment_clicked(self):
        """Handle comment button click."""
        current_tab = self.tabWidget.currentIndex()
        table_view = self._get_current_table_view(current_tab)
        rv_ops = self.rv_manager.get_rv_ops()

        self.comment_handler.create_comment(
            self.activity_ui.textEdit_comment,
            table_view,
            self.tabWidget,
            self.filter_controller,
            self.data_service,
            self._handle_comment_callback,
            rv_ops,
            self.activity_manager  # Pass activity_manager for mode detection
        )

    def _get_current_table_view(self, tab_index):
        """Get table view for current tab."""
        return self.tableView_review_versions if tab_index == 0 else self.tableView_list_versions

    def _handle_comment_callback(self, row_data):
        """Handle comment creation callback."""
        self.fetch_and_display_activities(row_data, from_comment=True)

    def _clear_activity_panel(self):
        """Clear all activity panel widgets when sorting."""
        self.activity_ui.textBrowser_activity_panel.clear()
        self.activity_ui.pathLabel_value.setText("")
        self.activity_ui.versionComboBox.clear()
        self.activity_ui.statusComboBox.setCurrentIndex(-1)
        self.activity_ui.authorLineEdit.clear()
        self.activity_ui.textEdit_comment.clear()

    # Delegation methods
    def open_persistent_editors(self):
        """Delegate to table manager."""
        self.table_manager.open_persistent_editors()

    def fetch_and_display_activities(self, row_data, from_rv=False, from_comment=False):
        """Delegate to activity manager."""
        self.activity_manager.fetch_and_display_activities(row_data, from_rv, from_comment)

    def detach_dock(self):
        """Detach dock and send to RV, replacing ReviewMenu"""
        try:
            import rv.qtutils

            # Get RV session window
            rv_window = rv.qtutils.sessionWindow()
            if rv_window:
                # Remove existing docks with same titles to prevent duplicates
                existing_docks = rv_window.findChildren(QDockWidget)
                for dock in existing_docks:
                    if dock.windowTitle() in ["AYON Review", "RV View Version Info"]:
                        rv_window.removeDockWidget(dock)
                        dock.close()

                # Remove from current parent first
                if self.activityCommentDock.parent():
                    self.removeDockWidget(self.activityCommentDock)

                # Reparent to RV and configure
                self.activityCommentDock.setParent(rv_window)
                self.activityCommentDock.setWindowTitle("RV View Version Info")
                self.activityCommentDock.setFloating(False)

                # Add to RV in the same position as ReviewMenu
                rv_window.addDockWidget(Qt.RightDockWidgetArea, self.activityCommentDock)
                self.activityCommentDock.show()
                # Sync activity panel with current RV ViewNode
                self.table_manager.handle_activity_panel_detach()
            else:
                # Fallback to standalone window if RV not available
                self.activityCommentDock.setFloating(True)
                self.activityCommentDock.setWindowFlags(Qt.Window)
                self.activityCommentDock.setParent(None)
                self.activityCommentDock.show()
        except ImportError:
            # RV not available, show as standalone
            self.activityCommentDock.setFloating(True)
            self.activityCommentDock.setWindowFlags(Qt.Window)
            self.activityCommentDock.setParent(None)
            self.activityCommentDock.show()

    def attach_dock(self):
        """Reattach dock to main window from RV or floating state"""
        try:
            import rv.qtutils
            # Remove from RV if it's there
            rv_window = rv.qtutils.sessionWindow()
            if rv_window and self.activityCommentDock.parent() == rv_window:
                rv_window.removeDockWidget(self.activityCommentDock)
        except ImportError:
            pass

        # Reattach to Review Browser
        self.activityCommentDock.setParent(self)
        self.activityCommentDock.setWindowFlags(Qt.Widget)
        self.activityCommentDock.setWindowTitle("Version Info")
        self.addDockWidget(Qt.RightDockWidgetArea, self.activityCommentDock)
        self.activityCommentDock.setFloating(False)
        self.activityCommentDock.show()

    def toggle_activity_mode(self):
        """Toggle between Browse Mode and Review Mode."""
        if self.activity_ui.modeToggleButton.text() == "SWITCH TO RV":
            # Switch to Review Mode (detach to RV)
            self.detach_dock()
            self.activity_ui.modeToggleButton.setText("SWITCH TO BROWSER")
        else:
            # Switch to Browse Mode (attach to browser)
            self.attach_dock()
            self.activity_ui.modeToggleButton.setText("SWITCH TO RV")
            # Handle attach transition
            self.table_manager.handle_activity_panel_attach()
    
    def _setup_rv_integration(self):
        """Setup RV integration if available."""
        try:
            from ...api.rv.rv_registry import initialize_rv_integration
            initialize_rv_integration()
            print("✅ RV integration initialized")
        except Exception as e:
            print(f"⚠️ RV integration not available: {e}")