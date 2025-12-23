"""
RV API Module for managing Sources, Sequences, Stacks, and Layouts
Provides CRUD operations for RV session management
"""

try:
    import rv.commands as commands
except ImportError:
    pass

from typing import List, Dict, Optional, Union


class RVAPIError(Exception):
    """Base exception for RV API operations"""
    pass


class SourceManager:
    """Manages RV Sources with CRUD operations"""

    @staticmethod
    def list() -> List[Dict]:
        """Get list of all sources"""
        try:
            sources = commands.sources()
            return [{"name": s[0], "start": s[1], "end": s[2], "inc": s[3],
                    "fps": s[4], "audio": s[5], "video": s[6]} for s in sources]
        except Exception as e:
            raise RVAPIError(f"Failed to list sources: {e}")

    @staticmethod
    def create(files: Union[str, List[str]], tag: str = "") -> str:
        """Create new source from file(s)"""
        try:
            if isinstance(files, str):
                commands.addSource(files, tag)
                return files
            else:
                return commands.addSourceVerbose(files, tag)
        except Exception as e:
            raise RVAPIError(f"Failed to create source: {e}")

    @staticmethod
    def rename(old_name: str, new_name: str) -> None:
        """Rename source media"""
        try:
            commands.relocateSource(old_name, new_name)
        except Exception as e:
            raise RVAPIError(f"Failed to rename source: {e}")

    @staticmethod
    def delete(node_name: str) -> None:
        """Delete source node"""
        try:
            commands.deleteNode(node_name)
        except Exception as e:
            raise RVAPIError(f"Failed to delete source: {e}")

    @staticmethod
    def add_media(node_name: str, files: List[str], tag: str = "") -> None:
        """Add media to existing source"""
        try:
            commands.setSourceMedia(node_name, files, tag)
        except Exception as e:
            raise RVAPIError(f"Failed to add media to source: {e}")

    @staticmethod
    def remove_media(node_name: str, media_name: str) -> None:
        """Remove media from source"""
        try:
            # Get current media list and remove specified media
            current_media = commands.getStringProperty(f"{node_name}.media.movie")
            if media_name in current_media:
                updated_media = [m for m in current_media if m != media_name]
                commands.setSourceMedia(node_name, updated_media)
        except Exception as e:
            raise RVAPIError(f"Failed to remove media from source: {e}")


