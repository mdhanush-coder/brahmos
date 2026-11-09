#!/usr/bin/env python3
"""Search the EngineX 3D library catalog (assets/catalog.json) by keyword, tag, type and category.

Examples
  python find_asset.py gear metal                     # keyword search, best first
  python find_asset.py --type HDRI studio softbox     # HDRIs
  python find_asset.py --type material --map normal --map orm brushed aluminium
  python find_asset.py --tag automotive --type material carbon
  python find_asset.py --type model --max-tris 200000 drone
  python find_asset.py --json --limit 3 motor         # machine-readable

Use the printed `id` with place_asset("<id>", ...) inside an EngineX blender/script job,
or as `asset` in blender/turntable, product-shot, preview. Paths are inside the Blender pod (/library/...).
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOG = os.path.join(HERE, 'catalog.json') if os.path.exists(os.path.join(HERE, 'catalog.json')) else os.path.join(HERE, '..', 'assets', 'catalog.json')
TYPES = ('model', 'rig', 'material', 'texture', 'HDRI', 'scene')
SYNONYMS = {  # cheap query expansion for common product-viz words
    'couch': ['sofa'], 'sofa': ['couch'], 'engine': ['motor'], 'motor': ['engine'],
    'aluminum': ['aluminium'], 'aluminium': ['aluminum'], 'hdr': ['hdri'], 'studio': ['softbox', 'backlight'],
    'chrome': ['metal', 'mirror'], 'gear': ['cog', 'gearbox'], 'bottle': ['flask'], 'phone': ['smartphone', 'mobile'],
}


def words(s):
    return re.findall(r'[a-z0-9]+', s.lower())


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)['assets']


def score(a, terms):
    name, tags, cat = set(words(a['name'])), set(t.lower() for t in a.get('tags', [])), a.get('category', '').lower()
    s = 0.0
    for t in terms:
        alts = [t] + SYNONYMS.get(t, [])
        if any(x in name for x in alts):
            s += 3
        elif any(x in tags for x in alts):
            s += 2
        elif any(x in cat for x in alts):
            s += 1
        elif any(x in a['name'].lower() or any(x in tg for tg in tags) for x in alts):  # prefix/substring
            s += 0.75
        else:
            return 0.0  # every term must match something
    return s


def search(assets, query='', types=(), tags=(), category=None, maps=(), min_tris=None, max_tris=None, limit=10):
    terms = words(query)
    tl = {t.lower() for t in types}
    out = []
    for a in assets:
        if tl and a['type'].lower() not in tl:
            continue
        if category and category.lower() not in a.get('category', '').lower():
            continue
        atags = {t.lower() for t in a.get('tags', [])}
        if any(t.lower() not in atags for t in tags):
            continue
        tm = a.get('texture_maps') or {}
        if any(m not in tm for m in maps):
            continue
        pc = a.get('polycount')
        if min_tris is not None and (pc is None or pc < min_tris):
            continue
        if max_tris is not None and (pc is None or pc > max_tris):
            continue
        s = score(a, terms) if terms else 1.0
        if s > 0:
            # prefer assets Blender can import directly and that have PBR maps
            s += 0.3 * bool(a.get('blender_file')) + 0.1 * len(tm)
            out.append((s, a))
    out.sort(key=lambda x: (-x[0], x[1]['name']))
    return [a for _, a in out[:limit]]


def fmt(a):
    pc = a.get('polycount')
    bits = [f"[{a['type']}] {a['id']}", f"  name: {a['name']}  | category: {a['category']}  | format: {a['format']}"]
    if pc:
        bits.append(f'  tris: {pc:,}')
    if a.get('texture_maps'):
        bits.append('  maps: ' + ', '.join(sorted(a['texture_maps'])))
    bits.append(f"  path: {a.get('blender_file') or a['path']}")
    if a.get('attribution') or a.get('licence'):
        bits.append(f"  licence: {a.get('licence') or ''} {a.get('attribution') or ''}".rstrip())
    return '\n'.join(bits)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('query', nargs='*', help='keywords (all must match name, tags or category)')
    p.add_argument('--type', action='append', default=[], choices=TYPES, help='repeatable')
    p.add_argument('--tag', action='append', default=[], help='exact tag, repeatable')
    p.add_argument('--category')
    p.add_argument('--map', action='append', default=[], help='required texture map: albedo normal roughness metallic orm ao height ...')
    p.add_argument('--min-tris', type=int)
    p.add_argument('--max-tris', type=int)
    p.add_argument('--limit', type=int, default=10)
    p.add_argument('--json', action='store_true')
    p.add_argument('--catalog', default=DEFAULT_CATALOG)
    a = p.parse_args(argv)
    res = search(load(a.catalog), ' '.join(a.query), a.type, a.tag, a.category, a.map, a.min_tris, a.max_tris, a.limit)
    if a.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        print('\n'.join(fmt(r) for r in res) if res else 'no match - try fewer words, a synonym, or drop --type')
    return 0


def _selfcheck():
    fake = [
        {'id': 'm1', 'name': 'brushed aluminium', 'type': 'material', 'category': 'materials', 'tags': ['metal'], 'texture_maps': {'albedo': 'x', 'normal': 'y'}, 'path': '/p', 'format': 'mdl'},
        {'id': 'm2', 'name': 'oak wood', 'type': 'material', 'category': 'materials', 'tags': ['wood'], 'texture_maps': {}, 'path': '/p', 'format': 'mdl'},
        {'id': 'g1', 'name': 'gearbox', 'type': 'model', 'category': 'industrial-equipment', 'tags': ['gear'], 'polycount': 50000, 'path': '/p', 'format': 'glb'},
    ]
    assert [r['id'] for r in search(fake, 'aluminum')] == ['m1'], 'synonym'
    assert search(fake, 'aluminium', maps=['normal'])[0]['id'] == 'm1'
    assert search(fake, 'oak', maps=['normal']) == [], 'map filter'
    assert search(fake, 'gear', types=['model'], max_tris=60000)[0]['id'] == 'g1'
    assert search(fake, 'gear', max_tris=1000) == [], 'tris filter'
    assert search(fake, 'gear wood') == [], 'all terms must match'
    print('selfcheck ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selfcheck']:
        _selfcheck()
    else:
        sys.exit(main())
