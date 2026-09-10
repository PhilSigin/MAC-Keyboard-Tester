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

    kind: str  # mac_vk | media | flag
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

NAME_TO_INDEX = {name: i for i, name in enumerate(SLOT_NAMES)}


def resolve_slot(ref: KeyRef) -> str | None:
    if ref.kind == "slot":
        return str(ref.code) if str(ref.code) in NAME_TO_INDEX else None
    if ref.kind == "mac_vk":
        slot = MAC_VK.get(int(ref.code))
    elif ref.kind == "media":
        slot = MEDIA_TO_SLOT.get(int(ref.code))
    elif ref.kind == "flag" and (ref.name == "fn" or ref.code == "fn"):
        slot = "fn"
    else:
        slot = None
    if slot is None and ref.name in NAME_TO_INDEX:
        return ref.name
    return slot