class SequenceManager:
    """Manages RV Sequences with CRUD operations"""

    @staticmethod
    def list() -> List[str]:
        """Get list of all sequence nodes"""
        try:
            return commands.nodesOfType("RVSequenceGroup")
        except Exception as e:
            raise RVAPIError(f"Failed to list sequences: {e}")

    @staticmethod
    def create(name: str, sources: List[str]) -> str:
        """Create new sequence from sources"""
        try:
            seq_node = commands.newNode("RVSequenceGroup", name)
            if sources:
                commands.setNodeInputs(seq_node, sources)
            return seq_node
        except Exception as e:
            raise RVAPIError(f"Failed to create sequence: {e}")

    @staticmethod
    def rename(node_name: str, new_name: str) -> None:
        """Rename sequence node"""
        try:
            commands.setStringProperty(f"{node_name}.ui.name", [new_name])
        except Exception as e:
            raise RVAPIError(f"Failed to rename sequence: {e}")

    @staticmethod
    def delete(node_name: str) -> None:
        """Delete sequence node"""
        try:
            commands.deleteNode(node_name)
        except Exception as e:
            raise RVAPIError(f"Failed to delete sequence: {e}")

    @staticmethod
    def add_source(seq_node: str, source_node: str) -> None:
        """Add source to sequence"""
        try:
            inputs = commands.nodeInputs(seq_node)
            inputs.append(source_node)
            commands.setNodeInputs(seq_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to add source to sequence: {e}")

    @staticmethod
    def remove_source(seq_node: str, source_node: str) -> None:
        """Remove source from sequence"""
        try:
            inputs = commands.nodeInputs(seq_node)
            if source_node in inputs:
                inputs.remove(source_node)
                commands.setNodeInputs(seq_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to remove source from sequence: {e}")


class StackManager:
    """Manages RV Stacks with CRUD operations"""

    @staticmethod
    def list() -> List[str]:
        """Get list of all stack nodes"""
        try:
            return commands.nodesOfType("RVStackGroup")
        except Exception as e:
            raise RVAPIError(f"Failed to list stacks: {e}")

    @staticmethod
    def create(name: str, sources: List[str]) -> str:
        """Create new stack from sources"""
        try:
            stack_node = commands.newNode("RVStackGroup", name)
            if sources:
                commands.setNodeInputs(stack_node, sources)
            return stack_node
        except Exception as e:
            raise RVAPIError(f"Failed to create stack: {e}")

    @staticmethod
    def rename(node_name: str, new_name: str) -> None:
        """Rename stack node"""
        try:
            commands.setStringProperty(f"{node_name}.ui.name", [new_name])
        except Exception as e:
            raise RVAPIError(f"Failed to rename stack: {e}")

    @staticmethod
    def delete(node_name: str) -> None:
        """Delete stack node"""
        try:
            commands.deleteNode(node_name)
        except Exception as e:
            raise RVAPIError(f"Failed to delete stack: {e}")

    @staticmethod
    def add_layer(stack_node: str, source_node: str) -> None:
        """Add layer to stack"""
        try:
            inputs = commands.nodeInputs(stack_node)
            inputs.append(source_node)
            commands.setNodeInputs(stack_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to add layer to stack: {e}")

    @staticmethod
    def remove_layer(stack_node: str, source_node: str) -> None:
        """Remove layer from stack"""
        try:
            inputs = commands.nodeInputs(stack_node)
            if source_node in inputs:
                inputs.remove(source_node)
                commands.setNodeInputs(stack_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to remove layer from stack: {e}")


class LayoutManager:
    """Manages RV Layouts with CRUD operations"""

    @staticmethod
    def list() -> List[str]:
        """Get list of all layout nodes"""
        try:
            return commands.nodesOfType("RVLayoutGroup")
        except Exception as e:
            raise RVAPIError(f"Failed to list layouts: {e}")

    @staticmethod
    def create(name: str, sources: List[str], mode: str = "packed") -> str:
        """Create new layout from sources"""
        try:
            layout_node = commands.newNode("RVLayoutGroup", name)
            if sources:
                commands.setNodeInputs(layout_node, sources)
            commands.setStringProperty(f"{layout_node}.layout.mode", [mode])
            return layout_node
        except Exception as e:
            raise RVAPIError(f"Failed to create layout: {e}")

    @staticmethod
    def rename(node_name: str, new_name: str) -> None:
        """Rename layout node"""
        try:
            commands.setStringProperty(f"{node_name}.ui.name", [new_name])
        except Exception as e:
            raise RVAPIError(f"Failed to rename layout: {e}")

    @staticmethod
    def delete(node_name: str) -> None:
        """Delete layout node"""
        try:
            commands.deleteNode(node_name)
        except Exception as e:
            raise RVAPIError(f"Failed to delete layout: {e}")

    @staticmethod
    def add_view(layout_node: str, source_node: str) -> None:
        """Add view to layout"""
        try:
            inputs = commands.nodeInputs(layout_node)
            inputs.append(source_node)
            commands.setNodeInputs(layout_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to add view to layout: {e}")

    @staticmethod
    def remove_view(layout_node: str, source_node: str) -> None:
        """Remove view from layout"""
        try:
            inputs = commands.nodeInputs(layout_node)
            if source_node in inputs:
                inputs.remove(source_node)
                commands.setNodeInputs(layout_node, inputs)
        except Exception as e:
            raise RVAPIError(f"Failed to remove view from layout: {e}")

    @staticmethod
    def set_mode(layout_node: str, mode: str) -> None:
        """Set layout mode (packed, row, column, manual)"""
        try:
            commands.setStringProperty(f"{layout_node}.layout.mode", [mode])
        except Exception as e:
            raise RVAPIError(f"Failed to set layout mode: {e}")


class RVAPI:
    """Main RV API class providing unified access to all managers"""

    def __init__(self):
        self.sources = SourceManager()
        self.sequences = SequenceManager()
        self.stacks = StackManager()
        self.layouts = LayoutManager()

    def get_session_info(self) -> Dict:
        """Get current session information"""
        try:
            return {
                "sources": self.sources.list(),
                "sequences": self.sequences.list(),
                "stacks": self.stacks.list(),
                "layouts": self.layouts.list(),
                "current_frame": commands.frame(),
                "fps": commands.fps()
            }
        except Exception as e:
            raise RVAPIError(f"Failed to get session info: {e}")