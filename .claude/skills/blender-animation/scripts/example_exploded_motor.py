"""Reference EngineX job: 10 s exploded view of a procedural 2207 drone motor -> clean plate + tracks.json.
Run as a blender/script job with files={'skilllib.py': <bundle.py output>, 'job.py': <this file>} and
code="exec(open(inputs['job.py']).read())". args: hdri (path), mode ('preview' = 3 gate frames only, 'plate' = gate then
full animation), plate_res [w,h], plate_samples.

The 2D callouts are NOT rendered by Blender: tracks.json (per-frame screen position of every part) drives a Motion
Graphic overlay (see scripts/callouts_page.py). Pipeline: this job -> motion-graphic/render with the plate as <video>.

Hard-won rules baked in (see SKILL.md 'Failure log'): assign_material() not materials.append; gate the long render on
pixel checks; camera dolly scales y AND z; explode axis horizontal for 16:9; frame range set AFTER any USD import."""
import bpy, os, math, json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
exec(open(inputs['skilllib.py']).read(), globals())

A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# 1. model: detailed procedural parts (library has no multi-part motor), library PBR for anodised parts
P = drone_motor()
ALU = '/library/materials/base-materials/Materials/Base/Metals/Aluminum_Anodized/Aluminum_Anodized_'
alu = {'albedo': ALU + 'BaseColor.png', 'orm': ALU + 'ORM.png', 'normal': ALU + 'Normal.png'}
M = {
    'base_mount': library_material('anod_black', alu, tint=(0.05, 0.05, 0.055), scale=3),
    'rotor_bell': library_material('anod_red', alu, tint=(0.75, 0.025, 0.02), scale=3),
    'prop_nut': library_material('anod_blue', alu, tint=(0.04, 0.2, 0.95), scale=3),
    'stator': metal('stator_steel', (0.30, 0.31, 0.33), 0.35),
    'windings': metal('copper', (0.955, 0.638, 0.538), 0.28),
    'magnets': metal('magnet', (0.22, 0.22, 0.24), 0.4),
    'shaft': metal('shaft_steel', (0.56, 0.57, 0.58), 0.12),
    'bearing_bottom': metal('bearing', (0.72, 0.72, 0.74), 0.2),
    'bearing_top': metal('bearing2', (0.72, 0.72, 0.74), 0.2),
    'circlip': metal('blackoxide', (0.04, 0.04, 0.045), 0.4),
    'screws': metal('screw_black', (0.06, 0.06, 0.065), 0.32)}
for k, o in P.items():
    assign_material(o, M[k])

# 2. explode plan: (part, signed distance along the assembly axis); top of the stack leaves first
plan = [('prop_nut', 1.15), ('shaft', 0.95), ('rotor_bell', 0.55), ('magnets', 0.55), ('bearing_top', 0.78),
        ('windings', 0.30), ('stator', 0.12), ('bearing_bottom', -0.16), ('base_mount', -0.30), ('screws', -0.55),
        ('circlip', -0.62)]
parts = [P[n] for n, _ in plan]
rotate_assembly(parts, 'Y', 90)                       # axis along X: fills a 16:9 frame
lo, hi = bounds_world(parts)
for o in parts:
    o.location.z += 0.45 - lo.z                       # floats above the floor
bpy.context.view_layer.update()
axes = {n: Vector((1 if d > 0 else -1, 0, 0)) for n, d in plan}
dist = {n: abs(d) for n, d in plan}
scene.frame_start, scene.frame_end = 1, 300           # 10 s @ 30 fps
n = len(parts)
stag, elen, rlen, start_hold = 6, 36, 30, 18         # hold ends up ~78 frames (2.6 s): every part gets a full read
hold = max(30, 300 - 18 - (start_hold + 2 * (n - 1) * stag + elen + rlen))
explode(parts, axes, start=1, assembled_hold=start_hold, explode_len=elen, stagger=stag, hold=hold,
        return_len=rlen, preset='smooth', order=parts, distances=dist)

# 3. camera: pivot orbit + breathing dolly (close on the assembled motor, wide for the explode)
scene.frame_set(1)
lo, hi = bounds_world(parts); c_asm = (lo + hi) / 2
scene.frame_set(150)
lo, hi = bounds_world(parts); c_exp, width = (lo + hi) / 2, (hi - lo).x
d = frame_width_distance(width, 50, fill=0.74)       # v1 used 0.60: subject too small next to the label pills
piv, cam = make_orbit_rig(c_exp, distance=d, height=d * 0.26, focal=50, name='shot1', fstop=11.0)
piv.rotation_euler.z = math.radians(-22)
orbit(piv, 1, 300, 44, preset='ease_in_out')
for f, c in ((1, c_asm), (70, c_exp), (250, c_exp), (300, c_asm)):
    key(piv, 'location', f, tuple(c))
