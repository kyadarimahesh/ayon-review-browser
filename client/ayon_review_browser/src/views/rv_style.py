"""
OpenRV-inspired styling for AYON Review Browser.
Matches OpenRV's typography, spacing, and visual design.
PySide2/PySide6 compatible.
"""

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class RVStyle:
    """OpenRV-inspired style constants and stylesheet generator."""

    # OpenRV Typography (matches RV's interface)
    FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    FONT_SIZE_BASE = 10  # Base font size in pt
    FONT_SIZE_LARGE = 11
    FONT_SIZE_SMALL = 9
    FONT_SIZE_HEADER = 11

    # OpenRV Colors (dark theme matching RV)
    BG_DARK = "#2b2b2b"
    BG_DARKER = "#1e1e1e"
    BG_LIGHTER = "#3c3c3c"
    BG_HOVER = "#404040"
    BG_SELECTED = "#4a4a4a"

    TEXT_PRIMARY = "#d4d4d4"
    TEXT_SECONDARY = "#9d9d9d"
    TEXT_DISABLED = "#6e6e6e"

    BORDER_COLOR = "#555555"
    BORDER_LIGHT = "#666666"

    ACCENT_BLUE = "#0e639c"
    ACCENT_BLUE_HOVER = "#1177bb"

    # Spacing (OpenRV uses generous spacing)
    PADDING_SMALL = 6
    PADDING_MEDIUM = 8
    PADDING_LARGE = 12
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 12

    # Table settings
    TABLE_ROW_HEIGHT = 32
    TABLE_HEADER_HEIGHT = 28
    THUMBNAIL_SIZE = 80

    @staticmethod
    def get_main_stylesheet():
        """Get main application stylesheet matching OpenRV."""
        return f"""
            /* Global Settings */
            QWidget {{
                font-family: {RVStyle.FONT_FAMILY};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                color: {RVStyle.TEXT_PRIMARY};
                background-color: {RVStyle.BG_DARK};
            }}
            
            /* Main Window */
            QMainWindow {{
                background-color: {RVStyle.BG_DARKER};
            }}
            
            /* Tables */
            QTableView {{
                background-color: {RVStyle.BG_DARK};
                alternate-background-color: {RVStyle.BG_DARKER};
                gridline-color: {RVStyle.BORDER_COLOR};
                selection-background-color: {RVStyle.BG_SELECTED};
                selection-color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
            }}
            
            QTableView::item {{
                padding: {RVStyle.PADDING_SMALL}px;
                border: none;
            }}
            
            QTableView::item:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            QTableView::item:selected {{
                background-color: {RVStyle.BG_SELECTED};
            }}
            
            /* Table Headers */
            QHeaderView::section {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                padding: {RVStyle.PADDING_MEDIUM}px;
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-size: {RVStyle.FONT_SIZE_HEADER}pt;
                font-weight: bold;
            }}
            
            QHeaderView::section:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_MEDIUM}px {RVStyle.PADDING_LARGE}px;
                border-radius: 3px;
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                min-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {RVStyle.BG_HOVER};
                border-color: {RVStyle.BORDER_LIGHT};
            }}
            
            QPushButton:pressed {{
                background-color: {RVStyle.BG_SELECTED};
            }}
            
            QPushButton:disabled {{
                color: {RVStyle.TEXT_DISABLED};
                background-color: {RVStyle.BG_DARK};
            }}
            
            /* Primary Button (Comment, etc) */
            QPushButton#primaryButton {{
                background-color: {RVStyle.ACCENT_BLUE};
                color: white;
                font-weight: bold;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {RVStyle.ACCENT_BLUE_HOVER};
            }}
            
            /* ComboBox */
            QComboBox {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_SMALL}px {RVStyle.PADDING_MEDIUM}px;
                border-radius: 3px;
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                min-height: 22px;
            }}
            
            QComboBox:hover {{
                border-color: {RVStyle.BORDER_LIGHT};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {RVStyle.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                selection-background-color: {RVStyle.BG_SELECTED};
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
            }}
            
            /* LineEdit */
            QLineEdit {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_SMALL}px {RVStyle.PADDING_MEDIUM}px;
                border-radius: 3px;
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                min-height: 22px;
            }}
            
            QLineEdit:focus {{
                border-color: {RVStyle.ACCENT_BLUE};
            }}
            
            QLineEdit:read-only {{
                background-color: {RVStyle.BG_DARK};
                color: {RVStyle.TEXT_SECONDARY};
            }}
            
            /* TextEdit */
            QTextEdit, QTextBrowser {{
                background-color: {RVStyle.BG_DARKER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_MEDIUM}px;
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                line-height: 1.4;
            }}
            
            QTextEdit:focus {{
                border-color: {RVStyle.ACCENT_BLUE};
            }}
            
            /* Labels */
            QLabel {{
                color: {RVStyle.TEXT_PRIMARY};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                background: transparent;
            }}
            
            /* TabWidget */
            QTabWidget::pane {{
                border: 1px solid {RVStyle.BORDER_COLOR};
                background-color: {RVStyle.BG_DARK};
            }}
            
            QTabBar::tab {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_SECONDARY};
                padding: {RVStyle.PADDING_MEDIUM}px {RVStyle.PADDING_LARGE}px;
                border: 1px solid {RVStyle.BORDER_COLOR};
                border-bottom: none;
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                min-height: 28px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {RVStyle.BG_DARK};
                color: {RVStyle.TEXT_PRIMARY};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            /* ListView */
            QListView {{
                background-color: {RVStyle.BG_DARK};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
            }}
            
            QListView::item {{
                padding: {RVStyle.PADDING_MEDIUM}px;
                min-height: 28px;
            }}
            
            QListView::item:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            QListView::item:selected {{
                background-color: {RVStyle.BG_SELECTED};
            }}
            
            /* DockWidget */
            QDockWidget {{
                color: {RVStyle.TEXT_PRIMARY};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }}
            
            QDockWidget::title {{
                background-color: {RVStyle.BG_LIGHTER};
                padding: {RVStyle.PADDING_MEDIUM}px;
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-weight: bold;
            }}
            
            /* ScrollBar */
            QScrollBar:vertical {{
                background-color: {RVStyle.BG_DARK};
                width: 14px;
                border: none;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {RVStyle.BG_LIGHTER};
                min-height: 30px;
                border-radius: 3px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            QScrollBar:horizontal {{
                background-color: {RVStyle.BG_DARK};
                height: 14px;
                border: none;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {RVStyle.BG_LIGHTER};
                min-width: 30px;
                border-radius: 3px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                border: none;
                background: none;
            }}
            
            /* Splitter */
            QSplitter::handle {{
                background-color: {RVStyle.BORDER_COLOR};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            
            /* ToolButton */
            QToolButton {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_MEDIUM}px;
                border-radius: 3px;
            }}
            
            QToolButton:hover {{
                background-color: {RVStyle.BG_HOVER};
            }}
            
            QToolButton::menu-indicator {{
                image: none;
            }}
            
            /* Menu */
            QMenu {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 1px solid {RVStyle.BORDER_COLOR};
                font-size: {RVStyle.FONT_SIZE_BASE}pt;
            }}
            
            QMenu::item {{
                padding: {RVStyle.PADDING_MEDIUM}px 24px;
            }}
            
            QMenu::item:selected {{
                background-color: {RVStyle.BG_SELECTED};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {RVStyle.BORDER_COLOR};
                margin: 4px 0px;
            }}
        """

    @staticmethod
    def get_activity_panel_html_style():
        """Get HTML/CSS for activity panel content."""
        return f"""
            <style>
                body {{
                    font-family: {RVStyle.FONT_FAMILY};
                    font-size: {RVStyle.FONT_SIZE_BASE}pt;
                    color: {RVStyle.TEXT_PRIMARY};
                    background-color: {RVStyle.BG_DARKER};
                    line-height: 1.5;
                    margin: 0;
                    padding: {RVStyle.PADDING_MEDIUM}px;
                }}
                .activity-item {{
                    margin-bottom: {RVStyle.SPACING_LARGE}px;
                    padding: {RVStyle.PADDING_MEDIUM}px;
                    background-color: {RVStyle.BG_DARK};
                    border-left: 3px solid {RVStyle.BORDER_COLOR};
                    border-radius: 3px;
                }}
                .activity-header {{
                    font-weight: bold;
                    font-size: {RVStyle.FONT_SIZE_LARGE}pt;
                    margin-bottom: {RVStyle.SPACING_SMALL}px;
                    color: {RVStyle.TEXT_PRIMARY};
                }}
                .activity-meta {{
                    font-size: {RVStyle.FONT_SIZE_SMALL}pt;
                    color: {RVStyle.TEXT_SECONDARY};
                    margin-bottom: {RVStyle.SPACING_MEDIUM}px;
                }}
                .activity-body {{
                    font-size: {RVStyle.FONT_SIZE_BASE}pt;
                    color: {RVStyle.TEXT_PRIMARY};
                    margin-top: {RVStyle.SPACING_MEDIUM}px;
                }}
                .status-change {{
                    border-left-color: {RVStyle.ACCENT_BLUE};
                }}
                .comment {{
                    border-left-color: #6a9955;
                }}
                a {{
                    color: {RVStyle.ACCENT_BLUE};
                    text-decoration: none;
                }}
                a:hover {{
                    color: {RVStyle.ACCENT_BLUE_HOVER};
                    text-decoration: underline;
                }}
                img {{
                    max-width: 100%;
                    border-radius: 3px;
                    margin-top: {RVStyle.SPACING_MEDIUM}px;
                }}
            </style>
        """

    @staticmethod
    def apply_to_widget(widget):
        """Apply RV-style to a specific widget."""
        widget.setStyleSheet(RVStyle.get_main_stylesheet())

    @staticmethod
    def configure_table(table_view):
        """Configure table with RV-style settings."""
        # Row height
        table_view.verticalHeader().setDefaultSectionSize(RVStyle.TABLE_ROW_HEIGHT)

        # Header height
        table_view.horizontalHeader().setMinimumHeight(RVStyle.TABLE_HEADER_HEIGHT)

        # Alternating row colors
        table_view.setAlternatingRowColors(True)

        # Selection behavior
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Font
        font = QFont(RVStyle.FONT_FAMILY.split(',')[0], RVStyle.FONT_SIZE_BASE)
        table_view.setFont(font)

    @staticmethod
    def style_button_primary(button):
        """Style a button as primary action."""
        button.setObjectName("primaryButton")
        button.setMinimumHeight(28)
        font = QFont(RVStyle.FONT_FAMILY.split(',')[0], RVStyle.FONT_SIZE_BASE)
        font.setBold(True)
        button.setFont(font)

    @staticmethod
    def style_mode_toggle_button(button):
        """Style the mode toggle button."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {RVStyle.BG_LIGHTER};
                color: {RVStyle.TEXT_PRIMARY};
                border: 2px solid {RVStyle.BORDER_COLOR};
                padding: {RVStyle.PADDING_LARGE}px;
                border-radius: 4px;
                font-size: {RVStyle.FONT_SIZE_LARGE}pt;
                font-weight: bold;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {RVStyle.BG_HOVER};
                border-color: {RVStyle.ACCENT_BLUE};
            }}
        """)
