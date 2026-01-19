import sys
import os

# Add activity panel path
activity_panel_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'ayon-activity-panel',
                                   'client')
activity_panel_path = os.path.abspath(activity_panel_path)
if os.path.exists(activity_panel_path):
    sys.path.insert(0, activity_panel_path)

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from ...ui.generated.review_browser_ui import Ui_BrowserWidget
    from ...services.data_service import DataService
    from ..models.table_models import ReviewTableModel, ListTableModel
    from ..controllers.advanced_filter_controller import AdvancedFilterController
    from ..controllers.lists_controller import ListsController
    from ..managers.table_manager import TableManager
    from ..managers.preferences_manager import PreferencesManager
except ImportError:
    from ui.generated.review_browser_ui import Ui_BrowserWidget
    from services.data_service import DataService
    from src.models.table_models import ReviewTableModel, ListTableModel
    from src.controllers.advanced_filter_controller import AdvancedFilterController
    from src.controllers.lists_controller import ListsController
    from src.managers.table_manager import TableManager
    from src.managers.preferences_manager import PreferencesManager

from ayon_activity_panel import ActivityPanel


class ReviewBrowser(QMainWindow, Ui_BrowserWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Create activity panel
        self.activity_panel = ActivityPanel(bind_rv_events=False)
        self.activity_dock = QDockWidget("Version Info", self)
        self.activity_dock.setWidget(self.activity_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.activity_dock)

        # Initialize core components
        self.data_service = DataService()

        # Data storage
        self.all_versions = []
        self.current_versions = []
        self.playlists = {}
        self._current_version_id = None

        # Initialize managers
        self.table_manager = TableManager(self)
        self.preferences_manager = PreferencesManager(self)

        # Setup components
        self._setup_models()
        self._setup_controllers()
        self._load_initial_data()
        self._setup_ui()

        # Load preferences after initialization
        QTimer.singleShot(100, self.preferences_manager.load_preferences)

        # Center on screen
        self._center_on_screen()

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

        # Configure tables through manager
        self.table_manager.setup_tables()
        self.table_manager.setup_context_menus()

        # Connect signals
        self.review_model.sorting_started.connect(self._clear_selection)
        self.list_model.sorting_started.connect(self._clear_selection)

        # Connect table double-click to activity panel
        self.tableView_review_versions.doubleClicked.connect(self._on_row_double_clicked)
        self.tableView_list_versions.doubleClicked.connect(self._on_row_double_clicked)

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

    def on_project_changed(self, project_name):
        """Handle project selection change."""
        if project_name:
            self.activity_panel.set_project(project_name)
            self._load_project_data(project_name)
        else:
            self._clear_project_data()

        self._update_ui_after_project_change(project_name)

        # Save project selection to QSettings
        settings = QSettings("ReviewBrowser1", "UIPreferences1")
        settings.setValue("current_project", project_name or "")

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

            # Set statuses for activity panel
            self.activity_panel.set_available_statuses(statuses)

            self.filter_controller.filter_manager.refresh_current_strategy()

        self.current_versions = []
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

    def _on_row_double_clicked(self, index):
        """Update activity panel when row is double-clicked."""
        if not index.isValid():
            return
        
        current_tab = self.tabWidget.currentIndex()
        table_view = self.tableView_review_versions if current_tab == 0 else self.tableView_list_versions
        model = table_view.model()
        row_data = model._data[index.row()]
        
        # Skip if same version (prevents redundant work)
        if row_data['version_id'] == self._current_version_id:
            return
        
        self._current_version_id = row_data['version_id']
        self.activity_panel.set_version(row_data['version_id'], row_data)

    def _clear_selection(self):
        """Clear selection when sorting."""
        pass

    def _center_on_screen(self):
        """Center window on screen."""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def open_persistent_editors(self):
        """Delegate to table manager."""
        self.table_manager.open_persistent_editors()