for fc in fcurves_of(piv):
    if fc.data_path == 'location':
        ease(fc, 'smooth')
dolly(cam, [(1, 0.3), (70, 1.0), (250, 1.0), (300, 0.3)], preset='smooth')
scene.camera = cam

# 4. look: dark cyclorama, HDRI for reflections only, three-point lights
cyclorama(size=150, height=40, bevel=12, color=(0.02, 0.021, 0.024), roughness=0.8)
hdri_world(A['hdri'], strength=0.5, rotation_deg=40, color=(0.02, 0.022, 0.025), background_strength=1.0)
three_point(c_exp, width / 2, camera=cam, key_power=320)

# 5. tracks for the Motion Graphic overlay
labels = {'prop_nut': ('M5 PROP NUT', 'M5 hex'), 'shaft': ('SHAFT', 'Ø5 mm'),
          'rotor_bell': ('ROTOR BELL', 'outrunner · 14P'), 'magnets': ('MAGNETS', 'N52 · ×14'),
          'bearing_top': ('TOP BEARING', '685ZZ · 5×11×5'), 'windings': ('WINDINGS', '12 coils'),
          'stator': ('STATOR', '12N · 22 mm'), 'bearing_bottom': ('BOTTOM BEARING', '685ZZ · 5×11×5'),
          'base_mount': ('BASE MOUNT', '4× M3 pattern'), 'screws': ('MOUNT SCREWS', 'M3 × 4'),
          'circlip': ('CIRCLIP', 'E-clip')}


def anchor(o):
    return o.matrix_world @ (sum((Vector(c) for c in o.bound_box), Vector()) / 8)


tracks = {'fps': 30, 'frames': 300, 'parts': []}
for o in parts:
    tracks['parts'].append({'id': o.name, 'label': labels[o.name][0], 'sub': labels[o.name][1],
                            'out': int(o['explode_out_frame']), 'back': int(o['explode_back_frame']), 'pts': []})
for f in range(1, 301):
    scene.frame_set(f)
    for tp, o in zip(tracks['parts'], parts):
        p = world_to_camera_view(scene, cam, anchor(o))
        tp['pts'].append([round(p.x, 4), round(1 - p.y, 4), 1 if p.z > 0 else 0])
xs = sorted(range(n), key=lambda i: tracks['parts'][i]['pts'][149][0])
for rank, i in enumerate(xs):
    tracks['parts'][i]['row'] = rank % 4              # staggered label rows by x order: neighbours never share a row
with open(os.path.join(out, 'tracks.json'), 'w') as fh:
    json.dump(tracks, fh)

# 6. gate: 3 review frames + pixel assertions BEFORE the long render
render_preset(scene, 'preview', res=(1920, 1080), fps=30)
render_review(scene, out, [1, 121, 180])
name_i = {tp['id']: i for i, tp in enumerate(tracks['parts'])}


def px(part, frame):
    pt = tracks['parts'][name_i[part]]['pts'][frame - 1]
    return sample_pixel(os.path.join(out, 'review_%04d.png' % frame), pt[0], pt[1])


s_bell, s_nut = px('rotor_bell', 121), px('prop_nut', 121)
framing = check_framing(scene, parts, [1, 40, 70, 110, 150, 200, 240, 280, 300])
fill150 = fill_fraction(scene, parts, 150)
gate = bool(s_bell[0] > 1.5 * max(s_bell[1], s_bell[2]) and s_nut[2] > 1.05 * s_nut[0] and s_nut[2] > s_nut[1]
            and framing['ok'] and 0.55 <= fill150['w'] <= 0.92)
result.update(bell_rgb=s_bell, nut_rgb=s_nut, gate=gate, framing=framing, fill150=fill150, audit=audit_fcurves())
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'exploded_motor.blend'), copy=True)

# 7. the plate (clean 3D, no labels)
if gate and A.get('mode') == 'plate':
    w, h = A.get('plate_res', [1280, 720])
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = w, h, 100
    scene.cycles.samples = A.get('plate_samples', 64)
    video_output(scene, os.path.join(out, 'plate.mp4'))
    progress(0, 300, 'rendering plate')
    bpy.ops.render.render(animation=True)
    result['plate'] = 'plate.mp4'
