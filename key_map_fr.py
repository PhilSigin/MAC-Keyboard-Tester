"""Physical key slots for Apple A1243 French AZERTY + code aliases."""

from __future__ import annotations

from dataclasses import dataclass

# Ordered to match svg_keys.load_key_geometries() sort (row Y, then X).
SLOT_NAMES: list[str] = [
    # row0 function
    "esc",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
    "eject",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    # row1 numbers + nav + numpad ops
    "at",
    "amp",
    "eacute",
    "quotedbl",
    "apostrophe",
    "parenleft",
    "section",
    "egrave",
    "exclam",
    "ccedilla",
    "agrave",
    "parenright",
    "minus",
    "backspace",
    "fn",
    "home",
    "pageup",
    "kp_clear",
    "kp_equal",
    "kp_divide",
    "kp_multiply",
    # row2 letters + return + nav + numpad
    "tab",
    "a",
    "z",
    "e",
    "r",
    "t",
    "y",
    "u",
    "i",
    "o",
    "p",
    "dead_circumflex",
    "dollar",
    "return",
    "fwd_delete",
    "end",
    "pagedown",
    "kp_7",
    "kp_8",
    "kp_9",
    "kp_subtract",
    # row3 home row
    "capslock",
    "q",
    "s",
    "d",
    "f",
    "g",
    "h",
    "j",
    "k",
    "l",
    "m",
    "ugrave",
    "dead_grave",
    "kp_4",
    "kp_5",
    "kp_6",
    "kp_add",
    # row4 shift row
    "shift_l",
    "less",
    "w",
    "x",
    "c",
    "v",
    "b",
    "n",
    "comma",
    "semicolon",
    "colon",
    "equal",
    "shift_r",
    "kp_1",
    "kp_2",
    "kp_3",
    "kp_enter",
    # arrow up (between shift and bottom)
    "up",
    # bottom modifiers + numpad 0 .
    "ctrl_l",
    "alt_l",
    "cmd_l",
    "space",
    "cmd_r",
    "alt_r",
    "ctrl_r",
    "kp_0",
    "kp_decimal",
    # arrow cluster bottom
    "left",
    "down",
    "right",
]


@dataclass(frozen=True)
class KeyRef:
    """Normalized key identity from any capture backend."""

    kind: str  # mac_vk | qt | media | hid | flag
    code: int | str
    name: str = ""


