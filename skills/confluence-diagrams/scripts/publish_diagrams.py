#!/usr/bin/env python3
"""Upload diagram PNGs to a Confluence page and swap mermaid blocks for images.

Usage:
  publish_diagrams.py SITE PAGE_ID DIAGRAM_DIR [--upload-only] [--dry-run]

  SITE          e.g. mycompany  (for mycompany.atlassian.net)
  PAGE_ID       numeric Confluence page id
  DIAGRAM_DIR   directory of NN-name.png files

Auth from $JIRA_EMAIL and $JIRA_API_TOKEN.

Uploads with PUT (create-or-update) so stable filenames version rather than
duplicate. Then replaces each mermaid code macro in the page body with an
<ac:image> plus a collapsed expand holding the original source.

Re-uploading the same filenames needs no body edit; run --upload-only.
"""
import sys, os, re, json, glob, subprocess, base64

def api(site, path):
    return f'https://{site}.atlassian.net/wiki{path}'

def creds():
    e, t = os.environ.get('JIRA_EMAIL'), os.environ.get('JIRA_API_TOKEN')
    if not e or not t:
        sys.exit('Set JIRA_EMAIL and JIRA_API_TOKEN')
    return e, t

def curl(args):
    r = subprocess.run(['curl', '-s'] + args, capture_output=True, text=True)
    return r.stdout

def upload(site, page_id, path):
    e, t = creds()
    out = curl(['-u', f'{e}:{t}', '-X', 'PUT',
                '-H', 'X-Atlassian-Token: nocheck',
                '-F', f'file=@{path}', '-F', 'minorEdit=true',
                '-w', '\n%{http_code}',
                api(site, f'/rest/api/content/{page_id}/child/attachment')])
    return out.strip().split('\n')[-1]

def get_page(site, page_id):
    e, t = creds()
    out = curl(['-u', f'{e}:{t}',
                api(site, f'/api/v2/pages/{page_id}?body-format=storage')])
    return json.loads(out)

def image_macro(name, src, width=900):
    return (
        f'<p><ac:image ac:align="center" ac:width="{width}">'
        f'<ri:attachment ri:filename="{name}.png" /></ac:image></p>'
        f'<ac:structured-macro ac:name="expand" ac:schema-version="1">'
        f'<ac:parameter ac:name="title">Mermaid source</ac:parameter>'
        f'<ac:rich-text-body>'
        f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
        f'<ac:parameter ac:name="language">text</ac:parameter>'
        f'<ac:plain-text-body><![CDATA[{src}]]></ac:plain-text-body>'
        f'</ac:structured-macro></ac:rich-text-body></ac:structured-macro>'
    )

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if len(args) < 3:
        sys.exit(__doc__)
    site, page_id, ddir = args[0], args[1], args[2]

    pngs = sorted(glob.glob(os.path.join(ddir, '*.png')))
    if not pngs:
        sys.exit(f'No PNGs in {ddir}')

    print(f'Uploading {len(pngs)} attachments to page {page_id}')
    for p in pngs:
        code = upload(site, page_id, p)
        mark = 'ok ' if code == '200' else 'ERR'
        print(f'  {mark} {code}  {os.path.basename(p)}')

    if '--upload-only' in flags:
        print('\nUpload only. Existing <ac:image> references pick up new versions.')
        return

    names = [os.path.splitext(os.path.basename(p))[0] for p in pngs]
    page = get_page(site, page_id)
    body = page['body']['storage']['value']

    pattern = re.compile(r'<ac:structured-macro ac:name="code"[^>]*>.*?</ac:structured-macro>', re.S)
    idx = [0]

    def repl(m):
        blk = m.group(0)
        if 'mermaid' not in blk:      # leave graphql/json/bash blocks alone
            return blk
        if idx[0] >= len(names):
            print(f'  WARN more mermaid blocks than images; leaving block {idx[0]+1}')
            idx[0] += 1
            return blk
        name = names[idx[0]]; idx[0] += 1
        src = re.search(r'<!\[CDATA\[(.*?)\]\]>', blk, re.S)
        return image_macro(name, src.group(1) if src else '')

    new = pattern.sub(repl, body)
    print(f'\nReplaced {idx[0]} mermaid blocks; {new.count("<ac:image")} images in body')

    if idx[0] != len(names):
        print(f'  WARN {len(names)} images but {idx[0]} blocks — check ordering')

    if '--dry-run' in flags:
        open('/tmp/new_body.html', 'w').write(new)
        print('Dry run: body written to /tmp/new_body.html, page not updated')
        return

    payload = {
        'id': str(page_id), 'status': 'current', 'title': page['title'],
        'body': {'representation': 'storage', 'value': new},
        'version': {'number': page['version']['number'] + 1,
                    'message': 'Replace mermaid blocks with rendered images'},
    }
    e, t = creds()
    open('/tmp/cd_payload.json', 'w').write(json.dumps(payload))
    out = curl(['-u', f'{e}:{t}', '-X', 'PUT', '-H', 'Content-Type: application/json',
                '-d', '@/tmp/cd_payload.json', '-w', '\n%{http_code}',
                api(site, f'/api/v2/pages/{page_id}')])
    code = out.strip().split('\n')[-1]
    print(f'Page update: HTTP {code} -> version {payload["version"]["number"]}')
    print('\nNow open the page and confirm the images display.')

if __name__ == '__main__':
    main()
