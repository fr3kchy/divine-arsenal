#!/usr/bin/env python3
"""
Sigil Renderer v1.0 — Solomonic Pentacles + Kamea-Trace Sigils
Friday (Venus day) energy: beauty, aesthetics, visual magick.

Generates:
  - SVG pentacles (Solomonic Key of Solomon style)
  - SVG kamea (Agrippa magic squares)
  - SVG kamea-trace sigils (Agrippa's name-on-kamea technique)

Usage:
  python3 sigil_renderer.py pentacle <planet> <num>   → single pentacle
  python3 sigil_renderer.py kamea <planet>            → single kamea
  python3 sigil_renderer.py sigil <planet> <name>     → kamea-trace sigil
  python3 sigil_renderer.py all                       → all 31 SVGs
  python3 sigil_renderer.py sample                    → 7 SVGs (one per planet)
"""

import sys
import os
import math
from pathlib import Path

# === PATHS ===
HOME = Path.home()
SCRIPT_DIR = HOME / ".hermes" / "scripts"
DATA_DIR = HOME / ".hermes" / "data" / "sigils"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# === PLANETARY COLORS ===
PLANET_COLORS = {
    "Saturn":   {"stroke": "#1a1a1a", "fill": "#2a2a2a", "text": "#888888", "accent": "#444444"},
    "Jupiter":  {"stroke": "#1a3a8a", "fill": "#1a2a5a", "text": "#6699ff", "accent": "#3366cc"},
    "Mars":     {"stroke": "#8a1a1a", "fill": "#5a1a1a", "text": "#ff6666", "accent": "#cc3333"},
    "Sun":      {"stroke": "#c8a020", "fill": "#5a4010", "text": "#ffd700", "accent": "#daa520"},
    "Venus":    {"stroke": "#1a6a3a", "fill": "#10402a", "text": "#66ff99", "accent": "#22cc66"},
    "Mercury":  {"stroke": "#8a6a10", "fill": "#5a4010", "text": "#ffaa44", "accent": "#cc8822"},
    "Moon":     {"stroke": "#6a6a8a", "fill": "#30304a", "text": "#ccccff", "accent": "#9999dd"},
}

