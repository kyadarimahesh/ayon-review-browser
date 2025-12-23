try:
    from qtpy.QtCore import *
except ImportError:
    from PySide2.QtCore import *


class ListsController:
    def __init__(self, main_window):
        self.main_window = main_window

        # Create and set up the proxy model for filtering
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(main_window.playlist_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # Set the proxy model to the list view instead of the source model
        self.main_window.listView.setModel(self.proxy_model)

        # Connect the search line edit to filter function
        self.main_window.searchLineEdit.textChanged.connect(self.filter_lists)

    def filter_lists(self, text):
        """Filter the lists based on search text"""
        self.proxy_model.setFilterFixedString(text)

    def update_list_items(self, items):
        """Update the list items and maintain the current filter"""
        current_filter = self.main_window.searchLineEdit.text()
        self.proxy_model.setFilterFixedString("")  # Clear filter temporarily
        self.main_window.playlist_model.setStringList(items)
        self.proxy_model.setFilterFixedString(current_filter)  # Reapply filter
