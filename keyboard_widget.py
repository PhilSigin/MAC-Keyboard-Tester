"""Keyboard display widget: padded gray canvas, PNG, multiply key highlights."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QWidget

from key_map_fr import NAME_TO_INDEX, SLOT_NAMES
from svg_keys import KeyGeom, load_key_geometries

BG_GRAY = QColor(128, 128, 128)  # 50% gray
PAD_X = 0.20
PAD_Y = 0.30
GREEN = QColor(0, 220, 0)


class KeyboardWidget(QWidget):
    def __init__(self, png_path: Path, svg_path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._png = QImage(str(png_path))
        if self._png.isNull():
            raise FileNotFoundError(png_path)
        self._png_w = self._png.width()
        self._png_h = self._png.height()
        self._canvas_w = int(self._png_w * (1 + 2 * PAD_X))
        self._canvas_h = int(self._png_h * (1 + 2 * PAD_Y))
        self._offset_x = int(self._png_w * PAD_X)
        self._offset_y = int(self._png_h * PAD_Y)

        geoms = load_key_geometries(svg_path, self._png_w, self._png_h)
        if len(geoms) != len(SLOT_NAMES):
            print(
                f"[warn] key count mismatch: svg={len(geoms)} slots={len(SLOT_NAMES)}",
                flush=True,
            )
        self._geoms: list[KeyGeom] = geoms
        self._pressed: set[int] = set()
        self.setMinimumSize(640, 240)

    def set_key_down(self, slot: str | None, is_down: bool) -> None:
        if not slot or slot not in NAME_TO_INDEX:
            return
        idx = NAME_TO_INDEX[slot]
        if idx >= len(self._geoms):
            return
        if is_down:
            self._pressed.add(idx)
        else:
            self._pressed.discard(idx)
        self.update()

    def clear_pressed(self) -> None:
        self._pressed.clear()
        self.update()

    def _target_rect(self) -> QRectF:
        side = self.contentsRect()
        scale = min(side.width() / self._canvas_w, side.height() / self._canvas_h)
        w = self._canvas_w * scale
        h = self._canvas_h * scale
        x = side.x() + (side.width() - w) / 2
        y = side.y() + (side.height() - h) / 2
        return QRectF(x, y, w, h)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), BG_GRAY)

        target = self._target_rect()
        scale = target.width() / self._canvas_w

        # Gray canvas (explicit, in case widget bg differs)
        painter.fillRect(target, BG_GRAY)

        png_rect = QRectF(
            target.x() + self._offset_x * scale,
            target.y() + self._offset_y * scale,
            self._png_w * scale,
            self._png_h * scale,
        )
        painter.drawImage(png_rect, self._png)

        if not self._pressed:
            return

        painter.save()
        painter.translate(png_rect.topLeft())
        painter.scale(scale, scale)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(GREEN)
        for idx in self._pressed:
            if 0 <= idx < len(self._geoms):
                painter.drawPath(self._geoms[idx].path)
        painter.restore()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.update()
