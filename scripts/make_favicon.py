#!/usr/bin/env python3
"""Build the MAR2 monogram favicon: favicon.svg, favicon.ico and apple-touch-icon.png.

The letters are Open Sans outlines, not live text, so the icon looks the same
whether or not the viewer has the font. Needs fontTools, cairosvg and Pillow:
    pip install fonttools cairosvg Pillow
Run from anywhere:  python3 scripts/make_favicon.py [--lines MA,R2] [--out DIR]
"""
import argparse, io, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.expanduser('~/Library/Fonts/OpenSans-Bold.ttf')  # adjust the typeface/weight here

TILE = '#252061'      # adjust the tile colour here (the dashboard's chip navy)
INK = '#FFFFFF'       # adjust the letter colour here
VIEW = 64             # SVG canvas units
PAD = 6               # adjust the margin around the letters here (canvas units)
TRACK = 20            # adjust letter spacing here (font units; Open Sans has 2048/em)
LEADING = 0.30        # adjust the gap between stacked lines here (fraction of cap height)
RADIUS = 0            # corner radius; 0 keeps the dashboard's square chips


def line_path(font, text, x0, y0, s):
    """SVG path for one line, baseline at y0, scaled by s, plus its ink bounds."""
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font['hmtx']
    svg, bounds = SVGPathPen(gs), BoundsPen(gs)
    x = 0
    for ch in text:
        name = cmap[ord(ch)]
        t = (s, 0, 0, -s, x0 + x * s, y0)
        gs[name].draw(TransformPen(svg, t))
        gs[name].draw(TransformPen(bounds, t))
        x += hmtx[name][0] + TRACK
    return svg.getCommands(), bounds.bounds


def build_svg(lines):
    font = TTFont(FONT)
    cap = font['OS/2'].sCapHeight
    # measure each line at scale 1 to size the block
    widths = [line_path(font, l, 0, 0, 1)[1] for l in lines]
    ink_w = max(b[2] - b[0] for b in widths)
    block_h = cap * len(lines) + cap * LEADING * (len(lines) - 1)
    s = min((VIEW - 2 * PAD) / ink_w, (VIEW - 2 * PAD) / block_h)
    top = (VIEW - block_h * s) / 2
    paths = []
    for i, (l, b) in enumerate(zip(lines, widths)):
        w = (b[2] - b[0]) * s
        x0 = (VIEW - w) / 2 - b[0] * s          # centre each line on its ink
        y0 = top + cap * s * (i + 1) + cap * LEADING * s * i
        paths.append(line_path(font, l, x0, y0, s)[0])
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {v} {v}">'
            '<rect width="{v}" height="{v}" rx="{r}" fill="{t}"/>'
            '<path fill="{i}" d="{d}"/></svg>\n').format(
        v=VIEW, r=RADIUS, t=TILE, i=INK, d=' '.join(paths))


def png(svg, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),
                                                  output_width=size, output_height=size)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lines', default='MA,R2', help='comma-separated lines, e.g. MAR2 or MA,R2')
    ap.add_argument('--out', default=ROOT)
    a = ap.parse_args()
    svg = build_svg(a.lines.split(','))
    open(os.path.join(a.out, 'favicon.svg'), 'w').write(svg)
    png(svg, 180).convert('RGB').save(os.path.join(a.out, 'apple-touch-icon.png'))
    # each .ico size is rasterised from the vector, not downscaled from one bitmap
    frames = [png(svg, n) for n in (16, 32, 48)]
    frames[-1].save(os.path.join(a.out, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)],
                    append_images=frames[:-1])
    print('wrote favicon.svg, favicon.ico, apple-touch-icon.png to', a.out)


if __name__ == '__main__':
    main()
