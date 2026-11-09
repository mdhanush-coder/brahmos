# Chapter 4 (How Temple works), 89.92 -> 129.37 s = 39.45 s = 1184 frames @ 30. Layers (reference picture): hollow gold shell, silver foil
# battery, black PCB with gold traces (chips + antenna ride it), sensor board with green micro-LEDs, foam ring, translucent pad
# (optical window + 3 emitters + photodiode ride its underside). The shell lifts first, layers separate at even spacing, the stack tips
# toward the camera while the light is explained (emitters pulse like a heartbeat), then re-assembles before the cut.
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30
END = int(round(A.get('duration_s', 39.45) * FPS))
scene.frame_start, scene.frame_end = 1, END

P = temple_device(pcb_image=inputs.get('pcb.png'))
parts = list(P.values())


def ride(children, host):
    """Parent children to host keeping their world position (so they travel with it during the explode)."""
    bpy.context.view_layer.update()
    for n in children:
        o = P[n]
        o.parent = host
        o.matrix_parent_inverse = host.matrix_world.inverted()


ride(['heart_rate_sensor', 'motion_sensor', 'thermometer', 'processor', 'antenna'], P['pcb'])
ride(['optical_window', 'led_green', 'led_red', 'led_infrared', 'photodiode'], P['adhesive_pad'])
top = [P[n] for n in ('shell', 'battery', 'pcb', 'sensor_board', 'foam_ring', 'adhesive_pad')]    # top-down: the shell opens first
LIFT = 0.03                                    # emitters sit 5.6 mm below the pad: keep the whole stack above the floor
for o in top:
    o.location.z += LIFT
bpy.context.view_layer.update()
asm = bpy.data.objects.new('assembly', None)   # one pivot so the stack can tip toward the camera
scene.collection.objects.link(asm)
asm.location = (0.0, -0.02, 0.20)
bpy.context.view_layer.update()
for o in top:
    o.parent = asm
    o.matrix_parent_inverse = asm.matrix_world.inverted()

dist = {'shell': 0.30, 'battery': 0.22, 'pcb': 0.15, 'sensor_board': 0.10, 'foam_ring': 0.05, 'adhesive_pad': 0.0}
axes = {k: Vector((0, 0, 1)) for k in dist}
axes['adhesive_pad'] = Vector((0, 0, 0))
n = len(top)
START, HOLD_IN, EXP, STAG, RET = 30, 40, 60, 14, 60
t0 = START + HOLD_IN
hold = END - 30 - (t0 + 2 * (n - 1) * STAG + EXP + RET)
last = explode(top, axes=axes, start=START, assembled_hold=HOLD_IN, explode_len=EXP, stagger=STAG, hold=hold, return_len=RET,
               preset='smooth', order=top, distances=dist)

# emitters: a heartbeat pulse (strength 3 -> 12 -> 3) every 33 frames from the first PPG word (frame 296) to the end of the chapter
for mname, phase in (('LED Green', 0), ('LED Red', 4), ('LED Infrared', 8)):
    sock = bpy.data.materials[mname].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    sock.default_value = 0.0
    sock.keyframe_insert('default_value', frame=1)
    sock.keyframe_insert('default_value', frame=285 + phase)
    f = 296 + phase
    while f + 24 < END - 10:
        for ff, v in ((f, 1.5), (f + 8, 5.0), (f + 22, 1.5)):     # 8 clipped green and red to white
            sock.default_value = v
            sock.keyframe_insert('default_value', frame=ff)
        f += 33
    sock.default_value = 0.0
    sock.keyframe_insert('default_value', frame=END)
    # the visible beam of that emitter pulses with it (strength 0 until the light explanation, then 1.2 -> 5 -> 1.2)
    bs = bpy.data.materials[mname.replace('LED', 'Beam')].node_tree.nodes['Emission'].inputs['Strength']
    bs.default_value = 0.0
    bs.keyframe_insert('default_value', frame=1)
    bs.keyframe_insert('default_value', frame=285 + phase)
    f = 296 + phase
    while f + 24 < END - 10:
        for ff, v in ((f, 1.2), (f + 8, 5.0), (f + 22, 1.2)):
            bs.default_value = v
            bs.keyframe_insert('default_value', frame=ff)
        f += 33
    bs.default_value = 0.0
    bs.keyframe_insert('default_value', frame=END)

# the returning light grows in cloud by cloud on "...बाक़ी लौटकर एक सेंसर तक आता है" (~104 s -> chapter frame ~420), holds,
# and fades back out (last cloud first) before re-assembly
glows = sorted((o for o in bpy.data.objects if o.name.startswith('return_glow_')), key=lambda o: o.name)
S = 0.009
for i, g in enumerate(glows):
    on, off = 410 + int(i * 2.5), 1000 - int(i * 1.2)       # in after the tip settles (400), out before the re-assembly (1024)
    for f, s in ((1, 0.0), (on, 0.0), (on + 12, S), (off - 12, S), (off, 0.0), (END, 0.0)):
        g.scale = (s, s, s)
        g.keyframe_insert('scale', frame=f)
    for fc in fcurves_of(g):
        if fc.data_path == 'scale':
            for k in range(len(fc.keyframe_points) - 1):
                ease_segment(fc, k, 0.4, 0.4)

