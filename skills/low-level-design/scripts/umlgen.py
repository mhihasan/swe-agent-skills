"""UML-notation SVG fragments that theme via CSS custom properties.

Every shape draws with var(--token) fills and strokes, so one diagram renders
correctly in a light page and a dark one without a second copy. Import into a
build script, lay out coordinates by hand, and write the result to .svg.

Covers: box (three-compartment classifier), link (six relationship types with
multiplicities), note, actor, ellipse, state, action, diamond, flow, package,
simple_class. See references/uml-toolkit.md for which to reach for.
"""

CW = 6.62          # JetBrains Mono advance width at 11px
LH = 15            # compartment line height
PAD = 8
HEAD = 22          # name compartment height (no stereotype)
HEAD_ST = 34       # name compartment height (with stereotype)

DEFS = """<defs>
<marker id="gen" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto">
  <path d="M 0 0 L 11 6 L 0 12 z" fill="var(--surface)" stroke="var(--ink-2)" stroke-width="1"/></marker>
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto">
  <path d="M 0 0 L 10 5 L 0 10" fill="none" stroke="var(--ink-2)" stroke-width="1.3"/></marker>
<marker id="comp" viewBox="0 0 14 10" refX="1" refY="5" markerWidth="14" markerHeight="10" orient="auto">
  <path d="M 0 5 L 7 0 L 14 5 L 7 10 z" fill="var(--ink-2)" stroke="var(--ink-2)" stroke-width="1"/></marker>
<marker id="agg" viewBox="0 0 14 10" refX="1" refY="5" markerWidth="14" markerHeight="10" orient="auto">
  <path d="M 0 5 L 7 0 L 14 5 L 7 10 z" fill="var(--surface)" stroke="var(--ink-2)" stroke-width="1"/></marker>
</defs>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, name, attrs=(), ops=(), stereotype=None, abstract=False, accent=None, minw=0):
    """A three-compartment UML classifier. Returns (svg, width, height)."""
    lines = list(attrs) + list(ops)
    widest = max([len(name) + (4 if abstract else 0)]
                 + [len(stereotype) + 4 if stereotype else 0]
                 + [len(l) for l in lines] + [0])
    w = max(minw, int(widest * CW) + PAD * 2 + 10)
    head = HEAD_ST if stereotype else HEAD
    h = head + (LH * len(attrs) + PAD if attrs else 0) + (LH * len(ops) + PAD if ops else 0)
    stroke = accent or "var(--line-strong)"
    p = [f'<g transform="translate({x},{y})">']
    p.append(f'<rect width="{w}" height="{h}" fill="var(--surface)" stroke="{stroke}" stroke-width="1.1"/>')
    cy = 0
    if stereotype:
        p.append(f'<text x="{w/2}" y="14" text-anchor="middle" font-size="10" '
                 f'fill="var(--ink-3)">«{esc(stereotype)}»</text>')
        p.append(f'<text x="{w/2}" y="28" text-anchor="middle" font-size="11.5" font-weight="700" '
                 f'font-style="{"italic" if abstract else "normal"}" fill="var(--ink)">{esc(name)}</text>')
    else:
        p.append(f'<text x="{w/2}" y="15" text-anchor="middle" font-size="11.5" font-weight="700" '
                 f'font-style="{"italic" if abstract else "normal"}" fill="var(--ink)">{esc(name)}</text>')
    cy = head
    for group in (attrs, ops):
        if not group:
            continue
        p.append(f'<line x1="0" y1="{cy}" x2="{w}" y2="{cy}" stroke="{stroke}" stroke-width="1"/>')
        ty = cy + 12
        for line in group:
            p.append(f'<text x="{PAD}" y="{ty}" font-size="11" fill="var(--ink-2)">{esc(line)}</text>')
            ty += LH
        cy += LH * len(group) + PAD
    p.append("</g>")
    return "\n".join(p), w, h


def link(x1, y1, x2, y2, kind="assoc", label=None, m1=None, m2=None, dash=None, mid=None):
    """kind: assoc | gen | realize | dep | comp | agg"""
    style = {
        "assoc":   ('var(--ink-2)', None, 'url(#arrow)', None),
        "gen":     ('var(--ink-2)', None, 'url(#gen)', None),
        "realize": ('var(--ink-2)', '5 4', 'url(#gen)', None),
        "dep":     ('var(--ink-2)', '4 3', 'url(#arrow)', None),
        "comp":    ('var(--ink-2)', None, None, 'url(#comp)'),
        "agg":     ('var(--ink-2)', None, None, 'url(#agg)'),
    }[kind]
    col, d, end, start = style
    if dash:
        d = dash
    a = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.2"']
    if d:
        a.append(f' stroke-dasharray="{d}"')
    if end:
        a.append(f' marker-end="{end}"')
    if start:
        a.append(f' marker-start="{start}"')
    a.append("/>")
    out = ["".join(a)]
    if m1:
        out.append(_mult(x1, y1, x2, y2, m1, True))
    if m2:
        out.append(_mult(x2, y2, x1, y1, m2, True))
    if label or mid:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        txt = label or mid
        out.append(f'<rect x="{mx - len(txt)*3.2 - 3}" y="{my - 8}" width="{len(txt)*6.4 + 6}" height="14" '
                   f'fill="var(--surface)"/>')
        out.append(f'<text x="{mx}" y="{my + 3}" text-anchor="middle" font-size="10" '
                   f'fill="var(--ink-3)">{esc(txt)}</text>')
    return "\n".join(out)


def _mult(x, y, tx, ty, text, near):
    dx, dy = (1 if tx > x else -1 if tx < x else 0), (1 if ty > y else -1 if ty < y else 0)
    ox = 12 * dx + (0 if dx else 0)
    oy = 14 * dy - 4
    anchor = "start" if dx > 0 else "end" if dx < 0 else "middle"
    return (f'<text x="{x + ox}" y="{y + oy}" text-anchor="{anchor}" font-size="10" '
            f'fill="var(--ink-3)">{esc(text)}</text>')


def note(x, y, w, text_lines):
    h = 12 + LH * len(text_lines)
    p = [f'<g transform="translate({x},{y})">',
         f'<path d="M 0 0 L {w-12} 0 L {w} 12 L {w} {h} L 0 {h} Z" fill="var(--warn-soft)" '
         f'stroke="var(--warn)" stroke-width="1"/>',
         f'<path d="M {w-12} 0 L {w-12} 12 L {w} 12" fill="none" stroke="var(--warn)" stroke-width="1"/>']
    ty = 18
    for l in text_lines:
        p.append(f'<text x="8" y="{ty}" font-size="10.5" fill="var(--ink-2)">{esc(l)}</text>')
        ty += LH
    p.append("</g>")
    return "\n".join(p), h


def actor(x, y, name):
    """UML stick-figure actor, feet at y+46, label below."""
    return f'''<g transform="translate({x},{y})">
<circle cx="0" cy="7" r="7" fill="var(--surface)" stroke="var(--ink-2)" stroke-width="1.3"/>
<line x1="0" y1="14" x2="0" y2="32" stroke="var(--ink-2)" stroke-width="1.3"/>
<line x1="-11" y1="21" x2="11" y2="21" stroke="var(--ink-2)" stroke-width="1.3"/>
<line x1="0" y1="32" x2="-9" y2="46" stroke="var(--ink-2)" stroke-width="1.3"/>
<line x1="0" y1="32" x2="9" y2="46" stroke="var(--ink-2)" stroke-width="1.3"/>
<text x="0" y="60" text-anchor="middle" font-size="10.5" font-weight="700" fill="var(--ink)">{esc(name)}</text>
</g>'''


def ellipse(cx, cy, text, rx=None):
    rx = rx or max(58, len(text) * 3.5 + 14)
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="19" fill="var(--surface)" '
            f'stroke="var(--line-strong)" stroke-width="1.1"/>'
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="10.5" fill="var(--ink)">{esc(text)}</text>')


def state(x, y, name, w=None, kind="normal"):
    w = w or max(84, len(name) * CW + 22)
    if kind == "initial":
        return f'<circle cx="{x}" cy="{y}" r="7" fill="var(--ink)"/>', 14, 14
    if kind == "final":
        return (f'<circle cx="{x}" cy="{y}" r="9" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.3"/>'
                f'<circle cx="{x}" cy="{y}" r="5" fill="var(--ink)"/>'), 18, 18
    svg = (f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="9" fill="var(--surface)" '
           f'stroke="var(--line-strong)" stroke-width="1.1"/>'
           f'<text x="{x + w/2}" y="{y+19}" text-anchor="middle" font-size="11" font-weight="600" '
           f'fill="var(--ink)">{esc(name)}</text>')
    return svg, w, 30


def svg_open(vw, vh, label):
    return (f'<svg viewBox="0 0 {vw} {vh}" role="img" aria-label="{esc(label)}" '
            f'font-family="JetBrains Mono, ui-monospace, monospace">{DEFS}')


SVG_CLOSE = "</svg>"


# ------------------------------------------------------- activity / state nodes

def action(x, y, w, text, h=34, accent="var(--line-strong)"):
    """Rounded action node for activity diagrams."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="var(--surface)" '
            f'stroke="{accent}" stroke-width="1.1"/>'
            f'<text x="{x+w/2}" y="{y+h/2+4}" text-anchor="middle" font-size="11" '
            f'fill="var(--ink)">{esc(text)}</text>')


