"""Build the profile header and footer SVGs (dark + light) into ../

    pip install -r requirements.txt
    python build.py

Text is converted to outlines, so the SVGs render the same everywhere
(GitHub shows them as <img>, where web fonts are not loaded). Fonts are
fetched from Google Fonts on first run and cached in ./fonts.
"""
import math
import pathlib
import random
import re
import urllib.request

from crystal import render as crystal
from textpath import Font

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent

# Header texts
LABEL = ("$", "whoami")
TITLE = "quartz-code"
TAGLINE = ("Mobile & Backend", "GameDev", "Data Analysis")
ALT = "quartz-code — Mobile &amp; Backend Developer · GameDev · Data Analysis"

THEMES = {
    "dark": {
        "bg": ("#120b22", "#1c1132", "#0e0a1a"),
        "border": ("#ffffff", 0.09),
        "lattice": ("#ffffff", 0.06),
        "glow1": ("#ff4fa0", 0.32),
        "glow2": ("#7c3aed", 0.28),
        "label": "#ff7eb6",
        "label_dim": "#7d7298",
        "title": ("#ffc6e0", "#ff5fa2", "#b07cff"),
        "title_stroke": "#ffb3d9",
        "tag": "#cbc3de",
        "accent": "#ff6fae",
        "particles": ("#ff8fc5", "#c4a7ff", "#ffffff"),
        "particle_op": 0.75,
        "floor": ("#ff4fa0", 0.45),
        "crystal": {
            "ramp": ((255, 120, 180), (228, 72, 220), (138, 84, 255)), "deep": (60, 24, 130),
            "ambient": 0.46, "diffuse": 0.74, "spec": 0.55, "gloss": 0.22,
            "edge": "#ffffff", "edge_op": 0.55,
        },
        "bed": {
            "ramp": ((255, 111, 174), (217, 70, 239), (139, 92, 246), (217, 70, 239), (255, 111, 174)),
            "back": (13, 17, 23), "depth": (0.5, 0.22), "fade": 0.3,
            "edge": ("#ffffff", 0.38), "glow": ("#ff4fa0", 0.30),
        },
    },
    "light": {
        "bg": ("#fff7fb", "#f8f1ff", "#f1eaff"),
        "border": ("#6d28d9", 0.14),
        "lattice": ("#6d28d9", 0.07),
        "glow1": ("#ff6fae", 0.28),
        "glow2": ("#8b5cf6", 0.20),
        "label": "#d6336c",
        "label_dim": "#9a8fb3",
        "title": ("#e83e8c", "#c026d3", "#6d28d9"),
        "title_stroke": "#c026d3",
        "tag": "#4f4566",
        "accent": "#e83e8c",
        "particles": ("#f472b6", "#a78bfa", "#c084fc"),
        "particle_op": 0.55,
        "floor": ("#c026d3", 0.30),
        "crystal": {
            "ramp": ((255, 98, 165), (214, 60, 210), (120, 70, 240)), "deep": (70, 30, 150),
            "ambient": 0.56, "diffuse": 0.60, "spec": 0.50, "gloss": 0.25,
            "edge": "#ffffff", "edge_op": 0.75,
        },
        "bed": {
            "ramp": ((236, 72, 153), (192, 38, 211), (124, 58, 237), (192, 38, 211), (236, 72, 153)),
            "back": (255, 255, 255), "depth": (0.42, 0.16), "fade": 0.6,
            "edge": ("#ffffff", 0.75), "glow": ("#c026d3", 0.16),
        },
    },
}

# Four-point sparkle, unit size.
SPARK = ("M0,-1 C0.12,-0.12 0.12,-0.12 1,0 C0.12,0.12 0.12,0.12 0,1 "
         "C-0.12,0.12 -0.12,0.12 -1,0 C-0.12,-0.12 -0.12,-0.12 0,-1Z")


def font(family, weight):
    path = HERE / "fonts" / f"{family.replace(' ', '')}-{weight}.ttf"
    if not path.exists():
        url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}"
        css = urllib.request.urlopen(url).read().decode()
        path.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(re.search(r"url\((\S+?\.ttf)\)", css).group(1), path)
    return Font(str(path))


def paths(glyphs):
    return "".join(f'<path d="{d}"/>' for _, d, _ in glyphs if d)


