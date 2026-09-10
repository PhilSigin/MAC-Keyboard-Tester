"""Qt widget key events capture mode."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget

from capture.base import CaptureBackend, KeyCallback
from key_map_fr import MAC_VK, KeyRef


class QtCapture(CaptureBackend):
    name = "Qt"

    def __init__(self, on_key: KeyCallback, target: QWidget) -> None:
        super().__init__(on_key)
        self._target = target
        self._filter = _KeyFilter(self)

    def start(self) -> tuple[bool, str]:
        self._target.installEventFilter(self._filter)
        self._target.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._target.setFocus()
        self._target.grabKeyboard()
        self._active = True
        return True, "Qt key events (focus required; Fn/media often missing)"

    def stop(self) -> None:
        if self._active:
            self._target.removeEventFilter(self._filter)
            self._target.releaseKeyboard()
            self._active = False


class _KeyFilter(QObject):
    def __init__(self, backend: QtCapture) -> None:
        super().__init__()
        self._backend = backend

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            assert isinstance(event, QKeyEvent)
            if event.isAutoRepeat():
                return False
            is_down = event.type() == QEvent.Type.KeyPress
            native = int(event.nativeVirtualKey())
            if native:
                name = MAC_VK.get(native, f"vk_{native:02X}")
                ref = KeyRef("mac_vk", native, name)
            else:
                ref = KeyRef(
                    "qt",
                    int(event.key()),
                    event.text() or f"Qt:{int(event.key())}",
                )
            self._backend.emit(ref, is_down)
            return False
        return False
