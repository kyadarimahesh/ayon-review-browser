"""
RV Operations Module

Comprehensive RV operations for media loading, session management, and annotations.
"""

import os
import platform
import re
import logging
from pathlib import Path
from datetime import datetime

try:
    from PySide2.QtCore import QTimer
except ImportError:
    from qtpy.QtCore import QTimer

try:
    import rv
    from rv import commands
    from pymu import MuSymbol
except ImportError:
    pass

from .rv_source_events import RVSourceEvents
from .rv_registry import set_rv_operations


class RVOperations:
    def __init__(self):
        self.current_session = None
        self.current_source = None
        self.source_change_callback = None
        self.frame_change_callback = None
        self.version_change_callback = None
        self.source_mapping = {}  # Maps source nodes to media paths and version data
        self.current_version_id = None  # Cache current version_id to avoid unnecessary API calls
        self._monitoring = False
        self.source_events = RVSourceEvents()  # New source events handler
        self.activity_update_timer = QTimer()
        self.activity_update_timer.setSingleShot(True)
        self.activity_update_timer.timeout.connect(self.update_activity_for_current_frame)
        # Register this instance globally for AYON integration
        set_rv_operations(self)

    def set_version_change_callback(self, callback):
        """Set callback for version changes."""
        self.version_change_callback = callback

    def set_frame_change_callback(self, callback):
        """Set callback for frame changes."""
        self.frame_change_callback = callback

    def load_media_with_versions(self, media_data, clear_session=True):
        """Load media with version information into RV."""
        if not media_data:
            return False

        source_groups = []
        rv_files_loaded = 0

        if clear_session:
            rv.commands.clearSession()
            self.source_mapping.clear()

        # Load each media item as individual source
        for i, media_item in enumerate(media_data):
            path = media_item['path']
            version_id = media_item.get('version_id')
            row_data = media_item.get('row_data', {})
            all_representations = media_item.get('all_representations', [])
            ext = Path(path).suffix.lower()

            if ext == '.rv':
                try:
                    sources_before = set(rv.commands.nodesOfType("RVSourceGroup"))
                    rv.commands.addSources([path])

                    # Wait for RV to load
                    from PySide2.QtCore import QEventLoop, QTimer
                    loop = QEventLoop()
                    timer = QTimer()
                    timer.setSingleShot(True)
                    timer.timeout.connect(loop.quit)

                    max_attempts = 20
                    attempt = 0
                    new_sources = set()

                    while attempt < max_attempts:
                        timer.start(100)
                        loop.exec_()
                        sources_after = set(rv.commands.nodesOfType("RVSourceGroup"))
                        new_sources = sources_after - sources_before
                        if new_sources:
                            break
                        attempt += 1

                    # Read version_id from each source's AYON metadata
                    for src_group in new_sources:
                        source_groups.append(src_group)
                        
                        src_version_id = None
                        try:
                            all_sources = rv.commands.nodesOfType("RVSource")
                            group_sources = [s for s in all_sources if rv.commands.nodeGroup(s) == src_group]
                            
                            if group_sources:
                                source = group_sources[0]
                                if rv.commands.propertyExists(f"{source}.ayon.version_id"):
                                    src_version_id = rv.commands.getStringProperty(f"{source}.ayon.version_id")[0]
                        except Exception as e:
                            print(f"Error reading version_id from {src_group}: {e}")
                        
                        self.source_mapping[src_group] = {
                            'path': path,
                            'version_id': src_version_id,
                            'row_data': row_data,
                            'all_representations': all_representations
                        }

                    rv_files_loaded += 1
                except Exception as e:
                    print(f"Error loading RV file: {str(e)}")
                    return False

            elif ext in ['.mov', '.mp4']:
                nodes = rv.commands.addSourcesVerbose([[path]])
                if nodes:
                    src_group = rv.commands.nodeGroup(nodes[0])
                    if src_group:
                        source_groups.append(src_group)
                        self.source_mapping[src_group] = {
                            'path': path,
                            'version_id': version_id,
                            'row_data': row_data,
                            'all_representations': all_representations
                        }

            elif ext in ['.exr', '.jpg', '.jpeg', '.png', '.tiff', '.dpx']:
                sequence_path = self.get_sequence_pattern(path)
                if sequence_path:
                    nodes = rv.commands.addSourcesVerbose([[sequence_path]])
                    if nodes:
                        src_group = rv.commands.nodeGroup(nodes[0])
                        if src_group:
                            source_groups.append(src_group)
                            self.source_mapping[src_group] = {
                                'path': path,
                                'version_id': version_id,
                                'row_data': row_data,
                                'all_representations': all_representations
                            }

        if source_groups:
            rv.commands.setViewNode(source_groups[0])

        rv.commands.setFrame(1)
        self.start_source_monitoring()
        self.current_version_id = None
        self.update_activity_for_current_frame()

        return len(source_groups) > 0 or rv_files_loaded > 0

    def start_source_monitoring(self):
        """Start monitoring for frame changes and source changes."""
        if self._monitoring:
            return

        self._monitoring = True

        try:
            self.source_events.add_source_change_callback(self._on_source_changed)
            self.source_events.add_view_change_callback(self._on_view_changed)
            self.source_events.add_stack_change_callback(self._on_stack_change)
            self.source_events.add_frame_change_callback(self._on_frame_changed)
            self.source_events.start_monitoring()
        except Exception as e:
            print(f"Error binding events: {e}")

    @staticmethod
    def get_current_view_source():
        """Get current TOP visible source from stack."""
        try:
            sources = rv.commands.sourcesAtFrame(rv.commands.frame())
            # sources[0] is always the TOP/visible layer in RV stack
            current_source = sources[0] if sources and len(sources) > 0 else None
            return current_source
        except Exception as e:
            print(f"Error getting sources: {e}")
            return None

    def _debounced_update(self):
        """Debounced version of update_activity_for_current_frame."""
        self.activity_update_timer.start(200)  # 200ms delay

    def update_activity_for_current_frame(self):
        """Update activity panel for current frame - only if version_id changed."""
        current_source_node = self.get_current_view_source()

        if current_source_node and self.version_change_callback:
            source_group = rv.commands.nodeGroup(current_source_node)

            if source_group in self.source_mapping:
                source_info = self.source_mapping[source_group]
                version_id = source_info.get('version_id')
                row_data = source_info.get('row_data', {})
                all_representations = source_info.get('all_representations', [])
                loaded_rep_path = source_info.get('path')

                row_data_with_reps = row_data.copy()
                if all_representations:
                    row_data_with_reps['representations'] = all_representations

                row_data_with_reps['current_representation_path'] = loaded_rep_path

                if version_id != self.current_version_id:
                    self.current_version_id = version_id
                    self.version_change_callback(version_id, row_data_with_reps)

    def clear_activity_panel(self):
        """Clear activity panel when attaching to browser."""
        if self.version_change_callback:
            self.version_change_callback(None, {})

    def sync_with_current_view(self):
        """Sync activity panel with current ViewNode when detaching to RV."""
        self.current_version_id = None
        self.update_activity_for_current_frame()

    def _on_frame_changed(self, current_frame, event):
        """Internal callback for frame changes."""
        if not self._monitoring:
            return

        self._debounced_update()

        if self.frame_change_callback:
            self.frame_change_callback(current_frame)

    def _on_source_changed(self, source, event):
        """Handle source change events."""
        self._debounced_update()
        if self.source_change_callback:
            self.source_change_callback(source, event)

    def _on_view_changed(self, source, event):
        """Handle view change events."""
        self._debounced_update()

    def _on_stack_change(self, direction, source, event):
        """Handle stack navigation - update activity panel for TOP visible source."""
        self.current_version_id = None
        self._debounced_update()

    def switch_representation(self, new_path, row_data, representations):
        """Switch the current source to a different representation."""
        try:
            # Get current source
            current_source_node = self.get_current_view_source()
            if not current_source_node:
                return False

            source_group = rv.commands.nodeGroup(current_source_node)
            if not source_group:
                return False

            # Get current frame to restore later
            current_frame = rv.commands.frame()

            # Determine the type of media and prepare path
            ext = Path(new_path).suffix.lower()

            if ext in ['.exr', '.jpg', '.jpeg', '.png', '.tiff', '.dpx']:
                # For image sequences, detect pattern
                load_path = self.get_sequence_pattern(new_path)
            else:
                # For video files, use path directly
                load_path = new_path

            # Delete the old source
            try:
                rv.commands.deleteNode(source_group)
            except Exception as e:
                print(f"⚠️ Error deleting old source: {e}")

            # Load new representation
            nodes = rv.commands.addSourcesVerbose([[load_path]])
            if not nodes:
                return False

            new_source_group = rv.commands.nodeGroup(nodes[0])

            # Update source mapping with new representation info
            version_id = row_data.get('version_id')
            all_representations = row_data.get('representations', representations)

            self.source_mapping[new_source_group] = {
                'path': new_path,
                'version_id': version_id,
                'row_data': row_data,
                'all_representations': all_representations
            }

            # Set view to new source
            rv.commands.setViewNode(new_source_group)

            # Try to restore frame position
            try:
                rv.commands.setFrame(current_frame)
            except:
                rv.commands.setFrame(1)

            print(f"✅ Successfully switched to representation: {new_path}")
            return True

        except Exception as e:
            print(f"❌ Error switching representation: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize incoming path for Linux environment."""
        if path.startswith("\\\\"):
            path = path.replace("\\\\", "/")
            path = path.replace("\\", "/")
        else:
            path = path.replace("\\", "/")
        return path

    def get_sequence_pattern(self, path: str) -> str:
        """Detects image sequence and returns normalized sequence string."""
        path = self.normalize_path(path)
        folder = os.path.dirname(path)
        filename = os.path.basename(path)

        match = re.match(r"^(.*?)(\d+)(\.[^.]+)$", filename)
        if not match:
            return path

        prefix, frame_str, ext = match.groups()

        # Collect frame numbers
        frames = []
        for f in os.listdir(folder):
            m = re.match(rf"^{re.escape(prefix)}(\d+){re.escape(ext)}$", f)
            if m:
                frames.append(int(m.group(1)))

        if not frames:
            return path

        start, end = min(frames), max(frames)
        return os.path.join(folder, f"{prefix}{start}-{end}#{ext}")

    def export_annotations(self, output_dir=None):
        """Export annotations to temp files and return paths."""
        from pathlib import Path
        import tempfile

        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(tempfile.gettempdir()) / "rv_annotations" / timestamp
        else:
            # Validate and sanitize output directory path
            try:
                output_dir = Path(output_dir).resolve()
                # Ensure path is within safe boundaries (basic check)
                if ".." in str(output_dir):
                    raise ValueError("Path traversal detected in output directory")
            except (OSError, ValueError) as e:
                print(f"Invalid output directory: {e}")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(tempfile.gettempdir()) / "rv_annotations" / timestamp

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Error creating output directory: {e}")
            return []

        print("[DEBUG] Starting export_annotations")
        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            import tempfile
            output_dir = Path(tempfile.gettempdir()) / "rv_annotations" / timestamp
            print(f"[DEBUG] No output_dir provided, using {output_dir}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[DEBUG] Output directory created: {output_dir}")

        try:
            # Get the currently active source node
            current_source_node = self.get_current_view_source()
            print(f"[DEBUG] Current source node: {current_source_node}")
            if not current_source_node:
                print("[DEBUG] No active source found")
                return []

            # Get the group for the current source
            current_source_group = rv.commands.nodeGroup(current_source_node)
            print(f"[DEBUG] Current source group: {current_source_group}")

            # Get all annotated frames
            all_annotated_frames = self.get_annotated_frames() if hasattr(self, 'get_annotated_frames') else []
            print(f"[DEBUG] All annotated frames: {all_annotated_frames}")
            if not all_annotated_frames:
                print("[DEBUG] No annotated frames found")
                return []

            # Filter frames that belong to the current source
            annotated_frames = []
            for frame in all_annotated_frames:
                sources = rv.commands.sourcesAtFrame(frame)
                print(f"[DEBUG] Frame {frame} sources: {sources}")
                if sources:
                    group = rv.commands.nodeGroup(sources[0])
                    print(f"[DEBUG] Frame {frame} group: {group}")
                    if group == current_source_group:
                        annotated_frames.append(frame)
            print(f"[DEBUG] Annotated frames for current source: {annotated_frames}")
            if not annotated_frames:
                print("[DEBUG] No annotated frames found for current version/source")
                return []

            # Unmark all frames first to avoid exporting frames from other sources
            all_marked_frames = rv.commands.markedFrames() if hasattr(rv.commands, 'markedFrames') else []
            print(f"[DEBUG] Unmarking all previously marked frames: {all_marked_frames}")
            for frame in all_marked_frames:
                rv.commands.markFrame(frame, False)
            rv.commands.redraw()
            print("[DEBUG] All frames unmarked before marking current source frames")

            # Mark only annotated frames for current source
            for frame in annotated_frames:
                print(f"[DEBUG] Marking frame {frame}")
                rv.commands.markFrame(frame, True)
            rv.commands.redraw()
            print("[DEBUG] Frames marked and redraw called")

            # Batch export marked frames
            export_pattern = str(output_dir / "annotation.####.jpg")
            print(f"[DEBUG] Export pattern: {export_pattern}")
            exportframes = MuSymbol("export_utils.exportMarkedFrames")
            exportframes(export_pattern)
            print("[DEBUG] Exported marked frames")

            import time
            expected_files = len(annotated_frames)
            exported_files = []
            max_wait = 20  # seconds
            waited = 0
            while waited < max_wait:
                exported_files = list(output_dir.glob("annotation.*.jpg"))
                print(f"[DEBUG] Exported files so far: {exported_files}")
                if len(exported_files) >= expected_files:
                    print("[DEBUG] All expected files exported")
                    break
                time.sleep(0.5)
                waited += 0.5

            # Unmark frames after export
            for frame in annotated_frames:
                print(f"[DEBUG] Unmarking frame {frame}")
                rv.commands.markFrame(frame, False)
            rv.commands.redraw()
            print("[DEBUG] Frames unmarked and redraw called")

            result_files = [str(f) for f in exported_files]
            print(f"[DEBUG] Returning exported files: {result_files}")
            return result_files

        except Exception as e:
            print(f"[DEBUG] Error exporting annotations: {e}")
            import logging
            logging.error(f"Error exporting annotations: {e}")
            return []

    @staticmethod
    def get_annotated_frames():
        """
        Return a list of frame numbers that have annotations using RV's API.
        This matches the logic from project1, which marks annotated frames via MuSymbol('rvui.markAnnotatedFrames').
        """
        try:
            # Mark annotated frames in RV (side effect: marks them in the session)
            markframes = MuSymbol('rvui.markAnnotatedFrames')
            markframes()
            # Retrieve marked frames
            marked_frames = rv.commands.markedFrames()
            return marked_frames if marked_frames else []
        except Exception as e:
            logging.error(f"Error getting annotated frames: {e}")
            return []
