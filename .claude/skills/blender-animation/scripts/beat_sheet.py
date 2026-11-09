#!/usr/bin/env python3
"""Narration -> beat sheet: when the camera must move to each named part (Branch-style sync, measured lead 0.6 s).

  python beat_sheet.py transcript.json terms.json beats.json [--fps 30] [--lead 0.6] [--min-hold 2.5]
transcript.json: EngineX transcribe output (segments[].words[] with start/end/word).
terms.json: {"driver gear": {"part": "driver_gear", "shot": "macro", "chip": "DRIVER GEAR"}, "32,768": {"number": "32,768"}, ...}
  keys are spoken phrases (lower case, matched on word starts, first occurrence after the previous beat).
beats.json: {"fps":..,"beats":[{"term","part","word_t","move_f","settle_f","end_f","shot","chip","number"}]}
  move_f = (word_t - lead)*fps - transition  (camera starts),  settle_f = (word_t - lead)*fps (camera arrived),
  end_f = next beat's move_f. Beats shorter than min_hold are merged into the previous one (nothing flashes).
"""
import argparse, json, re, sys


def norm(w):
    return re.sub(r"[^a-z0-9\-,.]", '', w.lower()).strip('.,')


def _same(tok, want):
    """Whole word (plural allowed). Prefix matching made 'cap' fire on 'capillary' (pen test, failure #21)."""
    return tok == want or tok in (want + 's', want + 'es')


def _anchor_index(toks, anchor):
    pw = [norm(p) for p in anchor.split()]
    for i in range(len(toks) - len(pw) + 1):
        if all(_same(toks[i + j], pw[j]) for j in range(len(pw))):
            return i + len(pw)       # first token AFTER the anchor phrase
    return 0


def find_beats(words, terms):
    """terms[phrase] may carry 'after': words that precede the term where it is first named ({Part} brace), so earlier
    casual mentions ('a metal ball' in the hook) do not move the camera."""
    toks = [norm(w['word']) for w in words]
    hits, pos = [], 0
    floor = {ph: (_anchor_index(toks, m['after']) if m.get('after') else 0) for ph, m in terms.items()}
    for _ in range(len(terms) * 4):
        best = None
        for phrase, meta in terms.items():
            pw = [norm(p) for p in phrase.split()]
            for i in range(max(pos, floor[phrase]), len(toks) - len(pw) + 1):
                if all(_same(toks[i + j], pw[j]) for j in range(len(pw))):
                    if best is None or i < best[0]:
                        best = (i, phrase, meta)
                    break
        if best is None:
            break
        i, phrase, meta = best
        hits.append({'term': phrase, 'word_t': round(words[i]['start'], 3), **{k: v for k, v in meta.items() if k != 'after'}})
        pos = i + 1
    return hits


def sentence_marks(words, gap=0.5):
    """Sentence starts (after . ? ! or a pause > gap) and sentence ends, in seconds."""
    starts, ends = [words[0]['start']] if words else [], []
    punct = any(w['word'].rstrip().endswith(('.', '?', '!')) for w in words)   # aligned words carry sentence punctuation
    for a, b in zip(words, words[1:]):                                          # (not commas): a comma pause is not a sentence
        if a['word'].rstrip().endswith(('.', '?', '!')) or (not punct and b['start'] - a['end'] > gap):
            starts.append(b['start'])
            ends.append(a['end'])
    if words:
        ends.append(words[-1]['end'])
    return starts, ends


