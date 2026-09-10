"""macOS CGEventTap capture: keys, Fn, media/brightness."""

from __future__ import annotations

import threading
from typing import Any

from PySide6.QtCore import QObject, Signal

from capture.base import CaptureBackend, KeyCallback
from key_map_fr import MAC_VK, MEDIA_TO_SLOT, KeyRef

# NX_SYSDEFINED
_NX_SYSDEFINED = 14
# NSEventSubtype media = 8
_MEDIA_SUBTYPE = 8
# Secondary Fn flag in CGEvent flags
_NS_FUNCTION_KEY_MASK = 1 << 23  # NSEventModifierFlagFunction / NX_DEVICELCMDKEYMASK varies
# Apple uses 0x800000 for fn in some versions; Quartz kCGEventFlagMaskSecondaryFn:
_SECONDARY_FN = 0x00800000


class _TapBridge(QObject):
    key_event = Signal(object, bool)  # KeyRef, is_down


class TapCapture(CaptureBackend):
    name = "CGEventTap"

    def __init__(self, on_key: KeyCallback) -> None:
        super().__init__(on_key)
        self._bridge = _TapBridge()
        self._bridge.key_event.connect(self._on_bridge)
        self._tap = None
        self._source = None
        self._fn_down = False
        self._lock = threading.Lock()

    def _on_bridge(self, ref: KeyRef, is_down: bool) -> None:
        self.emit(ref, is_down)

    def start(self) -> tuple[bool, str]:
        try:
            from Quartz import (
                CFMachPortCreateRunLoopSource,
                CFRunLoopAddSource,
                CFRunLoopGetCurrent,
                CGEventGetFlags,
                CGEventGetIntegerValueField,
                CGEventTapCreate,
                CGEventTapEnable,
                kCFRunLoopCommonModes,
                kCGEventFlagMaskSecondaryFn,
                kCGEventKeyDown,
                kCGEventKeyUp,
                kCGEventFlagsChanged,
                kCGEventTapOptionListenOnly,
                kCGHeadInsertEventTap,
                kCGKeyboardEventKeycode,
                kCGSessionEventTap,
            )
            from Cocoa import NSEvent
        except ImportError as exc:
            return False, f"PyObjC missing: {exc}"

        self._NSEvent = NSEvent
        self._CGEventGetIntegerValueField = CGEventGetIntegerValueField
        self._CGEventGetFlags = CGEventGetFlags
        self._kCGKeyboardEventKeycode = kCGKeyboardEventKeycode
        self._fn_mask = int(kCGEventFlagMaskSecondaryFn)

        mask = (
            (1 << kCGEventKeyDown)
            | (1 << kCGEventKeyUp)
            | (1 << kCGEventFlagsChanged)
            | (1 << _NX_SYSDEFINED)
        )

        def callback(proxy: Any, event_type: int, event: Any, refcon: Any) -> Any:
            try:
                self._handle(event_type, event)
            except Exception as exc:  # noqa: BLE001
                print(f"[CGEventTap] handler error: {exc}", flush=True)
            return event

        self._callback = callback
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionListenOnly,
            mask,
            callback,
            None,
        )
        if not tap:
            return (
                False,
                "CGEventTap failed — grant Accessibility (Privacy & Security) to Terminal/Python/Cursor, then retry",
            )

        source = CFMachPortCreateRunLoopSource(None, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
        CGEventTapEnable(tap, True)
        self._tap = tap
        self._source = source
        self._active = True
        return True, "CGEventTap listening (keys + Fn + media). Needs Accessibility."

    def stop(self) -> None:
        if self._tap is not None:
            try:
                from Quartz import CGEventTapEnable

                CGEventTapEnable(self._tap, False)
            except Exception:  # noqa: BLE001
                pass
        self._tap = None
        self._source = None
        self._active = False

    def _handle(self, event_type: int, event: Any) -> None:
        from Quartz import (
            kCGEventFlagsChanged,
            kCGEventKeyDown,
            kCGEventKeyUp,
        )

        if event_type in (kCGEventKeyDown, kCGEventKeyUp):
            keycode = int(
                self._CGEventGetIntegerValueField(event, self._kCGKeyboardEventKeycode)
            )
            is_down = event_type == kCGEventKeyDown
            name = MAC_VK.get(keycode, f"vk_{keycode:02X}")
            ref = KeyRef("mac_vk", keycode, name)
            self._bridge.key_event.emit(ref, is_down)
            return

        if event_type == kCGEventFlagsChanged:
            flags = int(self._CGEventGetFlags(event))
            fn_down = bool(flags & self._fn_mask)
            if fn_down != self._fn_down:
                self._fn_down = fn_down
                ref = KeyRef("flag", "fn", "fn")
                self._bridge.key_event.emit(ref, fn_down)
            # Also surface modifier keycodes via keycode field when available
            keycode = int(
                self._CGEventGetIntegerValueField(event, self._kCGKeyboardEventKeycode)
            )
            if keycode in MAC_VK and MAC_VK[keycode] != "fn":
                # Infer down from flags is complex; emit toggle based on typical bits
                name = MAC_VK[keycode]
                # Use a simple approach: read whether corresponding flag is set
                is_down = self._modifier_down(name, flags)
                ref = KeyRef("mac_vk", keycode, name)
                self._bridge.key_event.emit(ref, is_down)
            return

        if int(event_type) == _NX_SYSDEFINED:
            ns_event = self._NSEvent.eventWithCGEvent_(event)
            if ns_event is None:
                return
            if int(ns_event.subtype()) != _MEDIA_SUBTYPE:
                return
            data1 = int(ns_event.data1())
            key_code = (data1 & 0xFFFF0000) >> 16
            key_flags = data1 & 0x0000FFFF
            key_state = (key_flags & 0xFF00) >> 8
            is_down = key_state == 0x0A
            if key_state not in (0x0A, 0x0B):
                return
            slot_hint = MEDIA_TO_SLOT.get(key_code, "")
            name = slot_hint or f"media_{key_code}"
            ref = KeyRef("media", key_code, name)
            self._bridge.key_event.emit(ref, is_down)

    @staticmethod
    def _modifier_down(name: str, flags: int) -> bool:
        # CGEventFlag bits (approximate / Quartz)
        masks = {
            "shift_l": 0x00020000,
            "shift_r": 0x00020000,
            "ctrl_l": 0x00040000,
            "ctrl_r": 0x00040000,
            "alt_l": 0x00080000,
            "alt_r": 0x00080000,
            "cmd_l": 0x00100000,
            "cmd_r": 0x00100000,
            "capslock": 0x00010000,
        }
        return bool(flags & masks.get(name, 0))
