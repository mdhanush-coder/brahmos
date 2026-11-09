"""Reference EngineX job: 5 s (150 f @ 30) smooth hero transition on a LIBRARY product.
Two cameras on two pivot empties; shot 1 pushes in and whips out, the cut happens at peak velocity (mid-transition),
shot 2 arrives at speed and settles with a slow drift. Motion blur sells the whip. Run like example_exploded_motor.py
(files skilllib.py + job.py, code="exec(open(inputs['job.py']).read())"). args: asset, size, hdri, mode
('preview' 4 gate frames | 'final' full animation), res [w,h], samples, face_axis ('-Y' default: product front faces -Y),
rot_z (deg, turn the product), look_a/look_b ((x,y,z) offsets of the two camera targets as fractions of the size)."""
import bpy, os, math, json
from mathutils import Vector
exec(open(inputs['skilllib.py']).read(), globals())

A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# 1. library product, standing on the floor
size = A.get('size', 1.0)
holder = place_asset(A['asset'], location=(0, 0, 0), rotation=(0, 0, math.radians(A.get('rot_z', 0))), size=size)
bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
lo, hi = bounds_world(meshes)
c = (lo + hi) / 2
r = (hi - lo).length / 2                         # bounding sphere (includes chains/cables): use for lights and floor only
rh = (hi.z - lo.z) / 2                           # BODY half-height: size the cameras from this (v1 used r and the subject was 20 % of frame)
scene.frame_start, scene.frame_end = 1, 150     # set AFTER the import (USD import resets the range)

# 2. studio (dark cyclorama + HDRI reflections + three-point)
cyclorama(size=r * 60, height=r * 24, bevel=r * 8, color=(0.015, 0.016, 0.019), roughness=0.85)
hdri_world(A['hdri'], strength=0.5, rotation_deg=30, color=(0.02, 0.022, 0.025), background_strength=1.0)

# 3. cameras: A (wide-ish, pushes in) and B (tight detail, settles)
def target(frac):
    return Vector((c.x + frac[0] * size, c.y + frac[1] * size, c.z + frac[2] * size))

la, lb = A.get('look_a', (0, 0, 0.0)), A.get('look_b', (0.0, 0, 0.0))
dist_a = frame_distance(rh, 85, fill=0.66)       # shot A ends with the watch ~66 % of frame height; dolly starts 1.3x further
pivA, camA = make_orbit_rig(target(la), distance=dist_a, height=dist_a * 0.10, focal=85, name='shotA', fstop=5.6)
dist_b = frame_distance(rh, 85, fill=0.80)       # shot B is the tighter hero: 80 %, whole body in frame, no cropping
pivB, camB = make_orbit_rig(target(lb), distance=dist_b, height=dist_b * 0.08, focal=85, name='shotB', fstop=4.0)

# shot A: orbit -28 -> +4 over f1-52 (ease out into the hero angle), dolly in 1.35 -> 1.0, then exit +4 -> +46 over f58-80
# (transition_out: leaves at full speed). Cut at f76 = peak velocity of both curves.
pivA.rotation_euler.z = math.radians(-28)
key(pivA, 'rotation_euler', 1, tuple(pivA.rotation_euler), index=2)
for f, deg in ((52, 4), (58, 4), (80, 46)):
    pivA.rotation_euler.z = math.radians(deg)
    key(pivA, 'rotation_euler', f, tuple(pivA.rotation_euler), index=2)
for fc in fcurves_of(pivA):
    if fc.data_path == 'rotation_euler' and fc.array_index == 2:
        ease_segment(fc, 0, 0.30, 0.70)       # settle into the hero angle
        ease_segment(fc, 1, 0.50, 0.50)       # near-hold
        ease_segment(fc, 2, 0.90, 0.00)       # whip out
dolly(camA, [(1, 1.30), (58, 1.0)], preset='ease_out')

# shot B: arrives from -46 at f72 (transition_in), settles at 0 by f98, drifts +12 deg to f150, slow dolly 1.0 -> 0.82
pivB.rotation_euler.z = math.radians(-46)
key(pivB, 'rotation_euler', 72, tuple(pivB.rotation_euler), index=2)
for f, deg in ((98, 0), (150, 12)):
    pivB.rotation_euler.z = math.radians(deg)
    key(pivB, 'rotation_euler', f, tuple(pivB.rotation_euler), index=2)
for fc in fcurves_of(pivB):
    if fc.data_path == 'rotation_euler' and fc.array_index == 2:
        ease_segment(fc, 0, 0.00, 0.90)       # arrive at speed, long settle
        ease_segment(fc, 1, 0.45, 0.60)       # continuing drift, no stop
        remove_bump(fc, 1)
dolly(camB, [(72, 1.04), (150, 0.90)], preset='ease_in_out')
bind_camera(scene, camA, 1)
bind_camera(scene, camB, 76)
scene.camera = camA

# 4. lights aimed at the product
three_point(c, r, camera=camA, key_power=A.get('key_power', 330.0 * r * r))

# 5. gate + review. SIZE gate, not only 'inside the frame': the subject must be big enough at the start and the hero end.
render_preset(scene, 'preview', res=(1920, 1080), fps=30)
scene.render.motion_blur_shutter = 0.75          # whip blur
scene.cycles.samples = 32
frames = [1, 40, 76, 78, 120, 150]
checks = {f: fill_fraction(scene, meshes, f) for f in (1, 40, 76, 120, 150)}
size_ok = checks[1]['h'] >= 0.35 and checks[120]['h'] >= 0.6 and all(v['h'] <= 1.05 and v['w'] <= 0.95 for v in checks.values())
result.update(fill=checks, size_ok=size_ok, audit=audit_fcurves(), r=r, rh=rh, c=list(c))
render_review(scene, out, frames)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'hero.blend'), copy=True)
if A.get('mode') == 'final' and size_ok:
    w, h = A.get('res', [1920, 1080])
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = w, h, 100
    scene.cycles.samples = A.get('samples', 96)
    video_output(scene, os.path.join(out, 'hero.mp4'))
    bpy.ops.render.render(animation=True)
    result['video'] = 'hero.mp4'
