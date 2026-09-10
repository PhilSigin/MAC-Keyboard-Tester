# How to Launch Mac Keyboard Test

## Install

1. Open the disk image (DMG).
2. Drag **Mac Keyboard Test.app** into the **Applications** folder.
3. Eject the disk image, then open the app from **Applications**.

## If macOS blocks the app

**Mac Keyboard Test.app** is not signed or notarized by Apple. macOS may show a warning that the developer cannot be verified.

Only continue if you downloaded the app from the **official GitHub repository** for this project.

### Option 1: Open Anyway

1. Try to open **Mac Keyboard Test.app** once (it may be blocked).
2. Open **System Settings → Privacy & Security**.
3. Scroll to the **Security** section.
4. Click **Open Anyway** next to the message about **Mac Keyboard Test.app**.
5. Confirm with **Open**.

You usually only need to do this once. After that, macOS should allow the app to open normally.

### Option 2: Remove the quarantine flag (Terminal)

Use this if **Open Anyway** does not appear.

1. Make sure **Mac Keyboard Test.app** is already in **Applications**.
2. Open **Terminal**.
3. Run:

```bash
xattr -dr com.apple.quarantine "/Applications/Mac Keyboard Test.app"
```

If the app is somewhere else:

1. Type this (include a trailing space after `quarantine`):

```bash
xattr -dr com.apple.quarantine 
```

2. Drag **Mac Keyboard Test.app** from Finder into the Terminal window.
3. Press **Enter**.

This removes the quarantine flag from **Mac Keyboard Test.app** only. It does **not** turn off Gatekeeper for other apps.

**Important:** Bypass this warning only if you trust the app and got it from the official GitHub repository. Apple has not reviewed or notarized this release.

## Allow keyboard access (required)

After the app opens, macOS may ask for **Input Monitoring** (Allow Keystrokes). **Mac Keyboard Test** needs this to detect all keys, including **Fn**, media, and brightness keys.

1. Open **System Settings → Privacy & Security → Input Monitoring**.
2. Enable access for **Mac Keyboard Test** (or Terminal / Python if you launch from there).
3. Quit and reopen the app if keys still do not register.

Without Input Monitoring, many keys will not be detected.
