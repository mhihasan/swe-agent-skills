# Verification

Two loops, both mandatory. The lesson's whole claim is that it was executed.

## Loop 1 — the code

Write the complete system as one module, then a test file exercising every phase, then run it until green. Only then write prose.

**When a test fails, decide which side is wrong before changing either.** A wrong expectation in your own test is the common case. Silently adjusting the implementation to match a bad expectation produces a lesson that teaches a bug.

Observed on a real build: three of the first failures were arithmetic errors in the test — a discount chain computed by hand, and a misuse of the end-of-pages sentinel where `None` meant "start from the beginning" rather than "no more pages". The implementation was right all three times.

**Count with a command.** Never estimate.

```bash
grep -cE '^class [A-Za-z_]+' catalog.py          # classes
grep -cE '^check\(|^raises\(' test_catalog.py    # assertions
```

A first draft claimed thirty-one classes. The real count was fifty. A number a reader can check is the point; a wrong one destroys the warrant.

## Loop 2 — the rendering

Serve the page and drive a real browser. `file://` is blocked, so use a local server.

```bash
cd "$SCRATCH" && (python3 -m http.server 8731 >/dev/null 2>&1 &)
playwright-cli open "http://localhost:8731/preview-light.html"
playwright-cli resize 1280 900
```

Wrap the artifact body in a minimal skeleton for preview, and make a second copy with `data-theme="dark"` on the root to check the other theme.

### Detect clipping programmatically

Do not eyeball a dozen diagrams. Measure each SVG's content against its declared viewBox.

**`getBBox()` on child elements ignores ancestor `transform`.** Class boxes emitted inside a translated `<g>` go uncounted, and every diagram reports clean while several are visibly cut. Measure from the SVG **root**, whose `getBBox()` does account for child transforms.

```js
JSON.stringify([...document.querySelectorAll('figure svg, .notationbox svg')].map(s => {
  const vb = s.getAttribute('viewBox').split(' ').map(Number);
  const b = s.getBBox();                       // root: transforms included
  return {l: (s.getAttribute('aria-label')||'').slice(0,30), w: vb[2], h: vb[3],
          mx: Math.round(b.x+b.width), my: Math.round(b.y+b.height)};
}))
```

Anything where `mx > w` or `my > h` is clipped. On a real build this caught six diagrams: three with class boxes past the bottom edge, three with footnote text past the right. Long footnotes overflow constantly — split them across two lines rather than widening the viewBox, so all diagrams keep one scale.

### Check the page as a whole

```js
JSON.stringify({
  svgWidth: Math.round(document.querySelector('figure svg').getBoundingClientRect().width),
  bodyOverflow: document.documentElement.scrollWidth > window.innerWidth,
  proseWidth: Math.round(document.querySelector('.prose').getBoundingClientRect().width)
})
```

Diagrams should render at or above their viewBox width — below it means text is shrinking. Prose should land near 60–70 characters. `bodyOverflow` must be false, at desktop and at roughly 960px.

### Then look

Screenshot the diagrams that changed and read them. Measurement catches clipping; only looking catches an edge routed through a node, a label struck through by a line, or an arrowhead pointing at empty space.

## Cleanup

Kill the server, close the browser, and delete stray screenshots — `playwright-cli` writes into `.playwright-cli` relative to the working directory, so run it from a scratch directory or the files land in the repo.