# macOS virtual keycodes (physical positions)
MAC_VK: dict[int, str] = {
    0x35: "esc",
    0x7A: "f1",
    0x78: "f2",
    0x63: "f3",
    0x76: "f4",
    0x60: "f5",
    0x61: "f6",
    0x62: "f7",
    0x64: "f8",
    0x65: "f9",
    0x6D: "f10",
    0x67: "f11",
    0x6F: "f12",
    0x69: "f13",
    0x6B: "f14",
    0x71: "f15",
    0x6A: "f16",
    0x40: "f17",
    0x4F: "f18",
    0x50: "f19",
    # Special / media as virtual keycodes (Karabiner KeyCode.data + common volume)
    0x91: "f1",   # BRIGHTNESS_DOWN
    0x90: "f2",   # BRIGHTNESS_UP
    0xA0: "f3",   # MISSION_CONTROL / EXPOSE_ALL
    0x82: "f3",   # DASHBOARD (legacy)
    0x83: "f4",   # LAUNCHPAD
    0x4A: "f10",  # Mute
    0x49: "f11",  # Volume Down
    0x48: "f12",  # Volume Up
    # eject often arrives as media; keep vk if seen
    0x0A: "at",  # ISO section / @# on FR
    0x12: "amp",
    0x13: "eacute",
    0x14: "quotedbl",
    0x15: "apostrophe",
    0x17: "parenleft",
    0x16: "section",
    0x1A: "egrave",
    0x1C: "exclam",
    0x19: "ccedilla",
    0x1D: "agrave",
    0x1B: "parenright",
    0x18: "minus",
    0x33: "backspace",
    0x30: "tab",
    0x0C: "a",
    0x0D: "z",
    0x0E: "e",
    0x0F: "r",
    0x11: "t",
    0x10: "y",
    0x20: "u",
    0x22: "i",
    0x1F: "o",
    0x23: "p",
    0x21: "dead_circumflex",
    0x1E: "dollar",
    0x24: "return",
    0x39: "capslock",
    0x00: "q",
    0x01: "s",
    0x02: "d",
    0x03: "f",
    0x05: "g",
    0x04: "h",
    0x26: "j",
    0x28: "k",
    0x25: "l",
    0x29: "m",
    0x27: "ugrave",
    0x2A: "dead_grave",
    0x38: "shift_l",
    0x32: "less",  # ISO <>
    0x06: "w",
    0x07: "x",
    0x08: "c",
    0x09: "v",
    0x0B: "b",
    0x2D: "n",
    0x2E: "comma",
    0x2B: "semicolon",
    0x2F: "colon",
    0x2C: "equal",
    0x3C: "shift_r",
    0x3B: "ctrl_l",
    0x3A: "alt_l",
    0x37: "cmd_l",
    0x31: "space",
    0x36: "cmd_r",
    0x3D: "alt_r",
    0x3E: "ctrl_r",
    0x3F: "fn",
    0x72: "help",  # sometimes home-adjacent
    0x73: "home",
    0x74: "pageup",
    0x75: "fwd_delete",
    0x77: "end",
    0x79: "pagedown",
    0x7B: "left",
    0x7C: "right",
    0x7D: "down",
    0x7E: "up",
    0x47: "kp_clear",
    0x51: "kp_equal",
    0x4B: "kp_divide",
    0x43: "kp_multiply",
    0x4E: "kp_subtract",
    0x45: "kp_add",
    0x4C: "kp_enter",
    0x41: "kp_decimal",
    0x52: "kp_0",
    0x53: "kp_1",
    0x54: "kp_2",
    0x55: "kp_3",
    0x56: "kp_4",
    0x57: "kp_5",
    0x58: "kp_6",
    0x59: "kp_7",
    0x5B: "kp_8",
    0x5C: "kp_9",
}

# NX_KEYTYPE_* (IOKit/hidsystem/ev_keymap.h) → physical F-row slots
MEDIA_TO_SLOT = {
    0: "f12",   # SOUND_UP
    1: "f11",   # SOUND_DOWN
    2: "f2",    # BRIGHTNESS_UP
    3: "f1",    # BRIGHTNESS_DOWN
    7: "f10",   # MUTE
    14: "eject",  # EJECT
    16: "f8",   # PLAY
    17: "f9",   # NEXT
    18: "f7",   # PREVIOUS
    19: "f9",   # FAST
    20: "f7",   # REWIND
    21: "f6",   # ILLUMINATION_UP
    22: "f5",   # ILLUMINATION_DOWN
    23: "f5",   # ILLUMINATION_TOGGLE
}

