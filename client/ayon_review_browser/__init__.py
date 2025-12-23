from .version import __version__
from .src.views.main_window import ReviewBrowser
from .addon import TrayReviewAddon

__all__ = (
    "__version__",
    "ReviewBrowser",
    "TrayReviewAddon"
)
