from typing import Dict, Any, Optional

try:
    from qtpy.QtCore import *
except ImportError:
    from PySide2.QtCore import *

try:
    from .filter_strategy import FilterStrategy
    from ..views.widgets.standalone_search_bar import FiltersBar
except ImportError:
    from src.controllers.filter_strategy import FilterStrategy
    from src.views.widgets.standalone_search_bar import FiltersBar


class FilterManager(QObject):
    """Manages filter strategies and coordinates filter bar updates."""

    filters_changed = Signal(int, dict)  # tab_index, filters

    def __init__(self, parent=None):
        super().__init__(parent)
        self._strategies: Dict[int, FilterStrategy] = {}
        self._current_strategy: Optional[FilterStrategy] = None
        self._current_tab_index: int = -1
        self._filters_bar: Optional[FiltersBar] = None
        self._active_filters: Dict[str, Any] = {}

    def set_filters_bar(self, filters_bar: FiltersBar):
        """Set the filters bar widget."""
        self._filters_bar = filters_bar
        if self._filters_bar:
            self._filters_bar.filter_changed.connect(self._on_filter_changed)

    def register_strategy(self, tab_index: int, strategy: FilterStrategy):
        """Register a filter strategy for a specific tab."""
        self._strategies[tab_index] = strategy

    def switch_tab(self, tab_index: int):
        """Switch to a different tab and update filter definitions."""
        if tab_index == self._current_tab_index:
            return

        strategy = self._strategies.get(tab_index)
        if strategy != self._current_strategy:
            self._current_strategy = strategy
            self._current_tab_index = tab_index
            self._active_filters.clear()  # Clear filters when switching tabs
            self._update_filters_bar()

    def refresh_current_strategy(self):
        """Refresh the current strategy's filter definitions."""
        if self._current_strategy:
            self._update_filters_bar()

    def get_current_strategy(self) -> Optional[FilterStrategy]:
        """Get the currently active filter strategy."""
        return self._current_strategy

    def get_active_filters(self) -> Dict[str, Any]:
        """Get currently active filters."""
        return self._active_filters.copy()

    def clear_filters(self):
        """Clear all active filters."""
        if self._filters_bar and hasattr(self._filters_bar, '_widgets_by_name'):
            active_filters = list(self._filters_bar._widgets_by_name.keys())
            for filter_name in active_filters:
                self._filters_bar._on_item_close_requested(filter_name)

        self._active_filters.clear()
        self.filters_changed.emit(self._current_tab_index, self._active_filters)

    def set_filter_value(self, filter_name: str, value: Any):
        """Set a specific filter value programmatically."""
        if self._filters_bar:
            self._filters_bar.set_filter_value(filter_name, value)

    def _update_filters_bar(self):
        """Update the filters bar with current strategy's definitions."""
        if self._current_strategy and self._filters_bar:
            definitions = self._current_strategy.get_filter_definitions()
            self._filters_bar.set_search_items(definitions)

    def _on_filter_changed(self, filter_name: str):
        """Handle filter changes from the filters bar."""
        if self._filters_bar:
            value = self._filters_bar.get_filter_value(filter_name)
            if value:
                self._active_filters[filter_name] = value
            else:
                self._active_filters.pop(filter_name, None)

            self.filters_changed.emit(self._current_tab_index, self._active_filters)