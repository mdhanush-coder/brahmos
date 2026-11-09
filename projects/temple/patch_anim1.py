import ast
j = open('head_anim_job.py', encoding='utf-8').read()
a = j.index("def set_interp(")
b = j.index("for k, t in enumerate(BEATS):")
NEW = '''def set_interp(owner, interp, prefixes=None):
    """every key on the datablock's action (a node tree for socket keys, a curve for bevel factors); the Blender 5 action
    API differs from 4.x, so walk the fcurves defensively. prefixes: only fcurves whose data_path starts with one of them."""
    ad = owner.animation_data
    if not ad or not ad.action:
        return
    act = ad.action
    fcs = getattr(act, 'fcurves', None)
    if fcs is None:
        fcs = [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    for fc in fcs:
        if prefixes and not any(fc.data_path.startswith(p) for p in prefixes):
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = interp


'''
j = j[:a] + NEW + j[b:]
a = j.index("# colours step (constant)")
b = j.index("# ---- camera")
TAIL = '''# colours step (constant), bevel runs are linear (a lit segment travels at a steady speed), the swell eases
color_socks = {cone_em.id_data: [cone_em.inputs['Color']], art_b.id_data: [art_b.inputs['Emission Color'], art_b.inputs['Base Color']],
               brain_b.id_data: [brain_b.inputs['Emission Color']]}
for tree, socks in color_socks.items():
    set_interp(tree, 'CONSTANT', [s.path_from_id() for s in socks])
for sp in [sta_pulse, art_pulse] + [o for o in bpy.data.objects if o.name.startswith('TemporalBranch')]:
    set_interp(sp.data, 'LINEAR')

'''
j = j[:a] + TAIL + j[b:]
ast.parse(j)
open('head_anim_job.py', 'w', encoding='utf-8').write(j)
parts = ['../../.claude/skills/blender-animation/scripts/skilllib.py', 'temple_model.py', 'finish_plate.py', 'head_scene.py', 'head_anim_job.py']
b2 = '\n\n'.join(open(p, encoding='utf-8').read() for p in parts)
ast.parse(b2)
open('job_head_anim.py', 'w', encoding='utf-8').write(b2)
print('ok')
