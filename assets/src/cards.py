"""The profile cards: hero, specimen passport, gem stack and the crystal-growth chart."""
import datetime as dt
import json
import math
import random

from quartz3d import crystal, cyclic, hexc, mix, rgb
from theme import BODY, DISPLAY, HEADING, HERE, MONO, card, fit, font, heading, paths, spark, text

ROLES = ["Mobile & Backend Developer", "GameDev Enthusiast", "Data Analysis Explorer"]
MONTHS = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]

# (logo, label, gem colour, logo colour); logos are simple-icons paths (CC0) in logos.json
STACK = [
    ("kotlin", "Kotlin", "#8b5cf6", "#ffffff"),
    ("java", "Java", "#e03a4e", "#ffffff"),
    ("spring", "Spring", "#22b07d", "#ffffff"),
    ("docker", "Docker", "#2496ed", "#ffffff"),
    ("unity", "Unity", "#dfe3ee", "#22213a"),
    ("unreal", "Unreal", "#3a3655", "#ffffff"),
    ("js", "JavaScript", "#f5c518", "#2a2208"),
    ("ts", "TypeScript", "#2f6fdc", "#ffffff"),
    ("html", "HTML", "#f07a2a", "#ffffff"),
]
# A steaming cup for Java, drawn here (24x24 like the simple-icons paths).
JAVA_CUP = ('<path d="M4.5 8.6h13v4.4a6.5 6.5 0 0 1-13 0z"/>'
            '<g fill="none" stroke-width="1.7" stroke-linecap="round">'
            '<path d="M8 2.6c-1.1 1.3 1.1 2.3 0 3.7M11.5 1.8c-1.1 1.4 1.1 2.5 0 4M15 2.6c-1.1 1.3 1.1 2.3 0 3.7"/>'
            '<path d="M17.6 10.1h1.1a2.6 2.6 0 0 1 0 5.2h-1.5M3 21.6h17"/></g>')


def plural(n, one, few, many):
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def _typing(t, x_center, y, size, period=12.0):
    """Type each role, hold it, erase it; SMIL with discrete steps, one slot per role."""
    slot = period / len(ROLES)
    defs, out = [], []
    for i, role in enumerate(ROLES):
        width = font(MONO).layout(role, size)[1]
        x0 = x_center - width / 2
        glyphs, _ = font(MONO).layout(role, size, x0, y)
        adv = width / len(role)
        times, widths = [], []
        for c in range(len(role) + 1):                    # typing
            times.append(c * 0.045)
            widths.append(c * adv)
        hold_end = times[-1] + 0.55 * slot
        for c in range(len(role), -1, -1):                # erasing
            times.append(hold_end + (len(role) - c) * 0.02)
            widths.append(c * adv)
        keys = [(i * slot + tm) / period for tm in times]
        if i:
            keys, widths = [0.0] + keys, [0.0] + widths
        keys, widths = keys + [1.0], widths + [0.0]
        key_times = ";".join(f"{k:.4f}" for k in keys)
        anim = f'dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{key_times}"'
        defs.append(f'<clipPath id="type{i}"><rect x="{x0:.1f}" y="{y - size}" width="0" height="{size * 1.4:.0f}">'
                    f'<animate attributeName="width" {anim} values="{";".join(f"{w:.1f}" for w in widths)}"/></rect></clipPath>')
        out.append(f'<g clip-path="url(#type{i})" fill="{t["type"]}">{paths(glyphs)}</g>')
        out.append(f'<rect x="{x0:.1f}" y="{y - size * 0.82:.1f}" width="{size * 0.09:.1f}" height="{size}" fill="{t["cursor"]}" opacity="0">'
                   f'<animate attributeName="x" {anim} values="{";".join(f"{x0 + w:.1f}" for w in widths)}"/>'
                   f'<animate attributeName="opacity" {anim} values="{";".join("1" if w > 0 else "0" for w in widths)}"/></rect>')
    still, _ = text(ROLES[0], MONO, size, x_center, y, anchor="middle")
    return "".join(defs), f'<g class="type">{"".join(out)}</g><g class="type-static" fill="{t["type"]}">{still}</g>'


