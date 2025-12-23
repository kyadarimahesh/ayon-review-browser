"""Version comparison dialog for asking user preference."""

try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class VersionComparisonDialog:
    """Handles version comparison preference dialog."""

    def __init__(self, main_window):
        self.main_window = main_window
        # Session-only comparison preference (resets on app restart)
        self.comparison_preference = None  # None = ask, True = always compare, False = always replace

    def ask_comparison_preference(self, current_version, new_version):
        """Ask user if they want to compare versions (with session memory)."""
        print(f"\n🔔 _ask_comparison_preference called")
        print(f"   Current: {current_version}, New: {new_version}")
        print(f"   Session preference cached: {self.comparison_preference}")

        if self.comparison_preference is not None:
            print(f"   → Returning cached preference: {self.comparison_preference}")
            return self.comparison_preference

        print(f"   → Showing dialog to user...")
        dialog = QMessageBox(self.main_window)
        dialog.setWindowTitle("Compare Versions?")
        dialog.setText(f"Do you want to compare {new_version} with {current_version}?")
        dialog.setInformativeText("Yes: Create side-by-side comparison\nNo: Replace current version")
        dialog.setIcon(QMessageBox.Question)

        yes_btn = dialog.addButton("Compare", QMessageBox.YesRole)
        no_btn = dialog.addButton("Replace", QMessageBox.NoRole)
        cancel_btn = dialog.addButton("Cancel", QMessageBox.RejectRole)

        dialog.setDefaultButton(yes_btn)
        dialog.setEscapeButton(cancel_btn)  # Set Cancel as escape button

        checkbox = QCheckBox("Don't ask again this session", dialog)
        dialog.setCheckBox(checkbox)

        # Set minimum width to prevent button text cutoff
        dialog.setMinimumWidth(450)

        result = dialog.exec_()
        print(f"   Dialog exec_() result: {result}")
        print(f"   QDialog.Rejected={QDialog.Rejected}, QDialog.Accepted={QDialog.Accepted}")

        # PySide2: Check which button was clicked using buttonRole
        clicked_button = dialog.clickedButton()
        print(f"   Clicked button: {clicked_button}")
        print(f"   Clicked button is None: {clicked_button is None}")

        # If clicked_button is None, dialog was closed without clicking a button
        if clicked_button is None:
            print(f"   ❌ Dialog closed without button click - returning None")
            return None

        # Get the button role to determine which button was clicked
        button_role = dialog.buttonRole(clicked_button)
        print(f"   Button role: {button_role}")
        print(f"   YesRole={QMessageBox.YesRole}, NoRole={QMessageBox.NoRole}, RejectRole={QMessageBox.RejectRole}")

        # Check if Cancel or dialog was rejected
        if button_role == QMessageBox.RejectRole:
            print(f"   ❌ User clicked Cancel or closed dialog - returning None")
            return None

        if button_role == QMessageBox.YesRole:
            user_choice = True
            print(f"   ✅ User chose YES (compare)")
        elif button_role == QMessageBox.NoRole:
            user_choice = False
            print(f"   ✅ User chose NO (replace)")
        else:
            # Unknown role
            print(f"   ❌ Unknown button role ({button_role}) - returning None")
            return None

        checkbox_checked = checkbox.isChecked()
        print(f"   Checkbox 'Don't ask again': {checkbox_checked}")

        if checkbox_checked:
            self.comparison_preference = user_choice
            print(f"   → Caching preference for session: {user_choice}")

        print(f"   → Returning: {user_choice}\n")
        return user_choice

    def reset_preference(self):
        """Reset the cached preference."""
        self.comparison_preference = None

