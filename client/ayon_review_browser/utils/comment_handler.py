import traceback

try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except ImportError:
    from qtpy.QtCore import *
    from qtpy.QtWidgets import *

try:
    # Try relative imports first (when imported as part of package)
    from ..api.rv import RVOperations
    from ..api.rv.rv_annotation_manager import RVAnnotationManager, RV_AVAILABLE
except ImportError:
    # Fall back to absolute imports (when run directly)
    from api.rv import RVOperations
    from api.rv.rv_annotation_manager import RVAnnotationManager, RV_AVAILABLE


class CommentHandler:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.comment_worker = None

    def _auto_save_rv_session(self):
        """Auto-save RV session if current workfile is .rv file."""
        try:
            import rv.commands as rv_commands
            current_file = rv_commands.sessionFileName()
            
            if current_file and current_file != "Untitled" and current_file.endswith('.rv'):
                print(f"💾 Auto-saving RV session: {current_file}")
                rv_commands.saveSession(current_file)
                print("✅ RV session saved successfully")
        except ImportError:
            pass  # RV not available
        except Exception as e:
            print(f"⚠️ Failed to auto-save RV session: {e}")

    def create_comment(self, text_edit, table_view, tab_widget, filter_controller, data_service,
                       fetch_activities_callback, rv_ops=None, activity_manager=None):
        """
        Create a comment on a version with proper mode detection and annotation handling.

        Flow:
        1. Check activity panel mode (BROWSER_MODE or RV_MODE)
        2. In BROWSER_MODE: Always use table selection, never export annotations
        3. In RV_MODE: Use RV's current version, export annotations
        """
        try:
            message = text_edit.toPlainText().strip()
            if not message:
                QMessageBox.warning(self.parent, "Warning", "Please enter a comment message.")
                return

            # Auto-save RV session if loaded with .rv file
            self._auto_save_rv_session()

            # Step 1: Determine the activity panel mode
            panel_mode = 'BROWSER_MODE'  # Default to browser mode
            if activity_manager and hasattr(activity_manager, 'panel_mode'):
                panel_mode = activity_manager.panel_mode

            print(f"🎬 Activity Panel Mode: {panel_mode}")

            version_id = None
            row_data = None
            should_export_annotations = False

            # Step 2: Get version based on panel mode
            if panel_mode == 'RV_MODE':
                # RV MODE: Use RV's current view
                print("🎥 RV MODE: Getting version from RV's current view")
                if rv_ops and hasattr(rv_ops, 'source_mapping') and rv_ops.source_mapping:
                    try:
                        current_source = rv_ops.get_current_view_source()
                        if current_source:
                            import rv
                            source_group = rv.commands.nodeGroup(current_source)
                            if source_group in rv_ops.source_mapping:
                                source_info = rv_ops.source_mapping[source_group]
                                version_id = source_info.get('version_id')
                                row_data = source_info.get('row_data', {})
                                should_export_annotations = True  # Export in RV mode

                                # Fallback: Get version_id from row_data
                                if not version_id and row_data.get('version_id'):
                                    version_id = row_data['version_id']

                                print(f"✅ Got version from RV: {version_id}")
                    except Exception as e:
                        print(f"⚠️ Failed to get version from RV: {e}")

                # Fallback: Read version_id directly from current RV source
                if not version_id:
                    try:
                        import rv.commands as rv_cmd
                        current_view = rv_cmd.viewNode()
                        sources = rv_cmd.nodesInGroupOfType(current_view, "RVSource")
                        if sources:
                            source = sources[0]
                            if rv_cmd.propertyExists(f"{source}.ayon.version_id"):
                                version_id = rv_cmd.getStringProperty(f"{source}.ayon.version_id")[0]
                                should_export_annotations = True
                                print(f"✅ Got version_id from RV source: {version_id}")
                    except Exception as e:
                        print(f"⚠️ Failed to read RV source metadata: {e}")

                # If RV version not available, still use table selection as fallback
                if not version_id:
                    print("⚠️ RV version not available, falling back to table selection")
                    should_export_annotations = False

            # BROWSER_MODE or fallback: Always use table selection
            if not version_id or panel_mode == 'BROWSER_MODE':
                print("🌐 BROWSER MODE: Getting version from table selection")
                current_index = table_view.selectionModel().currentIndex()
                if not current_index.isValid():
                    QMessageBox.warning(self.parent, "Warning", "Please select a version from the table.")
                    return
                model = table_view.model()
                row_data = model._data[current_index.row()]
                version_id = row_data.get('version_id', '')
                should_export_annotations = False  # Never export in browser mode

            user_name = row_data.get('author', '')
            project_name = filter_controller.get_current_project()
            task_id = row_data.get('task_id')
            task_name = row_data.get('task_name')
            path = row_data.get('path')

            if not project_name or not version_id:
                QMessageBox.warning(self.parent, "Warning", "Missing project or version information.")
                return

            # Fetch actual version name using get_version_by_id
            version_name = None
            try:
                import ayon_api
                version = ayon_api.get_version_by_id(project_name, version_id)
                version_name = version.get('name') if version else None
            except Exception as e:
                print(f"Error fetching version name: {e}")

            # Show progress dialog
            progress = QProgressDialog("Preparing comment...", None, 0, 0, self.parent)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setAutoClose(False)
            progress.setAutoReset(False)
            progress.show()
            QApplication.processEvents()
            QThread.msleep(300)

            # Step 3: Extract RV annotations and export ONLY in RV mode
            annotation_paths = []
            if should_export_annotations and RV_AVAILABLE:
                progress.setLabelText("Checking for annotations...")
                QApplication.processEvents()

                try:
                    # Extract text annotations from RV
                    ann_manager = RVAnnotationManager()
                    ann_summary = ann_manager.get_annotation_summary()
                    
                    if ann_summary.get('has_annotations'):
                        # Append text annotations to comment
                        text_annotations = ann_summary.get('text_annotations', '')
                        if text_annotations:
                            message += f"\n\n--- RV Annotations ---\n{text_annotations}"
                            print(f"✅ Added {ann_summary.get('frame_count', 0)} frame annotations to comment")
                    
                    # Export annotation images
                    progress.setLabelText("Exporting annotations...")
                    QApplication.processEvents()
                    QThread.msleep(300)
                    annotation_paths = rv_ops.export_annotations()
                    if annotation_paths:
                        progress.setLabelText(f"Found {len(annotation_paths)} annotation(s)...")
                        QApplication.processEvents()
                        QThread.msleep(200)
                    else:
                        print("ℹ️ No annotation images found")
                except ImportError:
                    print("⚠️ RV module not available - continuing without annotations")
                    QThread.msleep(100)
                except Exception as e:
                    print(f"⚠️ Error extracting annotations: {e}")
                    QThread.msleep(100)
            else:
                print("🌐 Browser mode - skipping annotation export")
                QThread.msleep(100)

            # Step 4: Create comment on server
            progress.setLabelText("Uploading comment to server...")
            QApplication.processEvents()
            QThread.msleep(200)

            result = data_service.api.create_comment_on_version(
                project_name, version_id, message, user_name, annotation_paths,
                task_id=task_id, task_name=task_name, path=path, version_name=version_name
            )

            # Step 5: Show result
            progress.setLabelText("Processing response...")
            QApplication.processEvents()
            QThread.msleep(300)

            if result is not None:
                progress.close()
                text_edit.clear()
                fetch_activities_callback(row_data)
                QMessageBox.information(self.parent, "Success", "✓ Comment created successfully!")
            else:
                progress.close()
                QMessageBox.warning(self.parent, "Warning",
                                    "Comment created but there may have been issues with attachments.")

        except Exception as e:
            if 'progress' in locals():
                progress.close()
            print(traceback.format_exc())
            QMessageBox.critical(self.parent, "Error", f"Failed to create comment: {str(e)}")
