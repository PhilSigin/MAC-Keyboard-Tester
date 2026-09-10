#!/usr/bin/env python3
"""Mac A1243 French keyboard tester (PySide6)."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from key_map_fr import KeyRef
from keyboard_widget import KeyboardWidget
from tap_capture import TapCapture

ROOT = Path(__file__).resolve().parent
PNG = ROOT / "materials" / "Keyboard-8-bit.png"
SVG = ROOT / "materials" / "Keyboard-8-bit.svg"
ICON = ROOT / "materials" / "MacKeyboardTest.icns"

MODE_FREEWAY = "Freeway"
MODE_COVERAGE = "Coverage"
MODE_SIMULTANEOUS = "Simultaneous"

MODES = (MODE_FREEWAY, MODE_COVERAGE, MODE_SIMULTANEOUS)

MODE_INFO: dict[str, tuple[str, str, bool]] = {
    MODE_FREEWAY: (
        "Freeway",
        "Live highlight while keys are held.",
        False,
    ),
    MODE_COVERAGE: (
        "Coverage",
        "Marks every key you press so you can see what’s been tested.",
        True,
    ),
    MODE_SIMULTANEOUS: (
        "Simultaneous",
        "Flags multi-key presses in orange; single presses turn gray.",
        True,
    ),
}

TYPED_MAX_LEN = 500


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Apple Keyboard Test - A1243 FR")
        self.setWindowIcon(QIcon(str(ICON)))
        self._backend = None
        self._mode = MODE_FREEWAY
        self._down_slots: set[str] = set()
        self._chord_involved: set[str] = set()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        bar = QHBoxLayout()
        self._status = QLabel("")
        self._status.setWordWrap(True)
        bar.addWidget(self._status, stretch=1)
        bar.addWidget(QLabel("Mode:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(list(MODES))
        self._mode_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        bar.addWidget(self._mode_combo)
        layout.addLayout(bar)

        self._keyboard = KeyboardWidget(PNG, SVG)
        self._keyboard.reset_clicked.connect(self._reset_marks)
        self._keyboard.mark_erased.connect(self._on_mark_erased)
        layout.addWidget(self._keyboard, stretch=1)

        self._typed = QPlainTextEdit()
        self._typed.setReadOnly(True)
        self._typed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._typed.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._typed.setMaximumBlockCount(20)
        self._typed.setFixedHeight(72)
        self._typed.setPlaceholderText("Typed preview…")
        self._typed.setStyleSheet(
            "QPlainTextEdit { background: #f5f5f5; color: #222; border: 1px solid #999; }"
        )
        layout.addWidget(self._typed)

        self.resize(1280, 560)
        self._apply_mode_ui(MODE_FREEWAY)
        self._start_capture()

    def _apply_mode_ui(self, mode: str) -> None:
        title, desc, show_reset = MODE_INFO[mode]
        self._keyboard.set_mode_info(title, desc, show_reset)

    def _on_mode_changed(self, mode: str) -> None:
        if mode not in MODE_INFO:
            return
        self._mode = mode
        self._down_slots.clear()
        self._chord_involved.clear()
        self._keyboard.clear_pressed()
        self._apply_mode_ui(mode)
        print(f"\n=== Test mode → {mode} ===", flush=True)

    def _reset_marks(self) -> None:
        self._chord_involved.clear()
        # Keep currently held keys visually down, clear sticky marks only.
        self._keyboard.clear_marks()
        if self._down_slots:
            self._keyboard.set_chord_active(set())
            for slot in self._down_slots:
                self._keyboard.set_key_down(slot, True)
        print("[main] reset pressed-key marks", flush=True)

    def _on_mark_erased(self, slot: str) -> None:
        self._chord_involved.discard(slot)

    def _on_key(self, slot: str | None, is_down: bool, ref: KeyRef) -> None:
        if not slot:
            return

        if self._mode == MODE_FREEWAY:
            self._keyboard.set_key_down(slot, is_down)
            return

        if self._mode == MODE_COVERAGE:
            self._keyboard.set_key_down(slot, is_down)
            if not is_down:
                self._keyboard.mark_visited(slot)
            return

        # Simultaneous
        if is_down:
            self._down_slots.add(slot)
            self._keyboard.set_key_down(slot, True)
            if len(self._down_slots) >= 2:
                self._chord_involved.update(self._down_slots)
                for s in self._down_slots:
                    self._keyboard.mark_chord(s)
                self._keyboard.set_chord_active(set(self._down_slots))
            else:
                self._keyboard.set_chord_active(set())
        else:
            was_chord = slot in self._chord_involved
            self._down_slots.discard(slot)
            self._keyboard.set_key_down(slot, False)
            if was_chord:
                self._keyboard.mark_chord(slot)
            else:
                self._keyboard.mark_solo(slot)
            if len(self._down_slots) >= 2:
                self._keyboard.set_chord_active(set(self._down_slots))
            else:
                self._keyboard.set_chord_active(set())

    def _on_text(self, text: str) -> None:
        # Filter control characters except backspace / delete / newline / tab.
        if text in ("\x7f", "\b"):
            current = self._typed.toPlainText()
            if current:
                self._typed.setPlainText(current[:-1])
                cursor = self._typed.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self._typed.setTextCursor(cursor)
            return

        cleaned = "".join(
            ch for ch in text if ch in ("\n", "\t") or (ch.isprintable() and ord(ch) >= 32)
        )
        if not cleaned:
            return
        current = self._typed.toPlainText()
        merged = (current + cleaned)[-TYPED_MAX_LEN:]
        self._typed.setPlainText(merged)
        cursor = self._typed.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._typed.setTextCursor(cursor)

    def _stop_backend(self) -> None:
        if self._backend is not None:
            try:
                self._backend.stop()
            except Exception as exc:  # noqa: BLE001
                print(f"[main] stop error: {exc}", flush=True)
            self._backend = None
        self._down_slots.clear()
        self._chord_involved.clear()
        self._keyboard.clear_pressed()

    def _start_capture(self) -> None:
        self._stop_backend()
        print("\n=== Capture mode → CGEventTap ===", flush=True)

        backend = TapCapture(self._on_key, on_text=self._on_text)
        ok, msg = backend.start()
        self._backend = backend if ok else None
        self._status.setText(("OK: " if ok else "FAIL: ") + msg)
        print(f"[CGEventTap] start: {msg}", flush=True)
        if not ok:
            QMessageBox.warning(
                self,
                "Capture unavailable",
                msg
                + "\n\nSystem Settings → Privacy & Security → Accessibility "
                "(and Input Monitoring) — enable your terminal / Python / Cursor.",
            )

    def closeEvent(self, event) -> None:  # noqa: N802
        self._stop_backend()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON)))
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