# === SOLOMONIC PENTACLES (from divine-timing.py SOLOMON_PENTACLES) ===
SOLOMON_PENTACLES = {
    "Saturn": [
        {"num": 1, "name": "First Pentacle",  "power": "Invokes Saturn's spirits",
         "hebrew": "אלהים יהוה", "purpose": "Command over Saturn's forces, longevity, invisibility"},
        {"num": 2, "name": "Second Pentacle", "power": "Protects against enemies",
         "hebrew": "ALHYM YHVH", "purpose": "Defense against all enemies, binding foes"},
        {"num": 3, "name": "Third Pentacle",  "power": "Invisibility",
         "hebrew": "יהוה צבאות", "purpose": "Grants invisibility, discovery of treasures"},
    ],
    "Jupiter": [
        {"num": 1, "name": "First Pentacle",  "power": "Acquires treasures",
         "hebrew": "ABN MAS VH", "purpose": "Wealth, honors, favors from great personages"},
        {"num": 2, "name": "Second Pentacle", "power": "Protects from all dangers",
         "hebrew": "יהוה אלהים צבאות", "purpose": "Protection, defense against perils"},
        {"num": 3, "name": "Third Pentacle",   "power": "Brings honors",
         "hebrew": "אל הויה", "purpose": "Acquiring glory, honor, dignity, riches"},
        {"num": 4, "name": "Fourth Pentacle", "power": "Acquires wealth",
         "hebrew": "יהוה", "purpose": "Great riches, wealth, abundance"},
    ],
    "Mars": [
        {"num": 1, "name": "First Pentacle",  "power": "Victory in war",
         "hebrew": "יהוה אלהים", "purpose": "Victory in war, courage, striking terror in enemies"},
        {"num": 2, "name": "Second Pentacle", "power": "Strikes terror",
         "hebrew": "יהוה צבאות", "purpose": "Causes terror in enemies, destroys opposition"},
        {"num": 3, "name": "Third Pentacle",  "power": "Vengeance",
         "hebrew": "אלהים גבור", "purpose": "Vengeance against enemies, justice"},
    ],
    "Sun": [
        {"num": 1, "name": "First Pentacle",  "power": "Obtains glory",
         "hebrew": "יהוה אלהים צבאות", "purpose": "Glory, acquisition of riches, prevents poverty"},
        {"num": 2, "name": "Second Pentacle", "power": "Causes success",
         "hebrew": "שמש אלהים", "purpose": "Success in all undertakings, favor of all"},
        {"num": 3, "name": "Third Pentacle",  "power": "Acquires gold",
         "hebrew": "יהוה שמש", "purpose": "Great wealth, gold, treasures"},
        {"num": 4, "name": "Fourth Pentacle", "power": "Brings favor",
         "hebrew": "אלהים צבאות", "purpose": "Favor of rulers, success, prevents poverty"},
    ],
    "Venus": [
        {"num": 1, "name": "First Pentacle",  "power": "Obtains love",
         "hebrew": "יהוה", "purpose": "Love, friendship, harmony between people"},
        {"num": 2, "name": "Second Pentacle", "power": "Causes love",
         "hebrew": "אלהים", "purpose": "Inspires love, attraction, beauty"},
        {"num": 3, "name": "Third Pentacle",  "power": "Brings joy",
         "hebrew": "יהוה אלהים", "purpose": "Joy, harmony, reconciliation, peace"},
    ],
    "Mercury": [
        {"num": 1, "name": "First Pentacle",  "power": "Acquires knowledge",
         "hebrew": "יהוה אלהים", "purpose": "Knowledge, learning, understanding all sciences"},
        {"num": 2, "name": "Second Pentacle", "power": "Obtains answers",
         "hebrew": "אלהים שדי", "purpose": "Dreams, visions, answers to questions"},
        {"num": 3, "name": "Third Pentacle",  "power": "Brings success",
         "hebrew": "יהוה צבאות", "purpose": "Success in all things, eloquence, trade"},
    ],
    "Moon": [
        {"num": 1, "name": "First Pentacle",  "power": "Travel protection",
         "hebrew": "יהוה שדי", "purpose": "Protection during travel, safe journeys"},
        {"num": 2, "name": "Second Pentacle", "power": "Reveals truths",
         "hebrew": "יהוה אלהים", "purpose": "Reveals hidden things, brings news"},
        {"num": 3, "name": "Third Pentacle",  "power": "Waxing fortune",
         "hebrew": "יהוה צבאות שדי", "purpose": "Fortune in all things, especially sea voyages"},
    ],
}

# === KAMEA MAGIC SQUARES (Agrippa, from divine-timing.py) ===
KAMEA = {
    "Saturn":   [[8, 1, 6], [3, 5, 7], [4, 9, 2]],           # 3x3, magic sum = 15
    "Jupiter":  [[4, 14, 15, 1], [9, 7, 6, 12], [5, 11, 10, 8], [16, 2, 3, 13]],  # 4x4, sum = 34
    "Mars":     [[11, 24, 7, 20, 3], [4, 12, 25, 8, 16], [17, 5, 13, 21, 9], [10, 18, 1, 14, 22], [23, 6, 19, 2, 15]],  # 5x5, sum = 65
    "Sun":      [[6, 32, 3, 34, 35, 1], [7, 11, 27, 28, 8, 30], [19, 14, 16, 15, 23, 24], [18, 20, 22, 21, 17, 13], [25, 29, 10, 9, 26, 12], [36, 5, 33, 4, 2, 31]],  # 6x6, sum = 111
    "Venus":    [[22, 47, 16, 41, 10, 35, 4], [5, 23, 48, 17, 42, 11, 29], [30, 6, 24, 49, 18, 36, 12], [13, 31, 7, 25, 43, 19, 37], [38, 14, 32, 1, 26, 44, 20], [21, 39, 8, 33, 2, 27, 45], [46, 15, 40, 9, 34, 3, 28]],  # 7x7, sum = 175
    "Mercury":  [[8, 58, 59, 5, 4, 62, 63, 1], [49, 15, 14, 46, 45, 12, 11, 52], [41, 23, 22, 44, 43, 20, 19, 42], [32, 34, 35, 29, 28, 38, 39, 25], [17, 47, 48, 16, 15, 50, 51, 9], [9, 55, 54, 12, 13, 60, 59, 6], [1, 53, 52, 20, 21, 56, 55, 30], [40, 26, 27, 37, 38, 32, 33, 29]],  # 8x8, sum = 260
    "Moon":     [[37, 78, 29, 70, 21, 62, 13, 54, 5], [6, 38, 79, 30, 71, 22, 63, 14, 46], [47, 7, 39, 80, 31, 72, 23, 55, 15], [16, 48, 8, 40, 81, 32, 64, 24, 56], [57, 17, 49, 9, 41, 73, 33, 65, 25], [26, 58, 18, 50, 1, 42, 74, 34, 66], [67, 27, 59, 19, 51, 10, 43, 75, 35], [36, 68, 28, 60, 11, 52, 2, 44, 76], [77, 37, 69, 20, 61, 12, 53, 4, 45]],  # 9x9, sum = 369
}

