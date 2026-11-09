import ast
j = open('head_anim_job.py', encoding='utf-8').read()
def rep(old, new):
    global j
    assert old in j, old
    j = j.replace(old, new, 1)
rep("cer, cbl, stem, arteries, sta = parts['cerebrum'], parts['cerebellum'], parts['brainstem'], parts['arteries'], parts['sta']",
    "cer, cbl, stem, arteries, sta = parts['cerebrum'], parts['cerebellum'], parts['brainstem'], parts['arteries'], parts['sta']\nstem.hide_render = True       # a bare stump looked like a stray block; the neck's own vessels carry the story")
rep("(f0 + 20, 0.9), (f0 + 38, 0.0)", "(f0 + 20, 0.45), (f0 + 38, 0.0)")
rep("A.get('cam_offset', (0.42, -0.42, 0.056))", "A.get('cam_offset', (0.14, -0.66, 0.05))")
rep("art_pulse, art_b = pulse_copy(arteries, 'ArteryPulse', (1, 0.1, 0.05))", "art_pulse, art_b = pulse_copy(arteries, 'ArteryPulse', (1, 0.1, 0.05), strength=9.0, thick=2.4)")
ast.parse(j)
open('head_anim_job.py', 'w', encoding='utf-8').write(j)
parts = ['../../.claude/skills/blender-animation/scripts/skilllib.py', 'temple_model.py', 'finish_plate.py', 'head_scene.py', 'head_anim_job.py']
b2 = '\n\n'.join(open(p, encoding='utf-8').read() for p in parts)
ast.parse(b2)
open('job_head_anim.py', 'w', encoding='utf-8').write(b2)
print('ok')
