# RV Events Reference Guide

## Overview
Comprehensive reference for RV events used in AYON Review Browser for extending functionality.

## Currently Implemented Events

### Source Change Events
| Event | Description | Use Case |
|-------|-------------|----------|
| `after-graph-view-change` | View changes in RV | Update UI when switching between sources |
| `source-group-complete` | Source loading completes | Initialize source-specific functionality |
| `source-media-set` | Media is set on source | Track media changes |
| `source-media-rep-activated` | Media representation activated | Handle representation switches |
| `source-modified` | Source is modified | React to source modifications |

### Navigation Events
| Event | Description | Use Case |
|-------|-------------|----------|
| `key-down--(` | Stack backward navigation | Update activity panel for new top layer |
| `key-down--)` | Stack forward navigation | Update activity panel for new top layer |
| `frame-changed` | Frame position changes | Update frame-specific information |

## Available Events for Extension

### Session Management
| Event | Description | Potential Use |
|-------|-------------|---------------|
| `after-session-read` | Session loaded | Initialize session-specific settings |
| `before-session-read` | Before session load | Cleanup previous session |
| `before-session-deletion` | Before session deletion | Save state, cleanup |
| `session-clear-everything` | Session cleared | Reset all UI states |

### Playback Control
| Event | Description | Potential Use |
|-------|-------------|---------------|
| `play-start` | Playback started | Show playback indicators |
| `play-stop` | Playback stopped | Hide playback indicators |
| `key-down-- ` | Toggle play | Custom playback handling |

### Frame Navigation
| Event | Description | Potential Use |
|-------|-------------|---------------|
| `key-down--left` | Move back one frame | Custom frame navigation |
| `key-down--right` | Step forward 1 frame | Custom frame navigation |
| `key-down--home` | Go to beginning | Jump to start handling |
| `key-down--end` | Go to end | Jump to end handling |

### Timeline Events
| Event | Description | Potential Use |
|-------|-------------|---------------|
| `range-changed` | Timeline range changed | Update range indicators |
| `pointer-1--drag` | Drag frame on timeline | Custom scrubbing |
| `key-down--[` | Set in point | Mark range start |
| `key-down--]` | Set out point | Mark range end |

## Implementation Examples

### Basic Event Extension
```python
def add_playback_monitoring(self):
    """Add playback event monitoring."""
    rv.commands.bind("default", "global", "play-start", self._on_play_start, "Play start")
    rv.commands.bind("default", "global", "play-stop", self._on_play_stop, "Play stop")

def _on_play_start(self, event):
    """Handle playback start."""
    print("Playback started")
    # Show playback UI elements

def _on_play_stop(self, event):
    """Handle playback stop."""
    print("Playback stopped")
    # Hide playback UI elements
```

### Session Management
```python
def setup_session_monitoring(self):
    """Monitor session lifecycle events."""
    rv.commands.bind("default", "global", "after-session-read", self._on_session_loaded, "Session loaded")
    rv.commands.bind("default", "global", "before-session-deletion", self._on_session_cleanup, "Session cleanup")

def _on_session_loaded(self, event):
    """Handle session loaded."""
    print("Session loaded - initializing...")

def _on_session_cleanup(self, event):
    """Handle session cleanup."""
    print("Session cleanup - saving state...")
```

### Timeline Range Monitoring
```python
def setup_timeline_monitoring(self):
    """Monitor timeline range changes."""
    rv.commands.bind("default", "global", "range-changed", self._on_range_changed, "Range changed")
    rv.commands.bind("default", "global", "key-down--[", self._on_in_point, "In point set")

def _on_range_changed(self, event):
    """Handle range change."""
    # Update range display in UI
    pass

def _on_in_point(self, event):
    """Handle in point set."""
    current_frame = rv.commands.frame()
    print(f"In point set at frame {current_frame}")
```

## Extension Pattern

### Adding to RVSourceEvents
```python
# In rv_source_events.py
def add_playback_change_callback(self, callback):
    """Add callback for playback changes."""
    self.playback_change_callbacks.append(callback)

def start_monitoring(self):
    # Add to existing bindings
    rv.commands.bind("default", "global", "play-start", self._on_play_start, "Play start monitoring")
    rv.commands.bind("default", "global", "play-stop", self._on_play_stop, "Play stop monitoring")

def _on_play_start(self, event):
    """Handle playback start."""
    for callback in self.playback_change_callbacks:
        callback("start", event)
```

### Using in RVOperations
```python
# In rv_operations_module.py
def start_source_monitoring(self):
    # Add to existing callbacks
    self.source_events.add_playback_change_callback(self._on_playback_change)
    self.source_events.start_monitoring()

def _on_playback_change(self, state, event):
    """Handle playback state changes."""
    print(f"Playback {state}")
    # Update UI based on playback state
```

## Event Priority

### High Priority (Core Functionality)
- `frame-changed` - Activity panel updates
- `after-graph-view-change` - Source switching
- `source-group-complete` - Media loading
- Stack navigation - Version comparison

### Medium Priority (Enhancement)
- `play-start/stop` - Playback indicators
- `range-changed` - Timeline features
- Session events - State management

### Low Priority (Advanced Features)
- Color channel events - Display modes
- Zoom/scale events - View controls
- File operation events - Workflow

## Best Practices

### 1. Error Handling
```python
def event_callback(self, event):
    try:
        # Event handling logic
        pass
    except Exception as e:
        print(f"Error in event callback: {e}")
```

### 2. Performance
- Avoid heavy processing in callbacks
- Use debouncing for high-frequency events
- Cache expensive operations

### 3. Cleanup
```python
def stop_monitoring(self):
    try:
        rv.commands.unbind("default", "global", "event-name")
    except Exception as e:
        print(f"Error unbinding: {e}")
```

### 4. Modular Design
- Keep event handlers in separate modules
- Use consistent callback signatures
- Document all custom events

## Troubleshooting

### Common Issues
1. **Events not firing**: Check event name spelling
2. **Multiple bindings**: Use monitoring flags
3. **Memory leaks**: Always unbind events
4. **Performance**: Profile event callbacks

### Debug Pattern
```python
def debug_events(self):
    """Debug event system."""
    print(f"Monitoring active: {self._monitoring}")
    # Add logging to all callbacks for debugging
```

This reference enables developers to extend RV event handling systematically.