# === GEMATRIA (standard Mispar Gadol) ===
GEMATRIA = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
    'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
}

# === PLANET SYMBOLS ===
PLANET_SYMBOLS = {
    "Saturn": "♄", "Jupiter": "♃", "Mars": "♂", "Sun": "☉",
    "Venus": "♀", "Mercury": "☿", "Moon": "☽"
}

# === SVG HELPERS ===
def svg_header(w=800, h=800):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">\n')

def svg_footer():
    return '</svg>\n'

def svg_circle(cx, cy, r, stroke="#c8a020", stroke_width=2, fill="none"):
    return (f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}"/>\n')

def svg_line(x1, y1, x2, y2, stroke="#c8a020", stroke_width=2):
    return (f'  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"/>\n')

def svg_text(x, y, text, font_size=16, fill="#c8a020", anchor="middle",
             font_family="serif", font_weight="normal"):
    esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))
    return (f'  <text x="{x:.2f}" y="{y:.2f}" font-size="{font_size}" '
            f'fill="{fill}" text-anchor="{anchor}" '
            f'font-family="{font_family}" font-weight="{font_weight}">{esc}</text>\n')

def svg_path(d, stroke="#c8a020", stroke_width=2, fill="none"):
    return (f'  <path d="{d}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'fill="{fill}"/>\n')


# === PENTAGRAM POINTS ===
def pentagram_points(cx, cy, r):
    """5 points of a pentagram, starting from top (vertex up)."""
    pts = []
    for i in range(5):
        angle = -90 + i * 72  # start at top
        rad = math.radians(angle)
        pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    return pts

def hexagram_points(cx, cy, r):
    """6 points of a hexagram (Star of David)."""
    pts = []
    for i in range(6):
        angle = -90 + i * 60
        rad = math.radians(angle)
        pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    return pts

def draw_pentagram(cx, cy, r, stroke="#c8a020", sw=2):
    """Draw a pentagram as a continuous path (star, not pentagon)."""
    pts = pentagram_points(cx, cy, r)
    # Star order: 0→2→4→1→3→0
    order = [0, 2, 4, 1, 3, 0]
    d = " ".join(f"M {pts[order[i]][0]:.2f} {pts[order[i]][1]:.2f} L {pts[order[i+1]][0]:.2f} {pts[order[i+1]][1]:.2f}"
                 for i in range(5))
    return svg_path(d, stroke=stroke, stroke_width=sw)

def draw_hexagram(cx, cy, r, stroke="#c8a020", sw=2):
    """Draw a hexagram (two triangles)."""
    pts = hexagram_points(cx, cy, r)
    # Triangle 1: 0→2→4→0
    d1 = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} L {pts[2][0]:.2f} {pts[2][1]:.2f} L {pts[4][0]:.2f} {pts[4][1]:.2f} Z"
    # Triangle 2: 1→3→5→1
    d2 = f"M {pts[1][0]:.2f} {pts[1][1]:.2f} L {pts[3][0]:.2f} {pts[3][1]:.2f} L {pts[5][0]:.2f} {pts[5][1]:.2f} Z"
    return svg_path(d1, stroke=stroke, stroke_width=sw) + svg_path(d2, stroke=stroke, stroke_width=sw)

def draw_crescent(cx, cy, r, stroke="#c8a020", sw=2):
    """Draw a crescent (Moon)."""
    # Outer arc (left side of circle)
    outer = f"M {cx:.2f} {cy-r:.2f} A {r:.2f} {r:.2f} 0 1 0 {cx:.2f} {cy+r:.2f}"
    # Inner arc (bite taken out)
    inner = f"A {r*0.7:.2f} {r*0.7:.2f} 0 1 1 {cx:.2f} {cy-r:.2f}"
    return svg_path(outer, stroke=stroke, stroke_width=sw) + svg_path(inner, stroke=stroke, stroke_width=sw)


