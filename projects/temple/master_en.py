"""English narration (voice owen, speak 0faecdfe) fitted to the film's chapter slots -> music/voice_en_full.wav (275.5 s).
The voice is never sped up or slowed: only silences are trimmed (line gaps shrink from 0.35 s to >= 0.15 s) and a chapter may start up
to LEAD s before its slot when the previous one ran long. Prints the drift of every chapter against its Hindi-timed slot."""
import wave, array

SR = 44100
# lines per chapter (29 lines: 3,3,3,3,3,3,4,2,4) with (start, end) from the speak result
L = [(0, 8.824), (9.174, 17.161), (17.511, 22.901), (23.801, 28.721), (29.071, 39.841), (40.191, 46.551), (47.451, 57.854), (58.204, 71.346),
     (71.696, 79.08), (80.23, 88.81), (89.16, 100.213), (100.563, 120.143), (121.043, 134.975), (135.325, 147.585), (147.935, 154.111),
     (155.261, 160.921), (161.271, 173.061), (173.311, 185.99), (186.34, 193.04), (193.94, 205.549), (205.899, 212.549), (212.899, 222.791),
     (223.141, 237.398), (238.298, 250.512), (250.862, 258.562), (259.462, 262.142), (262.742, 272.202), (272.552, 278.012), (278.362, 280.637)]
F = 1.035                                                         # the whole narration was sped up once by 3.5 %
L = [(s / F, e / F) for s, e in L]
CH = [3, 3, 3, 3, 3, 4, 4, 2, 4]
SLOT = [24.3, 24.267, 32.233, 39.467, 31.567, 36.733, 42.233, 19.7, 23.0]      # rendered chapter lengths (frames/30), cumulative = film
TOTAL = 275.5
LEAD, GAP_MIN, GAP_LINE_MIN, TAIL = 1.0, 0.4, 0.12, 0.2

w = wave.open('music/en_speech.wav')
assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, SR)
A = array.array('h', w.readframes(w.getnframes()))
out = array.array('h', bytes(2 * int(TOTAL * SR)))
slot0, li, prev_end = 0.0, 0, 0.0
for c, n in enumerate(CH):
    lines = L[li:li + n]; li += n
    dur_lines = [e - s for s, e in lines]
    gap = 0.2
    total = sum(dur_lines) + gap * (n - 1)
    start = max(slot0 - LEAD, prev_end + GAP_MIN)
    avail = slot0 + SLOT[c] - TAIL - start
    if total > avail and n > 1:                                   # trim silences only
        gap = max(GAP_LINE_MIN, (avail - sum(dur_lines)) / (n - 1))
        total = sum(dur_lines) + gap * (n - 1)
    t = start
    for (s, e) in lines:
        seg = A[int(s * SR):int(e * SR)]
        i0 = int(round(t * SR))
        for k, x in enumerate(seg):
            if i0 + k < len(out):
                out[i0 + k] = x
        t += (e - s) + gap
    prev_end = t - gap
    print(f'ch{c + 1}: slot {slot0:7.2f}-{slot0 + SLOT[c]:7.2f}  speech {start:7.2f}-{prev_end:7.2f}  drift {start - slot0:+.2f}s  ends {slot0 + SLOT[c] - prev_end:+.2f}s before slot end')
    slot0 += SLOT[c]
o = wave.open('music/voice_en_full.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(out.tobytes()); o.close()
print('wrote', round(len(out) / SR, 1), 's')