def diamond(cx, cy, text, rx=54, ry=30):
    """Decision or merge node. Pass text="" with a small rx/ry for a merge."""
    d = (f'<path d="M {cx} {cy-ry} L {cx+rx} {cy} L {cx} {cy+ry} L {cx-rx} {cy} Z" '
         f'fill="var(--surface)" stroke="var(--accent)" stroke-width="1.2"/>')
    if text:
        d += f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="10" fill="var(--ink)">{esc(text)}</text>'
    return d


def flow(pts, guard=None, gx=None, gy=None):
    """Orthogonal control-flow edge through a list of (x, y) points.

    Route around nodes rather than through them: give every loop-back its own
    clear corridor. Guards render as [yes] / [no] on an opaque patch.
    """
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
    out = [f'<path d="{d}" fill="none" stroke="var(--ink-2)" stroke-width="1.2" marker-end="url(#arrow)"/>']
    if guard:
        out.append(f'<rect x="{gx-len(guard)*3.3-4}" y="{gy-11}" width="{len(guard)*6.6+8}" '
                   f'height="15" fill="var(--surface)"/>')
        out.append(f'<text x="{gx}" y="{gy}" text-anchor="middle" font-size="10" font-weight="700" '
                   f'fill="var(--accent)">{esc(guard)}</text>')
    return "\n".join(out)


