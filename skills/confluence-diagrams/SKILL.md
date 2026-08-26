---
name: confluence-diagrams
description: >
  Use when Mermaid diagrams need to appear as real images on a Confluence Cloud page, or when
  diagrams on a published page show as source text instead of pictures. Trigger on "the diagrams
  aren't rendering in Confluence", "attach these diagrams to the page", "render the mermaid and
  upload it", "images are cut off / clipped", or any request to publish, replace, or re-render
  diagram images on a Confluence page. Also use when uploading any local image file as a
  Confluence attachment, since the MCP tools cannot carry a binary.
---

# Confluence Diagrams

Render Mermaid locally, upload as attachments, reference from the page body. Keep the source.

## The fact that makes this skill necessary

**Confluence Cloud does not render Mermaid.** A fenced ```mermaid block publishes successfully and then displays as source text. The publish returning `<ac:structured-macro ac:name="code">` with `<ac:parameter ac:name="language">mermaid</ac:parameter>` means the block was *accepted*, not *rendered*. Native rendering requires a Marketplace app (Atlassian Labs "Mermaid diagrams viewer" is free).

Two consequences:

- Never claim a diagram renders without looking at the published page.
- If the instance has no Mermaid app, images are the only option, and the source must be preserved separately or the page loses diagram-as-code.

**Before rendering anything, ask whether the app can be installed.** Live rendering keeps the source versioned in the page and needs no image maintenance. This skill is the fallback for when Marketplace apps are unavailable, and the right recommendation is to name both options rather than defaulting to images.

## Prerequisites

- `playwright-cli` (`npm install -g @playwright/cli@latest`)
- `$JIRA_EMAIL` and `$JIRA_API_TOKEN` in the environment. These are Atlassian account credentials and work for Confluence, not only Jira. Verify with a read before uploading:
  ```bash
  curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -w "\nHTTP %{http_code}\n" \
    "https://YOUR-SITE.atlassian.net/wiki/api/v2/pages/PAGE_ID?body-format=storage" -o /tmp/page.json
  ```
- Network access to `cdn.jsdelivr.net`. Behind a corporate proxy this may fail; if it does, vendor `mermaid.min.js` locally.

## Scripts

Two scripts do the mechanical parts. Both are tested against a real nine-diagram document.

```bash
# 1. extract blocks and build the render page
scripts/extract_and_render.py DOC.md [OUTDIR]
#    -> OUTDIR/NN-name.mmd per block, OUTDIR/render.html
#    names come from the nearest preceding heading

# 2. upload and swap the page body
scripts/publish_diagrams.py SITE PAGE_ID DIAGRAM_DIR
scripts/publish_diagrams.py SITE PAGE_ID DIAGRAM_DIR --upload-only   # after a re-render
scripts/publish_diagrams.py SITE PAGE_ID DIAGRAM_DIR --dry-run       # writes /tmp/new_body.html
```

The rendering step in the middle is manual, because it needs judgement: check the SVG count, check the aspect ratios, and restructure any diagram that comes out as a strip. Steps 3 to 5 below are that step.

## Workflow

### 1. Extract the sources

Pull every ```mermaid block into its own `.mmd` file under a `diagrams/` directory beside the document. Name them ordered and descriptive: `01-request-flow.mmd`, `02-container-view.mmd`. The numeric prefix is what keeps images matched to blocks later.

Keep the files. They are the regeneration path when the design changes.

### 2. Build the render page

One HTML file loading Mermaid from CDN, one `<pre class="mermaid">` per diagram.

Four settings are not optional, each for a reason learned the hard way:

```html
<style>
  body { width: max-content; }              /* or wide diagrams clip */
  .wrap { display:inline-block; overflow:visible; }
</style>
<script>
mermaid.initialize({
  startOnLoad: true, theme: 'default', securityLevel: 'loose',
  flowchart: { useMaxWidth: false, htmlLabels: true },
  sequence:  { useMaxWidth: false }
});
</script>
```

**Element ids must not start with a digit.** `#01-foo` is an invalid CSS selector and `screenshot` throws a selector error. Prefix with a letter: `id="d01-foo"`.

### 3. Serve over HTTP

```bash
cd diagrams && python3 -m http.server 8899 &
```

**The `file:` protocol is blocked by playwright-cli.** A `file:///` URL fails with "Access to file: protocol is blocked". Always serve.

### 4. Render and capture

```bash
playwright-cli -s=diagrams open --browser=msedge "http://localhost:8899/render.html"
playwright-cli -s=diagrams resize 3400 2400
sleep 6                                   # Mermaid needs time; check before shooting
playwright-cli -s=diagrams --raw eval "document.querySelectorAll('.mermaid svg').length"
```

Confirm the SVG count matches the diagram count before screenshotting. Then per diagram:

```bash
playwright-cli -s=diagrams screenshot "#d01-request-flow" --filename="01-request-flow.png" --hires
```

**Sessions are headless by default.** If a step needs a human (an SSO login), pass `--headed` or the window is invisible and the user cannot act on a prompt they never see.

