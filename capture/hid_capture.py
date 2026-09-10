"""macOS IOHIDManager capture via ctypes (keyboard + consumer usages)."""

from __future__ import annotations

import ctypes
import ctypes.util
from typing import Any

from PySide6.QtCore import QObject, Signal

from capture.base import CaptureBackend, KeyCallback
from key_map_fr import HID_CONSUMER_USAGE, HID_KEYBOARD_USAGE, KeyRef

kHIDPage_KeyboardOrKeypad = 0x07
kHIDPage_Consumer = 0x0C
kHIDPage_AppleVendorKeyboard = 0xFF01
kIOHIDOptionsTypeNone = 0

CFTypeRef = ctypes.c_void_p
CFStringRef = ctypes.c_void_p
CFAllocatorRef = ctypes.c_void_p
CFRunLoopRef = ctypes.c_void_p
IOHIDManagerRef = ctypes.c_void_p
IOHIDValueRef = ctypes.c_void_p
IOHIDElementRef = ctypes.c_void_p
IOReturn = ctypes.c_int32


class _HidBridge(QObject):
    key_event = Signal(object, bool)


def _cf_ptr(obj: Any) -> ctypes.c_void_p:
    """PyObjC CFType → raw pointer for ctypes."""
    import objc

    return ctypes.c_void_p(objc.pyobjc_id(obj))