def header(t, fonts):
    W, H = 1200, 320
    x0, label_y, title_y, tag_y = 84, 112, 198, 250
    mono, display, sans = fonts

    dollar, _ = mono.layout(LABEL[0], 22, x0, label_y)
    who, _ = mono.layout(LABEL[1], 22, x0 + 26, label_y, tracking=1.5)
    title, _ = display.layout(TITLE, 80, x0 - 4, title_y)
    title_end = max(b[2] for _, _, b in title if b)
    cap_top = min(b[1] for _, _, b in title if b)
    letters = "".join(
        f'<path class="g" style="animation-delay:{0.15 + i * 0.07:.2f}s" pathLength="1" d="{d}"/>'
        for i, (_, d, _) in enumerate(title) if d
    )

    tag, x = [], x0
    for i, part in enumerate(TAGLINE):
        glyphs, w = sans.layout(part, 25, x, tag_y)
        tag.append(paths(glyphs))
        x += w
        if i < len(TAGLINE) - 1:
            cx, cy = x + 20, tag_y - 9
            tag.append(f'<rect class="dia" x="{cx - 4.5:.1f}" y="{cy - 4.5:.1f}" width="9" height="9" rx="1.5" '
                       f'transform="rotate(45 {cx:.1f} {cy:.1f})"/>')
            x += 40

    # The spinning crystal and two small shards around it.
    ccx, ccy = 968, 158
    pal = t["crystal"]
    d0, spin, still = crystal(ccx, ccy, 56, pal, "c", frames=24, dur=5.0)
    d1, s1, s1s = crystal(0, 0, 15, pal, "a", frames=12, dur=6.5, tilt=10, lean=26, edge_w=1)
    d2, s2, s2s = crystal(0, 0, 12, pal, "b", frames=12, dur=5.5, tilt=20, lean=-30, edge_w=1)

    rnd = random.Random(7)
    particles = []
    for _ in range(22):
        dur = rnd.uniform(7, 13)
        particles.append(
            f'<circle cx="{rnd.uniform(30, W - 30):.0f}" cy="{rnd.uniform(60, H + 10):.0f}" '
            f'r="{rnd.choice([1.2, 1.6, 2.0, 2.4])}" fill="{rnd.choice(t["particles"])}" '
            f'style="--rise:-{rnd.uniform(70, 140):.0f}px;animation-duration:{dur:.1f}s;'
            f'animation-delay:-{rnd.uniform(0, dur):.1f}s"/>'
        )
    sparks = "".join(
        f'<g transform="translate({sx} {sy}) scale({sr})"><path class="sp" d="{SPARK}" '
        f'style="animation-delay:{i * 0.55:.2f}s"/></g>'
        for i, (sx, sy, sr) in enumerate(
            [(898, 70, 11), (1050, 132, 8), (1030, 262, 6), (896, 168, 6), (1120, 54, 5), (944, 30, 5)])
    )

    bg0, bg1, bg2 = t["bg"]
    ti0, ti1, ti2 = t["title"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{ALT}">
<title>{ALT}</title>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg0}"/><stop offset=".55" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<radialGradient id="glow1" cx="{ccx}" cy="{ccy + 10}" r="230" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t["glow1"][0]}" stop-opacity="{t["glow1"][1]}"/><stop offset="1" stop-color="{t["glow1"][0]}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx="120" cy="20" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t["glow2"][0]}" stop-opacity="{t["glow2"][1]}"/><stop offset="1" stop-color="{t["glow2"][0]}" stop-opacity="0"/></radialGradient>
<radialGradient id="floor" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["floor"][0]}" stop-opacity="{t["floor"][1]}"/><stop offset="1" stop-color="{t["floor"][0]}" stop-opacity="0"/></radialGradient>
<linearGradient id="title" x1="{x0}" y1="0" x2="{title_end:.0f}" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
<stop offset="0" stop-color="{ti0}"/><stop offset=".5" stop-color="{ti1}"/><stop offset="1" stop-color="{ti2}"/>
<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{2 * (title_end - x0):.0f} 0" dur="14s" repeatCount="indefinite"/>
</linearGradient>
<pattern id="lattice" width="48" height="83.14" patternUnits="userSpaceOnUse">
<path d="M0 0L48 83.14M48 0L0 83.14M0 41.57H48" fill="none" stroke="{t["lattice"][0]}" stroke-opacity="{t["lattice"][1]}"/>
</pattern>
<radialGradient id="fade" cx="{ccx}" cy="{ccy}" r="520" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="latticeMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
{d0}{d1}{d2}
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>
.g{{fill:url(#title);stroke:{t["title_stroke"]};stroke-width:1.4;stroke-dasharray:1;stroke-dashoffset:0;stroke-opacity:0;animation:draw 2.6s cubic-bezier(.6,0,.2,1) backwards}}
@keyframes draw{{0%{{stroke-dashoffset:1;stroke-opacity:1;fill-opacity:0}}55%{{stroke-dashoffset:0;stroke-opacity:1;fill-opacity:0}}100%{{stroke-dashoffset:0;stroke-opacity:0;fill-opacity:1}}}}
.label{{animation:rise .9s ease-out backwards}}
.tag{{fill:{t["tag"]};animation:rise .9s ease-out 1.6s backwards}}
.dia{{fill:{t["accent"]}}}
@keyframes rise{{0%{{opacity:0;transform:translateY(10px)}}100%{{opacity:1;transform:none}}}}
.cursor{{fill:{t["accent"]};animation:show .3s 2.3s backwards,blink 1.1s steps(1) 2.6s infinite}}
@keyframes show{{0%{{opacity:0}}}}
@keyframes blink{{50%{{opacity:0}}}}
.float{{animation:float 6s ease-in-out infinite}}
@keyframes float{{0%,100%{{transform:translateY(-7px)}}50%{{transform:translateY(7px)}}}}
.floor{{transform-box:fill-box;transform-origin:center;animation:pulse 6s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{transform:scaleX(.82);opacity:.7}}50%{{transform:scaleX(1);opacity:1}}}}
.p circle{{opacity:0;animation:drift linear infinite}}
@keyframes drift{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:{t["particle_op"]}}}80%{{opacity:{t["particle_op"]}}}100%{{transform:translateY(var(--rise));opacity:0}}}}
.sp{{fill:#fff;transform-box:fill-box;transform-origin:center;transform:scale(0);animation:twinkle 3.3s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{transform:scale(0) rotate(0deg);opacity:0}}45%{{transform:scale(1) rotate(45deg);opacity:1}}70%{{transform:scale(0) rotate(90deg);opacity:0}}}}
.spin-static{{display:none}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.spin{{display:none}}.spin-static{{display:inline}}.sp{{transform:scale(1)}}}}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#glow2)"/>
<rect width="{W}" height="{H}" fill="url(#lattice)" mask="url(#latticeMask)"/>
<rect width="{W}" height="{H}" fill="url(#glow1)"/>
<g class="p">{"".join(particles)}</g>
<ellipse class="floor" cx="{ccx}" cy="{H - 26}" rx="120" ry="14" fill="url(#floor)"/>
<g transform="translate(852 236)"><g class="float" style="animation-delay:-2s">{s1}{s1s}</g></g>
<g transform="translate(1082 92)"><g class="float" style="animation-delay:-4s;animation-duration:7s">{s2}{s2s}</g></g>
<g class="float">{spin}{still}</g>
<g>{sparks}</g>
<g class="label"><g fill="{t["label_dim"]}">{paths(dollar)}</g><g fill="{t["label"]}">{paths(who)}</g></g>
<g>{letters}</g>
<rect class="cursor" x="{title_end + 12:.1f}" y="{cap_top:.1f}" width="9" height="{title_y - cap_top:.1f}" rx="2"/>
<g class="tag">{"".join(tag)}</g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="21.5" fill="none" stroke="{t["border"][0]}" stroke-opacity="{t["border"][1]}"/>
</svg>
'''


def _mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def _ramp(stops, t):
    t = min(1.0, max(0.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return _mix(stops[i], stops[i + 1], t - i)


def _hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def _point(x, base, w, h, tip, lean, col, back, depth):
    """A 2D quartz point (3 prism faces + 3 tip facets) leaned about its base.

    Returns (polygons, outline path for clipping, tip position)."""
    hw, a = w / 2, math.radians(lean)
    x1, x2 = -hw * 0.3, hw * 0.34
    apex = (w * 0.04, -h - tip)

    def place(px, py):
        return (x + px * math.cos(a) - py * math.sin(a), base + px * math.sin(a) + py * math.cos(a))

    faces = [
        ([(-hw, 0), (x1, 0), (x1, -h), (-hw, -h)], 0.16),
        ([(x1, 0), (x2, 0), (x2, -h), (x1, -h)], -0.08),
        ([(x2, 0), (hw, 0), (hw, -h), (x2, -h)], -0.42),
        ([(-hw, -h), (x1, -h), apex], 0.38),
        ([(x1, -h), (x2, -h), apex], 0.18),
        ([(x2, -h), (hw, -h), apex], -0.2),
    ]
    polys = []
    for pts, shade in faces:
        c = _mix(col, (255, 255, 255), shade) if shade > 0 else _mix(col, (25, 10, 50), -shade)
        c = _mix(c, back, depth)
        polys.append(f'<polygon points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in map(lambda p: place(*p), pts))}" '
                     f'fill="{_hex(c)}"/>')
    hull = [place(*p) for p in [(-hw, 0), (-hw, -h), apex, (hw, -h), (hw, 0)]]
    outline = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in hull) + "Z"
    return "".join(polys), outline, place(*apex)


def footer(t):
    W, H = 1200, 170
    bed = t["bed"]
    rnd = random.Random(11)
    layers, outlines, tips = [], [], []
    # back -> front; taller points toward the centre
    for depth, count, hscale, wscale in ((bed["depth"][0], 34, 0.78, 0.8), (bed["depth"][1], 30, 1.0, 1.0), (0.0, 22, 0.72, 1.1)):
        group = []
        for i in range(count):
            x = (i + rnd.uniform(0.1, 0.9)) * W / count
            centre = 1 - abs(x - W / 2) / (W / 2)
            h = (18 + 70 * centre ** 1.4 + rnd.uniform(0, 26)) * hscale
            w = rnd.uniform(16, 28) * wscale
            tip = w * rnd.uniform(0.7, 1.0)
            lean = rnd.uniform(-24, 24) + (x - W / 2) / W * 30
            polys, outline, apex = _point(x, H + 6, w, h, tip, lean, _ramp(bed["ramp"], x / W), bed["back"], depth)
            group.append(polys)
            outlines.append(outline)
            if depth == 0.0 or (depth == bed["depth"][1] and rnd.random() < 0.5):
                tips.append(apex)
        layers.append(f'<g>{"".join(group)}</g>')

    sparks = "".join(
        f'<g transform="translate({sx:.0f} {sy - 4:.0f}) scale({rnd.choice([5, 6, 7, 8])})">'
        f'<path class="sp" d="{SPARK}" style="animation-delay:{i * 0.7:.1f}s"/></g>'
        for i, (sx, sy) in enumerate(rnd.sample(tips, 7))
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Quartz crystals">
<title>Quartz crystals</title>
<defs>
<radialGradient id="glow" cx="{W / 2}" cy="{H}" r="{W * 0.45}" gradientTransform="translate(0 {H * 0.7}) scale(1 0.3)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{bed["glow"][0]}" stop-opacity="{bed["glow"][1]}"/><stop offset="1" stop-color="{bed["glow"][0]}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="{bed["fade"]}"/></linearGradient>
<linearGradient id="sides" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".1" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="sidesMask"><rect width="{W}" height="{H}" fill="url(#sides)"/></mask>
<mask id="fadeMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="points"><path d="{"".join(outlines)}"/></clipPath>
</defs>
<style>
.shine{{animation:sweep 7s ease-in-out infinite}}
@keyframes sweep{{0%{{transform:translateX(-300px)}}35%,100%{{transform:translateX({W + 300}px)}}}}
.sp{{fill:#fff;transform-box:fill-box;transform-origin:center;transform:scale(0);animation:twinkle 4.2s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{transform:scale(0) rotate(0);opacity:0}}40%{{transform:scale(1) rotate(45deg);opacity:1}}65%{{transform:scale(0) rotate(90deg);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.shine{{display:none}}}}
</style>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<g mask="url(#sidesMask)">
<g mask="url(#fadeMask)" stroke="{bed["edge"][0]}" stroke-opacity="{bed["edge"][1]}" stroke-width=".8" stroke-linejoin="round">{"".join(layers)}</g>
<g clip-path="url(#points)"><g class="shine"><rect x="-200" y="0" width="160" height="{H}" fill="url(#shine)" transform="skewX(-20)"/></g></g>
{sparks}
</g>
</svg>
'''


def main():
    fonts = (font("JetBrains Mono", 500), font("Unbounded", 700), font("Onest", 500))
    for name, theme in THEMES.items():
        for kind, svg in (("header", header(theme, fonts)), ("footer", footer(theme))):
            path = OUT / f"{kind}-{name}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(OUT.parent)}  {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
