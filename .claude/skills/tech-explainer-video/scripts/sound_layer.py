#!/usr/bin/env python3
"""Sound layer + patchable voice for a chapter / video. Pure planning: writes cue lists and <audio> tags that the
Motion Graphic page plays frame-exactly (data-start / data-duration / data-volume / data-media-start).

Mix (decided, do not ask):
  music bed  -> <audio> in the visual page, data-volume 0.1 (= -20 dB), looped to the duration, 1.5 s fade by split
  SFX        -> whoosh on every camera move (beat move_f), click on every part separation, volume 0.25-0.35
  voice      -> NOT in the page. video/duck {input: page mp4 (music+SFX), voice: voice audio, strength: normal}
               ducks the bed ~8 dB under speech and evens the mix to -14 LUFS.
Voice patch (one wrong line, no full re-take):
  1. ONE emotive-speech/speak of only that line: same voice, same brief line, same lineGapMs, a NEW idempotencyKey.
  2. ONE transcribe of the patch (word check + its exact length; trim lead/tail silence by its first/last word).
  3. voice_cues() splices: original audio up to the line, the patch, original audio after the line. A longer patch
     shifts everything after it by `delta` (returned) and shift_words() moves the transcript so beats stay exact.
  4. Render the splice with voice_page() (silent black page with the <audio> cues) -> its mp4 is the voice input.

  python sound_layer.py cues --beats NN.beats.json --duration 61.2 --music assets/music.mp3 --whoosh assets/whoosh.mp3 \
         --click assets/click.mp3 [--separations 45,51,57] --out NN.sound.json
  python sound_layer.py patch --lines lines.json --voice assets/voice.wav --line 7 --src assets/patch07.wav \
         --patch-start 0.12 --patch-end 4.31 --words transcript.json --out voice.json --page voice.html
"""
import argparse, json, sys

MUSIC_VOL, WHOOSH_VOL, CLICK_VOL = 0.1, 0.3, 0.35
FADE_STEPS = (0.03, 0.06)       # bed starts and ends with two short quieter slices (pages have no volume ramps)


def music_cues(src, duration, music_len, vol=MUSIC_VOL, fade=1.5):
    """Bed looped to `duration`; the first and last `fade` s are split into quieter slices for a soft in/out."""
    cues, t = [], 0.0
    while t < duration - 0.05:
        d = min(music_len, duration - t)
        cues.append({'src': src, 'start': round(t, 3), 'dur': round(d, 3), 'vol': vol, 'media_start': 0.0})
        t += d
    out = []
    for c in cues:                                   # soft head on the very first cue, soft tail on the last
        segs = [c]
        if c is cues[0] and c['dur'] > 3 * fade:
            h = fade / 2
            segs = [dict(c, dur=h, vol=FADE_STEPS[0]), dict(c, start=c['start'] + h, dur=h, media_start=h, vol=FADE_STEPS[1]),
                    dict(c, start=c['start'] + fade, dur=c['dur'] - fade, media_start=fade)]
        if c is cues[-1] and segs[-1]['dur'] > 3 * fade:
            last = segs.pop()
            h = fade / 2
            body = dict(last, dur=last['dur'] - fade)
            segs += [body, dict(last, start=body['start'] + body['dur'], dur=h, media_start=body['media_start'] + body['dur'],
                                vol=FADE_STEPS[1]),
                     dict(last, start=body['start'] + body['dur'] + h, dur=h,
                          media_start=body['media_start'] + body['dur'] + h, vol=FADE_STEPS[0])]
        out += segs
    return [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()} for c in out]


def sfx_cues(beats, whoosh, click, separations=(), fps=30, whoosh_len=1.2, click_len=0.4, min_gap=0.35):
    """Whoosh when the camera starts a focus move (move_f), click on each part separation frame."""
    cues = []
    for b in beats:
        if b.get('part') and 'move_f' in b:
            cues.append({'src': whoosh, 'start': max(0.0, (b['move_f'] - 1) / fps), 'dur': whoosh_len, 'vol': WHOOSH_VOL})
    last = -9.0
    for f in sorted(separations):
        t = (f - 1) / fps
        if t - last >= min_gap:                      # stagger of 6 frames -> clicks would machine-gun; keep spacing
            cues.append({'src': click, 'start': t, 'dur': click_len, 'vol': CLICK_VOL})
            last = t
    return sorted(({**c, 'start': round(c['start'], 3), 'media_start': 0.0} for c in cues), key=lambda c: c['start'])