def hero(t):
    W, H = 1200, 780
    pal = t["crystal"]
    defs, main = crystal(600, 300, 92, pal, "m", frames=20, dur=7.0, tilt=14, lean=-7)
    shards = []
    for i, (x, y, s, lean, tilt, th, delay) in enumerate([
            (330, 200, 24, 28, 10, 0.3, -1.5), (875, 168, 20, -32, 18, 1.1, -3.2), (300, 430, 16, -22, 12, 0.7, -0.6),
            (905, 420, 26, 34, 8, 0.2, -4.4), (190, 300, 11, 10, 20, 0.9, -2.0), (1010, 300, 13, -12, 16, 0.4, -5.1)]):
        d, g = crystal(0, 0, s, pal, f"s{i}_", tilt=tilt, lean=lean, spin=False, theta0=th, edge=1.0)
        defs += d
        shards.append(f'<g transform="translate({x} {y})"><g class="bob" style="animation-delay:{delay}s">{g}</g></g>')

    rnd = random.Random(5)
    particles = []
    for _ in range(26):
        dur = rnd.uniform(8, 14)
        particles.append(
            f'<circle cx="{rnd.uniform(40, W - 40):.0f}" cy="{rnd.uniform(80, H):.0f}" r="{rnd.choice([1.4, 1.8, 2.2, 2.8])}" '
            f'fill="{rnd.choice(t["particles"])}" style="--rise:-{rnd.uniform(80, 170):.0f}px;'
            f'animation-duration:{dur:.1f}s;animation-delay:-{rnd.uniform(0, dur):.1f}s"/>')
    sparks = "".join(spark(x, y, r, i * 0.6) for i, (x, y, r) in enumerate(
        [(548, 92, 13), (690, 210, 9), (470, 330, 8), (742, 410, 11), (402, 140, 6), (812, 300, 6), (612, 520, 7)]))

    title, tw = font(DISPLAY).layout("QUARTZ-CODE", 78, 0, 0, tracking=4)
    tx = (W - tw) / 2
    title, _ = font(DISPLAY).layout("QUARTZ-CODE", 78, tx, 636, tracking=4)
    tdefs, typing = _typing(t, W / 2, 712, 36)
    a0, a1, a2, a3 = t["accent"]
    defs += (f'<linearGradient id="title" x1="{tx:.0f}" x2="{tx + tw:.0f}" y1="0" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">'
             f'<stop offset="0" stop-color="{a0}"/><stop offset=".35" stop-color="{a1}"/><stop offset=".7" stop-color="{a2}"/><stop offset="1" stop-color="{a3}"/>'
             f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{2 * tw:.0f} 0" dur="16s" repeatCount="indefinite"/>'
             f'</linearGradient>'
             f'<radialGradient id="floor" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["floor"][0]}" stop-opacity="{t["floor"][1]}"/>'
             f'<stop offset="1" stop-color="{t["floor"][0]}" stop-opacity="0"/></radialGradient>{tdefs}')
    style = (".bob{animation:bob 7s ease-in-out infinite}"
             "@keyframes bob{0%,100%{transform:translateY(-6px)}50%{transform:translateY(6px)}}"
             ".float{animation:float 8s ease-in-out infinite}"
             "@keyframes float{0%,100%{transform:translateY(-8px)}50%{transform:translateY(8px)}}"
             ".floor{transform-box:fill-box;transform-origin:center;animation:pulse 8s ease-in-out infinite}"
             "@keyframes pulse{0%,100%{transform:scaleX(.8);opacity:.65}50%{transform:scaleX(1);opacity:1}}"
             ".p circle{opacity:0;animation:drift linear infinite}"
             f"@keyframes drift{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:{t['particle_op']}}}"
             f"80%{{opacity:{t['particle_op']}}}100%{{transform:translateY(var(--rise));opacity:0}}}}"
             ".title{animation:rise 1.2s cubic-bezier(.2,.7,.2,1) .2s backwards}"
             "@keyframes rise{0%{opacity:0;transform:translateY(16px)}100%{opacity:1;transform:none}}")
    glows = [(420, 250, 270, t["glows"]), (790, 230, 280, t["glow2"]), (640, 480, 240, t["glow4"]), (600, 130, 330, t["glow3"])]
    body = (f'<g class="p">{"".join(particles)}</g>'
            f'<ellipse class="floor" cx="600" cy="540" rx="170" ry="20" fill="url(#floor)"/>'
            f'{"".join(shards)}<g class="float">{main}</g><g>{sparks}</g>'
            f'<g class="title" fill="url(#title)">{paths(title)}</g>{typing}')
    return card(W, H, t, body, defs=defs, style=style, glows=glows,
                title="quartz-code — Mobile &amp; Backend Developer · GameDev Enthusiast · Data Analysis Explorer")


