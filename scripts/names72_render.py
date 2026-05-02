#!/usr/bin/env python3
"""
72 Names of God — SVG Card Renderer
Generates visual cards, grid poster, and fr3k's signature MYK card.
"""

import json, sys, os
from pathlib import Path

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False

DATA_DIR = Path.home() / ".hermes" / "data" / "names72"
OUT_DIR  = Path.home() / ".hermes" / "data" / "names72"
SCRIPT_DIR = Path.home() / ".hermes" / "scripts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Planetary colours ────────────────────────────────────────────────────────
PLANET_COLOR = {
    "Sun":     "#FFD700",
    "Moon":    "#C0C0C0",
    "Mercury": "#B5B5B5",
    "Venus":   "#9B59B6",
    "Mars":    "#E74C3C",
    "Jupiter": "#3498DB",
    "Saturn":  "#8E44AD",
}

# ── Zodiac glyphs (Unicode) ───────────────────────────────────────────────────
ZODIAC_GLYPH = {
    "Aries":        "♈", "Taurus":       "♉", "Gemini":       "♊",
    "Cancer":       "♋", "Leo":          "♌", "Virgo":        "♍",
    "Libra":        "♎", "Scorpio":      "♏", "Sagittarius":  "♐",
    "Capricorn":    "♑", "Aquarius":     "♒", "Pisces":       "♓",
}

PLANET_GLYPH = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

# ── Load catalog ───────────────────────────────────────────────────────────────
def load_catalog():
    with open(DATA_DIR / "catalog.json") as f:
        return json.load(f)

CATALOG = load_catalog()

# ── SVG helpers ───────────────────────────────────────────────────────────────
def svg_header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        '<defs>\n'
        '<style>\n'
        'text { font-family: Arial, Helvetica, sans-serif; }\n'
        '</style>\n'
        '</defs>\n'
    )

def card_bg(w, h, planet):
    color = PLANET_COLOR.get(planet, "#333333")
    return (
        f'<rect width="{w}" height="{h}" fill="#1a1a2e" rx="18"/>\n'
        f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="none" stroke="{color}" stroke-width="3" rx="14"/>\n'
    )

def zodiac_bar(zodiac_sign, deg_start):
    glyph = ZODIAC_GLYPH.get(zodiac_sign, "?")
    deg_end = deg_start + 4
    return (
        f'<text x="300" y="660" text-anchor="middle" font-size="42" '
        f'fill="#EEE">{glyph}</text>\n'
        f'<text x="300" y="710" text-anchor="middle" font-size="22" fill="#AAA" '
        f'font-family="Cinzel,serif">{zodiac_sign}</text>\n'
        f'<text x="300" y="742" text-anchor="middle" font-size="18" fill="#777" '
        f'font-family="Cinzel,serif">{deg_start}°–{deg_end}°</text>\n'
    )

def planet_bar(planet):
    glyph = PLANET_GLYPH.get(planet, "?")
    color = PLANET_COLOR.get(planet, "#888")
    return (
        f'<circle cx="300" cy="790" r="22" fill="{color}" opacity="0.3"/>\n'
        f'<text x="300" y="798" text-anchor="middle" font-size="26" fill="{color}">{glyph}</text>\n'
        f'<text x="300" y="825" text-anchor="middle" font-size="14" fill="#888" '
        f'font-family="Cinzel,serif">{planet}</text>\n'
    )

def power_bar(power):
    lines = power.split(" — ")
    y_start = 870
    for i, line in enumerate(lines):
        y = y_start + i * 26
        txt = f'<text x="300" y="{y}" text-anchor="middle" font-size="15" ' \
              f'fill="#B8860B" font-family="Cinzel,serif">{line}</text>\n'
    return txt

