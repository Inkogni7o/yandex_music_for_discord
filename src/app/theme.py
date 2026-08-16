"""Application palette and stylesheet loader."""

from pathlib import Path

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#101114"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#f3f3f5"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#101114"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#191a20"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#f3f3f5"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#24252c"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f3f3f5"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#ffcc00"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#111216"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#686b75"))
    app.setPalette(palette)

    stylesheet_path = Path(__file__).parent / "static" / "theme.qss"
    app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))
