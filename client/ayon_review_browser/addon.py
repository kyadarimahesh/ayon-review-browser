import os
import logging
from ayon_core.addon import AYONAddon, ITrayAction
from ayon_api import get_server_api_connection
from .version import __version__

from ayon_applications import ApplicationManager


class TrayReviewAddon(AYONAddon, ITrayAction):
    label = "Reviewer"
    name = "trayreviewer"
    host_name = "bot_review_notes"
    version = __version__

    def initialize(self, settings):
        """Initialization of addon."""
        self._dialog = None

    def tray_init(self):
        return

    def run_rv_reviewer(self):
        """
        Launches OpenRV from AYON environment WITHOUT project/folder/task context.
        """
        app_manager = ApplicationManager()
        openrv_app = app_manager.find_latest_available_variant_for_group("openrv")
        if not openrv_app:
            raise RuntimeError(
                "No configured OpenRV found in"
                " Applications. Ask admin to configure it"
                " in ayon+settings://applications/applications/openrv."
                "\nProvide '-network' there as argument."
            )

        # Launch OpenRV without context
        openrv_app.launch(
            project_name=None,
            folder_path=None,
            task_name=None,
            start_last_workfile=False
        )

    def on_action_trigger(self):
        self.run_rv_reviewer()
