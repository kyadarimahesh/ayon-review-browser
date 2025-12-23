# Icon definitions for the application
try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class Icons:
    @staticmethod
    def create_emoji_icon(emoji, size=16):
        """Create an icon from emoji"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("transparent"))

        painter = QPainter(pixmap)
        font = painter.font()
        font.setPixelSize(size - 2)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def settings():
        return Icons.create_emoji_icon("⚙️")

    @staticmethod
    def save():
        return Icons.create_emoji_icon("💾")

    @staticmethod
    def load():
        return Icons.create_emoji_icon("📁")

    @staticmethod
    def reset():
        return Icons.create_emoji_icon("🔄")

    @staticmethod
    def project():
        return Icons.create_emoji_icon("📁")

    @staticmethod
    def filter():
        return Icons.create_emoji_icon("🔍")

    @staticmethod
    def review():
        return Icons.create_emoji_icon("📦")

    @staticmethod
    def lists():
        return Icons.create_emoji_icon("📝")

    @staticmethod
    def clear():
        return Icons.create_emoji_icon("🗑️")

    @staticmethod
    def search():
        return Icons.create_emoji_icon("🔍")

    @staticmethod
    def refresh():
        return Icons.create_emoji_icon("🔄")
