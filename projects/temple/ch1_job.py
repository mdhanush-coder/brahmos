# Chapter 1 (Hook), 24.64 s = 739 frames @ 30. Device stands on its edge on a charcoal stage and turns 360 degrees
# (front, edge, optical underside, back) while the camera pushes in. Gates: framing + size + audit, then look at frames.
# Runs after skilllib.py and temple_model.py in the same file (job_all.py): no exec of other files here.
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30
END = int(round(A.get('duration_s', 24.64) * FPS))
scene.frame_start, scene.frame_end = 1, END

P = temple_device(pcb_image=inputs.get('pcb.png'))
parts = list(P.values())
for o in bpy.data.objects:                     # the light-in-skin visuals belong to chapter 4 only
    if o.name == 'skin_layer' or o.name.startswith(('glow_', 'return_glow_')):
        o.hide_render = True
root = bpy.data.objects.new('temple_root', None)
scene.collection.objects.link(root)
for o in parts + [bpy.data.objects['foam_cut']]:
    if o.parent is None:
        o.parent = root
root.rotation_euler.x = math.radians(A.get('tilt', 75))      # stands on its edge, outer face toward camera (-Y)
bpy.context.view_layer.update()
lo, hi = bounds_world(parts)
root.location.z -= lo.z                                       # lowest point touches the floor (z = 0)
bpy.context.view_layer.update()
lo, hi = bounds_world(parts)
c = (lo + hi) / 2
rh = (hi.z - lo.z) / 2                                        # BODY half-height sizes the camera
r = (hi - lo).length / 2

spin = bpy.data.objects.new('spin_pivot', None)
scene.collection.objects.link(spin)
spin.location = (c.x, c.y, c.z)
bpy.context.view_layer.update()
root.parent = spin
root.matrix_parent_inverse = spin.matrix_world.inverted()

# stage: charcoal (#1C1C1C ~ 0.0116 linear), studio HDRI for the gold's reflections only (camera sees the flat colour)
cyclorama(size=r * 60, height=r * 24, bevel=r * 8, color=(0.0045, 0.0045, 0.0045), roughness=0.9)
hdri_world(A.get('hdri', '/library/hdri/environments-skies/Assets/Skies/Studio/photo_studio_01_4k.hdr'),
           strength=0.85, rotation_deg=30, color=(0.0116, 0.0116, 0.0116), background_strength=1.0)

# camera: 85 mm, DOF on the device, pushes in 1.25 -> 0.85 with an ease
dist = frame_distance(rh, 85, fill=0.52)
piv, cam = make_orbit_rig(c, distance=dist, height=dist * 0.14, focal=85, name='hero', fstop=5.6)
dolly(cam, [(1, 1.08), (END, 0.94)], preset='ease_in_out')   # MOTION DIRECTOR: ~13 % over 24.6 s (~2.6 % per 5 s hold); 1.25->0.85 pushed 32 % under words
bind_camera(scene, cam, 1)
scene.camera = cam
three_point(c, r, camera=cam, key_power=A.get('key_power', 190.0 * r * r))

# the 360: eased in and out, one full turn over the chapter
spin.rotation_euler.z = 0
key(spin, 'rotation_euler', 1, tuple(spin.rotation_euler), index=2)
spin.rotation_euler.z = math.radians(360)
key(spin, 'rotation_euler', END, tuple(spin.rotation_euler), index=2)
for fc in fcurves_of(spin):
    if fc.data_path == 'rotation_euler' and fc.array_index == 2:
        ease_segment(fc, 0, 0.35, 0.35)

render_preset(scene, 'preview', res=tuple(A.get('res', [1920, 1080])), fps=FPS)
scene.cycles.samples = 32
scene.view_settings.view_transform = 'Standard'      # AgX washes gold to cream (EngineX checks.md); Standard keeps brand colours
scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.2
gate = [1, 150, 300, 450, 600, END]
fills = {f: fill_fraction(scene, parts, f) for f in gate}
framing = check_framing(scene, parts, gate)
size_ok = fills[1]['h'] >= 0.35 and fills[END]['h'] >= 0.5 and all(v['h'] <= 1.05 and v['w'] <= 0.95 for v in fills.values())
result.update(fills=fills, framing=framing, size_ok=size_ok, audit=audit_fcurves(), rh=rh, r=r, c=list(c),
              parts=[o.name for o in parts])
render_review(scene, out, gate)
finish_plate(scene)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'ch1.blend'), copy=True)
if A.get('mode') == 'final' and size_ok:
    scene.render.resolution_percentage = 100
    scene.cycles.samples = A.get('samples', 96)
    video_output(scene, os.path.join(out, 'plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'plate.mp4'
