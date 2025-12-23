from typing import List, Dict, Any

try:
    from qtpy.QtCore import *
except ImportError:
    from PySide2.QtCore import *

try:
    from .filter_strategy import FilterStrategy, ReviewTableFilterStrategy, ListTableFilterStrategy
except ImportError:
    from src.controllers.filter_strategy import FilterStrategy, ReviewTableFilterStrategy, ListTableFilterStrategy


class BaseTableFilterController(QObject):
    """Base controller for table-specific filtering."""

    def __init__(self, strategy: FilterStrategy, parent=None):
        super().__init__(parent)
        self.strategy = strategy
        self.active_filters: Dict[str, Any] = {}
        self.original_data: List[Dict[str, Any]] = []
        self.filtered_data: List[Dict[str, Any]] = []

    def set_data(self, data: List[Dict[str, Any]]):
        """Set the original data to be filtered."""
        self.original_data = data
        self.filtered_data = data.copy()

    def apply_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters and return filtered data."""
        self.active_filters = filters
        self.filtered_data = self.strategy.apply_filters(self.original_data, filters)
        return self.filtered_data

    def get_filtered_data(self) -> List[Dict[str, Any]]:
        """Get the currently filtered data."""
        return self.filtered_data

    def clear_filters(self):
        """Clear all filters and return original data."""
        self.active_filters.clear()
        self.filtered_data = self.original_data.copy()
        return self.filtered_data


class ReviewTableFilterController(BaseTableFilterController):
    """Filter controller specifically for Review table."""

    def __init__(self, parent=None):
        super().__init__(ReviewTableFilterStrategy(), parent)

    def set_reviewers(self, reviewers: List[str]):
        """Update available reviewers in the strategy."""
        # Update reviewer filter items
        for filter_def in self.strategy.get_filter_definitions():
            if filter_def.name == "reviewer":
                filter_def.items = [{"value": reviewer} for reviewer in ["All"] + reviewers]
                break


class ListTableFilterController(BaseTableFilterController):
    """Filter controller specifically for List table."""

    def __init__(self, parent=None):
        super().__init__(ListTableFilterStrategy(), parent)

    def set_authors(self, authors: List[str]):
        """Update available authors in the strategy."""
        # Update author filter items
        for filter_def in self.strategy.get_filter_definitions():
            if filter_def.name == "author":
                filter_def.items = [{"value": author} for author in ["All"] + authors]
                break