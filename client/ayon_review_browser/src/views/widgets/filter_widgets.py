try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from .standalone_search_bar import FiltersBar, FilterDefinition


class FilterWidgets:
    """Modern filter widgets using advanced search bar."""

    @staticmethod
    def create_advanced_filters_bar(parent=None):
        """Create the advanced filters bar (filter definitions set by strategies)."""
        filters_bar = FiltersBar(parent)
        # Filter definitions will be set by the FilterManager based on active strategy
        return filters_bar

    @staticmethod
    def create_refresh_button():
        button = QPushButton("Refresh")
        return button

    @staticmethod
    def create_clear_button():
        button = QPushButton("Clear")
        return button

    @staticmethod
    def create_project_selector():
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.setMinimumWidth(200)
        combo.setPlaceholderText("Select project...")
        return combo