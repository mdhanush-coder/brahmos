#!/usr/bin/env python3
"""Lint an annotated explainer script and export what the pipeline needs.

  python script_lint.py 03_script.md --minutes 6 [--out chapters]
Errors (must be 0): word count outside +-7 % of minutes x 146, digits in spoken text, forbidden brackets/emotion tags,
dashes, sentences > 28 words, lines > 240 characters, a {Part} used with a different spelling later, acronym used
before being defined with ", or ABC".
Warnings: no "?" in 220 words, hook first sentence > 25 words, chapter without an everyday comparison.
Exports per chapter NN: NN.speak.txt (Emotive Speech text, neutral brief per paragraph), NN.terms.json (beat sheet),
and shotlist.json.
"""
import argparse, json, os, re, sys

WPM = 146
BRIEF = '[a documentary narrator explaining to a friend, warm and clear, steady pace]'   # user-approved 2026-11-07
ALLOWED_SILENCE = {'[pause]', '[long pause]'}
COMPARE = re.compile(r"\b(like|imagine|think of|similar to|just as|kind of like)\b", re.I)


def parse(text):
    chapters, cur = [], None
    for raw in text.splitlines():
        line = re.sub(r'<!--.*?-->', '', raw).rstrip()
        if not line.strip() or line.startswith('# '):
            continue
        m = re.match(r'##\s*(\d+)\.\s*(.*?)\s*(?:\|\|\s*(.*))?$', line)
        if m:
            cur = {'n': int(m.group(1)), 'title': m.group(2), 'meta': _meta(m.group(3) or ''), 'lines': []}
            chapters.append(cur)
            continue
        if cur is None:
            continue
        speech, _, vis = line.partition('||')
        cur['lines'].append({'speech': speech.strip(), 'vis': _meta(vis)})
    return chapters


def _meta(s):
    out = {}
    for part in re.split(r'[;|]+', s):
        if '=' in part:
            k, v = part.split('=', 1)
            out[k.strip()] = v.strip()
    return out


def spoken(s):
    return s.replace('{', '').replace('}', '')


def lint(chapters, minutes=None):
    errors, warns, parts = [], [], {}
    all_words = 0
    since_q = 0
    defined_acr = set()
    for ch in chapters:
        has_cmp = False
        for i, ln in enumerate(ch['lines']):
            s = ln['speech']
            where = f"ch{ch['n']} line {i + 1}"
            if s in ALLOWED_SILENCE:
                continue
            for b in re.findall(r'\[[^\]]*\]', s):
                errors.append(f'{where}: bracket {b} not allowed (no emotion/tone tags; [pause] lines only)')
            if re.search(r'[<>]', s):
                errors.append(f'{where}: angle-bracket tags not allowed')
            if re.search(r'\d', s):
                errors.append(f'{where}: digits in spoken text, write numbers as words (put digits in || number=)')
            if re.search(r'\s[-–—]\s|—|–', s):
                errors.append(f'{where}: dash, use a comma')
            sp = spoken(s)
            if len(sp) > 240:
                errors.append(f'{where}: line {len(sp)} chars > 240 (split into two lines at the thought break)')
            for sent in re.split(r'(?<=[.?!])\s+', sp):
                n = len(sent.split())
                if n > 28:
                    errors.append(f'{where}: sentence of {n} words > 28: "{sent[:60]}..."')
            for p in re.findall(r'\{([^}]+)\}', s):
                key = p.lower()
                if key in parts and parts[key] != p:
                    errors.append(f'{where}: part spelled "{p}", first was "{parts[key]}"')
                parts.setdefault(key, p)
            for acr in re.findall(r'\b[A-Z]{2,}\b', sp):
                if acr not in defined_acr:
                    if re.search(r',\s*or\s+' + acr + r'\b', sp):
                        defined_acr.add(acr)
                    else:
                        errors.append(f'{where}: acronym {acr} used before ", or {acr}" definition')
                        defined_acr.add(acr)
            w = len(sp.split())
            all_words += w
            since_q = 0 if '?' in sp else since_q + w
            if since_q > 220:
                warns.append(f'{where}: 220+ words without a question (add a curiosity hook)')
                since_q = 0
            has_cmp = has_cmp or bool(COMPARE.search(sp))
            if ch is chapters[0] and i == 0 and len(re.split(r'(?<=[.?!])\s+', sp)[0].split()) > 25:
                warns.append('hook: first sentence > 25 words; open sharper')
        if not has_cmp and ch['meta'].get('shot') not in ('room', 'explode'):
            warns.append(f"ch{ch['n']}: no everyday comparison (like / imagine / think of)")
    if minutes:
        target = minutes * WPM
        if abs(all_words - target) > 0.07 * target:
            errors.append(f'word count {all_words} vs target {round(target)} (+-7 %)')
    return errors, warns, parts, all_words