def schedule(hits, fps=30, lead=0.6, min_hold=2.5, transition=0.8, end_t=None, words=None, snap=False,
             dwell=0.4, snap_window=1.5, min_transition=0.45, chip_repeat_s=15.0):
    """snap: settle on the sentence start when it is within snap_window before the word (Branch cuts on sentences).
    dwell: the camera may not leave a part before the end of the sentence that names it + dwell (viewer gets it).
    When the next part is named in the very next sentence the move is shortened (down to min_transition) and may start
    at the sentence end instead of end + dwell; if even that does not fit, the snap is dropped, then the hit is merged.
    Merged hits keep their own chip/number as 'overlays' (they still appear on their word).
    Returns (beats, overlays)."""
    starts, ends = sentence_marks(words) if words else ([], [])
    beats, overlays = [], []
    for h in hits:
        word_s = max(0.0, h['word_t'] - lead)
        settle = word_s
        if snap and starts:
            s = max((x for x in starts if x <= h['word_t'] + 1e-6), default=None)
            if s is not None and h['word_t'] - s <= snap_window:
                settle = max(0.0, min(word_s, s))
        s_end = min((e for e in ends if e >= h['word_t']), default=h['word_t'])
        h['_dwell'], h['_end'] = s_end + dwell, s_end
        trans, merge = transition, False
        if beats and h.get('part') and h['part'] == beats[-1].get('part'):
            beats[-1]['_dwell'] = max(beats[-1]['_dwell'], h['_dwell'])   # same part named again: stay, extend the hold
            beats[-1]['_end'] = max(beats[-1]['_end'], h['_end'])
            if h.get('chip') or h.get('number'):
                overlays.append({'term': h['term'], 'word_t': h['word_t'], 'chip': h.get('chip'), 'number': h.get('number')})
            continue
        if beats:
            pv = beats[-1]
            for cand in dict.fromkeys([settle, word_s]):          # snapped settle first, then the plain lead
                trans, merge = transition, False
                if cand - pv['_settle'] < min_hold:
                    merge = True
                    continue
                if cand - transition < pv['_dwell']:
                    trans = cand - pv['_dwell']                   # shorten the move...
                    if trans < min_transition:
                        trans = cand - pv['_end']                 # ...or leave right after the sentence ends
                    if trans < min_transition:
                        merge = True
                        continue
                    trans = min(trans, transition)
                settle = cand
                break
        if merge:
            pv = beats[-1]
            pv.setdefault('also', []).append(h['term'])
            if h.get('chip') or h.get('number'):
                overlays.append({'term': h['term'], 'word_t': h['word_t'], 'chip': h.get('chip'), 'number': h.get('number')})
            continue
        beats.append({**h, '_settle': settle, '_trans': trans})
    for i, b in enumerate(beats):
        b['settle_f'] = int(round(b['_settle'] * fps)) + 1
        b['move_f'] = max(1, b['settle_f'] - int(round(b['_trans'] * fps)))
        nxt = beats[i + 1]['_settle'] if i + 1 < len(beats) else (end_t or b['_settle'] + min_hold)
        b['end_f'] = int(round(nxt * fps)) + 1
        b['dwell_f'] = int(round(b['_dwell'] * fps)) + 1
        del b['_settle'], b['_dwell'], b['_end'], b['_trans']
    # one chip per text: a repeated mention only re-shows the chip after chip_repeat_s
    last = {}
    items = sorted([(b['word_t'], b) for b in beats] + [(o['word_t'], o) for o in overlays], key=lambda x: x[0])
    for t, o in items:
        for k in ('chip', 'number'):
            v = o.get(k)
            if v:
                if (k, v) in last and (k == 'number' or t - last[(k, v)] < chip_repeat_s):   # a number is slammed once
                    o[k] = None
                else:
                    last[(k, v)] = t
    return beats, [o for o in overlays if o.get('chip') or o.get('number')]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('transcript'), ap.add_argument('terms'), ap.add_argument('out')
    ap.add_argument('--fps', type=int, default=30), ap.add_argument('--lead', type=float, default=0.6)
    ap.add_argument('--min-hold', type=float, default=2.5), ap.add_argument('--transition', type=float, default=0.8)
    ap.add_argument('--snap', action='store_true', help='settle on sentence starts within 1.5 s (Branch)')
    ap.add_argument('--dwell', type=float, default=0.4)
    a = ap.parse_args(argv)
    tr = json.load(open(a.transcript, encoding='utf-8'))
    words = [w for s in tr['segments'] for w in s.get('words', []) if 'start' in w]
    terms = json.load(open(a.terms, encoding='utf-8'))
    beats, overlays = schedule(find_beats(words, terms), a.fps, a.lead, a.min_hold, a.transition, end_t=words[-1]['end'],
                               words=words, snap=a.snap, dwell=a.dwell)
    json.dump({'fps': a.fps, 'lead': a.lead, 'beats': beats, 'overlays': overlays}, open(a.out, 'w', encoding='utf-8'), indent=1)
    missing = [t for t in terms if not any(t == b['term'] or t in b.get('also', []) for b in beats)]
    print(f'{len(beats)} beats; terms never spoken: {missing}')


