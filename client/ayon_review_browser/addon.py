"""Review Browser addon for AYON.

Provides standalone review browser for viewing and managing
review submissions across projects.
"""
from ayon_core.addon import AYONAddon, ITrayAction
from ayon_applications import ApplicationManager

from .version import __version__


class ReviewBrowserAddon(AYONAddon, ITrayAction):
    """Review Browser addon for AYON."""

    name = "ayon_review_browser"
    version = __version__
    label = "Review with OpenRV"

    def initialize(self, settings):
        """Initialize addon with settings."""
        pass

    def connect_with_addons(self, enabled_addons):
        """Connect with other addons."""
        pass

    def tray_init(self):
        """Initialize tray integration."""
        pass

    def tray_start(self):
        """Start addon logic in tray."""
        pass

    def tray_exit(self):
        """Cleanup addon resources."""
        pass

    def on_action_trigger(self):
        """Launch OpenRV with Review Browser from tray."""
        app_manager = ApplicationManager()
        openrv_app = app_manager.find_latest_available_variant_for_group("openrv")

        if not openrv_app:
            raise RuntimeError(
                "OpenRV not configured. "
                "Configure in ayon+settings://applications/applications/openrv"
            )

        openrv_app.launch(
            project_name=None,
            folder_path=None,
            task_name=None,
            start_last_workfile=False
        )
