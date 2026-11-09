"""Generic EngineX blender/script job for ONE chapter of a tech explainer. Upload once; every chapter calls it with args.
files={'skilllib.py': <bundle>, 'job.py': <this file>, 'beats.json': <chapter beats>}, code="exec(open(inputs['job.py']).read())"
args: chapter (int), shot ('focus' | 'explode' | 'macro' | 'return'), source ({'procedural': 'drone_motor'} or
{'asset': '<library id>', 'size': m}), duration_s (exact voice length of the chapter), mode ('preview' | 'final'),
glow (bool, default true: rim glow in the material, keyed by the 'glow' property), res [w,h], samples, explode_at, explode_axes {part:[x,y,z]}, explode_distances {part:m}, hdri (path), fill (part share of frame height when named, default 0.45).
Produces: review_NNNN.png gate frames (preview) or plate.mp4 (final), plus tracks.json for callouts_page.py.
STATUS: assembled from tested helpers (gather_asset, drone_motor, explode, cyclorama, three_point, render_review,
check_framing, fill_fraction) and the UNTESTED focus_rig; its first run is a preview test - review before 'final'.
GHOST: every part gets Mix(real, x-ray) driven by its "ghost" property; ghost_beats keys 0->1 on every part except
the one being named (word-0.8 s .. sentence end+0.4 s). Preview gate frames sample the pixel of a ghosted part.
explode_at (frame, default 1) starts the explode in shot='explode'; separation frames are returned for SFX."""
import bpy, os, math, json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
exec(open(inputs['skilllib.py']).read(), globals())

A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
beats = json.load(open(inputs['beats.json']))['beats']
fps = 30
src = A.get('source', {'procedural': 'drone_motor'})
if 'procedural' in src:
    P = globals()[src['procedural']]()
    parts = list(P.values())
else:
    parts = gather_asset(src['asset'], size=src.get('size', 0.6))
by_name = {o.name: o for o in parts}
scene.frame_start, scene.frame_end = 1, max(2, int(round(A['duration_s'] * fps)))   # after any import

lo, hi = bounds_world(parts)
c, r = (lo + hi) / 2, (hi - lo).length / 2
cyclorama(size=r * 60, height=r * 24, bevel=r * 8, color=(0.012, 0.013, 0.015), roughness=0.85)   # black-void look
hdri_world(A.get('hdri'), strength=0.4, rotation_deg=40, color=(0.01, 0.011, 0.013), background_strength=1.0)
three_point(c, r, camera=None, key_power=330 * r * r)

piv = bpy.data.objects.new('focus_pivot', None)
scene.collection.objects.link(piv)
piv.location = c
cam = make_camera('chapter_cam', focal=A.get('focal', 135), fstop=A.get('fstop', 5.6), focus=piv,
                  clip=(r * 0.005, r * 200))
cam.parent = piv
wide = frame_distance(r, A.get('focal', 135), fill=0.55)       # opening wide shot; camera_to_beats keeps the aim (constant ratio)
cam.location = Vector((0, -wide, wide * 0.25))
look_at_local(cam, piv)                                        # pen test #1: unaimed camera -> every part 'behind camera'
scene.camera = cam
shot = A.get('shot', 'focus')
if shot == 'explode':
    ex0 = A.get('explode_at', 1)
    axes = auto_axes(parts)
    for n, v in (A.get('explode_axes') or {}).items():          # explicit assembly axes beat the auto ones (pen test #3: the ink
        axes[n] = Vector(v)                                        # tube slid out the wrong end, the cap hid the tip)
    explode(parts, axes, start=ex0, distances=A.get('explode_distances'), assembled_hold=18, explode_len=36, stagger=6,
            hold=max(30, scene.frame_end - ex0 - 120), preset='smooth')
install_ghost(parts)
ghost_render_settings(scene)
glow_shells = {}                                  # the old copied-shell glow is retired (solid orange fill, see failure log)
camera_to_beats(piv, cam, by_name, beats, focal=A.get('focal', 135), fill=A.get('fill', 0.45))
if A.get('glow', True):
    glow_property_beats(by_name, beats)
ghost_wins = ghost_beats(parts, beats, fps=fps)
separations = sorted(int(o['explode_out_frame'] - 36) for o in parts if 'explode_out_frame' in o)
bpy.context.view_layer.update()

# tracks for the overlay (named parts only)
tracks = {'fps': fps, 'frames': scene.frame_end, 'parts': []}
named = [o for o in parts if any(b.get('part') == o.name for b in beats)]
for o in named:
    tracks['parts'].append({'id': o.name, 'label': o.name.replace('_', ' ').title(), 'sub': '',
                            'out': min(b['settle_f'] for b in beats if b.get('part') == o.name),
                            'back': max(b['end_f'] for b in beats if b.get('part') == o.name), 'pts': []})
for f in range(1, scene.frame_end + 1):
    scene.frame_set(f)
    for tp, o in zip(tracks['parts'], named):
        p = world_to_camera_view(scene, cam, o.matrix_world @ (sum((Vector(k) for k in o.bound_box), Vector()) / 8))
        tp['pts'].append([round(p.x, 4), round(1 - p.y, 4), 1 if p.z > 0 else 0])
for i, tp in enumerate(sorted(tracks['parts'], key=lambda t: t['pts'][0][0])):
    tp['row'] = i % 4
json.dump(tracks, open(os.path.join(out, 'tracks.json'), 'w'))

# gates: the named part is in frame and big enough at every settle frame
render_preset(scene, 'preview', res=tuple(A.get('res', [1920, 1080])), fps=fps)
gate_frames = sorted({b['settle_f'] for b in beats if b.get('part') in by_name})[:6] or [1]
fills = {}
named_beats = [b for b in beats if b.get('part') in by_name]
for b in named_beats[1:]:          # the first named part is the establishing shot of the whole assembly (judged by eye)
    o = by_name.get(b.get('part'))
    if o:
        fills[b['settle_f']] = dict(fill_fraction(scene, [o], b['settle_f']), part=o.name)
size_ok = all((0.25 <= v['h'] <= 0.9 or 0.45 <= v['w'] <= 0.95) and v['h'] <= 0.95 and v['w'] <= 0.97 for v in fills.values())   # long thin part: judged by width
result.update(chapter=A.get('chapter'), separations=separations, ghost_windows=ghost_wins, gate_frames=gate_frames, fills=fills, size_ok=size_ok, audit=audit_fcurves(),
              framing={'problems': [p for b in beats if b.get('part') in by_name for p in check_framing(scene, [by_name[b['part']]], [b['settle_f']])['problems']]})
render_review(scene, out, gate_frames)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"chapter_{A.get('chapter', 0):02d}.blend"), copy=True)
if A.get('mode') == 'final' and size_ok:
    scene.render.resolution_percentage = 100
    scene.cycles.samples = A.get('samples', 96)
    video_output(scene, os.path.join(out, 'plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'plate.mp4'
