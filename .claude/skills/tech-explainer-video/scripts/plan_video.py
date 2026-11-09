#!/usr/bin/env python3
"""Topic + minutes -> plan.json, 00_plan.md and a 03_script.md skeleton (Branch-measured budgets).

  python plan_video.py "How a quartz watch works" 6 projects/quartz-watch [--systems 3]
"""
import argparse, json, math, os, sys

WPM = 146          # Branch Education, measured, pauses included
WORDS_PER_BEAT = 14  # ~one sentence per shot at 146 wpm (6 s median shot)
SHARES = [('Hook', 'room', 0.08), ('Open it', 'explode', 0.06), ('SYSTEMS', 'focus', 0.60),
          ('Dive', 'dive', 0.10), ('Connect', 'return', 0.10), ('Close', 'room', 0.06)]


def plan(topic, minutes, systems=None):
    words = round(minutes * WPM)
    n_sys = systems or max(2, min(6, round(minutes * 0.6)))
    chapters = []
    if minutes <= 1.5:   # short test video: ONE chapter = one Blender job, one overlay, no concat
        chapters = [{'title': 'Short', 'shot': 'explode', 'words': words}]
    for name, shot, share in ([] if chapters else SHARES):
        if name == 'SYSTEMS':
            for i in range(n_sys):
                chapters.append({'title': f'System {i + 1}', 'shot': 'focus', 'words': round(words * share / n_sys)})
        else:
            chapters.append({'title': name, 'shot': shot, 'words': round(words * share)})
    for i, c in enumerate(chapters, 1):
        c['n'] = i
        c['seconds'] = round(c['words'] / WPM * 60, 1)
        c['beats'] = max(1, round(c['words'] / WORDS_PER_BEAT))
    n = len(chapters)
    calls = {
        'voice_speak_whole_video': 1, 'voice_transcribe_whole_video': 1,   # one take keeps one voice; chapters cut by line timings
        'uploads_create_url': 2 + n,                     # skilllib + one generic chapter job (args select the chapter), one zip per chapter
        'blender_preview': n, 'blender_final': n,
        'review_montage': n, 'review_sign_batched': 2,   # one sign_output per review round (50 keys)
        'motion_graphic_render_silent': n,
        'concat_audio_replace_sprite_sign': 4,
        'sound_voice_duck_patch_reserve': 6,  # video/duck + voice-track page render + one line patch speak/transcribe           # video/concat, video/audio-replace (whole VO), video/sprite, sign
        'retake_reserve_20pct': 0,
    }
    calls['retake_reserve_20pct'] = math.ceil(sum(calls.values()) * 0.2)
    total = sum(calls.values())
    return {'topic': topic, 'minutes': minutes, 'wpm': WPM, 'words': words, 'chapters': chapters,
            'enginex_calls': calls, 'enginex_calls_total': total, 'budget_cap': 500,
            'voice': {'voice': 'owen', 'lineGapMs': 450, 'paragraphGapMs': 900, 'continuity': True, 'format': 'wav'},
            'render': {'res': [1920, 1080], 'fps': 30}}


def skeleton(p):
    out = [f"# {p['topic']}", '']
    for c in p['chapters']:
        out += [f"## {c['n']}. {c['title']} || shot={c['shot']}",
                f"<!-- ~{c['words']} words, ~{c['seconds']} s, ~{c['beats']} beats -->", '']
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('topic'), ap.add_argument('minutes', type=float), ap.add_argument('project_dir')
    ap.add_argument('--systems', type=int)
    a = ap.parse_args(argv)
    p = plan(a.topic, a.minutes, a.systems)
    os.makedirs(os.path.join(a.project_dir, 'chapters'), exist_ok=True)
    json.dump(p, open(os.path.join(a.project_dir, 'plan.json'), 'w'), indent=1)
    md = [f"# Plan - {p['topic']}", '', f"{p['minutes']} min, {p['words']} words at {WPM} wpm, "
          f"{len(p['chapters'])} chapters, voice owen.", '', '| # | Chapter | Shot | Words | Seconds | Beats |',
          '|---|---|---|---|---|---|']
    md += [f"| {c['n']} | {c['title']} | {c['shot']} | {c['words']} | {c['seconds']} | {c['beats']} |" for c in p['chapters']]
    md += ['', f"EngineX call plan: {p['enginex_calls']} = **{p['enginex_calls_total']}** (cap 500)."]
    open(os.path.join(a.project_dir, '00_plan.md'), 'w', encoding='utf-8').write('\n'.join(md))
    sk = os.path.join(a.project_dir, '03_script.md')
    if not os.path.exists(sk):
        open(sk, 'w', encoding='utf-8').write(skeleton(p))
    print('\n'.join(md))


def _selfcheck():
    p = plan('x', 6)
    assert p['words'] == 876 and abs(sum(c['words'] for c in p['chapters']) - 876) <= 6
    assert len(p['chapters']) == 9 and p['enginex_calls_total'] <= 15 * 6, p['enginex_calls_total']
    assert len(plan('x', 1)['chapters']) == 1
    assert plan('x', 10)['enginex_calls_total'] <= 500
    print('selfcheck ok')


if __name__ == '__main__':
    _selfcheck() if sys.argv[1:] == ['--selfcheck'] else main()