def _selfcheck():
    w = lambda t, s: {'word': t, 'start': s, 'end': s + 0.3}
    words = [w('the', 1.0), w('driver', 2.0), w('gear', 2.3), w('turns', 2.7), w('the', 3.0), w('idler', 3.4),
             w('then', 8.0), w('the', 8.2), w('second', 9.0), w('hand', 9.3)]
    terms = {'driver gear': {'part': 'driver_gear'}, 'idler': {'part': 'idler', 'chip': 'IDLER'},
             'second hand': {'part': 'second_hand'}}
    hits = find_beats(words, terms)
    assert [h['part'] for h in hits] == ['driver_gear', 'idler', 'second_hand']
    b, ov = schedule(hits, fps=30, lead=0.6, min_hold=2.5)
    assert len(b) == 2 and b[0]['also'] == ['idler'] and ov[0]['chip'] == 'IDLER', b   # idler came 1.4 s later: merged
    assert b[0]['settle_f'] == int(round(1.4 * 30)) + 1 and b[1]['settle_f'] == int(round(8.4 * 30)) + 1
    assert b[0]['end_f'] == b[1]['settle_f'] and b[1]['move_f'] == b[1]['settle_f'] - 24
    # snap + dwell: "Then the second hand." starts a sentence 1.0 s before the term -> settle there
    words2 = [w('The', 1.0), w('driver', 1.4), w('gear.', 1.8), w('Then', 6.0), w('the', 6.4), w('second', 7.0), w('hand.', 7.3)]
    b2, _ = schedule(find_beats(words2, terms), 30, 0.6, 2.5, 0.8, words=words2, snap=True)
    assert abs((b2[1]['settle_f'] - 1) / 30 - 6.0) < 0.05, b2
    # dwell: a part named while the previous sentence is still running is merged, not cut to
    seq = 'The driver gear meshes with a long chain of teeth, and then the second hand finally moves.'.split()
    words3 = [w(t, 1.0 + 0.4 * i) for i, t in enumerate(seq)]   # one continuous sentence (gaps 0.1 s)
    b3, _ = schedule(find_beats(words3, terms), 30, 0.6, 2.5, 0.8, words=words3, snap=True)
    assert len(b3) == 1 and 'second hand' in b3[0]['also'], b3
    # whole words + anchor: 'cap' must not fire on 'capillary'; an early casual 'ball' is skipped by 'after'
    w4 = [w(t, 1.0 + 0.5 * i) for i, t in enumerate('a metal ball rolls . capillary action . then the cap goes on'.split())]
    h4 = find_beats(w4, {'cap': {'part': 'cap', 'after': 'then the'}, 'ball': {'part': 'ball'}})
    assert [h['part'] for h in h4] == ['ball', 'cap'] and h4[1]['word_t'] == w4[-3]['start'], h4
    h5 = find_beats(w4, {'ball': {'part': 'ball', 'after': 'rolls'}})
    assert h5 == [], h5
    # back-to-back sentences: shortened move instead of a merge
    w6 = [w('Ink', 0.0), w('tube.', 0.4), w('The', 2.2), w('socket', 2.7), w('tip', 3.0), w('holds.', 3.4)]
    t6 = {'ink tube': {'part': 'ink_tube', 'chip': 'INK'}, 'tip': {'part': 'tip', 'chip': 'TIP'}}
    b6, o6 = schedule(find_beats(w6, t6), 30, 0.6, 1.0, 0.8, words=w6, snap=True)
    assert len(b6) == 2 and b6[1]['settle_f'] > b6[1]['move_f'] + 12, b6
    print('selfcheck ok')


if __name__ == '__main__':
    _selfcheck() if sys.argv[1:] == ['--selfcheck'] else main()
