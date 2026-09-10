"""Parse keyboard SVG hit paths into QPainterPath geometries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath, QTransform

TX = 3381.0
TY = 3818.36
VIEWBOX_W = 1238.16
VIEWBOX_H = 362.64
TOKEN_RE = re.compile(r"[MmHhVvAaLlZz]|[-+]?\d*\.?\d+(?:e[-+]?\d+)?")


@dataclass(frozen=True)
class KeyGeom:
    index: int
    path: QPainterPath
    bbox: QRectF  # PNG pixel space


def _bbox_from_d(d: str) -> tuple[float, float, float, float] | None:
    toks = TOKEN_RE.findall(d)
    x = y = None
    xs: list[float] = []
    ys: list[float] = []
    i = 0

    def add(px: float, py: float) -> None:
        xs.append(px)
        ys.append(py)

    while i < len(toks):
        t = toks[i]
        if t[0].isdigit() or t[0] in "+-.":
            i += 1
            continue
        if t == "M":
            x = float(toks[i + 1]) - TX
            y = float(toks[i + 2]) - TY
            add(x, y)
            i += 3
        elif t == "m":
            x = (x or 0.0) + float(toks[i + 1])
            y = (y or 0.0) + float(toks[i + 2])
            add(x, y)
            i += 3
        elif t == "h":
            x = float(x) + float(toks[i + 1])
            add(x, float(y))
            i += 2
        elif t == "H":
            x = float(toks[i + 1]) - TX
            add(x, float(y))
            i += 2
        elif t == "v":
            y = float(y) + float(toks[i + 1])
            add(float(x), y)
            i += 2
        elif t == "V":
            y = float(toks[i + 1]) - TY
            add(float(x), y)
            i += 2
        elif t == "a":
            x = float(x) + float(toks[i + 6])
            y = float(y) + float(toks[i + 7])
            add(x, y)
            i += 8
        elif t == "A":
            x = float(toks[i + 6]) - TX
            y = float(toks[i + 7]) - TY
            add(x, y)
            i += 8
        elif t == "l":
            x = float(x) + float(toks[i + 1])
            y = float(y) + float(toks[i + 2])
            add(x, y)
            i += 3
        elif t == "L":
            x = float(toks[i + 1]) - TX
            y = float(toks[i + 2]) - TY
            add(x, y)
            i += 3
        elif t in "Zz":
            i += 1
        else:
            i += 1
    if not xs:
        return None
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def _qpath_from_d(d: str) -> QPainterPath:
    bb = _bbox_from_d(d)
    path = QPainterPath()
    if bb is None:
        return path
    x, y, w, h = bb
    # L-shaped return spans ~2 rows
    if h > 70:
        toks = TOKEN_RE.findall(d)
        x0 = y0 = 0.0
        start_x = start_y = 0.0
        i = 0
        while i < len(toks):
            t = toks[i]
            if t[0].isdigit() or t[0] in "+-.":
                i += 1
                continue
            if t == "M":
                x0 = float(toks[i + 1]) - TX
                y0 = float(toks[i + 2]) - TY
                path.moveTo(x0, y0)
                start_x, start_y = x0, y0
                i += 3
            elif t == "h":
                x0 += float(toks[i + 1])
                path.lineTo(x0, y0)
                i += 2
            elif t == "H":
                x0 = float(toks[i + 1]) - TX
                path.lineTo(x0, y0)
                i += 2
            elif t == "v":
                y0 += float(toks[i + 1])
                path.lineTo(x0, y0)
                i += 2
            elif t == "V":
                y0 = float(toks[i + 1]) - TY
                path.lineTo(x0, y0)
                i += 2
            elif t == "a":
                x0 += float(toks[i + 6])
                y0 += float(toks[i + 7])
                path.lineTo(x0, y0)
                i += 8
            elif t == "A":
                x0 = float(toks[i + 6]) - TX
                y0 = float(toks[i + 7]) - TY
                path.lineTo(x0, y0)
                i += 8
            elif t == "l":
                x0 += float(toks[i + 1])
                y0 += float(toks[i + 2])
                path.lineTo(x0, y0)
                i += 3
            elif t == "L":
                x0 = float(toks[i + 1]) - TX
                y0 = float(toks[i + 2]) - TY
                path.lineTo(x0, y0)
                i += 3
            elif t in "Zz":
                path.closeSubpath()
                x0, y0 = start_x, start_y
                i += 1
            else:
                i += 1
        path.setFillRule(Qt.FillRule.WindingFill)
        return path

    path.addRoundedRect(QRectF(x, y, w, h), 4.8, 4.8)
    return path


def load_key_geometries(
    svg_path: Path,
    png_width: int,
    png_height: int,
) -> list[KeyGeom]:
    root = ET.parse(svg_path).getroot()
    d_list = [p.get("d", "") for p in root.findall(".//{http://www.w3.org/2000/svg}path")]

    sx = png_width / VIEWBOX_W
    sy = png_height / VIEWBOX_H
    scale = QTransform.fromScale(sx, sy)

    raw: list[tuple[int, str, tuple[float, float, float, float]]] = []
    for i, d in enumerate(d_list):
        bb = _bbox_from_d(d)
        if bb is None:
            continue
        raw.append((i, d, bb))

    seen: set[tuple[float, float, float, float]] = set()
    unique: list[tuple[int, str, tuple[float, float, float, float]]] = []
    for i, d, bb in raw:
        key = (round(bb[0], 1), round(bb[1], 1), round(bb[2], 1), round(bb[3], 1))
        if key in seen:
            continue
        seen.add(key)
        unique.append((i, d, bb))

    keys_raw = [item for item in unique if item[2][2] < 1000 and item[2][3] < 250]
    keys_raw.sort(key=lambda item: (round(item[2][1] / 6.0) * 6, item[2][0]))

    result: list[KeyGeom] = []
    for order, (i, d, bb) in enumerate(keys_raw):
        qpath = scale.map(_qpath_from_d(d))
        x, y, w, h = bb
        bbox = QRectF(x * sx, y * sy, w * sx, h * sy)
        result.append(KeyGeom(index=order, path=qpath, bbox=bbox))
    return result
