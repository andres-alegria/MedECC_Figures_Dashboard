#!/usr/bin/env python3
"""Rebuild figures-data.js and thumbnails from the files in figures/.

Run automatically by GitHub Actions on every push that touches figures/,
or manually:  python3 scripts/update_figures.py

- Scans figures/ for files named  Ch_<chapter>_Figure_<id>_v<version>.(png|jpg|jpeg)
  (<chapter> is 1-7 or SPM; <id> is a number with optional letter, e.g. 3 or 4a,
  or a text name starting with a letter, e.g. CRD, for figures not yet numbered)
- Merges them into figures-data.js, PRESERVING existing titles, captions,
  notes and contacts. New figures get empty metadata you can fill in by
  editing figures-data.js.
- Generates a small JPEG thumbnail in thumbs/ for any figure file that
  doesn't have one yet (needs Pillow: pip install Pillow).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, 'figures')
THUMB_DIR = os.path.join(ROOT, 'thumbs')
DATA_JS = os.path.join(ROOT, 'figures-data.js')
PATTERN = re.compile(
    r'^Ch_(\d+|SPM)_Figure_(?:(\d+)([a-z]?)|([A-Za-z][A-Za-z0-9-]*))_v(\d+)\.(png|jpe?g)$', re.I)

def chapter_key(ch):
    return ch if ch == 'SPM' else int(ch)

def load_existing():
    if not os.path.exists(DATA_JS):
        return []
    src = open(DATA_JS, encoding='utf-8').read()
    start, end = src.index('['), src.rindex(']') + 1
    return json.loads(src[start:end])

def main():
    records = {r['id']: r for r in load_existing()}
    found = {}
    for name in sorted(os.listdir(FIG_DIR)):
        m = PATTERN.match(name)
        if not m:
            continue
        ch, ver = chapter_key(m.group(1)), int(m.group(5))
        if m.group(2):
            num, var = int(m.group(2)), m.group(3).lower()
        else:
            num, var = m.group(4), ''   # named figure, e.g. CRD
        fid = 'ch{}-fig{}{}'.format(ch, str(num).lower(), var)
        found.setdefault(fid, {'ch': ch, 'num': num, 'var': var, 'versions': []})
        found[fid]['versions'].append({'v': ver, 'file': 'figures/' + name})

    for fid, info in found.items():
        versions = sorted(info['versions'], key=lambda v: v['v'])
        if fid in records:
            records[fid]['versions'] = versions
        else:
            records[fid] = {
                'id': fid, 'chapter': info['ch'], 'figure': info['num'], 'variant': info['var'],
                'label': 'Fig. {}.{}{}'.format(info['ch'], info['num'], info['var']),
                'title': '', 'caption': '', 'notes': '', 'contact': '', 'date': '',
                'versions': versions,
            }

    # numbered figures first, then named figures alphabetically
    ordered = sorted(records.values(), key=lambda r: (
        (8, 0) if r['chapter'] == 'SPM' else (0, r['chapter']),
        (0, r['figure'], '') if isinstance(r['figure'], int) else (1, 0, str(r['figure']).lower()),
        r['variant']))
    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write('window.MEDECC_FIGURES = ' + json.dumps(ordered, indent=1, ensure_ascii=False) + ';\n')
    print('figures-data.js: {} figures'.format(len(ordered)))

    # --- thumbnails ---
    try:
        from PIL import Image
    except ImportError:
        print('Pillow not installed - skipping thumbnails (pip install Pillow)')
        return
    os.makedirs(THUMB_DIR, exist_ok=True)
    made = 0
    for rec in ordered:
        for v in rec['versions']:
            src = os.path.join(ROOT, v['file'])
            base = os.path.splitext(os.path.basename(v['file']))[0]
            dst = os.path.join(THUMB_DIR, base + '.jpg')
            if os.path.exists(dst) or not os.path.exists(src):
                continue
            img = Image.open(src).convert('RGB')
            img.thumbnail((560, 560))
            img.save(dst, 'JPEG', quality=72)
            made += 1
    print('thumbnails generated: {}'.format(made))

if __name__ == '__main__':
    sys.exit(main())