# ── Single card renderer ──────────────────────────────────────────────────────
def render_card(n, out_path, signature=False):
    entry = next(e for e in CATALOG if e["n"] == n)
    w, h = 600, 900
    planet = entry["planet"]
    color  = PLANET_COLOR.get(planet, "#888")

    svg = [svg_header(w, h)]
    svg.append(card_bg(w, h, planet))

    # Border accent stripe
    svg.append(f'<rect x="4" y="4" width="{w-8}" height="8" fill="{color}" rx="4"/>\n')

    # Card number
    svg.append(f'<text x="570" y="55" text-anchor="end" font-size="28" '
                f'fill="{color}" font-family="Cinzel,serif">#{n:02d}</text>\n')

    # Hebrew triplet — RTL: text-anchor end, x = right margin
    he = entry["hebrew"]
    svg.append(f'<text x="580" y="200" text-anchor="end" font-size="200" '
                f'font-family="SBL+Biblit,Sedra SF,Arial" fill="#FFFFFF" '
                f'dominant-baseline="middle">{he}</text>\n')

    # Transliteration below Hebrew
    svg.append(f'<text x="580" y="260" text-anchor="end" font-size="24" '
                f'font-family="Cinzel,serif" fill="{color}" letter-spacing="3">'
                f'{entry["transliteration"]}</text>\n')

    # Angel name
    svg.append(f'<text x="20" y="330" text-anchor="start" font-size="38" '
                f'font-family="Cinzel,serif" font-weight="700" fill="#F0F0F0">'
                f'{entry["angel"]}</text>\n')

    # Separator
    svg.append(f'<line x1="20" y1="350" x2="580" y2="350" stroke="{color}" stroke-width="1" opacity="0.4"/>\n')

    # Zodiac section
    svg.append(zodiac_bar(entry["zodiac_sign"], entry["zodiac_deg_start"]))

    # Planet section
    svg.append(planet_bar(planet))

    # Power
    svg.append(power_bar(entry["power"]))

    if signature:
        # Ornamental border corners
        for cx, cy in [(20,20),(580,20),(20,880),(580,880)]:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{color}" opacity="0.6"/>\n')
        # Extra inscription line
        svg.append(f'<text x="300" y="895" text-anchor="middle" font-size="13" '
                    f'fill="#666" font-family="Cinzel,serif">'
                    f'Sun conjunct Arcturus · fr3k double-authority</text>\n')
        svg.append(f'<text x="300" y="915" text-anchor="middle" font-size="11" '
                    f'fill="#444" font-family="Cinzel,serif" font-style="italic">'
                    f'MICHAEL · Righteous Judge · Protector of Israel</text>\n')

    svg.append('</svg>\n')

    content = "".join(svg)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Card #{n:02d} → {out_path} ({len(content)} bytes)")
    return content

