"""Background worker for loading activity data."""

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class ActivityWorker(QThread):
    """Background worker for fetching and processing activity data."""

    text_ready = Signal(str, int)
    progress_update = Signal(int, int)  # loaded_count, total_count
    image_ready = Signal(object)  # Can be tuple or dict

    def __init__(self, data_service, version_id, task_id, path, fetch_id, status_colors=None, activity_manager=None):
        super().__init__()
        self.data_service = data_service
        self.version_id = version_id
        self.task_id = task_id
        self.path = path
        self.fetch_id = fetch_id
        self.status_colors = status_colors
        self.activity_manager = activity_manager
        self.cancelled = False

    def cancel(self):
        """Cancel the current operation."""
        self.cancelled = True

    def run(self):
        """Run the background worker to fetch activities."""
        try:
            loaded_count = 0
            total_count = 0

            def update_callback(data, update_type):
                if self.cancelled:
                    return

                nonlocal loaded_count, total_count

                if update_type == "text_ready":
                    self.text_ready.emit(data, self.fetch_id)
                elif update_type == "image_count":
                    total_count = data
                    self.progress_update.emit(0, total_count)
                elif update_type == "image_ready":
                    # Accept both 2-tuple and 3-tuple data
                    if isinstance(data, (list, tuple)):
                        if len(data) == 3:
                            file_id, img_tag, img_data = data
                        elif len(data) == 2:
                            file_id, img_tag = data
                            img_data = None
                        else:
                            return
                    else:
                        return

                    loaded_count += 1

                    self.progress_update.emit(loaded_count, total_count)
                    # Emit the tuple directly so img_tag is preserved for UI update
                    self.image_ready.emit(data)

            self.data_service.fetch_version_activities(
                self.version_id,
                task_id=self.task_id,
                path=self.path,
                status_colors=self.status_colors,
                update_callback=update_callback
            )
        except Exception as e:
            if not self.cancelled:
                self.text_ready.emit(f"<p>Error loading activities: {e}</p>", self.fetch_id)

