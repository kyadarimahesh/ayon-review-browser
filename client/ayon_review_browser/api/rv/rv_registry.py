"""Global RV Operations Registry for AYON integration."""

_rv_operations_instance = None

def get_rv_operations():
    """Get the global RVOperations instance."""
    return _rv_operations_instance

def set_rv_operations(rv_ops):
    """Set the global RVOperations instance."""
    global _rv_operations_instance
    _rv_operations_instance = rv_ops

def setup_rv_event_listeners():
    """Setup RV event listeners for source loading."""
    try:
        import rv.commands
        
        rv.commands.bind(
            "default",
            "global", 
            "ayon_source_loaded",
            _on_ayon_source_loaded_handler,
            "Handle AYON source loaded event"
        )
        
        print("✅ Review Browser: RV event listeners registered")
        
    except Exception as e:
        print(f"⚠️ Review Browser: Could not register RV listeners: {e}")

def _on_ayon_source_loaded_handler(event):
    """Handle ayon_source_loaded event from RV."""
    try:
        import json
        
        event_data = json.loads(event.contents())
        
        node = event_data['node']
        filepath = event_data['filepath']
        version_id = event_data['version_id']
        
        row_data = {
            'version_id': version_id,
            'task_id': event_data['task_id'],
            'product': event_data['product'],
            'folder_path': event_data['folder_path'],
            'project_name': event_data['project_name'],
            'path': event_data['path'],
            'current_version': event_data['current_version'],
            'versions': event_data['versions'],
            'version_status': event_data['version_status'],
            'author': event_data['author']
        }
        
        register_ayon_source(node, filepath, version_id, row_data)
        print(f"✅ Registered AYON source via event: {filepath}")
        
    except Exception as e:
        print(f"❌ Error handling ayon_source_loaded event: {e}")

def initialize_rv_integration():
    """Initialize RV integration if RV is available."""
    try:
        import rv.commands
        setup_rv_event_listeners()
    except ImportError:
        print("⚠️ RV not available - event listeners not registered")

def register_ayon_source(node, filepath, version_id=None, row_data=None):
    """Register AYON-loaded source with RVOperations."""
    rv_ops = get_rv_operations()
    if rv_ops:
        try:
            import rv
            source_group = rv.commands.nodeGroup(node)
            if source_group:
                # Fetch representations for the version if version_id is available
                enhanced_row_data = row_data.copy() if row_data else {}
                if version_id and 'representations' not in enhanced_row_data:
                    try:
                        from ...api.ayon.version_service import VersionService
                        version_service = VersionService()
                        project_name = enhanced_row_data.get('project_name')
                        if project_name:
                            version_details = version_service.get_version_details(project_name, version_id)
                            if version_details.get('representations'):
                                enhanced_row_data['representations'] = version_details['representations']
                                print(f"🔍 AYON: Fetched {len(version_details['representations'])} representations for version {version_id}")
                    except Exception as e:
                        print(f"🔍 AYON: Could not fetch representations: {e}")

                # Set current_representation_path for highlighting
                enhanced_row_data['current_representation_path'] = filepath

                rv_ops.source_mapping[source_group] = {
                    'path': filepath,
                    'version_id': version_id,
                    'row_data': enhanced_row_data,
                    'all_representations': enhanced_row_data.get('representations', [])
                }
                # Set as current view and trigger activity update
                rv.commands.setViewNode(source_group)
                rv_ops.current_version_id = None  # Reset to force update
                rv_ops.update_activity_for_current_frame()
                print(f"🔍 AYON: Registered source {source_group} with version_id={version_id}")
        except Exception as e:
            print(f"🔍 AYON: Error registering source: {e}")