# the faint skin layer exists only while the light is explained: fades in once the stack has tipped clear of the floor, out before it returns
skin_fac = bpy.data.materials['Skin Layer'].node_tree.nodes['Mix Shader'].inputs['Fac']
for f, v in ((1, 0.0), (385, 0.0), (420, 0.07), (975, 0.07), (1005, 0.0), (END, 0.0)):     # 0.2 read as a solid pink block
    skin_fac.default_value = v
    skin_fac.keyframe_insert('default_value', frame=f)

# MOTION DIRECTOR: one lead move at a time, the camera still while words are read (camera.md). The stack's tip is an OBJECT
# move (the lead) made while the camera holds: 0 -> -62 deg over f335-400 (after the camera's descent ends at 335), held,
# back to 0 over f880-940; the camera does not move during either.
for f, deg in ((1, 0), (335, 0), (400, -62), (END, -62)):     # stays tipped and re-assembles tipped: upright, the exploded stack crossed the frame top (f1030) with the camera held
    asm.rotation_euler.x = math.radians(deg)
    key(asm, 'rotation_euler', f, tuple(asm.rotation_euler), index=0)
for fc in fcurves_of(asm):
    if fc.data_path == 'rotation_euler' and fc.array_index == 0:
        for i in range(len(fc.keyframe_points) - 1):
            ease_segment(fc, i, 0.4, 0.4)

c = Vector((0.0, -0.02, 0.20))
rh = 0.19
r = 0.30
cyclorama(size=r * 60, height=r * 24, bevel=r * 8, color=(0.0045, 0.0045, 0.0045), roughness=0.9)
hdri_world(A.get('hdri', '/library/hdri/environments-skies/Assets/Skies/Studio/photo_studio_01_4k.hdr'),
           strength=0.85, rotation_deg=30, color=(0.0116, 0.0116, 0.0116), background_strength=1.0)
d = frame_distance(rh, 70, fill=0.60)               # sized for the fully exploded stack at factor 1.0
piv, cam = make_orbit_rig(c, distance=d, height=d * 0.22, focal=70, name='explode', fstop=8.0)    # low, near side-on like the reference
orbit(piv, 1, END, 14, preset='ease_in_out')        # a slow constant drift only (36 deg turned the frame while words were read)
# CAMERA = two composed moves, each in a gap between words, each one move (rise+pull back together, descend+push in together):
#   f20-70   pull back and rise to look down on the layers (before the explode and before the first word on screen, 3.1 s)
#   f300-335 descend and push in toward the emitters (between step 1 at 8.8 s and step 2 at 12.2 s)
# Everything else: the camera holds while the OBJECT moves lead (explode f70-200, tip f335-400, tip back, re-assembly).
for f, deg in ((1, 0), (20, 0), (70, -38), (300, -38), (335, 0), (END, 0)):
    piv.rotation_euler.x = math.radians(deg)
    key(piv, 'rotation_euler', f, tuple(piv.rotation_euler), index=0)
for fc in fcurves_of(piv):
    if fc.data_path == 'rotation_euler' and fc.array_index == 0:
        for i in range(len(fc.keyframe_points) - 1):
            ease_segment(fc, i, 0.4, 0.4)
dolly(cam, [(1, 0.5), (20, 0.5), (70, 0.97), (300, 0.97), (335, 0.72), (END, 0.72)], preset='ease_in_out')
for f, z in ((1, 0.07), (20, 0.07), (70, 0.19), (300, 0.19), (335, 0.17), (END, 0.17)):
    piv.location = (c.x, c.y, z)
    key(piv, 'location', f, tuple(piv.location))
for fc in fcurves_of(piv):
    if fc.data_path == 'location':
        for i in range(len(fc.keyframe_points) - 1):
            ease_segment(fc, i, 0.4, 0.4)
bind_camera(scene, cam, 1)
scene.camera = cam
three_point(c, r, camera=cam, key_power=190.0 * r * r)

render_preset(scene, 'preview', res=tuple(A.get('res', [1920, 1080])), fps=FPS)
scene.cycles.samples = 32
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.2
gate = [1, 200, 270, 345, 420, 600, 900, 1030, END]
fills = {f: fill_fraction(scene, parts, f) for f in gate}
framing = check_framing(scene, parts, gate)
size_ok = fills[1]['h'] >= 0.25 and all(v['h'] <= 1.0 and v['w'] <= 0.97 for v in fills.values())
result.update(fills=fills, framing=framing, size_ok=size_ok, audit=audit_fcurves(), last_key=last, hold=hold,
              out_frames={o.name: o.get('explode_out_frame') for o in top})
render_review(scene, out, gate)
finish_plate(scene)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'ch4.blend'), copy=True)
if A.get('mode') == 'final' and size_ok:
    scene.render.resolution_percentage = 100
    scene.cycles.samples = A.get('samples', 96)
    video_output(scene, os.path.join(out, 'plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'plate.mp4'