def voice_cues(lines, voice_src, total, patch=None):
    """Splice list for the voice. lines: [{start,end}] of the original take (s). patch: {line, src, start, end}
    = the line index to replace and the usable span inside the patch file. Returns (cues, delta, at)."""
    if not patch:
        return [{'src': voice_src, 'start': 0.0, 'dur': round(total, 3), 'vol': 1.0, 'media_start': 0.0}], 0.0, None
    L = lines[patch['line']]
    nxt = lines[patch['line'] + 1]['start'] if patch['line'] + 1 < len(lines) else total
    gap_after = nxt - L['end']
    plen = patch['end'] - patch['start']
    slot = L['end'] - L['start']
    delta = round(max(0.0, plen - slot), 3)          # a shorter patch keeps the slot (rest of the slot is silence)
    cues = [{'src': voice_src, 'start': 0.0, 'dur': round(L['start'], 3), 'vol': 1.0, 'media_start': 0.0},
            {'src': patch['src'], 'start': round(L['start'], 3), 'dur': round(plen, 3), 'vol': 1.0,
             'media_start': round(patch['start'], 3)},
            {'src': voice_src, 'start': round(L['end'] + delta, 3), 'dur': round(total - L['end'], 3), 'vol': 1.0,
             'media_start': round(L['end'], 3)}]
    assert gap_after >= 0
    return [c for c in cues if c['dur'] > 0.01], delta, L['end']


def shift_words(words, at, delta, line_span=None, patch_words=None):
    """Transcript after a splice: words after `at` move by delta; the patched line's words are replaced by the
    patch transcript's words (offset to the line start) so beat_sheet sees the new timing."""
    out = []
    for w in words:
        if line_span and line_span[0] - 0.02 <= w['start'] < line_span[1] + 0.02:
            continue
        if at is not None and w['start'] >= at:
            w = dict(w, start=round(w['start'] + delta, 3), end=round(w['end'] + delta, 3))
        out.append(w)
    for w in patch_words or []:
        out.append(w)
    return sorted(out, key=lambda w: w['start'])


def audio_html(cues, prefix='snd'):
    return '\n'.join(
        f'<audio id="{prefix}{i}" src="{c["src"]}" data-start="{c["start"]}" data-duration="{c["dur"]}" '
        f'data-volume="{c["vol"]}" data-media-start="{c.get("media_start", 0.0)}"></audio>' for i, c in enumerate(cues))


def voice_page(cues, duration):
    """Silent black page that only plays the spliced voice: its render is the `voice` input of video/duck."""
    return f'''<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>body{{margin:0;background:#000}}#root{{position:relative;width:1920px;height:1080px;background:#000}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080">
{audio_html(cues, 'vo')}
</div><script>
const tl=gsap.timeline({{paused:true}});tl.to({{}},{{duration:{duration}}});window.__timelines={{main:tl}};
</script></body></html>'''


