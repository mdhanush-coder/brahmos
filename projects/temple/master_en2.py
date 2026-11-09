"""English narration v2: every sentence starts when its matching graphic appears (never before: user, 2026-11-07 "the audio comes first,
the display comes later"). Input: music/en_speech.wav (owen, sped once 1.035x) + the speak line times. Each line is split at its sentence
pauses (silence detection), and each piece gets an ANCHOR = chapter-local time of the on-screen element it talks about (the overlays are timed
to the Hindi words). Piece start = max(anchor, previous end + gap). Writes music/voice_en_full.wav and prints how late each chapter runs."""
import wave, array, math

SR, F = 44100, 1.035
L = [(0, 8.824), (9.174, 17.161), (17.511, 22.901), (23.801, 28.721), (29.071, 39.841), (40.191, 46.551), (47.451, 57.854), (58.204, 71.346),
     (71.696, 79.08), (80.23, 88.81), (89.16, 100.213), (100.563, 120.143), (121.043, 134.975), (135.325, 147.585), (147.935, 154.111),
     (155.261, 160.921), (161.271, 173.061), (173.311, 185.99), (186.34, 193.04), (193.94, 205.549), (205.899, 212.549), (212.899, 222.791),
     (223.141, 237.398), (238.298, 250.512), (250.862, 258.562), (259.462, 262.142), (262.742, 272.202), (272.552, 278.012), (278.362, 280.637)]
L = [(s / F, e / F) for s, e in L]
SLOT = [24.3, 24.267, 32.233, 39.467, 31.567, 36.733, 42.233, 19.7, 23.0]
TOTAL = 275.5
# per chapter: list of (line index, [anchor per sentence; None = follow on straight away])
PLAN = [
    [(0, [0.1, None]), (1, [7.9]), (2, [18.3, None])],
    [(3, [0.5]), (4, [5.3]), (5, [16.9, None])],
    [(6, [0.4, 6.2]), (7, [11.4, 18.2]), (8, [24.9, None])],
    [(9, [0.0]), (10, [9.3]), (11, [20.9, 29.0])],
    [(12, [0.1, 1.5, 7.15]), (13, [12.9, 21.1]), (14, [25.0, 28.9])],
    [(15, [0.3]), (16, [6.6]), (17, [17.35, 25.45]), (18, [30.1])],
    [(19, [0.0, 2.2]), (20, [10.8]), (21, [19.2]), (22, [30.3, 32.0])],
    [(23, [1.2]), (24, [12.4])],
    [(25, [0.2]), (26, [4.0, 6.5, 9.8]), (27, [13.9]), (28, [20.3])],
]
GAP_LINE, GAP_CH = 0.14, 0.2

w = wave.open('music/en_speech.wav')
assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, SR)
A = array.array('h', w.readframes(w.getnframes()))


def split_line(s, e, k):
    """cut [s, e] seconds into k pieces at its k-1 longest internal pauses; returns [(a, b), ...]"""
    if k == 1:
        return [(s, e)]
    seg = A[int(s * SR):int(e * SR)]
    hop = SR // 100
    en = [math.sqrt(sum(x * x for x in seg[i:i + hop:2]) / max(1, len(seg[i:i + hop:2]))) for i in range(0, len(seg), hop)]
    thr = 0.05 * sorted(en)[int(0.95 * len(en))]
    runs, i = [], 0
    while i < len(en):
        if en[i] < thr:
            j = i
            while j < len(en) and en[j] < thr:
                j += 1
            if 25 <= i and j <= len(en) - 25 and j - i >= 8:       # not in the first/last 0.25 s, at least 80 ms
                runs.append((j - i, i, j))
            i = j
        else:
            i += 1
    cuts = sorted(sorted(runs, reverse=True)[:k - 1], key=lambda r: r[1])
    assert len(cuts) == k - 1, (s, e, k, len(runs))
    pts = [s] + [s + (r[1] + r[2]) / 2 / 100 for r in cuts] + [e]
    return list(zip(pts[:-1], pts[1:]))


out = array.array('h', bytes(2 * int(TOTAL * SR)))
slot0, prev_end, worst = 0.0, 0.0, 0.0
for c, lines in enumerate(PLAN):
    lags = []
    for li, anchors in lines:
        s, e = L[li]
        parts = split_line(s, e, len(anchors))
        for k, ((a, b), anc) in enumerate(zip(parts, anchors)):
            gap = (GAP_CH if (c > 0 and li == lines[0][0] and k == 0) else GAP_LINE if k == 0 else 0.0)
            start = max(slot0 + anc if anc is not None else 0.0, prev_end + gap)
            seg = A[int(a * SR):int(b * SR)]
            i0 = int(round(start * SR))
            for n, x in enumerate(seg):
                if i0 + n < len(out):
                    out[i0 + n] = x
            prev_end = start + (b - a)
            if anc is not None:
                lags.append(start - (slot0 + anc))
    over = prev_end - (slot0 + SLOT[c])
    print(f'ch{c + 1}: starts after its graphic by up to {max(lags):.2f} s (mean {sum(lags) / len(lags):.2f}); speech ends {-over:+.2f} s vs chapter end')
    slot0 += SLOT[c]
o = wave.open('music/voice_en_full.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(out.tobytes()); o.close()
print('final speech end', round(prev_end, 2), 's of', TOTAL)
