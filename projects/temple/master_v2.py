"""Master narration v2 (approved linked-clause style, 2026-11-07).
take A = speak d57c2cd1 (ch1-3, ch5-9), take B = speak b73db2e1 (ch4, approved, its composite already rendered).
Layout: A[0 : ch5 start in A] + B + silence so ch4 lasts exactly its rendered video (1184 frames) + A[ch5 start in A :].
Writes master_voice_v2.wav, words_raghav_v2.json (master times) and timings_v2.json (chapter start/end, master times).
usage: python -I master_v2.py"""
import json, wave

FPS = 30
CH4_VIDEO = 1184 / FPS                       # ch4 composite (95dfd3ab) length; the 3D plate is fixed to it
A_CH5 = 83.688                               # take A: first line of ch5 (lines[] of d57c2cd1)
# chapter first/last line in take A (speak d57c2cd1 result.lines); ch4 comes from take B
A_CH = {1: (0.0, 23.38), 2: (24.28, 48.64), 3: (49.54, 82.788), 5: (83.688, 120.758), 6: (121.908, 160.738),
        7: (161.638, 206.798), 8: (207.698, 227.528), 9: (228.428, 251.598)}
B_LEN = 38.963
# take A spans cut out: after the [pause] in ch2 the voice spoke a garbled word ("अरे डिपोलमोरो", 41.2-42.0 s, loud),
# found by checking every line's first heard word against the script. What is left of the pause is 1.0 s.
CUTS = [(41.15, 42.15)]


def clean(t):
    """take-A time -> time after the cuts"""
    return t - sum(e - s for s, e in CUTS if t >= e)
NAMES = {1: 'Hook', 2: 'What is Temple', 3: 'Why brain blood flow matters', 4: 'How Temple works',
         5: 'The reveal: two arteries', 6: "Temple's evidence", 7: 'Why doctors push back', 8: 'The gravity theory', 9: 'Verdict'}


def a_to_master(t):
    return clean(t) if t < A_CH5 else clean(t) + CH4_VIDEO


def main():
    a, b = wave.open('voice_raghav_v2_no_ch4.wav'), wave.open('ch4_retake_raghav_v2.wav')
    sr, bpf = a.getframerate(), a.getsampwidth() * a.getnchannels()
    assert (a.getnchannels(), a.getsampwidth(), sr) == (b.getnchannels(), b.getsampwidth(), b.getframerate())
    raw = a.readframes(a.getnframes())
    keep, pos = [], 0
    for s, e in CUTS:
        keep.append(raw[pos * bpf:round(s * sr) * bpf]); pos = round(e * sr)
    keep.append(raw[pos * bpf:])
    clean_a = b''.join(keep)
    cut = round(clean(A_CH5) * sr) * bpf
    head, tail = clean_a[:cut], clean_a[cut:]
    ch4 = b.readframes(b.getnframes())
    pad = b'\0' * (a.getsampwidth() * (round(CH4_VIDEO * sr) - b.getnframes()))
    with wave.open('master_voice_v2.wav', 'wb') as o:
        o.setparams(a.getparams())
        o.writeframes(head + ch4 + pad + tail)

    cut_out = lambda t: any(s <= t < e for s, e in CUTS)
    segs = []
    for s in json.load(open('words_take_v2_no_ch4.json', encoding='utf-8'))['segments']:
        ws = [{**w, 'start': a_to_master(w['start']), 'end': a_to_master(w['end'])}
              for w in s['words'] if 'start' in w and not cut_out(w['start'])]
        if ws:
            segs.append({**s, 'start': ws[0]['start'], 'end': ws[-1]['end'], 'words': ws,
                         'text': ' '.join(w['word'] for w in ws)})
    c4 = clean(A_CH5)
    for s in json.load(open('words_ch4_retake.json', encoding='utf-8'))['segments']:
        segs.append({**s, 'start': s['start'] + c4, 'end': s['end'] + c4,
                     'words': [{**w, 'start': w['start'] + c4, 'end': w['end'] + c4} for w in s['words'] if 'start' in w]})
    segs.sort(key=lambda s: s['start'])
    json.dump({'segments': segs}, open('words_raghav_v2.json', 'w', encoding='utf-8'), ensure_ascii=False)

    ch = {n: (a_to_master(s), a_to_master(e)) for n, (s, e) in A_CH.items()}
    ch[4] = (c4, c4 + B_LEN)
    total = (len(head) + len(ch4) + len(pad) + len(tail)) / (sr * bpf)
    chapters = [{'n': n, 'name': NAMES[n], 'start': round(ch[n][0], 3), 'end': round(ch[n][1], 3),
                 'video': round((ch[n + 1][0] if n < 9 else total) - ch[n][0], 3)} for n in sorted(ch)]
    json.dump({'voice': 'raghav', 'audio': 'master_voice_v2.wav', 'durationSec': round(total, 3),
               'takes': {'A': 'd57c2cd1-4732-49bb-a691-55d470ab7351', 'B_ch4': 'b73db2e1-748c-49ef-a1df-b3945054d4ab'},
               'note': 'video = this chapter start to the next chapter start (the last runs to the end of the voice)',
               'chapters': chapters}, open('timings_v2.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    # self-check: ch4 slot is exactly the rendered ch4 video, chapters in order, words land inside their chapters
    assert abs(ch[5][0] - ch[4][0] - CH4_VIDEO) < 1e-6
    assert all(ch[n][1] < ch[n + 1][0] for n in range(1, 9))
    assert all(segs[i]['start'] <= segs[i + 1]['start'] for i in range(len(segs) - 1))
    assert not any(w['word'] in ('अरे', 'डिपोलमोरो') for s in segs for w in s['words'])   # the garbled word is gone
    for c in chapters:
        print(f"ch{c['n']} {c['start']:7.2f}-{c['end']:7.2f}  video {c['video']:6.2f}s  {c['name']}")
    print('total', round(total, 2), 's')


if __name__ == '__main__':
    main()
