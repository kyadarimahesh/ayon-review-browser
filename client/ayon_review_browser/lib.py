"""Library utilities for Review Browser."""

from contextlib import contextmanager


@contextmanager
def qt_app_context():
    """Qt application context manager.
    
    Ensures Qt application exists before showing windows.
    """
    try:
        from qtpy.QtWidgets import QApplication
    except ImportError:
        from PySide2.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app