# === RENDER PENTACLE ===
def render_pentacle(planet, num, out_path):
    """Generate SVG of a Solomonic pentacle."""
    pen_data = None
    for p in SOLOMON_PENTACLES.get(planet, []):
        if p["num"] == num:
            pen_data = p
            break
    if not pen_data:
        raise ValueError(f"Pentacle {planet}/{num} not found")

    pc = PLANET_COLORS.get(planet, PLANET_COLORS["Sun"])
    cx, cy = 400.0, 400.0

    svg = svg_header()
    # Background
    svg += f'  <rect width="800" height="800" fill="#0a0a12"/>\n'

    # Outer double circle (ritual boundary)
    svg += svg_circle(cx, cy, 360, stroke=pc["stroke"], stroke_width=3)
    svg += svg_circle(cx, cy, 345, stroke=pc["stroke"], stroke_width=1)

    # Inner symbol
    if planet in ("Mars", "Venus", "Mercury"):
        svg += draw_pentagram(cx, cy, 240, stroke=pc["text"], sw=2.5)
    elif planet in ("Saturn", "Jupiter", "Sun"):
        svg += draw_hexagram(cx, cy, 240, stroke=pc["text"], sw=2.5)
    else:  # Moon
        svg += draw_crescent(cx, cy, 240, stroke=pc["text"], sw=2.5)
        # Also add a small circle for the Moon
        svg += svg_circle(cx, cy, 180, stroke=pc["text"], stroke_width=1.5)

    # Hebrew text (divine names) — arc around the outer ring
    # Use tspan for multi-line Hebrew text
    hebrew_text = pen_data["hebrew"]
    svg += svg_text(cx, cy - 290, hebrew_text,
                    font_size=22, fill=pc["text"],
                    font_family="serif", font_weight="bold")

    # Inner circle around Hebrew
    svg += svg_circle(cx, cy, 310, stroke=pc["accent"], stroke_width=1, fill="none")

    # Title: planet glyph + pentacle name + power
    sym = PLANET_SYMBOLS.get(planet, "☉")
    title_line1 = f"{sym} {pen_data['name']}"
    title_line2 = pen_data["power"]
    svg += svg_text(cx, 750, title_line1, font_size=18, fill=pc["text"],
                    font_family="serif", font_weight="bold")
    svg += svg_text(cx, 775, title_line2, font_size=13, fill=pc["accent"],
                    font_family="serif")

    # Planet name at top
    svg += svg_text(cx, 40, planet.upper(), font_size=28, fill=pc["text"],
                    font_family="serif", font_weight="bold")

    # Small decorative inner circles
    svg += svg_circle(cx, cy, 80, stroke=pc["accent"], stroke_width=1)
    svg += svg_circle(cx, cy, 20, stroke=pc["text"], stroke_width=2)

    svg += svg_footer()

    Path(out_path).write_text(svg)
    return out_path


