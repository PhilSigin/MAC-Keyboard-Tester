#!/usr/bin/env python3
"""Mac A1243 French keyboard tester (PySide6)."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from key_map_fr import KeyRef, SLOT_NAMES
from keyboard_widget import KeyboardWidget
from tap_capture import TapCapture

ROOT = Path(__file__).resolve().parent
PNG = ROOT / "materials" / "Keyboard-8-bit.png"
SVG = ROOT / "materials" / "Keyboard-8-bit.svg"
ICON = ROOT / "materials" / "Keyboard-Icon.ico"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Apple Keyboard Test - A1243 FR")
        self.setWindowIcon(QIcon(str(ICON)))
        self._backend = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        bar = QHBoxLayout()
        self._status = QLabel("")
        self._status.setWordWrap(True)
        bar.addWidget(self._status, stretch=1)
        layout.addLayout(bar)

        self._keyboard = KeyboardWidget(PNG, SVG)
        layout.addWidget(self._keyboard, stretch=1)

        hint = QLabel(
            f"Slots: {len(SLOT_NAMES)}. Press keys — green Multiply while held. "
            "Watch the terminal for DOWN/UP and mapped=yes/NO."
        )
        hint.setStyleSheet("color: #333;")
        layout.addWidget(hint)

        self.resize(1280, 520)
        self._start_capture()

    def _on_key(self, slot: str | None, is_down: bool, ref: KeyRef) -> None:
        self._keyboard.set_key_down(slot, is_down)

    def _stop_backend(self) -> None:
        if self._backend is not None:
            try:
                self._backend.stop()
            except Exception as exc:  # noqa: BLE001
                print(f"[main] stop error: {exc}", flush=True)
            self._backend = None
        self._keyboard.clear_pressed()

    def _start_capture(self) -> None:
        self._stop_backend()
        print("\n=== Capture mode → CGEventTap ===", flush=True)

        backend = TapCapture(self._on_key)
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