# ------------------------------------------------------------------- packages

def package(x, y, w, h, name, colour):
    """UML package: tabbed folder shape, for the finished-model diagram."""
    tw = max(96, len(name) * CW + 22)
    return (f'<path d="M {x} {y+16} L {x} {y} L {x+tw} {y} L {x+tw} {y+16} L {x+w} {y+16} '
            f'L {x+w} {y+h} L {x} {y+h} Z" fill="var(--surface-2)" stroke="{colour}" stroke-width="1.3"/>'
            f'<text x="{x+10}" y="{y+12}" font-size="10" font-weight="700" letter-spacing="1.2" '
            f'fill="{colour}">{esc(name)}</text>')


def simple_class(x, y, name, w=126, kind=None, colour="var(--line-strong)"):
    """Name-only class box for the finished model, where compartments would not fit."""
    h = 26 if not kind else 34
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="var(--surface)" '
           f'stroke="{colour}" stroke-width="1.1"/>']
    if kind:
        out.append(f'<text x="{x+w/2}" y="{y+13}" text-anchor="middle" font-size="9" '
                   f'fill="var(--ink-3)">«{esc(kind)}»</text>')
        out.append(f'<text x="{x+w/2}" y="{y+27}" text-anchor="middle" font-size="10.5" '
                   f'font-weight="700" fill="var(--ink)">{esc(name)}</text>')
    else:
        out.append(f'<text x="{x+w/2}" y="{y+17}" text-anchor="middle" font-size="10.5" '
                   f'font-weight="700" fill="var(--ink)">{esc(name)}</text>')
    return "\n".join(out), w, h


def text(x, y, s, size=10.5, anchor="start", fill="var(--ink-3)", weight="400"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')
