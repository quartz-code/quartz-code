"""What every card shares: palettes, fonts, the card background, section titles."""
import math
import pathlib
import re
import urllib.request

from quartz3d import rgb
from textpath import Font

HERE = pathlib.Path(__file__).resolve().parent

DISPLAY = ("Syncopate", 700)
HEADING = ("Montserrat", 600)
BODY = ("Montserrat", 500)
MONO = ("JetBrains Mono", 500)

_fonts = {}


def font(spec):
    """Load a font, fetching it from Google Fonts into ./fonts on first use."""
    family, weight = spec
    name = f"{family.replace(' ', '')}-{weight}"
    if name not in _fonts:
        path = HERE / "fonts" / f"{name}.ttf"
        if not path.exists():
            url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}"
            css = urllib.request.urlopen(url, timeout=30).read().decode()
            path.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(re.search(r"url\((\S+?\.ttf)\)", css).group(1), path)
        _fonts[name] = Font(str(path))
    return _fonts[name]


def _crystal(aura, back, front_op, back_op, edge_op, back_edge_op, gloss, spec, shadow):
    return {"aura": [rgb(c) for c in aura], "deep": rgb("#2b1d6b"), "gloss": gloss, "spec": spec, "shadow": shadow,
            "front_op": front_op, "back": back, "back_op": back_op, "edge": "#ffffff", "edge_op": edge_op,
            "back_edge_op": back_edge_op}


THEMES = {
    "dark": {
        "bg": ("#1c1533", "#0c0a15"), "edge": ("#ffffff", 0.08), "grid": ("#ffffff", 0.05),
        "glows": ("#ff6fc0", 0.22), "glow2": ("#4fd0ff", 0.17), "glow3": ("#9b6bff", 0.22), "glow4": ("#6dffc4", 0.12),
        "text": "#f1edff", "muted": "#9d95bb", "line": ("#ffffff", 0.14),
        "accent": ("#ffb8de", "#d1b8ff", "#a6e6ff", "#c4ffe6"),
        "type": "#e9e2ff", "cursor": "#ff9fd2",
        "particles": ("#ffd0ec", "#c9b8ff", "#b8f0ff"), "particle_op": 0.8, "floor": ("#c9a6ff", 0.40),
        "gem_edge": ("#ffffff", 0.32), "gem_halo": 0.55, "tile": ("#ffffff", 0.05), "tile_gloss": 0.04,
        "rock": ("#231e36", "#2d2745", "#1a1628"), "pebble": "#3a3452", "deep": "#24185c",
        "crystal": _crystal(("#ff8fd0", "#d9a0ff", "#a6b2ff", "#8fd8ff", "#8ff3dc", "#c2b4ff"), "#b9a8ff",
                            front_op=0.84, back_op=0.16, edge_op=0.7, back_edge_op=0.28, gloss=0.06, spec=0.8, shadow=0.55),
    },
    "light": {
        "bg": ("#ffffff", "#f1ecfa"), "edge": ("#5b3fb0", 0.12), "grid": ("#5b3fb0", 0.07),
        "glows": ("#ff7ac8", 0.18), "glow2": ("#3fc6ff", 0.14), "glow3": ("#a07bff", 0.16), "glow4": ("#3fe0a6", 0.10),
        "text": "#1f1934", "muted": "#6e6690", "line": ("#5b3fb0", 0.16),
        "accent": ("#e0479a", "#8b5cf6", "#1ea7e0", "#18b07a"),
        "type": "#2a2240", "cursor": "#e0479a",
        "particles": ("#f472b6", "#a78bfa", "#38bdf8"), "particle_op": 0.6, "floor": ("#8b5cf6", 0.28),
        "gem_edge": ("#ffffff", 0.55), "gem_halo": 0.35, "tile": ("#ffffff", 0.75), "tile_gloss": 0.5,
        "rock": ("#d9d1ea", "#e7e1f2", "#c8bedf"), "pebble": "#d6cfe6", "deep": "#3b2a85",
        "crystal": _crystal(("#ff5aa8", "#b065ff", "#6a7dff", "#2bb2f5", "#1fc9a8", "#8a6bff"), "#7b5cff",
                            front_op=0.9, back_op=0.14, edge_op=0.85, back_edge_op=0.35, gloss=0.10, spec=0.75, shadow=0.45),
    },
}

SPARK = ("M0,-1 C0.12,-0.12 0.12,-0.12 1,0 C0.12,0.12 0.12,0.12 0,1 "
         "C-0.12,0.12 -0.12,0.12 -1,0 C-0.12,-0.12 -0.12,-0.12 0,-1Z")


