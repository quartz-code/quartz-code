"""Text -> SVG path outlines (HarfBuzz shaping + fontTools outlines)."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen


def _num(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Font:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        self.upm = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def layout(self, text, size, x=0.0, y=0.0, tracking=0.0, anchor="start"):
        """Return (glyphs, width). glyphs = list of (char, path_d, (xmin, ymin, xmax, ymax))."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        k = size / self.upm
        advances = [p.x_advance * k for p in buf.glyph_positions]
        width = sum(advances) + tracking * (len(advances) - 1)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        out, pen_x = [], x
        for info, pos, adv in zip(buf.glyph_infos, buf.glyph_positions, advances):
            name = self.order[info.codepoint]
            t = (k, 0, 0, -k, pen_x + pos.x_offset * k, y - pos.y_offset * k)
            sp = SVGPathPen(self.glyphset, ntos=_num)
            self.glyphset[name].draw(TransformPen(sp, t))
            bp = BoundsPen(self.glyphset)
            self.glyphset[name].draw(TransformPen(bp, t))
            ch = text[info.cluster] if info.cluster < len(text) else ""
            out.append((ch, sp.getCommands(), bp.bounds))
            pen_x += adv + tracking
        return out, width
