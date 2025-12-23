"""Representation manager for handling representation switching and display."""

from pathlib import Path

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class RepresentationManager:
    """Manages representation switching and UI updates."""

    def __init__(self, main_window):
        self.main_window = main_window

    def update_representations_tab(self, row_data, panel_mode):
        """Update representations tab with buttons for all available representations."""
        # Get the representations layout
        rep_layout = self.main_window.activity_ui.representationsTabLayout

        # Clear existing widgets (except the vertical spacer at the end)
        while rep_layout.count() > 0:
            item = rep_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                # Don't delete spacer, we'll re-add it
                pass

        # Get representations from row_data
        representations = row_data.get('representations', [])
        # Use separate key for currently loaded representation path (not entity path)
        current_rep_path = row_data.get('current_representation_path', '')

        if not representations:
            # Add a label indicating no representations
            no_rep_label = QLabel("No representations available")
            no_rep_label.setAlignment(Qt.AlignCenter)
            rep_layout.addWidget(no_rep_label)
        else:
            # Group representations by extension/name
            rep_by_name = {}
            for rep in representations:
                path = rep.get('path', '')
                # Extract a meaningful name from the path
                if path:
                    ext = Path(path).suffix.lower()
                    basename = Path(path).stem
                    # Use extension as key, or create a descriptive name
                    rep_name = ext if ext else basename
                    if rep_name not in rep_by_name:
                        rep_by_name[rep_name] = []
                    rep_by_name[rep_name].append(rep)

            # Create a button for each representation type
            for rep_name, reps in rep_by_name.items():
                button = QPushButton(rep_name)
                button.setCheckable(True)
                button.setProperty('representations', reps)
                button.setProperty('row_data', row_data)

                # Check if this representation is currently loaded
                is_current = self._is_current_representation(reps, current_rep_path)

                # Disable button if representation name contains .rv
                is_rv_file = '.rv' in rep_name.lower()
                if is_rv_file:
                    button.setEnabled(False)
                    button.setToolTip("RV session files cannot be switched")

                # Highlight the currently loaded representation
                if is_current:
                    button.setChecked(True)
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            font-weight: bold;
                            border: 2px solid #45a049;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                else:
                    button.setChecked(False)
                    button.setStyleSheet("")

                # Connect button click to switch representation (only if not .rv)
                if not is_rv_file:
                    button.clicked.connect(
                        lambda checked=False, r=reps, rd=row_data, pm=panel_mode:
                        self.on_representation_clicked(r, rd, pm)
                    )
                rep_layout.addWidget(button)

        # Add vertical spacer at the end to push buttons to top
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        rep_layout.addItem(vertical_spacer)

    def _is_current_representation(self, reps, current_rep_path):
        """Check if any of the representations match the current loaded path."""
        if not current_rep_path:
            return False

        for rep in reps:
            rep_path = rep.get('path', '')
            # Normalize both paths for comparison
            if rep_path and current_rep_path:
                normalized_rep = Path(rep_path).as_posix()
                normalized_current = Path(current_rep_path).as_posix()

                # Handle sequence pattern matching
                if '#' in normalized_current and '.' in normalized_current:
                    import re
                    seq_match = re.match(r'(.+\.)\d+-\d+#(\..+)$', normalized_current)
                    if seq_match:
                        base_part, ext_part = seq_match.groups()
                        rep_pattern = re.match(r'(.+\.)\d+(\..+)$', normalized_rep)
                        if rep_pattern:
                            rep_base, rep_ext = rep_pattern.groups()
                            if base_part == rep_base and ext_part == rep_ext:
                                return True

                # Direct path comparison as fallback
                if normalized_rep == normalized_current:
                    return True

        return False

    def on_representation_clicked(self, representations, row_data, panel_mode):
        """Handle representation button click to switch representation in RV."""
        if not representations:
            return

        # Only allow switching in RV mode
        if panel_mode != 'RV_MODE':
            QMessageBox.information(
                self.main_window,
                "RV Mode Required",
                "Representation switching is only available when viewing in RV.\nPlease open the version in RV first."
            )
            return

        # Get the first representation (they're grouped by extension)
        new_rep = representations[0]
        new_path = new_rep.get('path', '')

        if not new_path:
            QMessageBox.warning(self.main_window, "Error", "No valid path for this representation.")
            return

        # Get RV operations
        rv_ops = self.main_window.rv_manager.get_rv_ops()
        if not rv_ops:
            QMessageBox.warning(self.main_window, "Error", "RV is not available.")
            return

        try:
            # Switch representation in RV
            success = rv_ops.switch_representation(new_path, row_data, representations)

            if success:
                # Update the current_representation_path (NOT the entity path!)
                row_data['current_representation_path'] = new_path

                # Refresh the representations tab to update highlighting
                self.update_representations_tab(row_data, panel_mode)

                return True
            else:
                QMessageBox.warning(self.main_window, "Error", "Failed to switch representation in RV.")
                return False
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error switching representation: {str(e)}")
            return False