def _gem(cx, cy, R, colour, glyph, logo_colour, label, t, idx):
    """A hexagonal gem seen from above: star facets around a table with the logo."""
    base, deep = rgb(colour), (24, 14, 54)
    light = math.radians(-125)                     # light from the upper left
    outer = [(cx + R * math.cos(math.radians(-90 + 60 * k)), cy + R * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    inner = [(cx + 0.6 * R * math.cos(math.radians(-90 + 60 * k)), cy + 0.6 * R * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    facets = []
    for k in range(6):
        n = (k + 1) % 6
        mid = ((outer[k][0] + outer[n][0]) / 2, (outer[k][1] + outer[n][1]) / 2)
        for tri, bias in (([outer[k], mid, inner[k]], 0.10), ([mid, inner[n], inner[k]], -0.12), ([mid, outer[n], inner[n]], 0.10)):
            gx = sum(p[0] for p in tri) / 3 - cx
            gy = sum(p[1] for p in tri) / 3 - cy
            b = 0.5 + 0.5 * math.cos(math.atan2(gy, gx) - light) + bias
            col = mix(base, (255, 255, 255), (b - 0.55) * 0.9) if b > 0.55 else mix(base, deep, (0.55 - b) * 0.75)
            facets.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in tri)}" fill="{hexc(col)}"/>')
    defs = (f'<radialGradient id="tbl{idx}" cx=".38" cy=".3" r=".85">'
            f'<stop offset="0" stop-color="{hexc(mix(base, (255, 255, 255), 0.42))}"/><stop offset=".55" stop-color="{colour}"/>'
            f'<stop offset="1" stop-color="{hexc(mix(base, deep, 0.35))}"/></radialGradient>'
            f'<radialGradient id="halo{idx}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{colour}" stop-opacity="{t["gem_halo"]}"/>'
            f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/></radialGradient>')
    size = R * 0.62
    table = " ".join(f"{x:.1f},{y:.1f}" for x, y in inner)
    label_d, _ = text(label, HEADING, 34, cx, cy + R + 52, anchor="middle")
    svg = (f'<ellipse cx="{cx:.0f}" cy="{cy + R * 0.15:.0f}" rx="{R * 1.25:.0f}" ry="{R * 1.1:.0f}" fill="url(#halo{idx})"/>'
           f'<g class="gem" style="animation-delay:{0.1 + idx * 0.09:.2f}s">'
           f'<g stroke="{t["gem_edge"][0]}" stroke-opacity="{t["gem_edge"][1]}" stroke-width="1.2" stroke-linejoin="round">'
           f'{"".join(facets)}<polygon points="{table}" fill="url(#tbl{idx})"/></g>'
           f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2 - R * 0.06:.1f}) scale({size / 24:.3f})" '
           f'fill="{logo_colour}" stroke="{logo_colour}" fill-opacity=".95">{glyph}</g></g>'
           f'<g fill="{t["text"]}">{label_d}</g>'
           + spark(outer[5][0] + R * 0.18, outer[5][1] + R * 0.1, 10, idx * 0.45))
    return defs, svg


def stack(t):
    logos = json.loads((HERE / "logos.json").read_text())
    W, R = 1200, 112
    col_w, row_h, top = R * math.sqrt(3) + 96, 2 * R + 96, 318
    H = int(top + 2 * row_h + R + 110)
    defs, body = [], [heading(t, W, 110, "Технологии")]
    for i, (key, label, colour, logo_colour) in enumerate(STACK):
        row, col = divmod(i, 3)
        glyph = JAVA_CUP if key == "java" else f'<path d="{logos[key]}"/>'
        d, g = _gem(W / 2 + (col - 1) * col_w, top + row * row_h, R, colour, glyph, logo_colour, label, t, i)
        defs.append(d)
        body.append(g)
    style = (".gem{transform-box:fill-box;transform-origin:center;animation:pop .7s cubic-bezier(.2,.8,.2,1.2) backwards}"
             "@keyframes pop{0%{opacity:0;transform:scale(.6)}100%{opacity:1;transform:none}}")
    return card(W, H, t, "".join(body), defs="".join(defs), style=style,
                title="Технологии: " + ", ".join(label for _, label, _, _ in STACK))


def passport(t, data):
    W, H = 1200, 920
    pal = t["crystal"]
    defs, body = [], [heading(t, W, 110, "Паспорт образца")]

    # the specimen: a little druse on a rock
    cluster = []
    for i, (x, y, s, lean, tilt, th) in enumerate([(205, 450, 40, -34, 12, 0.5), (402, 442, 44, 30, 16, 1.2),
                                                   (300, 400, 66, -6, 14, 0.15), (250, 515, 26, -58, 10, 0.9)]):
        d, g = crystal(x, y, s, pal, f"p{i}_", spin=False, tilt=tilt, lean=lean, theta0=th, edge=1.2)
        defs.append(d)
        cluster.append(g)
    r0, r1, r2 = t["rock"]
    rock = (f'<polygon points="128,570 168,528 236,516 300,530 372,514 446,536 478,576 440,620 300,634 170,620" fill="{r1}"/>'
            f'<polygon points="168,528 236,516 300,530 372,514 446,536 400,560 300,570 210,558" fill="{r2}"/>'
            f'<polygon points="128,570 168,528 210,558 300,570 300,634 170,620" fill="{r0}"/>')
    defs.append(f'<radialGradient id="specGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["accent"][1]}" stop-opacity=".35"/>'
                f'<stop offset="1" stop-color="{t["accent"][1]}" stop-opacity="0"/></radialGradient>')
    body.append('<ellipse cx="300" cy="400" rx="250" ry="230" fill="url(#specGlow)"/>')
    body.append("".join(cluster) + rock + spark(262, 230, 12, 0.2) + spark(430, 350, 8, 1.4) + spark(175, 370, 7, 2.3))

    # who: one line per fact, gem bullets, no field labels
    x0, max_w = 560, 590
    for k, value in enumerate(["Mobile & Backend Developer", "GameDev · Data Analysis", f"GitHub · с {data['since']} года"]):
        y = 318 + k * 92
        d, _ = text(value, HEADING, fit(value, HEADING, 40, max_w - 40), x0 + 40, y)
        body.append(f'<rect x="{x0 + 4}" y="{y - 22}" width="13" height="13" fill="url(#accent)" transform="rotate(45 {x0 + 10.5} {y - 15.5})"/>'
                    f'<g fill="{t["text"]}">{d}</g>')
        if k < 2:
            body.append(f'<rect x="{x0}" y="{y + 34}" width="{max_w}" height="1.5" fill="{t["line"][0]}" fill-opacity="{t["line"][1]}"/>')

    # headline numbers
    n = data["year_total"], data["commits_year"], data["prs_merged"], data["streak_longest"]
    tiles = [(n[0], plural(n[0], "вклад", "вклада", "вкладов") + " за год"),
             (n[1], plural(n[1], "коммит", "коммита", "коммитов") + " за год"),
             (n[2], "смёржено PR"),
             (n[3], plural(n[3], "день", "дня", "дней") + " — рекорд")]
    y, tw, gap = 640, 255, 20
    for i, (num, label) in enumerate(tiles):
        tx = (W - 4 * tw - 3 * gap) / 2 + i * (tw + gap)
        num_d, _ = text(str(num), DISPLAY, fit(str(num), DISPLAY, 74, tw - 30), tx + tw / 2, y + 112, anchor="middle")
        lbl_d, _ = text(label, BODY, fit(label, BODY, 30, tw - 28), tx + tw / 2, y + 168, anchor="middle")
        body.append(f'<g class="tile" style="animation-delay:{0.15 + i * 0.12:.2f}s">'
                    f'<rect x="{tx:.0f}" y="{y}" width="{tw}" height="210" rx="26" fill="{t["tile"][0]}" fill-opacity="{t["tile"][1]}" '
                    f'stroke="url(#accent)" stroke-opacity=".7" stroke-width="2"/>'
                    f'<path d="M{tx + 26:.0f} {y}H{tx + tw * 0.62:.0f}L{tx:.0f} {y + 130}V{y + 26}A26 26 0 0 1 {tx + 26:.0f} {y}Z" '
                    f'fill="#fff" fill-opacity="{t["tile_gloss"]}"/>'
                    f'<g fill="url(#accent)">{num_d}</g><g fill="{t["muted"]}">{lbl_d}</g></g>')
    style = (".tile{animation:up .8s cubic-bezier(.2,.8,.2,1) backwards}"
             "@keyframes up{0%{opacity:0;transform:translateY(24px)}100%{opacity:1;transform:none}}")
    summary = ", ".join(f"{num} {label}" for num, label in tiles)
    return card(W, H, t, "".join(body), defs="".join(defs), style=style,
                title=f"Mobile &amp; Backend Developer · GameDev · Data Analysis · GitHub с {data['since']} года · {summary}")


def _point(x, base, w, h, col, deep, lean=0.0):
    """2D quartz point (three prism faces, three tip facets) leaned about its base."""
    hw, tip, a = w / 2, w * 0.95, math.radians(lean)
    x1, x2 = -hw * 0.28, hw * 0.34
    apex = (w * 0.04, -h - tip)

    def place(px, py):
        return (x + px * math.cos(a) - py * math.sin(a), base + px * math.sin(a) + py * math.cos(a))

    white = (255, 255, 255)
    faces = [([(-hw, 0), (x1, 0), (x1, -h), (-hw, -h)], mix(col, white, 0.22)),
             ([(x1, 0), (x2, 0), (x2, -h), (x1, -h)], col),
             ([(x2, 0), (hw, 0), (hw, -h), (x2, -h)], mix(col, deep, 0.42)),
             ([(-hw, -h), (x1, -h), apex], mix(col, white, 0.45)),
             ([(x1, -h), (x2, -h), apex], mix(col, white, 0.18)),
             ([(x2, -h), (hw, -h), apex], mix(col, deep, 0.25))]
    svg = "".join('<polygon points="%s" fill="%s"/>' % (" ".join("%.1f,%.1f" % place(*p) for p in pts), hexc(c))
                  for pts, c in faces)
    return svg, place(*apex)


def _rock(t, x0, x1, base):
    """Low-poly stone the crystals grow out of."""
    r = random.Random(9)
    top, x = [(x0, base + 18)], x0
    while x < x1:
        x += r.uniform(40, 80)
        top.append((min(x, x1), base + r.uniform(-2, 14)))
    bottom = base + 46
    c0, c1, c2 = t["rock"]
    out = [f'<polygon points="{x0},{bottom} {" ".join(f"{px:.0f},{py:.0f}" for px, py in top)} {x1},{bottom}" fill="{c0}"/>']
    for (ax, ay), (bx, by) in zip(top, top[1:]):
        out.append(f'<polygon points="{ax:.0f},{ay:.0f} {bx:.0f},{by:.0f} {(ax + bx) / 2:.0f},{bottom - 8}" '
                   f'fill="{c1 if r.random() > .5 else c2}" fill-opacity=".9"/>')
    return "".join(out)


def druse(t, data):
    """The last year as a druse: one crystal per week, taller for more contributions."""
    W, H = 1200, 680
    weeks = data["weeks"]
    peak = max(1, max(w["count"] for w in weeks))
    x_left, x_right, base = 74, 1126, 520
    step = (x_right - x_left) / len(weeks)
    rnd = random.Random(3)
    aura, deep = t["crystal"]["aura"], rgb(t["deep"])
    items, tops = [], []
    for i, w in enumerate(weeks):
        x = x_left + step * (i + 0.5)
        lean = rnd.uniform(-9, 9)
        if w["count"] == 0:
            poly, _ = _point(x, base + 4, step * 0.7, 3, rgb(t["pebble"]), deep, lean)
            items.append((0, f"<g>{poly}</g>"))
            continue
        k = math.sqrt(w["count"] / peak)
        h = 10 + 300 * k
        col = mix(cyclic(aura, i / len(weeks) * 1.15), deep, 0.35 * (1 - k))
        poly, apex = _point(x, base + 6, step * 1.3, h, col, deep, lean)
        items.append((h, f'<g class="grow" style="animation-delay:{0.2 + i * 0.025:.3f}s">{poly}</g>'))
        tops.append((h, apex))
    edge = f'stroke="#ffffff" stroke-opacity="{t["gem_edge"][1] + 0.03:.2f}" stroke-width=".8" stroke-linejoin="round"'
    body = [heading(t, W, 110, "Рост кристаллов"),
            f'<g {edge}>{"".join(svg for _, svg in sorted(items, key=lambda it: -it[0]))}</g>',
            _rock(t, x_left - 30, x_right + 30, base)]
    for k, (_, (ax, ay)) in enumerate(sorted(tops, reverse=True)[:3]):
        body.append(spark(ax, ay - 14, 13 - 2 * k, 0.8 + k * 1.1))
    last_x = -100.0
    for i, w in enumerate(weeks):                     # a label at the first week of each month
        month = dt.date.fromisoformat(w["start"]).month
        x = x_left + step * (i + 0.5)
        if i and month != dt.date.fromisoformat(weeks[i - 1]["start"]).month and x - last_x > 72:
            d, _ = text(MONTHS[month - 1], BODY, 30, x, base + 96, anchor="middle")
            body.append(f'<g fill="{t["muted"]}">{d}</g>')
            last_x = x
    style = (".grow{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1s cubic-bezier(.2,.9,.25,1.1) backwards}"
             "@keyframes grow{0%{transform:scaleY(0)}100%{transform:none}}")
    total = data["year_total"]
    return card(W, H, t, "".join(body), style=style,
                title=f"Рост кристаллов: {total} {plural(total, 'вклад', 'вклада', 'вкладов')} за последний год")
