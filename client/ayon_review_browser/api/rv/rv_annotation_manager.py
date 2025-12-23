"""RV Annotation Manager - Handles RV annotation extraction and export."""
import os
import logging
from typing import List, Dict, Optional

try:
    import rv.commands as commands
    from pymu import MuSymbol
    RV_AVAILABLE = True
except ImportError:
    RV_AVAILABLE = False

LOG = logging.getLogger(__name__)


class RVAnnotationManager:
    """Manages RV annotations extraction and export."""
    
    def __init__(self):
        if not RV_AVAILABLE:
            raise ImportError("RV modules not available")
    
    def get_text_annotations(self) -> str:
        """Extract all text annotations from current RV session."""
        try:
            marked_frames = self._get_marked_frames()
            if not marked_frames:
                return ""
            
            annotations = []
            frame_offset = commands.frame() - 1
            
            for frame in marked_frames:
                texts = self._extract_frame_text(frame)
                for text in texts:
                    annotations.append(f"Frame {frame + frame_offset}: {text}")
            
            return "\n".join(annotations)
        except Exception as e:
            LOG.error(f"Error extracting annotations: {e}")
            return ""
    
    def get_annotation_summary(self) -> Dict[str, any]:
        """Get comprehensive annotation summary."""
        try:
            marked_frames = self._get_marked_frames()
            text_annotations = self.get_text_annotations()
            
            return {
                'has_annotations': bool(marked_frames),
                'frame_count': len(marked_frames),
                'text_annotations': text_annotations,
                'marked_frames': marked_frames
            }
        except Exception as e:
            LOG.error(f"Error getting annotation summary: {e}")
            return {'has_annotations': False}
    
    def export_marked_frames(self, output_path: str, pattern: str = "annotated.####.jpeg") -> bool:
        """Export marked frames to specified path."""
        try:
            export_pattern = os.path.join(output_path, pattern)
            export_frames = MuSymbol("export_utils.exportMarkedFrames")
            export_frames(export_pattern)
            return True
        except Exception as e:
            LOG.error(f"Error exporting frames: {e}")
            return False
    
    def _get_marked_frames(self) -> List[int]:
        """Get marked frames from RV."""
        try:
            marked_frames = commands.markedFrames()
            if not marked_frames:
                mark_frames = MuSymbol('rvui.markAnnotatedFrames')
                mark_frames()
                marked_frames = commands.markedFrames()
            return marked_frames
        except Exception as e:
            LOG.error(f"Error getting marked frames: {e}")
            return []
    
    def _extract_frame_text(self, frame: int) -> List[str]:
        """Extract text annotations from specific frame."""
        try:
            prop_order = f"#RVPaint.frame:{frame}.order"
            if not commands.propertyExists(prop_order):
                return []
            
            texts = []
            items = commands.getStringProperty(prop_order, 0, 2147483647)
            
            for item in items:
                if item.startswith("text"):
                    text_prop = f"#RVPaint.{item}.text"
                    if commands.propertyExists(text_prop):
                        text = commands.getStringProperty(text_prop, 0, 2147483647)
                        if text and text[0].strip():
                            texts.append(text[0].strip())
            
            return texts
        except Exception as e:
            LOG.error(f"Error extracting text from frame {frame}: {e}")
            return []