def _selfcheck():
    m = music_cues('m.mp3', 100.0, 85.9)
    assert abs(sum(c['dur'] for c in m) - 100.0) < 1e-6 and m[0]['vol'] == 0.03 and m[-1]['vol'] == 0.03, m
    assert max(c['vol'] for c in m) == MUSIC_VOL
    for a, b in zip(m, m[1:]):
        assert abs(a['start'] + a['dur'] - b['start']) < 1e-3
    beats = [{'part': 'ball', 'move_f': 31}, {'part': None}, {'part': 'tube', 'move_f': 121}]
    s = sfx_cues(beats, 'w.mp3', 'c.mp3', separations=[40, 46, 52, 70])
    assert [c['src'] for c in s] == ['w.mp3', 'c.mp3', 'c.mp3', 'c.mp3', 'w.mp3'] and s[0]['start'] == 1.0, s
    lines = [{'start': 0.0, 'end': 3.0}, {'start': 3.5, 'end': 6.0}, {'start': 6.5, 'end': 9.0}]
    c, d, at = voice_cues(lines, 'v.wav', 10.0, {'line': 1, 'src': 'p.wav', 'start': 0.1, 'end': 3.1})
    assert d == 0.5 and at == 6.0 and c[1]['start'] == 3.5 and c[2]['start'] == 6.5 and c[2]['media_start'] == 6.0, c
    c2, d2, _ = voice_cues(lines, 'v.wav', 10.0, {'line': 1, 'src': 'p.wav', 'start': 0.0, 'end': 2.0})
    assert d2 == 0 and c2[2]['start'] == 6.0
    words = [{'w': 'a', 'start': 1.0, 'end': 1.2}, {'w': 'old', 'start': 4.0, 'end': 4.3}, {'w': 'z', 'start': 7.0, 'end': 7.2}]
    sw = shift_words(words, at, d, (3.5, 6.0), [{'w': 'new', 'start': 3.6, 'end': 3.9}])
    assert [w['w'] for w in sw] == ['a', 'new', 'z'] and sw[2]['start'] == 7.5, sw
    assert 'data-media-start="6.0"' in audio_html(c)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['cues', 'patch', 'selfcheck'])
    ap.add_argument('--beats'), ap.add_argument('--duration', type=float), ap.add_argument('--out')
    ap.add_argument('--music'), ap.add_argument('--music-len', type=float, default=85.9)
    ap.add_argument('--whoosh'), ap.add_argument('--click'), ap.add_argument('--separations', default='')
    ap.add_argument('--lines'), ap.add_argument('--voice'), ap.add_argument('--line', type=int), ap.add_argument('--src')
    ap.add_argument('--patch-start', type=float), ap.add_argument('--patch-end', type=float)
    ap.add_argument('--words'), ap.add_argument('--patch-words'), ap.add_argument('--page')
    a = ap.parse_args(argv)
    if a.mode == 'selfcheck':
        print('selfcheck', _selfcheck())
        return
    if a.mode == 'cues':
        beats = json.load(open(a.beats, encoding='utf-8'))['beats'] if a.beats else []
        seps = [int(x) for x in a.separations.split(',') if x]
        cues = music_cues(a.music, a.duration, a.music_len) + sfx_cues(beats, a.whoosh, a.click, seps)
        json.dump({'cues': cues}, open(a.out, 'w', encoding='utf-8'), indent=1)
        print(f'wrote {a.out}: {len(cues)} cues')
        return
    lines = json.load(open(a.lines, encoding='utf-8'))
    total = a.duration or lines[-1]['end'] + 0.5
    cues, delta, at = voice_cues(lines, a.voice, total, {'line': a.line, 'src': a.src, 'start': a.patch_start,
                                                          'end': a.patch_end})
    res = {'cues': cues, 'delta': delta, 'at': at, 'duration': round(total + delta, 3)}
    if a.words:
        W = json.load(open(a.words, encoding='utf-8'))
        words = W['words'] if isinstance(W, dict) else W
        L = lines[a.line]
        pw = []
        if a.patch_words:
            P = json.load(open(a.patch_words, encoding='utf-8'))
            pw = [dict(w, start=round(w['start'] - a.patch_start + L['start'], 3), end=round(w['end'] - a.patch_start + L['start'], 3))
                  for w in (P['words'] if isinstance(P, dict) else P)]
        res['words'] = shift_words(words, at, delta, (L['start'], L['end']), pw)
    json.dump(res, open(a.out, 'w', encoding='utf-8'), indent=1)
    if a.page:
        open(a.page, 'w', encoding='utf-8').write(voice_page(cues, res['duration']))
    print(f'wrote {a.out}: {len(cues)} voice cues, delta {delta}s')


if __name__ == '__main__':
    sys.exit(main())
