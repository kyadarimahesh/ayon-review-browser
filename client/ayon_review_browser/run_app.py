#!/usr/bin/env python3
"""
Entry point script to run the AYON Review Browser application.
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from src.views.main_window import ReviewBrowser


def main():
    app = QApplication(sys.argv)
    window = ReviewBrowser()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()