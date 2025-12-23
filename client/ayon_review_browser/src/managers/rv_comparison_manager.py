"""RV comparison manager for creating and managing version comparisons."""

import os
import re
from pathlib import Path

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class RVComparisonManager:
    """Manages RV version comparisons and stacks."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.comparison_stack_node = None  # Track active comparison stack
        self.comparison_layout_node = None  # Track active comparison layout

    def create_comparison_stack(self, old_row_data, new_row_data):
        """Create comparison stack and layout in RV."""
        try:
            import rv.commands as commands
            from ...api.rv.rv_api import RVAPI

            rv_api = RVAPI()
            rv_ops = self.main_window.rv_manager.get_rv_ops()

            if not rv_ops:
                QMessageBox.warning(self.main_window, "Error", "RV is not available.")
                return False

            old_rep_path = old_row_data.get('current_representation_path', '')
            old_ext = Path(old_rep_path).suffix.lower() if old_rep_path else None

            new_representations = new_row_data.get('representations', [])
            new_rep_path = None

            if old_ext:
                for rep in new_representations:
                    rep_path = rep.get('path', '')
                    if rep_path and Path(rep_path).suffix.lower() == old_ext:
                        new_rep_path = rep_path
                        break

            if not new_rep_path and new_representations:
                new_rep_path = new_representations[0].get('path', '')

            if not new_rep_path:
                QMessageBox.warning(self.main_window, "Error", "No representations available for new version.")
                return False

            old_load_path = self._prepare_load_path(old_rep_path)
            new_load_path = self._prepare_load_path(new_rep_path)

            current_source_node = rv_ops.get_current_view_source()
            if current_source_node:
                current_source_group = commands.nodeGroup(current_source_node)
                commands.deleteNode(current_source_group)

            old_nodes = commands.addSourcesVerbose([[old_load_path]])
            new_nodes = commands.addSourcesVerbose([[new_load_path]])

            if not old_nodes or not new_nodes:
                QMessageBox.warning(self.main_window, "Error", "Failed to load versions.")
                return False

            old_source_group = commands.nodeGroup(old_nodes[0])
            new_source_group = commands.nodeGroup(new_nodes[0])

            entity_path = old_row_data.get('path', 'unknown')
            # Remove version from path if present
            if '/' in entity_path:
                path_parts = entity_path.split('/')
                if path_parts[-1].startswith('v') and path_parts[-1][1:].isdigit():
                    entity_path = '/'.join(path_parts[:-1])

            old_version = old_row_data.get('current_version', 'v001')
            new_version = new_row_data.get('current_version', 'v002')
            comparison_name = f"{entity_path} ({old_version} vs {new_version})"

            # Create stack
            stack_node = commands.newNode("RVStackGroup")
            commands.setNodeInputs(stack_node, [old_source_group, new_source_group])
            commands.setStringProperty(f"{stack_node}.ui.name", [comparison_name])
            self.comparison_stack_node = stack_node

            # Create layout
            layout_node = commands.newNode("RVLayoutGroup")
            commands.setNodeInputs(layout_node, [old_source_group, new_source_group])
            commands.setStringProperty(f"{layout_node}.layout.mode", ["packed"])
            commands.setStringProperty(f"{layout_node}.ui.name", [comparison_name])
            self.comparison_layout_node = layout_node

            rv_ops.source_mapping[old_source_group] = {
                'path': old_rep_path,
                'version_id': old_row_data.get('version_id'),
                'row_data': old_row_data,
                'all_representations': old_row_data.get('representations', [])
            }

            rv_ops.source_mapping[new_source_group] = {
                'path': new_rep_path,
                'version_id': new_row_data.get('version_id'),
                'row_data': new_row_data,
                'all_representations': new_row_data.get('representations', [])
            }

            commands.setViewNode(stack_node)
            commands.setFrame(1)

            # No need to use it for now for UX reasons
            # self._show_comparison_feedback(old_version, new_version, old_ext or Path(new_rep_path).suffix)

            print(f"✅ Created comparison: {comparison_name}")
            return True

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to create comparison: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _prepare_load_path(self, path):
        """Prepare path for RV loading (handle sequences)."""
        ext = Path(path).suffix.lower()

        if ext in ['.exr', '.jpg', '.jpeg', '.png', '.tiff', '.dpx']:
            folder = os.path.dirname(path)
            filename = os.path.basename(path)

            match = re.match(r"^(.*?)(\d+)(\.[^.]+)$", filename)
            if match and os.path.exists(folder):
                prefix, frame_str, ext = match.groups()
                frames = []

                for f in os.listdir(folder):
                    m = re.match(rf"^{re.escape(prefix)}(\d+){re.escape(ext)}$", f)
                    if m:
                        frames.append(int(m.group(1)))

                if frames:
                    start, end = min(frames), max(frames)
                    return os.path.join(folder, f"{prefix}{start}-{end}#{ext}")

        return path

    def _show_comparison_feedback(self, old_version, new_version, rep_type):
        """Show visual feedback about the comparison."""
        msg = QMessageBox(self.main_window)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Comparison Created")
        msg.setText(f"Comparing {old_version} vs {new_version}")
        msg.setInformativeText(
            f"Representation: {rep_type}\n\n"
            f"• Use ( ) keys to switch between versions\n"
            f"• Stack view shows overlay comparison\n"
            f"• Layout view shows side-by-side\n\n"
            f"Click 'Exit Comparison' button to return to single view."
        )

        exit_btn = msg.addButton("Exit Comparison", QMessageBox.ActionRole)
        ok_btn = msg.addButton("OK", QMessageBox.AcceptRole)
        msg.setDefaultButton(ok_btn)

        msg.exec_()

        if msg.clickedButton() == exit_btn:
            self.exit_comparison_mode()

    def exit_comparison_mode(self):
        """Exit comparison mode and return to single view."""
        try:
            import rv.commands as commands

            if self.comparison_stack_node:
                commands.deleteNode(self.comparison_stack_node)
                self.comparison_stack_node = None

            if self.comparison_layout_node:
                commands.deleteNode(self.comparison_layout_node)
                self.comparison_layout_node = None

            QMessageBox.information(self.main_window, "Comparison Exited", "Returned to single view mode.")
            return True

        except Exception as e:
            QMessageBox.warning(self.main_window, "Error", f"Failed to exit comparison: {str(e)}")
            return False

