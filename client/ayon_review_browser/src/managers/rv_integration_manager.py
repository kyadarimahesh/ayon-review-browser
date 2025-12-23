try:
    from PySide2.QtCore import *
except ImportError:
    from qtpy.QtCore import *


class RVIntegrationManager:
    """Manager for all RV-related functionality and integration."""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self._rv_ops = None

    def initialize(self):
        """Initialize RV integration components."""
        self._setup_rv_event_listener()
        self.setup_rv_operations_callback()

    def _setup_rv_event_listener(self):
        """Setup listener for RV asset loading events."""
        try:
            import rv.commands
            rv.commands.bind("default", "global", "ayon_asset_loaded",
                             self._on_rv_asset_loaded, "Handle AYON asset loaded")
        except Exception as e:
            print(f"Could not setup RV event listener: {e}")

    def _on_rv_asset_loaded(self, event):
        """Handle RV asset loaded event."""
        try:
            import json
            event_data = json.loads(event.contents())

            row_data = {
                'version_id': event_data['version_id'],
                'task_id': event_data['task_id'],
                'product': event_data['product'],
                'folder_path': event_data['folder_path'],
                'project_name': event_data['project_name']
            }

            self.parent.fetch_and_display_activities(row_data, from_rv=True)
            QTimer.singleShot(500, self._monitor_existing_rv_sources)
        except Exception as e:
            print(f"Error handling RV asset loaded event: {e}")

    def setup_rv_operations_callback(self):
        """Setup RV operations callback for activity updates."""
        try:
            if not self._rv_ops:
                from ....api.rv.rv_operations import RVOperations
                self._rv_ops = RVOperations()

            self._rv_ops.set_version_change_callback(self.on_rv_version_changed)

            if not self._rv_ops._monitoring:
                self._rv_ops.start_source_monitoring()

            self._monitor_existing_rv_sources()
        except Exception as e:
            print(f"Could not setup RV operations callback: {e}")

    def on_rv_version_changed(self, version_id, row_data):
        """Handle RV version change callback."""
        if not version_id and row_data.get('representation_id'):
            try:
                import ayon_api
                project_name = self.parent.filter_controller.get_current_project()
                if project_name:
                    rep = ayon_api.get_representation_by_id(project_name, row_data['representation_id'])
                    if rep:
                        version_id = rep.get('versionId')
                        row_data['version_id'] = version_id
            except Exception as e:
                print(f"Could not resolve version_id: {e}")

        if not version_id and row_data.get('path'):
            try:
                project_name = self.parent.filter_controller.get_current_project()
                if project_name:
                    file_path = row_data['path']
                    row_data['version_id'] = 'path_based'
                    row_data['display_info'] = f"File: {file_path}"
                    version_id = 'path_based'
            except Exception as e:
                print(f"Could not resolve version from path: {e}")

        if version_id:
            self.parent.activity_manager.fetch_and_display_activities(row_data, from_rv=True)

    def _monitor_existing_rv_sources(self):
        """Monitor existing RV sources that were loaded via Loader."""
        try:
            import rv.commands
            from ayon_openrv.api.pipeline import parse_container

            if not self._rv_ops:
                return

            try:
                source_nodes = rv.commands.nodesOfType("RVSourceGroup")
            except Exception:
                return

            for source in source_nodes:
                try:
                    source_group = source
                    if source_group and source_group not in self._rv_ops.source_mapping:
                        file_source = None

                        try:
                            all_file_sources = rv.commands.nodesOfType("RVFileSource")
                            for fs in all_file_sources:
                                fs_group = rv.commands.nodeGroup(fs)
                                if fs_group == source_group:
                                    file_source = fs
                                    break
                        except Exception:
                            pass

                        if not file_source:
                            file_source = source_group

                        if file_source:
                            container = parse_container(file_source)
                            if container:
                                self._rv_ops.source_mapping[source_group] = {
                                    'path': container.get('objectName', ''),
                                    'version_id': None,
                                    'representation_id': container.get('representation'),
                                    'row_data': {'representation_id': container.get('representation')}
                                }
                            else:
                                try:
                                    media_info = rv.commands.sourceMediaInfo(file_source)
                                    if media_info and len(media_info) > 0:
                                        media_path = media_info[0]
                                        self._rv_ops.source_mapping[source_group] = {
                                            'path': media_path,
                                            'version_id': None,
                                            'representation_id': None,
                                            'row_data': {'path': media_path}
                                        }
                                except Exception:
                                    pass
                except Exception:
                    pass
        except Exception:
            pass

    def get_rv_ops(self):
        """Get RV operations instance."""
        return self._rv_ops

    def has_rv_sources(self):
        """Check if RV has any sources loaded."""
        return self._rv_ops and self._rv_ops.source_mapping