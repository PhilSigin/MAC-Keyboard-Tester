"""macOS Accessibility + Input Monitoring permission checks and prompts."""

from __future__ import annotations

from typing import Any


def _open_privacy_pane(pane: str) -> None:
    """Open a Privacy & Security pane in System Settings (best-effort)."""
    try:
        from AppKit import NSWorkspace
        from Foundation import NSURL
    except ImportError:
        return

    # Legacy + newer Settings URL forms (macOS varies by version).
    candidates = (
        f"x-apple.systempreferences:com.apple.preference.security?{pane}",
        f"x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?{pane}",
    )
    workspace = NSWorkspace.sharedWorkspace()
    for url_str in candidates:
        url = NSURL.URLWithString_(url_str)
        if url is not None and workspace.openURL_(url):
            return


def input_monitoring_granted() -> bool:
    try:
        from Quartz import CGPreflightListenEventAccess
    except ImportError:
        return False
    return bool(CGPreflightListenEventAccess())


def accessibility_granted() -> bool:
    try:
        from ApplicationServices import AXIsProcessTrusted
    except ImportError:
        return False
    return bool(AXIsProcessTrusted())


def request_input_monitoring() -> bool:
    """Ask macOS to prompt for Input Monitoring (Allow Keystrokes)."""
    try:
        from Quartz import CGRequestListenEventAccess
    except ImportError:
        return False
    try:
        return bool(CGRequestListenEventAccess())
    except Exception:  # noqa: BLE001
        return False


def request_accessibility(prompt: bool = True) -> bool:
    """Check Accessibility; if prompt=True, ask macOS to show the trust dialog."""
    try:
        from ApplicationServices import (
            AXIsProcessTrusted,
            AXIsProcessTrustedWithOptions,
            kAXTrustedCheckOptionPrompt,
        )
    except ImportError:
        return False
    if not prompt:
        return bool(AXIsProcessTrusted())
    try:
        opts: dict[Any, Any] = {kAXTrustedCheckOptionPrompt: True}
        return bool(AXIsProcessTrustedWithOptions(opts))
    except Exception:  # noqa: BLE001
        return bool(AXIsProcessTrusted())


def open_privacy_and_security_settings() -> None:
    """Open System Settings → Privacy & Security (Input Monitoring pane)."""
    _open_privacy_pane("Privacy_ListenEvent")


def ensure_capture_permissions(*, prompt: bool = True) -> tuple[bool, str]:
    """
    Ensure permissions for CGEventTap key capture.

    Input Monitoring (Allow Keystrokes) is required. Without it a tap may still
    be created but only modifier / FlagsChanged events arrive.

    Accessibility is requested as well (helps on some macOS versions) but a
    missing Accessibility grant alone does not block start when Listen access
    is already present.

    Does not open System Settings automatically; the UI can call
    open_privacy_and_security_settings() when the user asks.
    """
    listen_ok = input_monitoring_granted()
    ax_ok = accessibility_granted()

    if listen_ok and ax_ok:
        return True, "Input Monitoring and Accessibility are granted."

    if prompt:
        if not listen_ok:
            print("[permissions] requesting Input Monitoring…", flush=True)
            request_input_monitoring()
        if not ax_ok:
            print("[permissions] requesting Accessibility…", flush=True)
            request_accessibility(prompt=True)

        listen_ok = input_monitoring_granted()
        ax_ok = accessibility_granted()
        if listen_ok and ax_ok:
            return True, "Permissions granted."

    if not listen_ok:
        return (
            False,
            "Input Monitoring (Allow Keystrokes) is not granted. "
            "Without it, normal keys are not delivered to the app "
            "(only some modifier keys may appear). "
            "Enable Mac Keyboard Test in System Settings → Privacy & Security "
            "→ Input Monitoring, then restart the app.",
        )

    if not ax_ok:
        print(
            "[permissions] Accessibility not granted yet; continuing with "
            "Input Monitoring only.",
            flush=True,
        )
    return True, "Input Monitoring granted."