# HID Keyboard page 0x07 usage → slot (USB HID usages)
HID_KEYBOARD_USAGE: dict[int, str] = {
    0x29: "esc",
    0x3A: "f1",
    0x3B: "f2",
    0x3C: "f3",
    0x3D: "f4",
    0x3E: "f5",
    0x3F: "f6",
    0x40: "f7",
    0x41: "f8",
    0x42: "f9",
    0x43: "f10",
    0x44: "f11",
    0x45: "f12",
    0x68: "f13",
    0x69: "f14",
    0x6A: "f15",
    0x6B: "f16",
    0x6C: "f17",
    0x6D: "f18",
    0x6E: "f19",
    0x35: "at",  # `~ position; on ISO FR @#
    0x1E: "amp",
    0x1F: "eacute",
    0x20: "quotedbl",
    0x21: "apostrophe",
    0x22: "parenleft",
    0x23: "section",
    0x24: "egrave",
    0x25: "exclam",
    0x26: "ccedilla",
    0x27: "agrave",
    0x2D: "parenright",
    0x2E: "minus",
    0x2A: "backspace",
    0x2B: "tab",
    0x14: "a",
    0x1A: "z",
    0x08: "e",
    0x15: "r",
    0x17: "t",
    0x1C: "y",
    0x18: "u",
    0x0C: "i",
    0x12: "o",
    0x13: "p",
    0x2F: "dead_circumflex",
    0x30: "dollar",
    0x28: "return",
    0x39: "capslock",
    0x04: "q",
    0x16: "s",
    0x07: "d",
    0x09: "f",
    0x0A: "g",
    0x0B: "h",
    0x0D: "j",
    0x0E: "k",
    0x0F: "l",
    0x33: "m",
    0x34: "ugrave",
    0x31: "dead_grave",
    0xE1: "shift_l",
    0x64: "less",  # ISO
    0x1D: "w",
    0x1B: "x",
    0x06: "c",
    0x19: "v",
    0x05: "b",
    0x11: "n",
    0x36: "comma",
    0x37: "semicolon",
    0x38: "colon",
    0x32: "equal",  # may vary on ISO
    0xE5: "shift_r",
    0xE0: "ctrl_l",
    0xE2: "alt_l",
    0xE3: "cmd_l",
    0x2C: "space",
    0xE7: "cmd_r",
    0xE6: "alt_r",
    0xE4: "ctrl_r",
    0x4A: "home",
    0x4B: "pageup",
    0x4C: "fwd_delete",
    0x4D: "end",
    0x4E: "pagedown",
    0x50: "left",
    0x4F: "right",
    0x51: "down",
    0x52: "up",
    0x53: "kp_clear",
    0x54: "kp_divide",
    0x55: "kp_multiply",
    0x56: "kp_subtract",
    0x57: "kp_add",
    0x58: "kp_enter",
    0x63: "kp_decimal",
    0x62: "kp_0",
    0x59: "kp_1",
    0x5A: "kp_2",
    0x5B: "kp_3",
    0x5C: "kp_4",
    0x5D: "kp_5",
    0x5E: "kp_6",
    0x5F: "kp_7",
    0x60: "kp_8",
    0x61: "kp_9",
    0x67: "kp_equal",
}

# HID Consumer page 0x0C
HID_CONSUMER_USAGE: dict[int, str] = {
    0xE9: "f12",  # Volume Increment
    0xEA: "f11",  # Volume Decrement
    0xE2: "f10",  # Mute
    0xCD: "f8",   # Play/Pause
    0xB5: "f9",   # Scan Next
    0xB6: "f7",   # Scan Previous
    0x6F: "f2",   # Brightness up
    0x70: "f1",   # Brightness down
    0xB8: "eject",
}

# Qt.Key_* → slot (layout-ish; nativeScanCode preferred when available)
QT_KEY_TO_SLOT: dict[int, str] = {}


