"""Base widget classes required by search bar."""
try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class BaseClickableFrame(QFrame):
    """Widget that catch left mouse click and can trigger a callback."""

    def __init__(self, parent):
        super().__init__(parent)
        self._mouse_pressed = False
        self.setFrameShape(QFrame.StyledPanel)

    def _mouse_release_callback(self):
        pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.isAccepted():
            return
        if event.button() == Qt.LeftButton:
            self._mouse_pressed = True
            event.accept()

    def mouseReleaseEvent(self, event):
        pressed, self._mouse_pressed = self._mouse_pressed, False
        super().mouseReleaseEvent(event)
        if event.isAccepted():
            return

        accepted = pressed and self.rect().contains(event.pos())
        if accepted:
            event.accept()
            self._mouse_release_callback()


class SquareButton(QPushButton):
    """Make button square shape."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(32, 32)


class PixmapLabel(QLabel):
    """Label resizing image to height of font."""

    def __init__(self, pixmap, parent):
        super().__init__(parent)
        self._empty_pixmap = QPixmap(0, 0)
        self._source_pixmap = pixmap
        self._last_width = 0
        self._last_height = 0

    def set_source_pixmap(self, pixmap):
        """Change source image."""
        self._source_pixmap = pixmap
        self._set_resized_pix()

    def _get_pix_size(self):
        size = self.fontMetrics().height()
        size += size % 2
        return size, size

    def minimumSizeHint(self):
        width, height = self._get_pix_size()
        if width != self._last_width or height != self._last_height:
            self._set_resized_pix()
        return QSize(width, height)

    def _set_resized_pix(self):
        if self._source_pixmap is None:
            self.setPixmap(self._empty_pixmap)
            return
        width, height = self._get_pix_size()
        self.setPixmap(
            self._source_pixmap.scaled(
                width,
                height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self._last_width = width
        self._last_height = height

    def resizeEvent(self, event):
        self._set_resized_pix()
        super().resizeEvent(event)


class SeparatorWidget(QFrame):
    """Separator widget with predefined size."""

    def __init__(self, size=2, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.setObjectName("Separator")
        maximum_width = self.maximumWidth()
        maximum_height = self.maximumHeight()
        self._size = None
        self._orientation = orientation
        self._maximum_width = maximum_width
        self._maximum_height = maximum_height
        self.set_size(size)

    def set_size(self, size):
        if size != self._size:
            self._set_size(size)

    def _set_size(self, size):
        if self._orientation == Qt.Vertical:
            self.setMinimumWidth(size)
            self.setMaximumWidth(size)
        else:
            self.setMinimumHeight(size)
            self.setMaximumHeight(size)
        self._size = size

    def set_orientation(self, orientation):
        if self._orientation == orientation:
            return
        if self._orientation == Qt.Vertical:
            self.setMinimumHeight(0)
            self.setMaximumHeight(self._maximum_height)
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(self._maximum_width)
        self._orientation = orientation
        self._set_size(self._size)