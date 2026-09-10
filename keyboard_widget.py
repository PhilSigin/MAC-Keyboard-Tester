"""Keyboard display widget: padded gray canvas, PNG, multiply key highlights."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from key_map_fr import NAME_TO_INDEX, SLOT_NAMES
from svg_keys import KeyGeom, load_key_geometries

BG_GRAY = QColor(128, 128, 128)  # 50% gray
PAD_X = 0.20
PAD_Y = 0.30

GREEN = QColor(0, 220, 0)
PALE_BLUE = QColor(0xA8, 0xD4, 0xF0)
MARK_GRAY = QColor(0xB0, 0xB0, 0xB0)
PALE_ORANGE = QColor(0xF0, 0xC0, 0x90)
ORANGE = QColor(0xFF, 0x8C, 0x00)


class KeyboardWidget(QWidget):
    reset_clicked = Signal()

    def __init__(self, png_path: Path, svg_path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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

        self._held: set[int] = set()
        self._visited: set[int] = set()
        self._solo_marked: set[int] = set()
        self._chord_marked: set[int] = set()
        self._chord_active: set[int] = set()

        self.setMinimumSize(640, 240)
        self._build_overlay()

    def _build_overlay(self) -> None:
        self._overlay = QWidget(self)
        self._overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._overlay.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self._overlay)
        lay.setContentsMargins(8, 4, 8, 12)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        self._mode_title = QLabel("")
        self._mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_title.setStyleSheet(
            "color: #1a1a1a; font-size: 15px; font-weight: 600; background: transparent;"
        )
        lay.addWidget(self._mode_title)

        self._mode_desc = QLabel("")
        self._mode_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_desc.setWordWrap(True)
        self._mode_desc.setStyleSheet(
            "color: #333; font-size: 12px; background: transparent;"
        )
        lay.addWidget(self._mode_desc)

        self._reset_btn = QPushButton("Reset pressed keys")
        self._reset_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_btn.clicked.connect(self.reset_clicked.emit)
        self._reset_btn.setVisible(False)
        lay.addWidget(self._reset_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._overlay.raise_()

    def set_mode_info(self, title: str, description: str, show_reset: bool) -> None:
        self._mode_title.setText(title)
        self._mode_desc.setText(description)
        self._reset_btn.setVisible(show_reset)
        self._position_overlay()

    def _slot_index(self, slot: str | None) -> int | None:
        if not slot or slot not in NAME_TO_INDEX:
            return None
        idx = NAME_TO_INDEX[slot]
        if idx >= len(self._geoms):
            return None
        return idx

    def set_key_down(self, slot: str | None, is_down: bool) -> None:
        idx = self._slot_index(slot)
        if idx is None:
            return
        if is_down:
            self._held.add(idx)
        else:
            self._held.discard(idx)
        self.update()

    def mark_visited(self, slot: str | None) -> None:
        idx = self._slot_index(slot)
        if idx is None:
            return
        self._visited.add(idx)
        self.update()

    def mark_solo(self, slot: str | None) -> None:
        idx = self._slot_index(slot)
        if idx is None:
            return
        if idx in self._chord_marked:
            return
        self._solo_marked.add(idx)
        self.update()

    def mark_chord(self, slot: str | None) -> None:
        idx = self._slot_index(slot)
        if idx is None:
            return
        self._solo_marked.discard(idx)
        self._chord_marked.add(idx)
        self.update()

    def set_chord_active(self, slots: set[str]) -> None:
        active: set[int] = set()
        for slot in slots:
            idx = self._slot_index(slot)
            if idx is not None:
                active.add(idx)
        self._chord_active = active
        self.update()

    def clear_held(self) -> None:
        self._held.clear()
        self._chord_active.clear()
        self.update()

    def clear_marks(self) -> None:
        self._visited.clear()
        self._solo_marked.clear()
        self._chord_marked.clear()
        self._chord_active.clear()
        self.update()

    def clear_pressed(self) -> None:
        self._held.clear()
        self.clear_marks()

    def _target_rect(self) -> QRectF:
        side = self.contentsRect()
        scale = min(side.width() / self._canvas_w, side.height() / self._canvas_h)
        w = self._canvas_w * scale
        h = self._canvas_h * scale
        x = side.x() + (side.width() - w) / 2
        y = side.y() + (side.height() - h) / 2
        return QRectF(x, y, w, h)

    def _position_overlay(self) -> None:
        target = self._target_rect()
        hint = self._overlay.sizeHint()
        w = min(int(target.width() * 0.7), max(hint.width(), 280))
        h = hint.height()
        x = int(target.x() + (target.width() - w) / 2)
        y = int(target.y() + target.height() - h - 8)
        self._overlay.setGeometry(x, y, w, h)
        self._overlay.raise_()

    def _draw_slots(self, painter: QPainter, indices: set[int], color: QColor) -> None:
        if not indices:
            return
        painter.setBrush(color)
        for idx in indices:
            if 0 <= idx < len(self._geoms):
                painter.drawPath(self._geoms[idx].path)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), BG_GRAY)

        target = self._target_rect()
        scale = target.width() / self._canvas_w

        painter.fillRect(target, BG_GRAY)

        png_rect = QRectF(
            target.x() + self._offset_x * scale,
            target.y() + self._offset_y * scale,
            self._png_w * scale,
            self._png_h * scale,
        )
        painter.drawImage(png_rect, self._png)

        layers = (
            (self._visited, PALE_BLUE),
            (self._solo_marked, MARK_GRAY),
            (self._chord_marked, PALE_ORANGE),
            (self._chord_active, ORANGE),
            (self._held, GREEN),
        )
        if any(indices for indices, _ in layers):
            painter.save()
            painter.translate(png_rect.topLeft())
            painter.scale(scale, scale)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
            painter.setPen(Qt.PenStyle.NoPen)
            for indices, color in layers:
                self._draw_slots(painter, indices, color)
            painter.restore()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_overlay()
        self.update()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._position_overlay()