def export(chapters, parts, out):
    os.makedirs(out, exist_ok=True)
    shots = []
    for ch in chapters:
        lines, terms = [BRIEF + ' '], {}
        first = True
        for ln in ch['lines']:
            s = ln['speech']
            if s in ALLOWED_SILENCE:
                lines.append(s)
                continue
            txt = spoken(s)
            if first:
                lines[0] += txt
                first = False
            else:
                lines.append(txt)
            named = re.findall(r'\{([^}]+)\}', s)
            vis = ln['vis']
            for j, p in enumerate(named):
                meta = {'part': re.sub(r'[^a-z0-9]+', '_', p.lower()).strip('_'), 'shot': vis.get('shot', ch['meta'].get('shot', 'focus'))}
                if j == len(named) - 1:   # the chip belongs to the part the sentence is about: the last one named
                    meta.update({k: vis[k] for k in ('chip', 'number', 'note') if k in vis})
                pre = re.findall(r"[A-Za-z']+", s.split('{' + p + '}')[0].replace('{', '').replace('}', ''))
                if pre:   # earlier casual mentions must not move the camera: only count the term from its first braced use
                    meta['after'] = ' '.join(pre[-2:]).lower()
                terms.setdefault(p.lower(), meta)
            if not named and ('chip' in vis or 'number' in vis):
                key = ' '.join(txt.split()[:2]).lower().strip('.,?')
                terms.setdefault(key, {k: vis[k] for k in ('chip', 'number', 'note') if k in vis})
        nn = f"{ch['n']:02d}"
        open(os.path.join(out, f'{nn}.speak.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
        json.dump(terms, open(os.path.join(out, f'{nn}.terms.json'), 'w', encoding='utf-8'), indent=1)
        shots.append({'chapter': ch['n'], 'title': ch['title'], 'shot': ch['meta'].get('shot', 'focus'),
                      'parts': sorted({t['part'] for t in terms.values() if 'part' in t})})
    json.dump({'chapters': shots, 'parts': sorted(parts.values())}, open(os.path.join(out, 'shotlist.json'), 'w'), indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('script'), ap.add_argument('--minutes', type=float), ap.add_argument('--out')
    a = ap.parse_args(argv)
    chapters = parse(open(a.script, encoding='utf-8').read())
    errors, warns, parts, words = lint(chapters, a.minutes)
    for e in errors:
        print('ERROR', e)
    for w in warns:
        print('warn ', w)
    print(f'{len(chapters)} chapters, {words} words (~{words / WPM:.1f} min), {len(parts)} parts, '
          f'{len(errors)} errors, {len(warns)} warnings')
    if not errors:
        export(chapters, parts, a.out or os.path.join(os.path.dirname(os.path.abspath(a.script)), 'chapters'))
    return 1 if errors else 0


def _selfcheck():
    good = ("# T\n## 1. Hook || shot=room\nYour watch hides a tiny fork. It vibrates thirty-two thousand times a second. || number=32,768 Hz\n"
            "So how does a fork keep time?\n[pause]\n## 2. Crystal || shot=focus\n"
            "The {Crystal Oscillator} is like a tiny tuning fork. || chip=CRYSTAL OSCILLATOR\n"
            "A voltage-controlled oscillator, or VCO, follows it. The {Crystal Oscillator} sets the pace.\n")
    ch = parse(good)
    e, w, parts, n = lint(ch)
    assert not e, e
    assert list(parts) == ['crystal oscillator']
    bad = "# T\n## 1. Hook\n[excited] It has 3 parts — VCO and {Gear}.\nThe {gear} turns.\n"
    e, _, _, _ = lint(parse(bad))
    kinds = ' '.join(e)
    assert 'bracket' in kinds and 'digits' in kinds and 'dash' in kinds and 'acronym' in kinds and 'spelled' in kinds, e
    import tempfile
    d = tempfile.mkdtemp()
    export(ch, parts, d)
    sp = open(os.path.join(d, '01.speak.txt'), encoding='utf-8').read()
    assert sp.startswith(BRIEF) and '[pause]' in sp and '||' not in sp and '{' not in sp
    t = json.load(open(os.path.join(d, '02.terms.json')))
    assert t['crystal oscillator']['part'] == 'crystal_oscillator' and t['crystal oscillator']['chip'] == 'CRYSTAL OSCILLATOR'
    print('selfcheck ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selfcheck']:
        _selfcheck()
    else:
        sys.exit(main())
