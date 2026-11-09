"""Smooth music bed under a voice (user, 2026-11-07: reduce the ducking, it should feel very smooth).
usage: python -I mix_music.py <voice.wav> <out.wav> [music_start_s]   (music = music/lib_prologue.wav, 44.1 kHz mono 16-bit)
1. the library cue builds from a whisper to a huge climax: a SLOW automatic gain (3 s window, gain 0.15x-6x) holds it at one level
2. a soft limiter (tanh) rounds any drum hits the gain follower cannot catch
3. ducking is only ~3 dB, with a 0.4 s attack and a 1.6 s release (no pumping between sentences)
4. fade in 3 s, fade out 5 s; music sits ~16 dB under the voice, ~19 dB while he speaks"""
import wave, array, math, sys

SR = 44100
voice_p, out_p = sys.argv[1], sys.argv[2]
m_start = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0


def rd(p):
    w = wave.open(p)
    assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, SR), p
    return array.array('h', w.readframes(w.getnframes()))


voice = rd(voice_p)
import os
music = rd(os.environ.get('MUSIC_FILE', 'music/lib_prologue.wav'))   # default was a copyrighted library cue: pass MUSIC_FILE=an original bed
N = len(voice)
s0 = int(m_start * SR)
mus = music[s0:s0 + N]
assert len(mus) >= N, 'music shorter than the voice'
B = SR // 10                                                  # 0.1 s blocks


def blocks_rms(a):
    return [math.sqrt(sum(x * x for x in a[i:i + B:3]) / max(1, len(a[i:i + B:3]))) for i in range(0, len(a), B)]


# 1) slow AGC on the music
mr = blocks_rms(mus)
K = 30                                                        # 3 s window
sm = [sum(mr[max(0, i - K // 2):i + K // 2 + 1]) / len(mr[max(0, i - K // 2):i + K // 2 + 1]) for i in range(len(mr))]
vr = blocks_rms(voice)
voiced = [x for x in vr if x > 1500]
v_ref = sum(voiced) / len(voiced)
M_TARGET = v_ref * 0.158                                      # about -16 dB under the voice
g = [min(6.0, max(0.05, M_TARGET / max(20.0, s))) for s in sm]
# 3) ducking envelope from the voice: attack 0.4 s, release 1.6 s, depth 3 dB
env, e = [], 0.0
for x in vr:
    t = min(1.0, x / (0.6 * v_ref))
    a = 0.1 / 0.4 if t > e else 0.1 / 1.6
    e += (t - e) * min(1.0, a)
    env.append(e)
duck = [1.0 - 0.29 * x for x in env]                          # 0.71 = -3 dB while he speaks
# per-sample gain by linear interpolation between block centres, then soft limit
out = array.array('h', bytes(2 * N))
FI, FO = 3 * SR, 5 * SR
LIM = 9000.0
nb = len(g)
for i in range(N):
    p = i / B - 0.5
    b0 = int(p) if p > 0 else 0
    b1 = b0 + 1 if b0 + 1 < nb else nb - 1
    f = p - b0 if p > 0 else 0.0
    gg = (g[b0] * (1 - f) + g[b1] * f) * (duck[b0] * (1 - f) + duck[b1] * f)
    y = mus[i] * gg
    y = LIM * math.tanh(y / LIM)
    if i < FI:
        y *= i / FI
    elif i > N - FO:
        y *= (N - i) / FO
    v = voice[i] + y
    out[i] = -32767 if v < -32767 else 32767 if v > 32767 else int(v)
pk = max(abs(x) for x in out)
w = wave.open(out_p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
mo = blocks_rms(out)
print(f'voice ref rms {v_ref:.0f}; music target {M_TARGET:.0f}; mix peak {pk}/32767; length {N / SR:.1f}s')
