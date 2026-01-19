#!/usr/bin/env python3
"""
Entry point script to run the AYON Review Browser application.
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add activity panel path
activity_panel_path = os.path.join(os.path.dirname(current_dir), '..', '..', 'ayon-activity-panel', 'client')
activity_panel_path = os.path.abspath(activity_panel_path)
if os.path.exists(activity_panel_path):
    sys.path.insert(0, activity_panel_path)

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from ayon_core.style import load_stylesheet, get_app_icon_path
except ImportError:
    load_stylesheet = None
    get_app_icon_path = None

from src.views.main_window import ReviewBrowser

os.environ.setdefault("AYON_SERVER_URL", "http://localhost:5000")
os.environ.setdefault("AYON_API_KEY", "a63d0afa350bf72b193ee2452ec2b3f1b4a9c8d76af216e1cf5aad4e90af9ab5")


def main():
    app = QApplication(sys.argv)

    # Apply AYON stylesheet
    if load_stylesheet:
        app.setStyleSheet(load_stylesheet())

    # Set app icon
    if get_app_icon_path:
        app.setWindowIcon(QIcon(get_app_icon_path()))

    window = ReviewBrowser()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