**Verify dimensions, not just file existence.** If every PNG comes out the same width, the viewport clipped them:

```bash
python3 -c "
import struct
with open('01-request-flow.png','rb') as f:
    f.read(16); w,h=struct.unpack('>II', f.read(8)); print(w,'x',h)"
```

### 5. Check aspect ratios before uploading

A diagram wider than about 4:1 is unreadable on a Confluence page. Measure every image and fix the layout rather than shipping a strip.

**`direction TB` inside a subgraph will not fix a wide graph.** N sibling nodes feeding one target always spread horizontally in Dagre. The fix is to group siblings into labelled cluster nodes:

```
# 12 nodes -> one target: comes out 10:1, unreadable
a --> target
b --> target
...

# grouped: comes out near square
g1["a<br/>b<br/>c"] --> target
g2["d<br/>e<br/>f"] --> target
```

Some diagrams are legitimately wide. A linear five-node chain at 17:1 reads fine as a banner. Judge by whether a reader can follow it, not by the number.

### 6. Upload as attachments

**Use `PUT`, not `POST`.** `POST` fails when the filename already exists; `PUT` is create-or-update, so stable filenames produce new versions instead of `diagram-v2.png` accumulating.

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -X PUT -H "X-Atlassian-Token: nocheck" \
  -F "file=@01-request-flow.png" -F "minorEdit=true" \
  -w "%{http_code}\n" -o /dev/null \
  "https://YOUR-SITE.atlassian.net/wiki/rest/api/content/PAGE_ID/child/attachment"
```

`X-Atlassian-Token: nocheck` is required. The multipart field must be named `file`. Expect `200`.

The MCP Confluence tools cannot do this step — they do not transport binaries. Page read and write can stay on MCP; the upload has to be REST.

### 7. Replace the blocks in the page body

Read the live storage body, substitute each Mermaid macro with an image plus a collapsed source block, and write it back with an incremented version.

```python
image = (
  f'<p><ac:image ac:align="center" ac:width="900">'
  f'<ri:attachment ri:filename="{name}.png" /></ac:image></p>'
  f'<ac:structured-macro ac:name="expand" ac:schema-version="1">'
  f'<ac:parameter ac:name="title">Mermaid source</ac:parameter>'
  f'<ac:rich-text-body>'
  f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
  f'<ac:parameter ac:name="language">text</ac:parameter>'
  f'<ac:plain-text-body><![CDATA[{src}]]></ac:plain-text-body>'
  f'</ac:structured-macro></ac:rich-text-body></ac:structured-macro>'
)
```

The expand block is what keeps this from being a downgrade. Readers see images; editors see source; the page stays self-contained and the diagram is still code.

**Match only Mermaid macros.** A page has other code blocks — GraphQL, JSON, bash. Filter on the language parameter, or the substitution eats them:

```python
if 'mermaid' not in block:
    return block
```

Then `PUT /wiki/api/v2/pages/{id}` with `representation: "storage"` and `version.number` incremented.

### 8. Verify

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://YOUR-SITE.atlassian.net/wiki/api/v2/pages/PAGE_ID?body-format=storage" \
  | python3 -c "
import json,sys,re
b=json.load(sys.stdin)['body']['storage']['value']
print('images:', len(re.findall(r'ri:filename', b)))
print('mermaid blocks left:', b.count('>mermaid<'))"
```

Then **ask the user to look at the page.** Reference integrity is not the same as visible rendering, and the failure mode this skill exists to prevent is exactly the gap between those two.

### 9. Clean up

```bash
pkill -f "http.server 8899"
playwright-cli -s=diagrams close
```

## Updating a diagram later

Edit the `.mmd`, re-render, re-`PUT` the same filename. No page edit needed — Confluence serves the new attachment version against the existing `<ac:image>` reference. Keep the source in the local markdown in sync, or the expand blocks on the page will describe a diagram that no longer matches the image.

## Failure modes, in the order they usually happen

| Symptom | Cause | Fix |
|---|---|---|
| Diagrams show as code text on the page | Confluence has no Mermaid app | This skill, or install the app |
| `Access to "file:" protocol is blocked` | playwright-cli refuses `file://` | Serve over HTTP |
| Screenshot throws a selector error | Element id starts with a digit | Prefix ids with a letter |
| Every PNG is the same width | Viewport clipped the element | Larger viewport, `width:max-content` |
| SVG count is 0 | Mermaid not loaded, or CDN blocked | Check console; vendor the library |
| Page URL reads `about:blank` | Headless session, navigation failed | Reopen with the URL as the `open` target |
| Login prompt appears to do nothing | Session is headless, window invisible | `--headed` |
| Attachment upload returns 400 | `POST` on an existing filename | Use `PUT` |
| Other code blocks turned into images | Substitution matched every code macro | Filter on the language parameter |
| Diagram is a thin unreadable strip | Sibling nodes spread horizontally | Group into cluster nodes |
