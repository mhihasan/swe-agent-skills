#!/usr/bin/env python3
"""Extract ```mermaid blocks from a markdown file and build a render page.

Usage: extract_and_render.py DOC.md [OUTDIR]
Writes OUTDIR/NN-name.mmd for each block plus OUTDIR/render.html.
Block names come from the nearest preceding heading, slugified.
"""
import sys, os, re, html

def slug(t):
    t = re.sub(r'[`*_#]', '', t).strip().lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return t[:40] or 'diagram'

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    doc = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(doc) or '.', 'diagrams')
    os.makedirs(out, exist_ok=True)
    s = open(doc).read()

    # capture each block with the heading above it, for naming
    blocks, names, pos = [], [], 0
    for m in re.finditer(r'```mermaid\n(.*?)```', s, re.S):
        head = None
        for h in re.finditer(r'^#{2,4}\s+(.+)$', s[:m.start()], re.M):
            head = h.group(1)
        blocks.append(m.group(1).strip())
        names.append(slug(head) if head else f'diagram-{len(blocks)}')

    # de-duplicate names
    seen = {}
    final = []
    for i, n in enumerate(names, 1):
        seen[n] = seen.get(n, 0) + 1
        suffix = f'-{seen[n]}' if seen[n] > 1 else ''
        final.append(f'{i:02d}-{n}{suffix}')

    parts = []
    for name, src in zip(final, blocks):
        open(os.path.join(out, name + '.mmd'), 'w').write(src + '\n')
        parts.append(
            f'<div class="wrap"><div class="name">{name}</div>'
            f'<pre class="mermaid" id="d{name}">{html.escape(src)}</pre></div>'
        )
        print(f'  {name}.mmd  ({src.splitlines()[0]})')

    page = (
        '<!doctype html><html><head><meta charset="utf-8">\n'
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>\n'
        '<style>\n'
        ' body{background:#fff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;'
        'margin:0;padding:24px;width:max-content}\n'
        ' .wrap{margin:0 0 56px 0;padding:20px;background:#fff;display:inline-block;overflow:visible}\n'
        ' .name{font:600 13px monospace;color:#666;margin-bottom:12px}\n'
        ' .mermaid{background:#fff}\n'
        '</style></head><body>\n' + '\n'.join(parts) + '\n'
        '<script>mermaid.initialize({startOnLoad:true,theme:"default",securityLevel:"loose",'
        'flowchart:{useMaxWidth:false,htmlLabels:true,nodeSpacing:40,rankSpacing:70},'
        'sequence:{useMaxWidth:false}});</script>\n</body></html>'
    )
    open(os.path.join(out, 'render.html'), 'w').write(page)
    print(f'\n{len(blocks)} diagrams -> {out}/render.html')
    print(f'Next: cd {out} && python3 -m http.server 8899 &')

if __name__ == '__main__':
    main()
