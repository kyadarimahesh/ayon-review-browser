try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from ..views.widgets.filter_widgets import FilterWidgets
    from ...icons.icons import Icons
    from .filter_manager import FilterManager
    from .table_filter_controller import ReviewTableFilterController, ListTableFilterController
except ImportError:
    from src.views.widgets.filter_widgets import FilterWidgets
    from icons.icons import Icons
    from src.controllers.filter_manager import FilterManager
    from src.controllers.table_filter_controller import ReviewTableFilterController, ListTableFilterController


class AdvancedFilterController(QObject):
    """Modular advanced filter controller using filter strategies."""
    filters_changed = Signal(int, dict)  # tab_index, filters
    project_changed = Signal(str)

    def __init__(self, filters_layout=None, tool_button=None):
        super().__init__()
        self.filters_layout = filters_layout
        self.tool_button = tool_button
        self._available_projects = []

        # Initialize modular components
        self.filter_manager = FilterManager(self)
        self.review_filter_controller = ReviewTableFilterController(self)
        self.list_filter_controller = ListTableFilterController(self)

        # Register strategies
        self.filter_manager.register_strategy(0, self.review_filter_controller.strategy)
        self.filter_manager.register_strategy(1, self.list_filter_controller.strategy)
        
        # Initialize default tab (fixes Linux issue where currentChanged doesn't fire)
        self.filter_manager.switch_tab(0)

        if filters_layout:
            self._setup_layout()
        else:
            self.filters_bar = FilterWidgets.create_advanced_filters_bar()
            self.filter_manager.set_filters_bar(self.filters_bar)

        self._connect_signals()

    def _setup_layout(self):
        """Setup the complete filters layout with buttons."""
        # Create project selector (separate from advanced filters)
        self.project_selector = FilterWidgets.create_project_selector()

        # Create advanced filters bar (without project)
        self.filters_bar = FilterWidgets.create_advanced_filters_bar()
        self.filter_manager.set_filters_bar(self.filters_bar)

        self.refresh_btn = FilterWidgets.create_refresh_button()
        self.refresh_btn.setIcon(Icons.refresh())
        self.clear_btn = FilterWidgets.create_clear_button()
        self.clear_btn.setIcon(Icons.clear())

        # Set consistent height
        consistent_height = 34
        self.project_selector.setFixedHeight(consistent_height)
        self.filters_bar.setFixedHeight(consistent_height)
        self.refresh_btn.setFixedHeight(consistent_height)
        self.clear_btn.setFixedHeight(consistent_height)

        # Clear existing layout
        while self.filters_layout.count():
            item = self.filters_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.spacerItem():
                del item

        # Add project label and selector
        project_label = QLabel("Project:")
        self.filters_layout.addWidget(project_label)
        self.filters_layout.addWidget(self.project_selector)

        # Add advanced filters and buttons
        self.filters_layout.addWidget(self.filters_bar)
        self.filters_layout.addWidget(self.refresh_btn)
        self.filters_layout.addWidget(self.clear_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)  # PySide2

        self.filters_layout.addItem(spacer)

        if self.tool_button:
            self.filters_layout.addWidget(self.tool_button)

    def _connect_signals(self):
        self.filter_manager.filters_changed.connect(self._on_filters_changed)

        # Connect project selector if it exists
        if hasattr(self, 'project_selector'):
            self.project_selector.activated.connect(self._on_project_selected)
            self.project_selector.lineEdit().returnPressed.connect(self._on_project_entered)

        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.clicked.connect(self.refresh_data)
        if hasattr(self, 'clear_btn'):
            self.clear_btn.clicked.connect(self.clear_filters)

    def _on_filters_changed(self, tab_index, filters):
        """Handle filter changes from filter manager."""
        self.filters_changed.emit(tab_index, filters)

    def _on_project_selected(self):
        """Handle project selection from dropdown."""
        if hasattr(self, 'project_selector'):
            project_value = self.project_selector.currentText()
            self.project_changed.emit(project_value)

    def _on_project_entered(self):
        """Handle project entered via typing."""
        if hasattr(self, 'project_selector'):
            project_value = self.project_selector.currentText()
            self.project_changed.emit(project_value)

    def get_widget(self):
        """Return the filters bar widget for adding to layouts."""
        return self.filters_bar

    def switch_tab(self, tab_index: int):
        """Switch to a different tab and update filters accordingly."""
        self.filter_manager.switch_tab(tab_index)

    def clear_filters(self, clear_project=False):
        """Clear all active filters.

        Args:
            clear_project (bool): Whether to clear project selection as well. Defaults to False.
        """
        # Clear project selector only if explicitly requested
        if clear_project and hasattr(self, 'project_selector'):
            self.project_selector.setCurrentIndex(0)
            self.project_changed.emit("")

        # Clear filters through filter manager
        self.filter_manager.clear_filters()

    def get_filter_values(self):
        """Get current filter values."""
        return self.filter_manager.get_active_filters()

    def apply_filters(self, data, tab_index: int):
        """Apply filters to data using the appropriate strategy."""
        filters = self.get_filter_values()

        if tab_index == 0:  # Review table
            self.review_filter_controller.set_data(data)
            result = self.review_filter_controller.apply_filters(filters)
            return result
        elif tab_index == 1:  # List table
            self.list_filter_controller.set_data(data)
            result = self.list_filter_controller.apply_filters(filters)
            return result

        return data

    def set_projects(self, projects):
        """Set available projects (for compatibility)."""
        self._available_projects = projects

        # Update project selector
        if hasattr(self, 'project_selector') and projects:
            self.project_selector.clear()
            self.project_selector.addItem("")  # Empty item
            self.project_selector.addItems(projects)
            self.project_selector.setCurrentIndex(0)

    def get_current_project(self):
        """Get current project value."""
        if hasattr(self, 'project_selector'):
            return self.project_selector.currentText()
        return ''

    def set_reviewers(self, reviewers):
        """Set available reviewers for review table."""
        self.review_filter_controller.set_reviewers(reviewers)

    def set_authors(self, authors):
        """Set available authors for list table."""
        self.list_filter_controller.set_authors(authors)

    def refresh_data(self):
        """Refresh data - functionality matches original."""
        current_project = self.get_current_project()
        self.project_changed.emit(current_project)