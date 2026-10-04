"""Low-poly double-terminated quartz crystal spinning about its axis (SMIL).

The prism has 6-fold symmetry, so spinning it by 60 degrees lands on an
identical silhouette: one 60-degree turn, looped, reads as endless rotation.
Back faces are hidden by opacity (the solid is convex, so no depth sort).
"""
import math


def _norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / l for c in v)


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


def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def _ramp(stops, t):
    t = min(1.0, max(0.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return _lerp(stops[i], stops[i + 1], t - i)


def _hex(c):
    return "#" + "".join(f"{max(0, min(255, round(x))):02x}" for x in c)


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


def render(cx, cy, scale, pal, prefix="c", frames=30, dur=5.0, tilt=16, lean=-9, edge_w=1.3):
    """Return (defs, animated_group, static_group) SVG fragments."""
    light = _norm((-0.5, 0.8, 0.6))
    half = _norm((light[0], light[1], light[2] + 1))
    tx, lz = math.radians(tilt), math.radians(lean)

    faces = [{"pts": [], "hi": [], "lo": [], "op": []} for _ in _faces(0.0)]
    for f in range(frames + 1):
        for face, (kind, verts) in zip(faces, _faces(math.radians(60.0 * f / frames))):
            world = [_rz(_rx(v, tx), lz) for v in verts]
            n = _norm(_cross(_sub(world[1], world[0]), _sub(world[2], world[0])))
            centroid = tuple(sum(c) / len(world) for c in zip(*world))
            if _dot(n, centroid) < 0:
                n = tuple(-c for c in n)
            diff = max(0.0, _dot(n, light))
            spec = max(0.0, _dot(n, half)) ** 24
            base = _ramp(pal["ramp"], 0.5 + 0.6 * n[0])
            if kind == "foot":
                base = _lerp(base, pal["deep"], 0.4)
            k = pal["ambient"] + pal["diffuse"] * diff
            col = tuple(min(255.0, c * k + 255 * spec * pal["spec"]) for c in base)
            face["pts"].append(" ".join(f"{cx + scale * x:.1f},{cy - scale * y:.1f}" for x, y, _ in world))
            face["hi"].append(_hex(_lerp(col, (255, 255, 255), pal["gloss"])))
            face["lo"].append(_hex(tuple(c * 0.74 for c in col)))
            face["op"].append("1" if n[2] > 0 else "0")

    anim_attr = f'dur="{dur}s" repeatCount="indefinite"'
    defs, anim, static = [], [], []
    for i, face in enumerate(faces):
        if all(o == "0" for o in face["op"]):
            continue
        gid, sid = f"{prefix}{i}", f"{prefix}s{i}"
        defs.append(
            f'<linearGradient id="{gid}" x1="0" y1="0" x2=".3" y2="1">'
            f'<stop offset="0" stop-color="{face["hi"][0]}"><animate attributeName="stop-color" {anim_attr} values="{";".join(face["hi"])}"/></stop>'
            f'<stop offset="1" stop-color="{face["lo"][0]}"><animate attributeName="stop-color" {anim_attr} values="{";".join(face["lo"])}"/></stop>'
            "</linearGradient>"
        )
        op_anim = (f'<animate attributeName="opacity" {anim_attr} values="{";".join(face["op"])}"/>'
                   if len(set(face["op"])) > 1 else "")
        anim.append(
            f'<polygon points="{face["pts"][0]}" fill="url(#{gid})" opacity="{face["op"][0]}">'
            f'<animate attributeName="points" {anim_attr} values="{";".join(face["pts"])}"/>{op_anim}</polygon>'
        )
        if face["op"][0] == "1":
            defs.append(
                f'<linearGradient id="{sid}" x1="0" y1="0" x2=".3" y2="1">'
                f'<stop offset="0" stop-color="{face["hi"][0]}"/><stop offset="1" stop-color="{face["lo"][0]}"/></linearGradient>'
            )
            static.append(f'<polygon points="{face["pts"][0]}" fill="url(#{sid})"/>')
    edge = (f'stroke="{pal["edge"]}" stroke-opacity="{pal["edge_op"]}" '
            f'stroke-width="{edge_w}" stroke-linejoin="round"')
    return ("".join(defs),
            f'<g class="spin" {edge}>' + "".join(anim) + "</g>",
            f'<g class="spin-static" {edge}>' + "".join(static) + "</g>")
