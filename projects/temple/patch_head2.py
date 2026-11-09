import ast
s = open('head_scene.py', encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert old in s, old
    s = s.replace(old, new, count)

rep("vein = _emit_mat('Vein', (0.10, 0.30, 0.95), 1.4, rough=0.3)", "vein = _emit_mat('Vein', (0.04, 0.22, 1.0), 0.9, base=(0.02, 0.08, 0.5), rough=0.3)")
rep("steps=(30, 14, 7), step=0.006, r0=0.0011,", "steps=(30, 14, 7), step=0.006, r0=0.0008,")
rep("art = _emit_mat('Artery', (0.85, 0.06, 0.05), 0.6, rough=0.3)", "art = _emit_mat('Artery', (0.95, 0.04, 0.03), 1.3, rough=0.3)")
rep("steps=(18, 10, 6), step=0.004, r0=0.00095)", "steps=(18, 10, 6), step=0.004, r0=0.0014)")
rep("sta_m = _emit_mat('STA Glow', (1.0, 0.82, 0.10), 9.0, rough=0.2)", "sta_m = _emit_mat('STA Glow', (1.0, 0.78, 0.05), 3.2, rough=0.2)")
# cone: bright at the device end (local z = 0), fading into the head
rep("ramp.color_ramp.elements[0].color = (0, 0, 0, 1)\n    ramp.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1)", "ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1)\n    ramp.color_ramp.elements[1].color = (0.06, 0.06, 0.06, 1)")
# brain: less specular wash
rep("b.inputs['Roughness'].default_value = 0.42", "b.inputs['Roughness'].default_value = 0.55")
rep("b.inputs['Coat Weight'].default_value = 0.25", "b.inputs['Coat Weight'].default_value = 0.08")
ast.parse(s)
open('head_scene.py', 'w', encoding='utf-8').write(s)

j = open('head_review_job.py', encoding='utf-8').read()
old = j[j.index("w = bpy.data.worlds.new('W')"):j.index("scene.view_settings.view_transform")]
j = j.replace(old, "hdri_world(color=(0.55, 0.62, 0.80), strength=1.0, background_strength=0.0)   # reflections for the gold; the camera sees black\n")
j = j.replace("A.get('key', 45)", "A.get('key', 25)").replace("A.get('rim', 70)", "A.get('rim', 45)")
j = j.replace("views = {'three_quarter': (0.6, -0.6, 0.08), 'side': (1.0, 0.0, 0.05), 'front': (0.0, -1.0, 0.05)}",
              "views = {'three_quarter': (0.6, -0.6, 0.08), 'side': (1.0, 0.0, 0.05), 'front': (0.12, -1.0, 0.05)}")
open('head_review_job.py', 'w', encoding='utf-8').write(j)
parts = ['../../.claude/skills/blender-animation/scripts/skilllib.py', 'temple_model.py', 'head_scene.py', 'head_review_job.py']
b = '\n\n'.join(open(p, encoding='utf-8').read() for p in parts)
ast.parse(b)
open('job_head_review2.py', 'w', encoding='utf-8').write(b)
print('ok')
