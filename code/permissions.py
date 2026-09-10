"""macOS Input Monitoring permission checks and prompts."""

from __future__ import annotations


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


def open_privacy_and_security_settings() -> None:
    """Open System Settings → Privacy & Security (Input Monitoring pane)."""
    _open_privacy_pane("Privacy_ListenEvent")


def ensure_capture_permissions(*, prompt: bool = True) -> tuple[bool, str]:
    """
    Ensure Input Monitoring for CGEventTap key capture.

    Input Monitoring (Allow Keystrokes) is required. Without it a tap may still
    be created but only modifier / FlagsChanged events arrive.

    Does not open System Settings automatically; the UI can call
    open_privacy_and_security_settings() when the user asks.
    """
    if input_monitoring_granted():
        return True, "Input Monitoring is granted."

    if prompt:
        print("[permissions] requesting Input Monitoring…", flush=True)
        request_input_monitoring()
        if input_monitoring_granted():
            return True, "Input Monitoring granted."

    return (
        False,
        "Input Monitoring (Allow Keystrokes) is not granted. "
        "Without it, normal keys are not delivered to the app "
        "(only some modifier keys may appear). "
        "Enable Mac Keyboard Test in System Settings → Privacy & Security "
        "→ Input Monitoring, then restart the app.",
    )
