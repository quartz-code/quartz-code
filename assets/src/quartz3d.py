"""Iridescent ("aura") quartz crystals rendered as SVG.

A crystal is a double-terminated hexagonal prism. Faces are coloured by the
direction they point in, the way aura quartz shifts colour with the viewing
angle, so a spinning crystal runs through the whole rainbow.

The prism has 6-fold symmetry: spinning it by 60 degrees lands on the same
silhouette, so one looped 60-degree turn reads as endless rotation. The solid
is convex, so faces never need depth sorting: back faces go in a faint layer
behind, front faces in a glassy layer on top, and each face switches layers
with an opacity animation.
"""
import math


def _norm(v):
    length = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / length for c in v)


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _rx(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0], c * v[1] - s * v[2], s * v[1] + c * v[2])


def _rz(v, a):
    c, s = math.cos(a), math.sin(a)
    return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def cyclic(stops, t):
    """Sample a closed colour loop at t (wraps around)."""
    t = (t % 1.0) * len(stops)
    i = int(t) % len(stops)
    return mix(stops[i], stops[(i + 1) % len(stops)], t - int(t))


def _faces(theta, R=1.0, H=1.2, P=1.05, Pb=0.9):
    top = [(R * math.cos(theta + k * math.pi / 3), H, R * math.sin(theta + k * math.pi / 3)) for k in range(6)]
    bot = [(x, -H, z) for x, _, z in top]
    apex_t, apex_b = (0.0, H + P, 0.0), (0.0, -H - Pb, 0.0)
    out = []
    for k in range(6):
        n = (k + 1) % 6
        out.append(("side", [top[k], top[n], bot[n], bot[k]]))
        out.append(("cap", [apex_t, top[n], top[k]]))
        out.append(("foot", [apex_b, bot[k], bot[n]]))
    return out


def _frame(theta, tilt, lean):
    """World-space faces with outward unit normals (z points at the viewer)."""
    out = []
    for kind, verts in _faces(theta):
        world = [_rz(_rx(v, tilt), lean) for v in verts]
        n = _norm(_cross(_sub(world[1], world[0]), _sub(world[2], world[0])))
        centroid = tuple(sum(c) / len(world) for c in zip(*world))
        if _dot(n, centroid) < 0:
            n = tuple(-c for c in n)
        out.append((kind, world, n))
    return out


def shade(n, kind, pal):
    """(highlight, lowlight) colours of a face with outward normal n.

    Shadowed sides sink into a deep violet instead of black, so the glass
    keeps its colour; the facing side and the specular glint go to white."""
    light = _norm((-0.45, 0.75, 0.6))
    half = _norm((light[0], light[1], light[2] + 1))
    diff = max(0.0, _dot(n, light))
    spec = max(0.0, _dot(n, half)) ** 18
    base = cyclic(pal["aura"], math.atan2(n[1], n[0]) / (2 * math.pi) + 0.5 * n[2])
    if kind == "foot":
        base = mix(base, pal["deep"], 0.3)
    col = mix(base, pal["deep"], (1 - diff) * pal["shadow"])
    col = mix(col, (255, 255, 255), min(1.0, pal["gloss"] + pal["spec"] * spec))
    return hexc(mix(col, (255, 255, 255), 0.16)), hexc(mix(col, pal["deep"], 0.22))


def crystal(cx, cy, scale, pal, prefix, frames=20, dur=6.0, tilt=14, lean=-8, edge=1.4, spin=True, theta0=0.0):
    """Return (defs, svg) for one crystal; a crystal that doesn't spin is a single frame.

    The svg has a faint back layer and a glassy front layer. A spinning crystal
    also carries a still copy of its first frame, shown when motion is reduced.
    """
    tilt, lean = math.radians(tilt), math.radians(lean)
    data = None
    for f in range(frames + 1 if spin else 1):
        frame = _frame(theta0 + math.radians(60.0 * f / frames), tilt, lean)
        if data is None:
            data = [{"pts": [], "hi": [], "lo": [], "front": []} for _ in frame]
        for d, (kind, world, n) in zip(data, frame):
            d["pts"].append(" ".join(f"{cx + scale * x:.1f},{cy - scale * y:.1f}" for x, y, _ in world))
            hi, lo = shade(n, kind, pal)
            d["hi"].append(hi)
            d["lo"].append(lo)
            d["front"].append(n[2] > 0)

    anim = f'dur="{dur}s" repeatCount="indefinite"'
    defs, back, front, still_back, still_front = [], [], [], [], []
    for i, d in enumerate(data):
        gid = f"{prefix}{i}"
        if d["front"][0]:
            defs.append(f'<linearGradient id="{gid}s" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="{d["hi"][0]}"/>'
                        f'<stop offset="1" stop-color="{d["lo"][0]}"/></linearGradient>')
            still_front.append(f'<polygon points="{d["pts"][0]}" fill="url(#{gid}s)"/>')
        else:
            still_back.append(f'<polygon points="{d["pts"][0]}"/>')
        if not spin:
            continue
        move = f'<animate attributeName="points" {anim} values="{";".join(d["pts"])}"/>'
        if any(d["front"]):
            defs.append(
                f'<linearGradient id="{gid}" x1="0" y1="0" x2=".35" y2="1">'
                f'<stop offset="0" stop-color="{d["hi"][0]}"><animate attributeName="stop-color" {anim} values="{";".join(d["hi"])}"/></stop>'
                f'<stop offset="1" stop-color="{d["lo"][0]}"><animate attributeName="stop-color" {anim} values="{";".join(d["lo"])}"/></stop>'
                "</linearGradient>")
            shown = ";".join("1" if x else "0" for x in d["front"])
            toggle = f'<animate attributeName="opacity" {anim} values="{shown}"/>' if "0" in shown else ""
            front.append(f'<polygon points="{d["pts"][0]}" fill="url(#{gid})" opacity="{shown[0]}">{move}{toggle}</polygon>')
        if not all(d["front"]):
            shown = ";".join("0" if x else "1" for x in d["front"])
            toggle = f'<animate attributeName="opacity" {anim} values="{shown}"/>' if "0" in shown else ""
            back.append(f'<polygon points="{d["pts"][0]}" opacity="{shown[0]}">{move}{toggle}</polygon>')

    back_attr = (f'fill="{pal["back"]}" fill-opacity="{pal["back_op"]}" stroke="{pal["edge"]}" '
                 f'stroke-opacity="{pal["back_edge_op"]}" stroke-width="{edge * 0.7:.2f}" stroke-linejoin="round"')
    front_attr = (f'fill-opacity="{pal["front_op"]}" stroke="{pal["edge"]}" stroke-opacity="{pal["edge_op"]}" '
                  f'stroke-width="{edge}" stroke-linejoin="round"')
    still = f'<g {back_attr}>{"".join(still_back)}</g><g {front_attr}>{"".join(still_front)}</g>'
    if not spin:
        return "".join(defs), still
    moving = f'<g {back_attr}>{"".join(back)}</g><g {front_attr}>{"".join(front)}</g>'
    return "".join(defs), f'<g class="spin">{moving}</g><g class="spin-static">{still}</g>'
