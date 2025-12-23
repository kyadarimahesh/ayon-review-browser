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
    from ...icons.icons import Icons
except ImportError:
    # Fall back to absolute imports (when run directly)
    from icons.icons import Icons


class PreferencesManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def setup_tool_button_menu(self):
        """Setup toolButton menu with preferences options."""
        try:
            menu = QMenu(self.main_window)

            save_action = menu.addAction(Icons.save(), "Save UI Preferences")
            save_action.triggered.connect(self.save_preferences)

            load_action = menu.addAction(Icons.load(), "Load UI Preferences")
            load_action.triggered.connect(self.load_preferences)

            reset_action = menu.addAction(Icons.reset(), "Reset UI")
            reset_action.triggered.connect(self.reset_columns)

            menu.addSeparator()

            # Add row height control
            self._add_row_height_control(menu)

            # Set toolButton icon
            if hasattr(self.main_window, 'toolButton'):
                self.main_window.toolButton.setIcon(Icons.settings())
                self.main_window.toolButton.setMenu(menu)
                self.main_window.toolButton.setPopupMode(QToolButton.InstantPopup)
        except (AttributeError, RuntimeError) as e:
            print(f"Warning: Could not setup tool button menu: {e}")

    def save_preferences(self):
        """Save UI preferences to settings."""
        settings = QSettings("ReviewBrowser1", "UIPreferences1")

        # Save main window geometry and state
        settings.setValue("geometry", self.main_window.saveGeometry())
        settings.setValue("windowState", self.main_window.saveState())
        settings.setValue("currentTab", self.main_window.tabWidget.currentIndex())

        # Cache table references for performance
        review_table = self.main_window.tableView_review_versions
        list_table = self.main_window.tableView_list_versions
        review_header = review_table.horizontalHeader()
        list_header = list_table.horizontalHeader()

        # Save review table preferences
        review_col_count = self.main_window.review_model.columnCount()
        review_columns = [not review_table.isColumnHidden(col) for col in range(review_col_count)]
        review_order = [review_header.visualIndex(col) for col in range(review_col_count)]
        review_widths = [review_header.sectionSize(col) for col in range(review_col_count)]

        settings.setValue("review_columns", review_columns)
        settings.setValue("review_order", review_order)
        settings.setValue("review_widths", review_widths)

        # Save list table preferences
        list_col_count = self.main_window.list_model.columnCount()
        list_columns = [not list_table.isColumnHidden(col) for col in range(list_col_count)]
        list_order = [list_header.visualIndex(col) for col in range(list_col_count)]
        list_widths = [list_header.sectionSize(col) for col in range(list_col_count)]

        settings.setValue("list_columns", list_columns)
        settings.setValue("list_order", list_order)
        settings.setValue("list_widths", list_widths)

        # Save splitter sizes
        settings.setValue("list_splitter", self.main_window.splitterLists.saveState())
        settings.setValue("main_splitter", self.main_window.activity_ui.mainSplitter.saveState())

        # Save row height
        settings.setValue("row_height",
                          self.main_window.tableView_review_versions.verticalHeader().defaultSectionSize())

        # Save current project selection
        if hasattr(self.main_window, 'filter_controller'):
            current_project = self.main_window.filter_controller.get_current_project()
            settings.setValue("current_project", current_project)

        settings.sync()

    def load_preferences(self):
        """Load UI preferences from settings."""
        settings = QSettings("ReviewBrowser1", "UIPreferences1")

        # Load main window geometry and state
        geometry = settings.value("geometry")
        if geometry:
            self.main_window.restoreGeometry(geometry)

        window_state = settings.value("windowState")
        if window_state:
            self.main_window.restoreState(window_state)

        current_tab = settings.value("currentTab")
        if current_tab is not None:
            if isinstance(current_tab, str):
                current_tab = int(current_tab)
            self.main_window.tabWidget.setCurrentIndex(current_tab)

        # Cache table references and column counts
        review_table = self.main_window.tableView_review_versions
        list_table = self.main_window.tableView_list_versions
        review_col_count = self.main_window.review_model.columnCount()
        list_col_count = self.main_window.list_model.columnCount()

        # Load review table preferences
        review_columns = settings.value("review_columns", [])
        review_order = settings.value("review_order", [])
        review_widths = settings.value("review_widths", [])

        if review_columns and len(review_columns) == review_col_count:
            review_header = review_table.horizontalHeader()

            # Apply column order first
            if review_order and len(review_order) == review_col_count:
                for logical_index, visual_index in enumerate(review_order):
                    visual_index = int(visual_index) if isinstance(visual_index, str) else visual_index
                    review_header.moveSection(review_header.visualIndex(logical_index), visual_index)

            # Apply column visibility and widths in single loop
            for col, visible in enumerate(review_columns):
                visible = visible if isinstance(visible, bool) else visible.lower() == 'true'
                review_table.setColumnHidden(col, not visible)

                # Apply width if available
                if review_widths and col < len(review_widths):
                    width = int(review_widths[col]) if isinstance(review_widths[col], str) else review_widths[col]
                    review_header.resizeSection(col, width)

        # Load list table preferences
        list_columns = settings.value("list_columns", [])
        list_order = settings.value("list_order", [])
        list_widths = settings.value("list_widths", [])

        if list_columns and len(list_columns) == list_col_count:
            list_header = list_table.horizontalHeader()

            # Apply column order first
            if list_order and len(list_order) == list_col_count:
                for logical_index, visual_index in enumerate(list_order):
                    visual_index = int(visual_index) if isinstance(visual_index, str) else visual_index
                    list_header.moveSection(list_header.visualIndex(logical_index), visual_index)

            # Apply column visibility and widths in single loop
            for col, visible in enumerate(list_columns):
                visible = visible if isinstance(visible, bool) else visible.lower() == 'true'
                list_table.setColumnHidden(col, not visible)

                # Apply width if available
                if list_widths and col < len(list_widths):
                    width = int(list_widths[col]) if isinstance(list_widths[col], str) else list_widths[col]
                    list_header.resizeSection(col, width)

        # Load splitter sizes
        list_splitter_state = settings.value("list_splitter")
        if list_splitter_state:
            self.main_window.splitterLists.restoreState(list_splitter_state)

        main_splitter_state = settings.value("main_splitter")
        if main_splitter_state:
            self.main_window.activity_ui.mainSplitter.restoreState(main_splitter_state)

        # Load row height
        row_height = settings.value("row_height", 30)
        if isinstance(row_height, str):
            row_height = int(row_height)
        if hasattr(self, 'row_height_slider'):
            self.row_height_slider.setValue(row_height)
        self._apply_row_height(row_height)

        # Load project selection first
        current_project = settings.value("current_project", "")
        if current_project and hasattr(self.main_window, 'filter_controller'):
            if hasattr(self.main_window.filter_controller, 'project_selector'):
                # Use direct Qt method instead of list comprehension
                index = self.main_window.filter_controller.project_selector.findText(current_project)
                if index >= 0:
                    self.main_window.filter_controller.project_selector.setCurrentIndex(index)
                    # Trigger project change after a delay to ensure UI is ready
                    QTimer.singleShot(200,
                                      lambda: self.main_window.filter_controller.project_changed.emit(current_project))

    def reset_columns(self):
        """Reset all columns to default state."""
        # Show all columns
        for col in range(self.main_window.review_model.columnCount()):
            self.main_window.tableView_review_versions.showColumn(col)
        for col in range(self.main_window.list_model.columnCount()):
            self.main_window.tableView_list_versions.showColumn(col)

        self.main_window.tableView_review_versions.resizeColumnsToContents()
        self.main_window.tableView_list_versions.resizeColumnsToContents()

    def _add_row_height_control(self, menu):
        """Add row height slider to menu."""
        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel("Row Height:")
        slider_layout.addWidget(label)

        self.row_height_slider = QSlider(Qt.Horizontal)
        self.row_height_slider.setRange(30, 150)
        self.row_height_slider.setValue(30)
        self.row_height_slider.setFixedWidth(100)
        self.row_height_slider.valueChanged.connect(self._apply_row_height)
        slider_layout.addWidget(self.row_height_slider)

        self.height_value_label = QLabel("30")
        self.height_value_label.setFixedWidth(30)
        slider_layout.addWidget(self.height_value_label)

        slider_action = QWidgetAction(menu)
        slider_action.setDefaultWidget(slider_widget)
        menu.addAction(slider_action)

    def _apply_row_height(self, value):
        """Apply row height to both tables."""
        if hasattr(self, 'height_value_label'):
            self.height_value_label.setText(str(value))

        # Cache table references
        review_table = self.main_window.tableView_review_versions
        list_table = self.main_window.tableView_list_versions

        review_table.verticalHeader().setDefaultSectionSize(value)
        list_table.verticalHeader().setDefaultSectionSize(value)

        # Refresh thumbnails efficiently
        try:
            thumb_col_review = self.main_window.review_model.COLUMNS.index("Thumbnail")
            review_model = self.main_window.review_model
            review_rows = review_model.rowCount()
            if review_rows > 0:
                top_left = review_model.index(0, thumb_col_review)
                bottom_right = review_model.index(review_rows - 1, thumb_col_review)
                review_model.dataChanged.emit(top_left, bottom_right)
        except (ValueError, AttributeError):
            pass

        try:
            thumb_col_list = self.main_window.list_model.COLUMNS.index("Thumbnail")
            list_model = self.main_window.list_model
            list_rows = list_model.rowCount()
            if list_rows > 0:
                top_left = list_model.index(0, thumb_col_list)
                bottom_right = list_model.index(list_rows - 1, thumb_col_list)
                list_model.dataChanged.emit(top_left, bottom_right)
        except (ValueError, AttributeError):
            pass
