"""Keyboard display widget: padded gray canvas, PNG, multiply key highlights."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from .key_map_fr import NAME_TO_INDEX, SLOT_NAMES
from .svg_keys import KeyGeom, load_key_geometries

BG_GRAY = QColor(128, 128, 128)  # 50% gray
PAD_X = 0.10  # left/right grey (half of original 0.20)
PAD_Y_TOP = 0.15  # above keyboard (half of original 0.30)
PAD_Y_BOTTOM = 0.30  # below keyboard (same as original vertical pad)
# Fixed height for title + subtitle + Reset; placed closer to keyboard (1/3 above, 2/3 below).
CONTENT_H = 100

GREEN = QColor(0, 220, 0)
PALE_BLUE = QColor(0xA8, 0xD4, 0xF0)
MARK_GRAY = QColor(0xB0, 0xB0, 0xB0)
PALE_ORANGE = QColor(0xF0, 0xC0, 0x90)
ORANGE = QColor(0xFF, 0x8C, 0x00)


class KeyboardWidget(QWidget):
    reset_clicked = Signal()
    mark_erased = Signal(str)  # slot name cleared by click/drag

    def __init__(self, png_path: Path, svg_path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        self._png = QImage(str(png_path))
        if self._png.isNull():
            raise FileNotFoundError(png_path)
        self._png_w = self._png.width()
        self._png_h = self._png.height()
        self._canvas_w = self._png_w * (1 + 2 * PAD_X)

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

        self._erase_enabled = False
        self._erasing = False
        self._last_erased_idx: int | None = None

        # Cached layout rects (widget coords), updated on resize/paint.
        self._lay_target = QRectF()
        self._lay_png = QRectF()
        self._lay_bottom = QRectF()
        self._lay_scale = 1.0

        self.setMinimumSize(640, 320)
        self._build_overlay()

    def _build_overlay(self) -> None:
        # Full bottom-pad host: spacer 1/3 | content ~100px | spacer 2/3
        self._overlay = QWidget(self)
        self._overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._overlay.setStyleSheet("background: transparent;")
        host = QVBoxLayout(self._overlay)
        host.setContentsMargins(0, 0, 0, 0)
        host.setSpacing(0)
        host.addStretch(1)

        self._content = QWidget(self._overlay)
        self._content.setFixedHeight(CONTENT_H)
        self._content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self._content)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self._mode_title = QLabel("")
        self._mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_title.setStyleSheet(
            "color: #1a1a1a; font-size: 18px; font-weight: 600; background: transparent;"
        )
        lay.addWidget(self._mode_title)

        self._mode_desc = QLabel("")
        self._mode_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_desc.setWordWrap(False)
        self._mode_desc.setStyleSheet(
            "color: #333; font-size: 14px; background: transparent;"
        )
        lay.addWidget(self._mode_desc)

        lay.addSpacing(10)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_btn.setMinimumWidth(110)
        self._reset_btn.setFixedHeight(32)
        self._reset_style_visible = """
            QPushButton {
                background-color: #e6e6e6;
                color: #1a1a1a;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 6px 18px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #f2f2f2; }
            QPushButton:pressed { background-color: #cfcfcf; }
        """
        self._reset_style_invisible = """
            QPushButton {
                background-color: transparent;
                color: transparent;
                border: 1px solid transparent;
                border-radius: 5px;
                padding: 6px 18px;
                font-size: 14px;
                font-weight: 600;
            }
        """
        self._reset_btn.setStyleSheet(self._reset_style_invisible)
        self._reset_btn.setEnabled(False)
        self._reset_btn.clicked.connect(self.reset_clicked.emit)
        self._reset_btn.setVisible(True)
        lay.addWidget(self._reset_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        host.addWidget(self._content, 0, Qt.AlignmentFlag.AlignHCenter)
        host.addStretch(2)
        self._overlay.raise_()

    def set_mode_info(self, title: str, description: str, show_reset: bool) -> None:
        self._mode_title.setText(title)
        self._mode_desc.setText(description)
        # Keep Reset in the layout always (invisible in Freeway) so spacing stays stable.
        self._reset_btn.setVisible(True)
        self._reset_btn.setEnabled(show_reset)
        self._reset_btn.setStyleSheet(
            self._reset_style_visible if show_reset else self._reset_style_invisible
        )
        self._reset_btn.setCursor(
            Qt.CursorShape.PointingHandCursor if show_reset else Qt.CursorShape.ArrowCursor
        )
        self._erase_enabled = show_reset
        self._erasing = False
        self._last_erased_idx = None
        self.unsetCursor()
        self._recompute_layout()
        self._apply_overlay_geometry()

    def clear_mark_at(self, idx: int) -> bool:
        """Clear sticky marks for one key index. Returns True if anything changed."""
        if idx < 0 or idx >= len(self._geoms):
            return False
        changed = False
        if idx in self._visited:
            self._visited.discard(idx)
            changed = True
        if idx in self._solo_marked:
            self._solo_marked.discard(idx)
            changed = True
        if idx in self._chord_marked:
            self._chord_marked.discard(idx)
            changed = True
        if changed:
            if 0 <= idx < len(SLOT_NAMES):
                self.mark_erased.emit(SLOT_NAMES[idx])
            self.update()
        return changed

    def _widget_to_png(self, pos) -> QPointF | None:
        png = self._lay_png
        scale = self._lay_scale
        if scale <= 0 or png.width() <= 0 or png.height() <= 0:
            return None
        x = (float(pos.x()) - png.x()) / scale
        y = (float(pos.y()) - png.y()) / scale
        if x < 0 or y < 0 or x > self._png_w or y > self._png_h:
            return None
        return QPointF(x, y)

    def _hit_key_index(self, pos) -> int | None:
        pt = self._widget_to_png(pos)
        if pt is None:
            return None
        hits: list[tuple[float, int]] = []
        for i, geom in enumerate(self._geoms):
            if not geom.bbox.contains(pt):
                continue
            if geom.path.contains(pt):
                hits.append((geom.bbox.width() * geom.bbox.height(), i))
        if not hits:
            return None
        hits.sort(key=lambda item: item[0])
        return hits[0][1]

    def _erase_at(self, pos) -> None:
        if not self._erase_enabled:
            return
        idx = self._hit_key_index(pos)
        if idx is None or idx == self._last_erased_idx:
            return
        self._last_erased_idx = idx
        self.clear_mark_at(idx)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if (
            self._erase_enabled
            and event.button() == Qt.MouseButton.LeftButton
            and self._lay_png.contains(event.position())
        ):
            self._erasing = True
            self._last_erased_idx = None
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self._erase_at(event.position())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._erasing and event.buttons() & Qt.MouseButton.LeftButton:
            self._erase_at(event.position())
            event.accept()
            return
        if self._erase_enabled and self._lay_png.contains(event.position()):
            idx = self._hit_key_index(event.position())
            marked = idx is not None and (
                idx in self._visited
                or idx in self._solo_marked
                or idx in self._chord_marked
            )
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if marked else Qt.CursorShape.ArrowCursor
            )
        elif self._erase_enabled:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._erasing:
            self._erasing = False
            self._last_erased_idx = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        if not self._erasing:
            self.unsetCursor()
        super().leaveEvent(event)

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

    def _recompute_layout(self) -> None:
        """Fit keyboard with obligatory pads; bottom pad never smaller than CONTENT_H."""
        side = self.contentsRect()
        sw = max(1.0, float(side.width()))
        sh = max(1.0, float(side.height()))

        s_w = sw / self._canvas_w
        # Height if bottom pad stays proportional to the image.
        h_prop_unit = self._png_h * (1.0 + PAD_Y_TOP + PAD_Y_BOTTOM)
        s_h_prop = sh / h_prop_unit
        # Height if bottom pad is floored at CONTENT_H (prevents clipping when small).
        top_and_png_unit = self._png_h * (1.0 + PAD_Y_TOP)
        s_h_floor = max(0.01, (sh - CONTENT_H) / top_and_png_unit)
        scale = min(s_w, s_h_prop, s_h_floor)

        png_w = self._png_w * scale
        png_h = self._png_h * scale
        pad_x = self._png_w * PAD_X * scale
        pad_top = self._png_h * PAD_Y_TOP * scale
        pad_bottom = max(self._png_h * PAD_Y_BOTTOM * scale, float(CONTENT_H))

        total_w = png_w + 2 * pad_x
        total_h = pad_top + png_h + pad_bottom
        x0 = float(side.x()) + (sw - total_w) / 2.0
        y0 = float(side.y()) + (sh - total_h) / 2.0

        self._lay_scale = scale
        self._lay_target = QRectF(x0, y0, total_w, total_h)
        self._lay_png = QRectF(x0 + pad_x, y0 + pad_top, png_w, png_h)
        self._lay_bottom = QRectF(x0, self._lay_png.bottom(), total_w, pad_bottom)

    def _apply_overlay_geometry(self) -> None:
        r = self._lay_bottom
        self._overlay.setGeometry(int(r.x()), int(r.y()), max(1, int(r.width())), max(1, int(r.height())))
        self._content.setFixedWidth(max(1, int(r.width())))
        self._overlay.raise_()

    def _draw_slots(self, painter: QPainter, indices: set[int], color: QColor) -> None:
        if not indices:
            return
        painter.setBrush(color)
        for idx in indices:
            if 0 <= idx < len(self._geoms):
                painter.drawPath(self._geoms[idx].path)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        self._recompute_layout()
        self._apply_overlay_geometry()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), BG_GRAY)

        target = self._lay_target
        png_rect = self._lay_png
        scale = self._lay_scale

        painter.fillRect(target, BG_GRAY)
        painter.drawImage(png_rect, self._png)

        # While held, suppress sticky marks so green/orange stay clean (no muddy multiply).
        live = self._held | self._chord_active
        held_green = self._held - self._chord_active
        layers = (
            (self._visited - live, PALE_BLUE),
            (self._solo_marked - live, MARK_GRAY),
            (self._chord_marked - live, PALE_ORANGE),
            (self._chord_active, ORANGE),
            (held_green, GREEN),
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
        self._recompute_layout()
        self._apply_overlay_geometry()
        self.update()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._recompute_layout()
        self._apply_overlay_geometry()
