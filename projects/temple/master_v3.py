"""Master narration v3 (2026-11-07). The user: ch2's delivery is right; ch6-8 sounded slower and lower.
Measured: the one long take drifted from 9.0 syllables/s (ch2) to ~8.1 and got quieter (continuity carries the read).
Fix: ch3 and ch5-9 re-voiced as fresh takes (louder), then sped up 1.09x with the pitch kept (video/speed + extract-audio)
to ch2's pace. Layout: ch1+ch2 from master_voice_v2.wav (unchanged, ch1 already rendered), every other chapter's speech
followed by a 0.9 s gap; ch4 = the approved take padded to its rendered video (1184 frames).
Writes master_voice_v3.wav and timings_v3.json (chapter start/end in master time).  usage: python -I master_v3.py"""
import json, wave, array

SR, GAP, FPS = 44100, 0.9, 30
SPEED = 1.09
TARGET = 4250          # voiced RMS every chapter is levelled to (ch1 and ch4 sit here already)
CH4_VIDEO = 1184 / FPS
fresh = json.load(open('takes/fresh_all.json'))          # offsets of each fresh take inside fresh_all.wav (before speed-up)
NAMES = {1: 'Hook', 2: 'What is Temple', 3: 'Why brain blood flow matters', 4: 'How Temple works',
         5: 'The reveal: two arteries', 6: "Temple's evidence", 7: 'Why doctors push back', 8: 'The gravity theory', 9: 'Verdict'}


def read(path):
    w = wave.open(path)
    assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, SR), path
    return array.array('h', w.readframes(w.getnframes()))


def speech(a, lo=0, hi=None, thr=300, pad=0.04):
    """the speech inside a[lo:hi], first to last loud 10 ms block, with a small pad"""
    hi = len(a) if hi is None else hi
    blk = SR // 100
    loud = [i for i in range(lo, hi - blk, blk) if max(abs(x) for x in a[i:i + blk]) > thr]
    s, e = max(lo, loud[0] - int(pad * SR)), min(hi, loud[-1] + blk + int(pad * SR))
    return a[s:e]


def main():
    v2, ch4, sped = read('master_voice_v2.wav'), read('ch4_retake_raghav_v2.wav'), read('takes/fresh_all_109.wav')
    out, chapters = array.array('h'), []
    def put(n, seg, slot=None):
        start = len(out) / SR
        out.extend(seg)
        chapters.append({'n': n, 'name': NAMES[n], 'start': round(start, 3), 'end': round(len(out) / SR, 3)})
        tail = (round(slot * SR) - len(seg)) if slot else round(GAP * SR)
        out.extend(array.array('h', bytes(2 * tail)))
    # ch1 + ch2 exactly as in v2 (ch1 starts at 0, ch2 at 24.28; ch2 speech ends 47.64)
    put(1, v2[:round(23.38 * SR)], slot=24.28)
    put(2, speech(v2, round(24.28 * SR), round(48.2 * SR)))
    offs = {int(k): v for k, v in fresh['offsets'].items()}
    order = fresh['order']
    for n in [3, 4, 5, 6, 7, 8, 9]:
        if n == 4:
            put(4, ch4, slot=CH4_VIDEO)
            continue
        i = order.index(n)
        lo = round(offs[n] / SPEED * SR)
        hi = round((offs[order[i + 1]] / SPEED) * SR) if i + 1 < len(order) else len(sped)
        put(n, speech(sped, lo, hi))
    # one loudness for every chapter (the takes differ by up to 2 dB): voiced RMS -> TARGET
    for c in chapters:
        a, b = round(c['start'] * SR), round(c['end'] * SR)
        blocks = [out[i:i + 1024] for i in range(a, b - 1024, 1024)]
        rms = [(sum(x * x for x in f) / 1024) ** 0.5 for f in blocks]
        voiced = [r for r in rms if r > 400]
        g = TARGET / (sum(voiced) / len(voiced))
        for i in range(a, b):
            out[i] = max(-32767, min(32767, round(out[i] * g)))
        c['gain_db'] = round(20 * __import__('math').log10(g), 2)
    with wave.open('master_voice_v3.wav', 'wb') as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(out.tobytes())
    total = len(out) / SR
    for i, c in enumerate(chapters):
        c['video'] = round((chapters[i + 1]['start'] if i + 1 < len(chapters) else total) - c['start'], 3)
    json.dump({'voice': 'raghav', 'audio': 'master_voice_v3.wav', 'durationSec': round(total, 3),
               'note': 'video = chapter start to next chapter start; ch1, ch2, ch4 unchanged from v2', 'chapters': chapters},
              open('timings_v3.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    # self-check: ch1/ch2/ch4 keep their rendered lengths, chapters in order with gaps
    c = {x['n']: x for x in chapters}
    assert c[2]['start'] == 24.28 and abs(c[4]['video'] - CH4_VIDEO) < 0.01
    assert all(chapters[i]['end'] < chapters[i + 1]['start'] for i in range(8))
    for x in chapters:
        print(f"ch{x['n']} {x['start']:7.2f}-{x['end']:7.2f}  video {x['video']:6.2f}s  {x['name']}")
    print('total', round(total, 2))


if __name__ == '__main__':
    main()