def paths(glyphs):
    return "".join(f'<path d="{d}"/>' for _, d, _ in glyphs if d)


def text(s, spec, size, x, y, anchor="start", tracking=0.0):
    """Text as outlines: (svg paths, advance width)."""
    glyphs, width = font(spec).layout(s, size, x, y, tracking=tracking, anchor=anchor)
    return paths(glyphs), width


def fit(s, spec, size, max_width):
    """Largest size up to `size` at which `s` fits in max_width."""
    width = font(spec).layout(s, size)[1]
    return size if width <= max_width else size * max_width / width


def spark(x, y, r, delay):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({r})"><path class="sp" d="{SPARK}" '
            f'style="animation-delay:{delay:.1f}s"/></g>')


def heading(t, W, y, title):
    """Centred section title over an iridescent rule with a diamond."""
    d, _ = text(title.upper(), HEADING, 50, W / 2, y, anchor="middle", tracking=10)
    ry = y + 34
    return (f'<g fill="{t["text"]}">{d}</g>'
            f'<rect x="{W / 2 - 150:.0f}" y="{ry}" width="300" height="2" fill="url(#accent)" opacity=".9"/>'
            f'<rect x="{W / 2 - 7:.1f}" y="{ry - 6:.1f}" width="14" height="14" fill="url(#accent)" '
            f'transform="rotate(45 {W / 2:.1f} {ry + 1:.1f})"/>')


def card(W, H, t, body, defs="", style="", glows=None, title=""):
    """A rounded card: radial background, soft colour glows and a hexagonal lattice."""
    glows = glows or [(W * 0.22, H * 0.3, W * 0.35, t["glows"]), (W * 0.8, H * 0.25, W * 0.33, t["glow2"]),
                      (W * 0.5, H * 0.05, W * 0.4, t["glow3"])]
    grads = "".join(
        f'<radialGradient id="glow{i}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, r, (c, o)) in enumerate(glows))
    lights = "".join(f'<rect width="{W}" height="{H}" fill="url(#glow{i})"/>' for i in range(len(glows)))
    hw = 40
    hh = hw * math.sqrt(3)
    lattice = (f"M0 {hh / 2:.2f}L{hw / 4:.2f} 0H{hw * 3 / 4:.2f}L{hw:.2f} {hh / 2:.2f}"
               f"L{hw * 3 / 4:.2f} {hh:.2f}H{hw / 4:.2f}Z M{hw:.2f} {hh / 2:.2f}H{hw * 1.5:.2f}")
    a0, a1, a2, a3 = t["accent"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
<radialGradient id="bg" cx="{W / 2:.0f}" cy="{H * 0.4:.0f}" r="{max(W, H) * 0.75:.0f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t["bg"][0]}"/><stop offset="1" stop-color="{t["bg"][1]}"/></radialGradient>
{grads}
<pattern id="hex" width="{hw * 1.5:.2f}" height="{hh:.2f}" patternUnits="userSpaceOnUse"><path d="{lattice}" fill="none" stroke="{t["grid"][0]}" stroke-opacity="{t["grid"][1]}"/></pattern>
<radialGradient id="hexFade" cx="{W / 2:.0f}" cy="{H / 2:.0f}" r="{max(W, H) * 0.6:.0f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="hexMask"><rect width="{W}" height="{H}" fill="url(#hexFade)"/></mask>
<linearGradient id="accent" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{a0}"/><stop offset=".35" stop-color="{a1}"/><stop offset=".7" stop-color="{a2}"/><stop offset="1" stop-color="{a3}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="32"/></clipPath>
{defs}
</defs>
<style>
.sp{{fill:#fff;transform-box:fill-box;transform-origin:center;transform:scale(0);animation:twinkle 3.6s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{transform:scale(0) rotate(0deg);opacity:0}}45%{{transform:scale(1) rotate(45deg);opacity:1}}70%{{transform:scale(0) rotate(90deg);opacity:0}}}}
.spin-static,.type-static{{display:none}}
{style}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.spin,.type{{display:none}}.spin-static,.type-static{{display:inline}}.sp{{transform:scale(1)}}}}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{lights}
<rect width="{W}" height="{H}" fill="url(#hex)" mask="url(#hexMask)"/>
{body}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="31.5" fill="none" stroke="{t["edge"][0]}" stroke-opacity="{t["edge"][1]}"/>
</svg>
'''
