"""Capture backend interface and terminal logging."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from .key_map_fr import KeyRef, resolve_slot

KeyCallback = Callable[[str | None, bool, KeyRef], None]


def log_event(backend: str, is_down: bool, ref: KeyRef, slot: str | None) -> None:
    state = "DOWN" if is_down else "UP  "
    mapped = f"slot={slot:<14} mapped=yes" if slot else "slot=-              mapped=NO"
    code = ref.code if isinstance(ref.code, str) else f"0x{int(ref.code):02X}"
    name = ref.name or "-"
    print(
        f"[{backend:<10}] {state}  kind={ref.kind:<12} code={code:<8} name={name:<16} {mapped}",
        flush=True,
    )


class CaptureBackend(ABC):
    name: str = "base"

    def __init__(self, on_key: KeyCallback) -> None:
        self.on_key = on_key
        self._active = False

    @abstractmethod
    def start(self) -> tuple[bool, str]:
        """Start capture. Returns (ok, message)."""

    @abstractmethod
    def stop(self) -> None:
        ...

    def emit(self, ref: KeyRef, is_down: bool) -> None:
        slot = resolve_slot(ref)
        log_event(self.name, is_down, ref, slot)
        self.on_key(slot, is_down, ref)

    @property
    def active(self) -> bool:
        return self._active
