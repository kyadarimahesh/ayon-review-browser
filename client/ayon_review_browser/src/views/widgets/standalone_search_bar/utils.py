"""Utility functions for the search bar module."""
try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    import qtawesome
except ImportError:
    qtawesome = None

try:
    import qtmaterialsymbols
except ImportError:
    qtmaterialsymbols = None

from .constants import DEFAULT_WEB_ICON_COLOR


def set_style_property(widget, property_name, property_value):
    """Set widget's property that may affect style."""
    cur_value = widget.property(property_name)
    if cur_value == property_value:
        return
    widget.setProperty(property_name, property_value)
    style = widget.style()
    style.polish(widget)


class _IconsCache:
    """Cache for icons."""
    _cache = {}
    _qtawesome_cache = {}

    @classmethod
    def get_qta_icon_by_name_and_color(cls, icon_name, icon_color):
        if not qtawesome or not icon_name or not icon_color:
            return None

        full_icon_name = f"{icon_name}-{icon_color}"
        if full_icon_name in cls._qtawesome_cache:
            return cls._qtawesome_cache[full_icon_name]

        variants = [icon_name]
        try:
            qta_instance = qtawesome._instance()
            for key in qta_instance.charmap.keys():
                variants.append(f"{key}.{icon_name}")
        except Exception:
            pass

        icon = None
        for variant in variants:
            try:
                icon = qtawesome.icon(variant, color=icon_color)
                break
            except Exception:
                pass

        cls._qtawesome_cache[full_icon_name] = icon
        return icon

    @classmethod
    def get_icon(cls, icon_def):
        if not icon_def:
            return cls.get_default()

        icon_type = icon_def["type"]
        cache_key = cls._get_cache_key(icon_def)
        cache = cls._cache.get(cache_key)
        if cache is not None:
            return cache

        icon = None
        if icon_type == "material-symbols":
            icon_name = icon_def["name"]
            icon_color = icon_def.get("color") or DEFAULT_WEB_ICON_COLOR
            if qtmaterialsymbols and qtmaterialsymbols.get_icon_name_char(icon_name) is not None:
                icon = qtmaterialsymbols.get_icon(icon_name, icon_color)

        elif icon_type == "awesome-font":
            icon_name = icon_def["name"]
            icon_color = icon_def.get("color")
            icon = cls.get_qta_icon_by_name_and_color(icon_name, icon_color)

        elif icon_type == "transparent":
            size = icon_def.get("size", 256)
            pix = QPixmap(size, size)
            pix.fill(Qt.transparent)
            icon = QIcon(pix)

        if icon is None:
            icon = cls.get_default()
        cls._cache[cache_key] = icon
        return icon

    @classmethod
    def get_default(cls):
        pix = QPixmap(1, 1)
        pix.fill(Qt.transparent)
        return QIcon(pix)

    @classmethod
    def _get_cache_key(cls, icon_def):
        parts = []
        icon_type = icon_def["type"]
        if icon_type == "material-symbols":
            color = icon_def.get("color") or DEFAULT_WEB_ICON_COLOR
            if isinstance(color, QColor):
                color = color.name()
            parts = [icon_type, icon_def["name"] or "", color]
        elif icon_type == "awesome-font":
            color = icon_def.get("color") or ""
            if isinstance(color, QColor):
                color = color.name()
            parts = [icon_type, icon_def["name"] or "", color]
        elif icon_type == "transparent":
            size = icon_def.get("size", 256)
            parts = [icon_type, str(size)]
        return "|".join(parts)


def get_qt_icon(icon_def):
    """Returns icon from cache or creates new one."""
    return _IconsCache.get_icon(icon_def)