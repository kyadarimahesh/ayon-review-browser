"""Helper tools for showing Review Browser."""

from ayon_review_browser.lib import qt_app_context


class ReviewBrowserHelper:
    """Create and cache Review Browser window in memory."""

    def __init__(self, parent=None):
        self._parent = parent
        self._review_browser_tool = None

    def get_review_browser_tool(self, parent):
        """Create, cache and return Review Browser window."""
        if self._review_browser_tool is None:
            from ayon_review_browser.src.views.main_window import ReviewBrowser
            
            review_browser_window = ReviewBrowser(parent=parent or self._parent)
            self._review_browser_tool = review_browser_window

        return self._review_browser_tool

    def show_review_browser(self, parent=None):
        """Show Review Browser window."""
        with qt_app_context():
            review_browser_tool = self.get_review_browser_tool(parent)
            review_browser_tool.show()
            review_browser_tool.raise_()
            review_browser_tool.activateWindow()
            review_browser_tool.showNormal()


class _SingletonPoint:
    """Singleton access to Review Browser."""
    helper = None

    @classmethod
    def _create_helper(cls):
        if cls.helper is None:
            cls.helper = ReviewBrowserHelper()

    @classmethod
    def show_review_browser(cls, parent=None):
        cls._create_helper()
        cls.helper.show_review_browser(parent)

    @classmethod
    def get_review_browser_tool(cls, parent=None):
        cls._create_helper()
        return cls.helper.get_review_browser_tool(parent)


# Public API
def show_review_browser(parent=None):
    """Show Review Browser with singleton pattern.
    
    Args:
        parent: Parent widget (typically RV main window)
        
    Returns:
        ReviewBrowser: The browser window
    """
    _SingletonPoint.show_review_browser(parent)
    return _SingletonPoint.get_review_browser_tool(parent)
