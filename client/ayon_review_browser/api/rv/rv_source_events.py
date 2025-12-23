"""
RV Source Change Events Module

Provides easy-to-use event handlers for RV source changes and related events.
Based on RV event system analysis.
"""

try:
    import rv
    from rv import commands
except ImportError:
    pass

try:
    from PySide2.QtCore import QTimer
except ImportError:
    from qtpy.QtCore import QTimer

# Global debug flag
DEBUG_EVENTS = False


class RVSourceEvents:
    """Handles RV source change events and related functionality."""

    def __init__(self):
        self.source_change_callbacks = []
        self.view_change_callbacks = []
        self.media_change_callbacks = []
        self.stack_change_callbacks = []
        self.frame_change_callbacks = []
        self._monitoring = False

        # Timer-based monitoring as fallback
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._check_changes)
        self.last_frame = None
        self.last_source = None

    def add_source_change_callback(self, callback):
        """Add callback for source changes."""
        self.source_change_callbacks.append(callback)

    def add_view_change_callback(self, callback):
        """Add callback for view changes."""
        self.view_change_callbacks.append(callback)

    def add_media_change_callback(self, callback):
        """Add callback for media/representation changes."""
        self.media_change_callbacks.append(callback)

    def add_stack_change_callback(self, callback):
        """Add callback for stack navigation changes."""
        self.stack_change_callbacks.append(callback)

    def add_frame_change_callback(self, callback):
        """Add callback for frame changes."""
        self.frame_change_callbacks.append(callback)

    def start_monitoring(self):
        """Start monitoring source change events."""
        if self._monitoring:
            return

        self._monitoring = True

        try:
            # View change events
            rv.commands.bind("default", "global", "after-graph-view-change",
                           self._on_view_change, "View change monitoring")

            # Source-related events
            rv.commands.bind("default", "global", "source-group-complete",
                           self._on_source_complete, "Source complete monitoring")
            rv.commands.bind("default", "global", "source-media-set",
                           self._on_media_set, "Media set monitoring")
            rv.commands.bind("default", "global", "source-media-rep-activated",
                           self._on_media_rep_activated, "Media representation monitoring")
            rv.commands.bind("default", "global", "source-modified",
                           self._on_source_modified, "Source modified monitoring")

            # Stack navigation events - correct key bindings
            rv.commands.bind("default", "global", "key-down--(",
                           self._on_stack_backward, "Stack backward navigation")
            rv.commands.bind("default", "global", "key-down--)",
                           self._on_stack_forward, "Stack forward navigation")

            # Frame change events
            rv.commands.bind("default", "global", "frame-changed",
                           self._on_frame_changed, "Frame change monitoring")

            # Start timer-based monitoring as fallback (every 100ms)
            self.monitor_timer.start(100)

            print("RV source change monitoring started (events + timer fallback)")
        except Exception as e:
            print(f"Error binding source events: {e}")

    def stop_monitoring(self):
        """Stop monitoring source change events."""
        if not self._monitoring:
            return

        self._monitoring = False

        try:
            rv.commands.unbind("default", "global", "after-graph-view-change")
            rv.commands.unbind("default", "global", "source-group-complete")
            rv.commands.unbind("default", "global", "source-media-set")
            rv.commands.unbind("default", "global", "source-media-rep-activated")
            rv.commands.unbind("default", "global", "source-modified")
            rv.commands.unbind("default", "global", "key-down--(")
            rv.commands.unbind("default", "global", "key-down--)")
            rv.commands.unbind("default", "global", "frame-changed")
            # Stop timer monitoring
            self.monitor_timer.stop()

            print("RV source change monitoring stopped")
        except Exception as e:
            print(f"Error unbinding source events: {e}")

    def _on_view_change(self, event):
        """Handle view change events."""
        if DEBUG_EVENTS:
            print("🔥 VIEW CHANGE EVENT FIRED - after-graph-view-change")
        try:
            current_source = self.get_current_source()
            for callback in self.view_change_callbacks:
                callback(current_source, event)
        except Exception as e:
            print(f"Error in view change callback: {e}")

    def _on_source_complete(self, event):
        """Handle source group complete events."""
        if DEBUG_EVENTS:
            print("🔥 SOURCE COMPLETE EVENT FIRED - source-group-complete")
        try:
            current_source = self.get_current_source()
            for callback in self.source_change_callbacks:
                callback(current_source, event)
        except Exception as e:
            print(f"Error in source complete callback: {e}")

    def _on_media_set(self, event):
        """Handle media set events."""
        if DEBUG_EVENTS:
            print("🔥 MEDIA SET EVENT FIRED - source-media-set")
        try:
            current_source = self.get_current_source()
            for callback in self.media_change_callbacks:
                callback(current_source, event)
        except Exception as e:
            print(f"Error in media set callback: {e}")

    def _on_media_rep_activated(self, event):
        """Handle media representation activated events."""
        if DEBUG_EVENTS:
            print("🔥 MEDIA REP ACTIVATED EVENT FIRED - source-media-rep-activated")
        try:
            current_source = self.get_current_source()
            for callback in self.media_change_callbacks:
                callback(current_source, event)
        except Exception as e:
            print(f"Error in media rep activated callback: {e}")

    def _on_source_modified(self, event):
        """Handle source modified events."""
        if DEBUG_EVENTS:
            print("🔥 SOURCE MODIFIED EVENT FIRED - source-modified")
        try:
            current_source = self.get_current_source()
            for callback in self.source_change_callbacks:
                callback(current_source, event)
        except Exception as e:
            print(f"Error in source modified callback: {e}")

    def _on_stack_backward(self, event):
        """Handle stack backward navigation (key-down--()."""
        if DEBUG_EVENTS:
            print("🔥 STACK BACKWARD EVENT FIRED - ( key pressed!")
        try:
            current_source = self.get_current_source()
            for callback in self.stack_change_callbacks:
                callback("backward", current_source, event)
        except Exception as e:
            print(f"Error in stack backward callback: {e}")

    def _on_stack_forward(self, event):
        """Handle stack forward navigation (key-down--))."""
        if DEBUG_EVENTS:
            print("🔥 STACK FORWARD EVENT FIRED - ) key pressed!")
        try:
            current_source = self.get_current_source()
            for callback in self.stack_change_callbacks:
                callback("forward", current_source, event)
        except Exception as e:
            print(f"Error in stack forward callback: {e}")



    def _on_frame_changed(self, event):
        """Handle frame change events."""
        if DEBUG_EVENTS:
            print("🔥 FRAME CHANGED EVENT FIRED - frame-changed")
        try:
            current_frame = rv.commands.frame()
            for callback in self.frame_change_callbacks:
                callback(current_frame, event)
        except Exception as e:
            print(f"Error in frame change callback: {e}")

    @staticmethod
    def get_current_source():
        """Get current active source."""
        try:
            sources = rv.commands.sourcesAtFrame(rv.commands.frame())
            return sources[0] if sources else None
        except Exception as e:
            print(f"Error getting current source: {e}")
            return None

    @staticmethod
    def get_current_view_node():
        """Get current view node."""
        try:
            return rv.commands.viewNode()
        except Exception as e:
            print(f"Error getting view node: {e}")
            return None

    def _check_changes(self):
        """Timer-based monitoring for frame and source changes."""
        if not self._monitoring:
            return

        try:
            # Check frame changes
            current_frame = rv.commands.frame()
            if current_frame != self.last_frame:
                self.last_frame = current_frame
                if DEBUG_EVENTS:
                    print(f"⏰ TIMER FRAME CHANGE: {current_frame}")
                for callback in self.frame_change_callbacks:
                    callback(current_frame, "timer-frame-change")

            # Check source changes
            current_source = self.get_current_source()
            if current_source != self.last_source:
                self.last_source = current_source
                print(f"⏰ TIMER SOURCE CHANGE: {current_source}")
                for callback in self.source_change_callbacks:
                    callback(current_source, "timer-source-change")

        except Exception as e:
            # Silently handle errors to avoid spam
            pass


# Convenience functions for quick setup
def setup_source_monitoring(source_callback=None, view_callback=None, media_callback=None):
    """Quick setup for source monitoring with callbacks."""
    monitor = RVSourceEvents()

    if source_callback:
        monitor.add_source_change_callback(source_callback)
    if view_callback:
        monitor.add_view_change_callback(view_callback)
    if media_callback:
        monitor.add_media_change_callback(media_callback)

    monitor.start_monitoring()
    return monitor

def set_debug_events(enabled=True):
    """Enable or disable debug event prints."""
    global DEBUG_EVENTS
    DEBUG_EVENTS = enabled
    print(f"RV Events debug: {'ON' if enabled else 'OFF'}")

def simple_source_change_handler(callback):
    """Simple decorator for source change handling."""
    def wrapper():
        monitor = RVSourceEvents()
        monitor.add_source_change_callback(lambda source, event: callback(source))
        monitor.start_monitoring()
        return monitor
    return wrapper