class HidCapture(CaptureBackend):
    name = "HID"

    def __init__(self, on_key: KeyCallback) -> None:
        super().__init__(on_key)
        self._bridge = _HidBridge()
        self._bridge.key_event.connect(self._on_bridge)
        self._manager = None
        self._cb = None
        self._iokit: Any = None
        self._cf: Any = None
        self._runloop = None
        self._runloop_mode = None

    def _on_bridge(self, ref: KeyRef, is_down: bool) -> None:
        self.emit(ref, is_down)

    def start(self) -> tuple[bool, str]:
        iokit_path = ctypes.util.find_library("IOKit")
        cf_path = ctypes.util.find_library("CoreFoundation")
        if not iokit_path or not cf_path:
            return False, "IOKit/CoreFoundation not found"

        iokit = ctypes.CDLL(iokit_path)
        cf = ctypes.CDLL(cf_path)
        self._iokit = iokit
        self._cf = cf
        self._bind(iokit, cf)

        manager = iokit.IOHIDManagerCreate(None, kIOHIDOptionsTypeNone)
        if not manager:
            return False, "IOHIDManagerCreate failed"

        # Match all HID devices; filter in callback by usage page
        iokit.IOHIDManagerSetDeviceMatching(manager, None)

        CB = ctypes.CFUNCTYPE(
            None, ctypes.c_void_p, IOReturn, ctypes.c_void_p, IOHIDValueRef
        )

        def raw_callback(context: Any, result: int, sender: Any, value: Any) -> None:
            try:
                self._handle_value(value)
            except Exception as exc:  # noqa: BLE001
                print(f"[HID] handler error: {exc}", flush=True)

        self._cb = CB(raw_callback)
        iokit.IOHIDManagerRegisterInputValueCallback(manager, self._cb, None)

        from Quartz import CFRunLoopGetCurrent

        # Common modes so events arrive while Qt is spinning the run loop
        runloop = CFRunLoopGetCurrent()
        mode = CFStringRef.in_dll(cf, "kCFRunLoopCommonModes")
        self._runloop = runloop
        self._runloop_mode = mode
        iokit.IOHIDManagerScheduleWithRunLoop(manager, _cf_ptr(runloop), mode)

        kr = int(iokit.IOHIDManagerOpen(manager, kIOHIDOptionsTypeNone))
        self._manager = manager
        self._active = True

        if kr != 0:
            msg = (
                f"IOHIDManager open=0x{kr & 0xFFFFFFFF:08X}. "
                "Grant Input Monitoring (Privacy & Security) to Terminal/Python/Cursor, then retry."
            )
            return True, msg
        return True, "IOHIDManager listening (keyboard + consumer pages)."

    def stop(self) -> None:
        if self._manager and self._iokit:
            try:
                if self._runloop is not None and self._runloop_mode is not None:
                    self._iokit.IOHIDManagerUnscheduleFromRunLoop(
                        self._manager,
                        _cf_ptr(self._runloop),
                        self._runloop_mode,
                    )
                self._iokit.IOHIDManagerClose(self._manager, kIOHIDOptionsTypeNone)
            except Exception as exc:  # noqa: BLE001
                print(f"[HID] stop error: {exc}", flush=True)
        self._manager = None
        self._cb = None
        self._runloop = None
        self._runloop_mode = None
        self._active = False

    def _handle_value(self, value: Any) -> None:
        iokit = self._iokit
        element = iokit.IOHIDValueGetElement(value)
        if not element:
            return
        page = int(iokit.IOHIDElementGetUsagePage(element))
        usage = int(iokit.IOHIDElementGetUsage(element))
        ival = int(iokit.IOHIDValueGetIntegerValue(value))
        is_down = ival != 0

        if page == kHIDPage_KeyboardOrKeypad:
            if usage < 4:
                return
            name = HID_KEYBOARD_USAGE.get(usage, f"kbd_{usage:02X}")
            self._bridge.key_event.emit(KeyRef("hid_kbd", usage, name), is_down)
        elif page == kHIDPage_Consumer:
            name = HID_CONSUMER_USAGE.get(usage, f"cons_{usage:02X}")
            self._bridge.key_event.emit(KeyRef("hid_consumer", usage, name), is_down)
        elif page == kHIDPage_AppleVendorKeyboard:
            if usage in (0x03, 0x01, 0x0A):
                self._bridge.key_event.emit(KeyRef("flag", "fn", "fn"), is_down)
            else:
                self._bridge.key_event.emit(
                    KeyRef("hid_kbd", usage, f"av_{usage:02X}"), is_down
                )

    def _bind(self, iokit: ctypes.CDLL, cf: ctypes.CDLL) -> None:
        iokit.IOHIDManagerCreate.restype = IOHIDManagerRef
        iokit.IOHIDManagerCreate.argtypes = [CFAllocatorRef, ctypes.c_uint32]
        iokit.IOHIDManagerSetDeviceMatching.argtypes = [IOHIDManagerRef, CFTypeRef]
        iokit.IOHIDManagerRegisterInputValueCallback.argtypes = [
            IOHIDManagerRef,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        iokit.IOHIDManagerScheduleWithRunLoop.argtypes = [
            IOHIDManagerRef,
            CFRunLoopRef,
            CFStringRef,
        ]
        iokit.IOHIDManagerUnscheduleFromRunLoop.argtypes = [
            IOHIDManagerRef,
            CFRunLoopRef,
            CFStringRef,
        ]
        iokit.IOHIDManagerOpen.restype = IOReturn
        iokit.IOHIDManagerOpen.argtypes = [IOHIDManagerRef, ctypes.c_uint32]
        iokit.IOHIDManagerClose.restype = IOReturn
        iokit.IOHIDManagerClose.argtypes = [IOHIDManagerRef, ctypes.c_uint32]
        iokit.IOHIDValueGetElement.restype = IOHIDElementRef
        iokit.IOHIDValueGetElement.argtypes = [IOHIDValueRef]
        iokit.IOHIDElementGetUsagePage.restype = ctypes.c_uint32
        iokit.IOHIDElementGetUsagePage.argtypes = [IOHIDElementRef]
        iokit.IOHIDElementGetUsage.restype = ctypes.c_uint32
        iokit.IOHIDElementGetUsage.argtypes = [IOHIDElementRef]
        iokit.IOHIDValueGetIntegerValue.restype = ctypes.c_long
        iokit.IOHIDValueGetIntegerValue.argtypes = [IOHIDValueRef]
