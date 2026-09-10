# Apple Keyboard Test - A1243 FR

A macOS tool for testing an Apple A1243 French (AZERTY) keyboard.

Press keys and see them light up on an on-screen layout. Capture uses CGEventTap so you get the full range of key events (letters, modifiers, Fn, media, and brightness). Events are also logged in the terminal so you can check which physical slots map correctly.

## Test modes

- **Freeway** — Live highlight while keys are held.
- **Coverage** — Marks every key you press (pale blue) so you can see what’s been tested. Use **Reset pressed keys** to clear marks.
- **Simultaneous** — Expect one key at a time; multi-key presses flag orange, solo presses turn gray. Use **Reset pressed keys** to clear marks.

A read-only typed preview at the bottom shows characters as macOS would type them (Shift, Backspace, etc.).

Grant **Accessibility** (and **Input Monitoring** if prompted) to your terminal / Python when asked.

```bash
python main.py
```

## Icon credit

App icon from the [Apple Keyboard Icons](https://www.softicons.com/social-media-icons/apple-keyboard-icons-by-creative-ninja/apple-icon) set by [Creative Ninja](https://creativeninjas.com/) (SoftIcons). Free license; commercial use allowed; link to the author’s website required.
