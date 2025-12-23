"""Standalone Search Bar Module

A reusable Qt-based search bar with advanced filtering capabilities.
Extracted from AYON Core for use in any Qt application.
"""

from .search_bar import (
    FilterDefinition,
    FiltersBar,
    FiltersPopup,
    FilterValuePopup,
    SearchItemDisplayWidget,
    FilterItemButton,
    set_line_edit_focus,
)

from .widgets import (
    BaseClickableFrame,
    SquareButton,
    PixmapLabel,
    SeparatorWidget,
)

from .utils import (
    get_qt_icon,
    set_style_property,
)

from .colors import get_objected_colors

__all__ = [
    "FilterDefinition",
    "FiltersBar",
    "FiltersPopup",
    "FilterValuePopup",
    "SearchItemDisplayWidget",
    "FilterItemButton",
    "set_line_edit_focus",
    "BaseClickableFrame",
    "SquareButton",
    "PixmapLabel",
    "SeparatorWidget",
    "get_qt_icon",
    "set_style_property",
    "get_objected_colors",
]

__version__ = "1.0.0"