# ── Full-grid poster ──────────────────────────────────────────────────────────
def render_grid(out_path):
    cols, rows = 9, 8
    cw, ch = 200, 260
    w = cols * cw
    h = rows * ch

    svg = [svg_header(w, h)]
    svg.append(f'<rect width="{w}" height="{h}" fill="#0d0d1a"/>\n')

    for entry in CATALOG:
        n = entry["n"]
        col = (n - 1) % cols
        row = (n - 1) // cols
        x = col * cw + 4
        y = row * ch + 4

        planet = entry["planet"]
        color  = PLANET_COLOR.get(planet, "#555")

        svg.append(f'<g transform="translate({x},{y})">\n')
        svg.append(f'<rect width="{cw-8}" height="{ch-8}" fill="#1a1a2e" rx="8"/>\n')
        svg.append(f'<rect x="2" y="2" width="{cw-12}" height="6" fill="{color}" rx="3"/>\n')

        # Hebrew
        svg.append(f'<text x="{cw-20}" y="70" text-anchor="end" font-size="64" '
                    f'font-family="SBL+Biblit,Sedra SF,Arial" fill="#FFF" '
                    f'dominant-baseline="middle">{entry["hebrew"]}</text>\n')
        # Angel
        svg.append(f'<text x="10" y="105" text-anchor="start" font-size="13" '
                    f'font-family="Cinzel,serif" font-weight="700" fill="#DDD">'
                    f'{entry["angel"]}</text>\n')
        # #N
        svg.append(f'<text x="{cw-16}" y="105" text-anchor="end" font-size="12" '
                    f'font-family="Cinzel,serif" fill="{color}">'
                    f'#{n:02d}</text>\n')
        # Zodiac
        zg = ZODIAC_GLYPH.get(entry["zodiac_sign"], "?")
        svg.append(f'<text x="10" y="130" font-size="20" fill="#888">{zg}</text>\n')
        svg.append(f'<text x="36" y="132" font-size="11" font-family="Cinzel,serif" fill="#666">'
                    f'{entry["zodiac_sign"]} {entry["zodiac_deg_start"]}°</text>\n')
        # Planet
        pg = PLANET_GLYPH.get(planet, "?")
        svg.append(f'<text x="10" y="155" font-size="14" fill="{color}">{pg}</text>\n')
        svg.append(f'<text x="30" y="158" font-size="10" font-family="Cinzel,serif" fill="#555">'
                    f'{planet}</text>\n')
        # Power (truncated)
        power_short = entry["power"].split(" — ")[0][:28]
        svg.append(f'<text x="10" y="180" font-size="9" font-family="Cinzel,serif" fill="#888">'
                    f'{power_short}</text>\n')

        # fr3k signature highlight
        if n == 42:
            svg.append(f'<rect width="{cw-8}" height="{ch-8}" fill="none" '
                        f'stroke="#FFD700" stroke-width="3" rx="8"/>\n')
            svg.append(f'<text x="{cw//2}" y="240" text-anchor="middle" font-size="9" '
                        f'fill="#FFD700" font-family="Cinzel,serif">★ fr3k ★</text>\n')

        svg.append('</g>\n')

    svg.append('</svg>\n')

    content = "".join(svg)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Grid → {out_path} ({len(content)} bytes)")

# ── Signature card ─────────────────────────────────────────────────────────────
def render_signature(out_path):
    return render_card(42, out_path, signature=True)

# ── PNG conversion ─────────────────────────────────────────────────────────────
def svg_to_png(svg_path, png_path=None):
    if not HAS_CAIRO:
        print("  [cairosvg not available — skipping PNG]")
        return
    if png_path is None:
        png_path = str(svg_path).replace(".svg", ".png")
    try:
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=1200, output_height=1800)
        sz = os.path.getsize(png_path)
        print(f"  PNG → {png_path} ({sz} bytes)")
    except Exception as e:
        print(f"  PNG conversion failed: {e}")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    args = sys.argv[2:]

    if cmd == "card":
        n = int(args[0]) if args else 42
        out = OUT_DIR / f"card_{n:02d}_{CATALOG[n-1]['transliteration']}.svg"
        render_card(n, out)
        svg_to_png(out)

    elif cmd == "all":
        for e in CATALOG:
            out = OUT_DIR / f"card_{e['n']:02d}_{e['transliteration']}.svg"
            render_card(e['n'], out)
        print(f"  All 72 cards rendered.")

    elif cmd == "grid":
        out = OUT_DIR / "names72_grid.svg"
        render_grid(out)
        svg_to_png(out)

    elif cmd == "signature":
        out = OUT_DIR / "card_042_MYK_signature.svg"
        render_signature(out)
        svg_to_png(out)

    elif cmd == "info":
        n = int(args[0]) if args else 42
        e = next((x for x in CATALOG if x["n"] == n), None)
        if not e:
            print(f"Name #{n} not found.")
            return
        print(f"  #{e['n']:02d}  {e['hebrew']}  ({e['transliteration']})")
        print(f"  Angel:  {e['angel']}")
        print(f"  Power:  {e['power']}")
        print(f"  Planet: {e['planet']}")
        print(f"  Zodiac: {e['zodiac_sign']} {e['zodiac_deg_start']}°–{e['zodiac_deg_start']+4}°")
        print(f"  Decan:  {e['decan_ruler']}")
        if e.get("__note__"):
            print(f"  Note:   {e['__note__']}")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: names72_render.py [card|all|grid|signature|info] [n]")

if __name__ == "__main__":
    main()