def _init_qt_map() -> None:
    from PySide6.QtCore import Qt

    mapping = {
        Qt.Key.Key_Escape: "esc",
        Qt.Key.Key_F1: "f1",
        Qt.Key.Key_F2: "f2",
        Qt.Key.Key_F3: "f3",
        Qt.Key.Key_F4: "f4",
        Qt.Key.Key_F5: "f5",
        Qt.Key.Key_F6: "f6",
        Qt.Key.Key_F7: "f7",
        Qt.Key.Key_F8: "f8",
        Qt.Key.Key_F9: "f9",
        Qt.Key.Key_F10: "f10",
        Qt.Key.Key_F11: "f11",
        Qt.Key.Key_F12: "f12",
        Qt.Key.Key_F13: "f13",
        Qt.Key.Key_F14: "f14",
        Qt.Key.Key_F15: "f15",
        Qt.Key.Key_F16: "f16",
        Qt.Key.Key_F17: "f17",
        Qt.Key.Key_F18: "f18",
        Qt.Key.Key_F19: "f19",
        Qt.Key.Key_Backspace: "backspace",
        Qt.Key.Key_Tab: "tab",
        Qt.Key.Key_Return: "return",
        Qt.Key.Key_Enter: "kp_enter",
        Qt.Key.Key_CapsLock: "capslock",
        Qt.Key.Key_Shift: "shift_l",
        Qt.Key.Key_Control: "ctrl_l",
        Qt.Key.Key_Alt: "alt_l",
        Qt.Key.Key_Meta: "cmd_l",
        Qt.Key.Key_Space: "space",
        Qt.Key.Key_Home: "home",
        Qt.Key.Key_End: "end",
        Qt.Key.Key_PageUp: "pageup",
        Qt.Key.Key_PageDown: "pagedown",
        Qt.Key.Key_Delete: "fwd_delete",
        Qt.Key.Key_Left: "left",
        Qt.Key.Key_Right: "right",
        Qt.Key.Key_Up: "up",
        Qt.Key.Key_Down: "down",
        Qt.Key.Key_Clear: "kp_clear",
        Qt.Key.Key_Equal: "equal",
        Qt.Key.Key_Slash: "kp_divide",
        Qt.Key.Key_Asterisk: "kp_multiply",
        Qt.Key.Key_Minus: "minus",
        Qt.Key.Key_Plus: "kp_add",
        Qt.Key.Key_Period: "kp_decimal",
        Qt.Key.Key_VolumeUp: "f12",
        Qt.Key.Key_VolumeDown: "f11",
        Qt.Key.Key_VolumeMute: "f10",
        Qt.Key.Key_MediaPlay: "f8",
        Qt.Key.Key_MediaNext: "f9",
        Qt.Key.Key_MediaPrevious: "f7",
        Qt.Key.Key_Dead_Circumflex: "dead_circumflex",
        Qt.Key.Key_Dead_Grave: "dead_grave",
        Qt.Key.Key_Less: "less",
        Qt.Key.Key_Greater: "less",
    }
    # Letters A-Z by physical FR labels via text is unreliable; use mac vk from native
    for ch, slot in [
        ("A", "a"),
        ("Z", "z"),
        ("E", "e"),
        ("R", "r"),
        ("T", "t"),
        ("Y", "y"),
        ("U", "u"),
        ("I", "i"),
        ("O", "o"),
        ("P", "p"),
        ("Q", "q"),
        ("S", "s"),
        ("D", "d"),
        ("F", "f"),
        ("G", "g"),
        ("H", "h"),
        ("J", "j"),
        ("K", "k"),
        ("L", "l"),
        ("M", "m"),
        ("W", "w"),
        ("X", "x"),
        ("C", "c"),
        ("V", "v"),
        ("B", "b"),
        ("N", "n"),
    ]:
        mapping[getattr(Qt.Key, f"Key_{ch}")] = slot
    QT_KEY_TO_SLOT.update({int(k): v for k, v in mapping.items()})


_init_qt_map()

NAME_TO_INDEX = {name: i for i, name in enumerate(SLOT_NAMES)}


def resolve_slot(ref: KeyRef) -> str | None:
    if ref.kind == "slot":
        return str(ref.code) if str(ref.code) in NAME_TO_INDEX else None
    if ref.kind == "mac_vk":
        slot = MAC_VK.get(int(ref.code))
    elif ref.kind == "media":
        slot = MEDIA_TO_SLOT.get(int(ref.code))
    elif ref.kind == "hid_kbd":
        slot = HID_KEYBOARD_USAGE.get(int(ref.code))
    elif ref.kind == "hid_consumer":
        slot = HID_CONSUMER_USAGE.get(int(ref.code))
    elif ref.kind == "qt":
        slot = QT_KEY_TO_SLOT.get(int(ref.code))
    elif ref.kind == "flag" and (ref.name == "fn" or ref.code == "fn"):
        slot = "fn"
    else:
        slot = None
    if slot is None and ref.name in NAME_TO_INDEX:
        return ref.name
    return slot