# === RENDER KAMEA ===
def render_kamea(planet, out_path):
    """Render the magic square as SVG."""
    if planet not in KAMEA:
        raise ValueError(f"Kamea for {planet} not found")

    grid = KAMEA[planet]
    n = len(grid)
    pc = PLANET_COLORS.get(planet, PLANET_COLORS["Sun"])

    # Kamea drawing area: 500x500, centered in 800x800
    margin = 150
    cell_size = (800 - 2 * margin) / n

    svg = svg_header()
    svg += f'  <rect width="800" height="800" fill="#0a0a12"/>\n'

    # Title
    sym = PLANET_SYMBOLS.get(planet, "☉")
    svg += svg_text(400, 50, f"{sym} {planet.upper()} KAMEA", font_size=24,
                    fill=pc["text"], font_family="serif", font_weight="bold")
    svg += svg_text(400, 75, f"{n}×{n} — Magic Sum: {grid[0][0] * n + sum(grid[i][i] for i in range(n)) - grid[0][0]}",
                    font_size=12, fill=pc["accent"], font_family="serif")

    # Draw grid
    for row in range(n):
        for col in range(n):
            x = margin + col * cell_size
            y = margin + row * cell_size
            val = grid[row][col]

            # Cell border
            svg += (f'  <rect x="{x:.2f}" y="{y:.2f}" width="{cell_size:.2f}" height="{cell_size:.2f}" '
                    f'stroke="{pc["stroke"]}" stroke-width="1" fill="{pc["fill"]}"/>\n')

            # Cell number
            cx_cell = x + cell_size / 2
            cy_cell = y + cell_size / 2
            svg += svg_text(cx_cell, cy_cell + 5, str(val),
                            font_size=min(14, 200 // n),
                            fill=pc["text"], font_family="monospace")

    # Outer double border for the whole kamea
    svg += svg_rect(margin, margin, 800 - 2*margin, 800 - 2*margin,
                    stroke=pc["stroke"], stroke_width=3)
    svg += svg_rect(margin - 5, margin - 5, 800 - 2*margin + 10, 800 - 2*margin + 10,
                    stroke=pc["accent"], stroke_width=1)

    svg += svg_footer()
    Path(out_path).write_text(svg)
    return out_path

def svg_rect(x, y, w, h, stroke="#c8a020", stroke_width=2):
    return (f'  <rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>\n')


# === KAMEA-TRACE SIGIL ===
def gematria_value(text):
    """Calculate gematria value for a string (Hebrew letters or Latin transliteration)."""
    # Handle Hebrew directly
    val = sum(GEMATRIA.get(c, 0) for c in text if c in GEMATRIA)
    if val > 0:
        return val

    # Transliteration fallback (Atbash-inspired rough mapping)
    # For Latin text, sum ordinal values mod 9 + 1 (simplified)
    val = sum(ord(c) for c in text.lower()) % 81 + 1
    return val

def find_kamea_position(value, grid):
    """Find row, col of value in kamea. Returns first match or None."""
    n = len(grid)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == value:
                return r, c
    return None

def render_kamea_sigil(planet, name_or_intent, out_path):
    """Agrippa's kamea-trace technique: map name→positions→connect lines."""
    if planet not in KAMEA:
        raise ValueError(f"Kamea for {planet} not found")

    grid = KAMEA[planet]
    n = len(grid)
    pc = PLANET_COLORS.get(planet, PLANET_COLORS["Sun"])

    # Calculate gematria values for each character of name
    # For Hebrew: use each letter; for Latin: use each char's ordinal
    if any(c in GEMATRIA for c in name_or_intent):
        # Hebrew input: use each letter's gematria value
        values = [GEMATRIA[c] for c in name_or_intent if c in GEMATRIA]
    else:
        # Latin input: each character's ordinal value
        values = [ord(c) for c in name_or_intent.lower()]

    # Reduce values mod n (to fit kamea dimensions), ensure ≥1
    # Agrippa's method: find each number's position in the kamea
    positions = []
    for v in values:
        pos = find_kamea_position(v, grid)
        if pos is None:
            # Fall back: reduce mod magic sum and search
            reduced = ((v - 1) % (n * n)) + 1
            pos = find_kamea_position(reduced, grid)
        if pos:
            positions.append(pos)

    if not positions:
        raise ValueError(f"Could not map '{name_or_intent}' to kamea positions")

    # Drawing area
    margin = 100
    cell_size = (800 - 2 * margin) / n

    svg = svg_header()
    svg += f'  <rect width="800" height="800" fill="#0a0a12"/>\n'

    # Title
    sym = PLANET_SYMBOLS.get(planet, "☉")
    safe_name = name_or_intent.replace("&", "and").replace("<", "").replace(">", "")
    svg += svg_text(400, 50, f"{sym} {planet.upper()} SIGIL: {safe_name}",
                    font_size=20, fill=pc["text"], font_family="serif", font_weight="bold")

    # Draw kamea grid (faint)
    for row in range(n):
        for col in range(n):
            x = margin + col * cell_size
            y = margin + row * cell_size
            val = grid[row][col]
            cx_cell = x + cell_size / 2
            cy_cell = y + cell_size / 2

            # Cell
            svg += (f'  <rect x="{x:.2f}" y="{y:.2f}" width="{cell_size:.2f}" height="{cell_size:.2f}" '
                    f'stroke="{pc["stroke"]}" stroke-width="0.5" fill="{pc["fill"]}" opacity="0.5"/>\n')
            svg += svg_text(cx_cell, cy_cell + 4, str(val),
                            font_size=min(12, 160 // n),
                            fill=pc["accent"], font_family="monospace")

    # Draw trace lines connecting positions in order
    path_data = ""
    for i, (r, c) in enumerate(positions):
        x = margin + c * cell_size + cell_size / 2
        y = margin + r * cell_size + cell_size / 2
        if i == 0:
            path_data += f"M {x:.2f} {y:.2f} "
        else:
            path_data += f"L {x:.2f} {y:.2f} "

    svg += svg_path(path_data, stroke=pc["text"], stroke_width=3)

    # Mark start position with circle
    if positions:
        sr, sc = positions[0]
        sx = margin + sc * cell_size + cell_size / 2
        sy = margin + sr * cell_size + cell_size / 2
        svg += svg_circle(sx, sy, 12, stroke=pc["text"], stroke_width=3, fill=pc["fill"])

        # Mark end position with bar
        er, ec = positions[-1]
        ex = margin + ec * cell_size + cell_size / 2
        ey = margin + er * cell_size + cell_size / 2
        svg += (f'  <line x1="{ex-10:.2f}" y1="{ey:.2f}" x2="{ex+10:.2f}" y2="{ey:.2f}" '
                f'stroke="{pc["text"]}" stroke-width="4"/>\n')
        svg += (f'  <line x1="{ex:.2f}" y1="{ey-10:.2f}" x2="{ex:.2f}" y2="{ey+10:.2f}" '
                f'stroke="{pc["text"]}" stroke-width="4"/>\n')

    # Outer border
    svg += svg_rect(margin - 10, margin - 10, 800 - 2*margin + 20, 800 - 2*margin + 20,
                    stroke=pc["stroke"], stroke_width=2)

    svg += svg_footer()
    Path(out_path).write_text(svg)
    return out_path


# === SVG → PNG ===
def svg_to_png(svg_path_str, png_path_str=None):
    """Convert SVG to PNG using cairosvg."""
    try:
        import cairosvg
    except ImportError:
        return None

    svg_path = Path(svg_path_str)
    if png_path_str is None:
        png_path = svg_path.with_suffix(".png")
    else:
        png_path = Path(png_path_str)

    cairosvg.svg2png(url=str(svg_path.absolute()), write_to=str(png_path.absolute()),
                      output_width=1200, output_height=1200)
    return str(png_path)


# === CLI ===
def cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    def normalize_planet(p):
        return p.capitalize()

    if cmd == "pentacle":
        if len(sys.argv) != 4:
            print("Usage: sigil_renderer.py pentacle <planet> <num>")
            return
        planet, num = normalize_planet(sys.argv[2]), int(sys.argv[3])
        out = DATA_DIR / f"{planet.lower()}_pentacle_{num}.svg"
        render_pentacle(planet, num, out)
        svg_to_png(out)
        print(f"Written: {out}  ({Path(str(out).replace('.svg','.png')).stat().st_size // 1024}KB PNG)")

    elif cmd == "kamea":
        if len(sys.argv) != 3:
            print("Usage: sigil_renderer.py kamea <planet>")
            return
        planet = normalize_planet(sys.argv[2])
        out = DATA_DIR / f"{planet.lower()}_kamea.svg"
        render_kamea(planet, out)
        svg_to_png(out)
        print(f"Written: {out}  ({Path(str(out).replace('.svg','.png')).stat().st_size // 1024}KB PNG)")

    elif cmd == "sigil":
        if len(sys.argv) != 4:
            print("Usage: sigil_renderer.py sigil <planet> <name_or_intent>")
            return
        planet, name = normalize_planet(sys.argv[2]), sys.argv[3]
        safe_name = "".join(c if c.isalnum() else "_" for c in name)
        out = DATA_DIR / f"{planet.lower()}_sigil_{safe_name}.svg"
        render_kamea_sigil(planet, name, out)
        svg_to_png(out)
        print(f"Written: {out}  ({Path(str(out).replace('.svg','.png')).stat().st_size // 1024}KB PNG)")

    elif cmd == "all":
        planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        count = 0
        for planet in planets:
            # All pentacles
            for pen in SOLOMON_PENTACLES.get(planet, []):
                out = DATA_DIR / f"{planet.lower()}_pentacle_{pen['num']}.svg"
                render_pentacle(planet, pen["num"], out)
                svg_to_png(out)
                count += 1
            # Kamea
            out = DATA_DIR / f"{planet.lower()}_kamea.svg"
            render_kamea(planet, out)
            svg_to_png(out)
            count += 1
        print(f"Generated {count} SVGs + PNGs in {DATA_DIR}")

    elif cmd == "sample":
        planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        for planet in planets:
            out = DATA_DIR / f"{planet.lower()}_pentacle_1.svg"
            render_pentacle(planet, 1, out)
            svg_to_png(out)
            print(f"Sample: {out}")
        print(f"7 sample SVGs generated in {DATA_DIR}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    cli()
