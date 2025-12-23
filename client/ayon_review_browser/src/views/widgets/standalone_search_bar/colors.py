"""Simplified color system for standalone module."""
try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class ColorObject:
    """Simple color wrapper."""

    def __init__(self, color_string):
        self._color_string = color_string

    def get_qcolor(self):
        """Return QColor representation."""
        return QColor(self._color_string)


def get_objected_colors(*keys):
    """Get color object by key path.

    Simplified version with default fallback colors.
    """
    color_map = {
        "bg-view-selection-hover": "#3d4852",
        "font": "#e6e6e6",
    }

    if not keys:
        return ColorObject("#e6e6e6")

    key = keys[0] if len(keys) == 1 else ":".join(keys)
    color_string = color_map.get(key, "#e6e6e6")
    return ColorObject(color_string)