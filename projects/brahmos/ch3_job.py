# Chapter 3 (Launch) plate, 37.92 s @ 30 fps, opaque (dusk sky). Runs after skilllib.py + brahmos_scene.py.
# Cues (absolute s): canister 81.19, truck 86.31, booster 90.56, diwali 93.92, supersonic 103.09, separation 105.83,
# why 116.41. Chapter starts at 79.897 s. Lines: 79.897 / 90.277 / 98.087 / 104.987 / 110.607.
# The booster sits INSIDE the aft chamber (model v2) and slides out backwards at separation.
import os, math
from mathutils import Matrix
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30; T0 = 79.897
def F(t): return int(round((t - T0) * FPS)) + 1
END = int(round(37.92 * FPS))
scene.frame_start, scene.frame_end = 1, END
fWide, fLaunch, fDiCam, fArc, fSep, fWhy = F(84.6), F(90.277), F(93.5), F(98.087), F(104.987), F(110.607)

P = brahmos_import(inputs['brahmos.glb'])
mroot, croot = P['missile_root'], P['canister_root']
M = {n: o for n, o in P.items() if not n.endswith('_root') and not n.startswith('canister')}

# ---------- dusk world: blaze-tinted horizon to the palette's night at the zenith
w = bpy.data.worlds.new('dusk'); scene.world = w; w.use_nodes = True
nt = w.node_tree; nt.nodes.clear()
o_ = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 0.0, (0.50, 0.17, 0.05, 1)
cr.elements[1].position, cr.elements[1].color = 0.45, (*NIGHT, 1)
e = cr.elements.new(0.12); e.color = (0.10, 0.065, 0.08, 1)
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], o_.inputs['Surface'])
def sunlamp(name, energy, color, rot):
    s = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); scene.collection.objects.link(s)
    s.data.energy = energy; s.data.color = color; s.rotation_euler = rot; return s
sunlamp('dusk_sun', 1.6, (1.0, 0.55, 0.3), (math.radians(80), 0, math.radians(-115)))
sunlamp('sky_fill', 0.35, (0.6, 0.72, 1.0), (math.radians(35), 0, math.radians(60)))

sand = bpy.data.materials.new('sand'); sand.use_nodes = True; sn = sand.node_tree; sb = sn.nodes['Principled BSDF']
sb.inputs['Base Color'].default_value = (0.16, 0.11, 0.07, 1); sb.inputs['Roughness'].default_value = 0.95
snz = sn.nodes.new('ShaderNodeTexNoise'); snz.inputs['Scale'].default_value = 0.6
sbump = sn.nodes.new('ShaderNodeBump'); sbump.inputs['Strength'].default_value = 0.25
sn.links.new(snz.outputs['Fac'], sbump.inputs['Height']); sn.links.new(sbump.outputs['Normal'], sb.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, 0)); ground = bpy.context.active_object; ground.name = 'ground'
assign_material(ground, sand)

# ---------- 12x12 launcher (procedural, from the parade photo): camo chassis, box cab, 6 axles, erector + 3 canisters
camo = bpy.data.materials['canister_camo']
tyre = simple_material('tyre', (0.02, 0.02, 0.02), roughness=0.85)
glassc = simple_material('cab_glass', (0.03, 0.05, 0.07), roughness=0.1)
def cube(name, size, loc, mat, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object
    o.name = name; o.scale = size; bpy.ops.object.transform_apply(scale=True); assign_material(o, mat)
    if bevel:
        m = o.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = 2
    return o
truck = [cube('truck_chassis', (11.6, 2.5, 0.7), (4.6, 0, 1.35), camo),
         cube('truck_deck', (8.6, 2.6, 0.25), (3.4, 0, 1.85), camo),
         cube('truck_cab', (2.4, 2.55, 2.0), (9.3, 0, 2.6), camo, 0.12),
         cube('truck_cab_glass', (0.06, 2.2, 0.75), (10.52, 0, 3.05), glassc, 0),
         cube('truck_bumper', (0.3, 2.5, 0.35), (10.55, 0, 1.25), camo)]
for i, x in enumerate((-0.2, 1.4, 3.0, 6.0, 7.6, 9.2)):
    for s_ in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.62, depth=0.45, location=(x, s_ * 1.1, 0.62), rotation=(math.pi / 2, 0, 0))
        wh = bpy.context.active_object; wh.name = f'truck_wheel_{i}{s_}'; assign_material(wh, tyre); truck.append(wh)

# erector pivot at the rear; canisters (and the missile inside the middle one) lie forward over the deck
rig = bpy.data.objects.new('erector', None); scene.collection.objects.link(rig); rig.location = (-0.45, 0, 2.92)
cans = [croot]
for k, dy in enumerate((-0.86, 0.86)):
    cp = bpy.data.objects.new(f'canister_root_{k}', None); scene.collection.objects.link(cp); cp.location = croot.location
    bpy.context.view_layer.update()
    for n in CANISTER_PARTS:
        src = P[n]; d = src.copy(); scene.collection.objects.link(d)
        d.parent = cp; d.matrix_parent_inverse = src.matrix_parent_inverse.copy()
    cp.location.y += dy; cans.append(cp)
for o in cans + [mroot]:
    o.location.z += 2.92
bpy.context.view_layer.update()
for o in cans + [mroot]:
    o.parent = rig; o.matrix_parent_inverse = rig.matrix_world.inverted()
fRaise0, fRaise1 = F(86.3), F(88.9)
for f, a in [(1, 0), (fRaise0, 0), (fRaise1, -90)]:
    rig.rotation_euler.y = math.radians(a); key(rig, 'rotation_euler', f, index=1)
for fc in fcurves_of(rig): ease(fc, 'smooth')

# the middle canister goes glass on "canister" so the missile shows inside it
cmat = bpy.data.materials['canister_camo'].copy(); cmat.name = 'canister_xray'
assign_material(P['canister_tube'], cmat)
cn = cmat.node_tree; cb = cn.nodes['Principled BSDF']; co = cn.nodes['Material Output']
tr = cn.nodes.new('ShaderNodeBsdfTransparent'); cmix = cn.nodes.new('ShaderNodeMixShader')
cn.links.new(cb.outputs[0], cmix.inputs[1]); cn.links.new(tr.outputs[0], cmix.inputs[2]); cn.links.new(cmix.outputs[0], co.inputs['Surface'])
for f, v in [(1, 0), (F(80.9), 0), (F(81.5), 0.85), (F(83.8), 0.85), (F(84.4), 0)]:
    cmix.inputs[0].default_value = v; cmix.inputs[0].keyframe_insert('default_value', frame=f)

# ---------- launch: the cap blows, the missile climbs out along the (vertical) canister axis
cap = P['canister_cap_front']; fCap = F(90.45); c0 = cap.location.copy()
for f, dl, rot in [(1, Vector((0, 0, 0)), 0), (fCap, Vector((0, 0, 0)), 0), (fCap + 30, Vector((6, 3, -9)), 380)]:
    cap.location = c0 + dl; key(cap, 'location', f); cap.rotation_euler.y = math.radians(rot); key(cap, 'rotation_euler', f, index=1)
for fc in fcurves_of(cap): ease(fc, 'smooth')
m0 = mroot.location.copy()
for f, dx in [(1, 0), (F(90.6), 0), (F(92.0), 3.0), (fArc - 1, 36.0)]:
    mroot.location = m0 + Vector((dx, 0, 0)); key(mroot, 'location', f)
for fc in fcurves_of(mroot): ease(fc, 'smooth')

# bake the ride on the erector into world keys, then hand over to the free-flight path (no re-parenting mid-shot)
mats = {}
for f in range(1, fArc):
    scene.frame_set(f); mats[f] = mroot.matrix_world.copy()
mroot.animation_data_clear(); mroot.parent = None; mroot['allow_linear'] = True
from mathutils import Euler
prev = Euler((0, 0, 0))
for f, m in mats.items():                       # Euler kept compatible with the last frame: no flip at pitch -90
    prev = m.to_euler('XYZ', prev)
    mroot.location = m.to_translation(); mroot.rotation_euler = prev
    mroot.keyframe_insert('location', frame=f); mroot.keyframe_insert('rotation_euler', frame=f)
top = mats[fArc - 1].to_translation(); pitch0 = math.degrees(prev.y)
result['bake_end_euler'] = [round(math.degrees(a), 1) for a in prev]
path = [(fArc, top + Vector((0.3, 0, 1.2)), pitch0), (F(100.5), top + Vector((26, 0, 20)), -52.0),
        (F(103.0), top + Vector((90, 0, 30)), -6.0), (fSep, top + Vector((150, 0, 31)), 0.0),
        (END, top + Vector((150 + 40 * (END - fSep) / FPS, 0, 31)), 0.0)]
for f, loc, pitch in path:
    mroot.location = loc; mroot.rotation_euler = (0, math.radians(pitch), 0)
    mroot.keyframe_insert('location', frame=f); mroot.keyframe_insert('rotation_euler', frame=f)
for fc in fcurves_of(mroot):
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR' if kp.co.x < fArc else 'BEZIER'
    for i in range(len(fc.keyframe_points) - 1):
        if fc.keyframe_points[i].co.x >= fArc: ease_segment(fc, i, 0.3, 0.3)

# ---------- booster: flame + smoke while it burns; x-ray on "Diwali"; separation: slides out backwards and tumbles
def volume_mat(name, color, strength, density=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; t = m.node_tree; t.nodes.clear()
    out = t.nodes.new('ShaderNodeOutputMaterial'); pv = t.nodes.new('ShaderNodeVolumePrincipled')
    tc_ = t.nodes.new('ShaderNodeTexCoord'); gr = t.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    pw = t.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0
    mul = t.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength
    t.links.new(tc_.outputs['Object'], gr.inputs['Vector']); t.links.new(gr.outputs['Fac'], pw.inputs[0])
    t.links.new(pw.outputs[0], mul.inputs[0]); t.links.new(mul.outputs[0], pv.inputs['Emission Strength'])
    pv.inputs['Emission Color'].default_value = (*color, 1); pv.inputs['Density'].default_value = 0.0
    if density:
        nz = t.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0
        dm = t.nodes.new('ShaderNodeMath'); dm.operation = 'MULTIPLY'; dm.inputs[1].default_value = density
        dm2 = t.nodes.new('ShaderNodeMath'); dm2.operation = 'MULTIPLY'
        t.links.new(tc_.outputs['Object'], nz.inputs['Vector'])
        t.links.new(pw.outputs[0], dm.inputs[0]); t.links.new(dm.outputs[0], dm2.inputs[0]); t.links.new(nz.outputs['Fac'], dm2.inputs[1])
        t.links.new(dm2.outputs[0], pv.inputs['Density']); pv.inputs['Color'].default_value = (0.45, 0.42, 0.42, 1)
    t.links.new(pv.outputs[0], out.inputs['Volume'])
    return m
B = M['booster']
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0); flame = bpy.context.active_object; flame.name = 'booster_flame'
assign_material(flame, volume_mat('flame_vol', (1.0, 0.45, 0.08), 90.0))
flame.parent = B; flame.matrix_parent_inverse = Matrix.Identity(4)
bl, bh = bounds_world([B]); flame.location = B.matrix_world.inverted() @ Vector((bl.x - 1.2, 0, 0)); flame.scale = (1.7, 0.4, 0.4)
fl = bpy.data.objects.new('flame_light', bpy.data.lights.new('flame_light', 'POINT')); scene.collection.objects.link(fl)
fl.parent = B; fl.location = B.matrix_world.inverted() @ Vector((bl.x - 2.0, 0, 0)); fl.data.color = (1.0, 0.5, 0.15)
fl.data.shadow_soft_size = 1.0
fIgn = F(90.5)
for f, on in [(1, False), (fIgn, True), (fSep + 18, False)]:
    flame.hide_render = not on; flame.keyframe_insert('hide_render', frame=f)
for f, en in [(1, 0), (fIgn - 1, 0), (fIgn, 150000), (fSep + 17, 150000), (fSep + 18, 0)]:
    fl.data.energy = en; fl.data.keyframe_insert('energy', frame=f)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0); smoke = bpy.context.active_object; smoke.name = 'launch_smoke'
assign_material(smoke, volume_mat('smoke_vol', (1.0, 0.45, 0.1), 2.0, density=1.4))
smoke.location = (-0.45, 0, 2.92 + 9.4)
for f, s_ in [(1, 0.01), (fIgn, 0.01), (fIgn + 25, 4.5), (fArc, 10.0)]:
    smoke.scale = (s_, s_, s_ * 1.4); key(smoke, 'scale', f)
for fc in fcurves_of(smoke): ease(fc, 'smooth')

alu = bpy.data.materials['alu_brushed']; an = alu.node_tree; pb = an.nodes['Principled BSDF']; outm = an.nodes['Material Output']
gl = an.nodes.new('ShaderNodeBsdfTransparent'); mx = an.nodes.new('ShaderNodeMixShader')
an.links.new(pb.outputs[0], mx.inputs[1]); an.links.new(gl.outputs[0], mx.inputs[2]); an.links.new(mx.outputs[0], outm.inputs['Surface'])
fDi = F(93.92)
for f, v in [(1, 0), (fDi - 8, 0), (fDi, 0.88), (F(97.3), 0.88), (F(97.9), 0)]:
    mx.inputs[0].default_value = v; mx.inputs[0].keyframe_insert('default_value', frame=f)
bw = bpy.data.materials['booster_white'].node_tree.nodes['Principled BSDF']; bw.inputs['Emission Color'].default_value = (1.0, 0.42, 0.05, 1)
for f, v in [(1, 0), (fDi - 8, 0), (fDi, 3.0), (F(97.3), 3.0), (F(97.9), 0)]:
    bw.inputs['Emission Strength'].default_value = v; bw.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

# separation (slow motion feel: the missile's speed is held low on screen): booster slides out and tumbles back and down
fSepGo = F(105.6)
for o in (B, M['booster_band']):
    b0 = o.location.copy(); r0 = o.rotation_euler.copy()
    for f, dl, rot in [(1, (0, 0, 0), 0), (fSepGo, (0, 0, 0), 0), (fSepGo + 45, (-6.0, 0, -0.8), 18), (END, (-26.0, 0.5, -9.0), 140)]:
        o.location = b0 + Vector(dl); key(o, 'location', f)
        o.rotation_euler = (r0.x, r0.y + math.radians(rot), r0.z); key(o, 'rotation_euler', f)
    for fc in fcurves_of(o): ease(fc, 'smooth')
# the ramjet lights once the booster is out: an orange exhaust at the nozzle
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0); rj = bpy.context.active_object; rj.name = 'ramjet_flame'
assign_material(rj, volume_mat('ramjet_vol', (1.0, 0.35, 0.05), 60.0))
rj.parent = mroot; rj.matrix_parent_inverse = Matrix.Identity(4); rj.location = (-4.2 - 1.3, 0, 0); rj.scale = (1.5, 0.3, 0.3)
fRJ = fSepGo + 30
for f, on in [(1, False), (fRJ, True)]:
    rj.hide_render = not on; rj.keyframe_insert('hide_render', frame=f)
# shock cone at the nose on "supersonic": a faint fresnel cone
bpy.ops.mesh.primitive_cone_add(radius1=1.6, radius2=0.02, depth=3.2, vertices=64); sc = bpy.context.active_object
sc.name = 'shock_cone'; sc.parent = mroot; sc.matrix_parent_inverse = Matrix.Identity(4)
sc.location = (4.2 - 1.0, 0, 0); sc.rotation_euler = (0, math.radians(90), 0)
scm = bpy.data.materials.new('shock'); scm.use_nodes = True; st = scm.node_tree; st.nodes.clear()
so = st.nodes.new('ShaderNodeOutputMaterial'); fr = st.nodes.new('ShaderNodeLayerWeight'); fr.inputs['Blend'].default_value = 0.25
em = st.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.85, 0.95, 1.0, 1)
tp = st.nodes.new('ShaderNodeBsdfTransparent'); mxs = st.nodes.new('ShaderNodeMixShader')
emk = st.nodes.new('ShaderNodeMath'); emk.operation = 'MULTIPLY'; emk.inputs[1].default_value = 0.35
st.links.new(fr.outputs['Facing'], emk.inputs[0]); st.links.new(emk.outputs[0], mxs.inputs[0])
st.links.new(tp.outputs[0], mxs.inputs[1]); st.links.new(em.outputs[0], mxs.inputs[2]); st.links.new(mxs.outputs[0], so.inputs['Surface'])
em.inputs['Strength'].default_value = 1.5; assign_material(sc, scm)
fSS = F(103.09)
for f, on in [(1, False), (fSS - 4, True)]:
    sc.hide_render = not on; sc.keyframe_insert('hide_render', frame=f)

# ---------- cameras
for o in scene.objects:
    if o.type == 'LIGHT': o.visible_camera = False
camCan = cam_at('camCan', (9.5, -7.5, 4.6), (4.3, 0, 2.95), focal=40, fstop=5.6); camCan.data.shift_x = -0.12
camWide = cam_at('camWide', (6.0, -27.0, 5.0), (3.5, 0, 6.5), focal=32, fstop=11); camWide.data.shift_x = -0.12
camLaunch = cam_at('camLaunch', (10.0, -24.0, 1.4), (-0.45, 0, 15.0), focal=26, fstop=11); camLaunch.data.shift_x = -0.1
def follow(cam, target, offset):
    c = cam.constraints.new('COPY_LOCATION'); c.target = target; c.use_offset = True
    cam.location = Vector(offset); return c
camDi = cam_at('camDi', (0, -13.0, 0), (0, 0, 0), focal=40, fstop=8); camDi.data.shift_x = -0.1
camDi.rotation_euler = (math.radians(90), 0, 0); follow(camDi, mroot, (0.6, -13.0, -2.5))
camArc = cam_at('camArc', (top.x + 70, -170.0, top.z + 6), (top.x + 70, 0, top.z + 15), focal=55, fstop=16)
camArc.data.shift_x = -0.1
tt = camArc.constraints.new('TRACK_TO'); tt.target = mroot; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
camSep = cam_at('camSep', (0, -16.0, 0), (0, 0, 0), focal=40, fstop=8); camSep.data.shift_x = -0.14
camSep.rotation_euler = (math.radians(88), 0, 0); follow(camSep, mroot, (-3.5, -16.0, 0.8))
camWhy = cam_at('camWhy', (0, -14.0, 0), (0, 0, 0), focal=45, fstop=8); camWhy.data.shift_x = -0.16
camWhy.rotation_euler = (math.radians(88), 0, 0); follow(camWhy, B, (1.2, -14.0, 0.6))
shots = [(camCan, 1), (camWide, fWide), (camLaunch, fLaunch), (camDi, fDiCam), (camArc, fArc), (camSep, fSep), (camWhy, fWhy)]
for cam, f in shots: bind_camera(scene, cam, f)
scene.camera = camCan
def cam_for(f):
    cam = camCan
    for m in sorted(scene.timeline_markers, key=lambda m: m.frame):
        if m.frame <= f and m.camera: cam = m.camera
    return cam

# ---------- render
scene.render.engine = 'CYCLES'
try: gpu(scene)
except NameError: scene.cycles.device = 'GPU'
scene.cycles.samples = int(A.get('samples', 24)); scene.cycles.use_denoising = True
scene.cycles.volume_step_rate = 4.0
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = int(A.get('pct', 50))
scene.render.fps = FPS; scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.5
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'

from bpy_extras.object_utils import world_to_camera_view
gate = {}
for name, f, obj in [('canister', F(82.0), P['canister_tube']), ('raise', F(89.5), P['canister_tube']), ('launch', F(91.5), M['nose_cowl']),
                     ('diwali', F(94.5), B), ('arc', F(101.0), M['nose_cowl']), ('sep', F(107.0), B), ('why', F(116.4), B)]:
    scene.frame_set(f); cam = cam_for(f)
    p = world_to_camera_view(scene, cam, obj.matrix_world.translation if obj is not B else bounds_world([B])[0].lerp(bounds_world([B])[1], 0.5))
    gate[name] = dict(frame=f, cam=cam.name, x=round(p.x, 3), y=round(p.y, 3), ok=bool(0.02 < p.x < 0.98 and 0.02 < p.y < 0.98 and p.z > 0))
result['gate'] = gate
result['frames'] = dict(wide=fWide, launch=fLaunch, diwali_cam=fDiCam, arc=fArc, sep=fSep, why=fWhy, end=END)

if A.get('mode', 'preview') == 'preview':
    frames = A.get('frames') or [F(82.2), F(88.0), F(91.0), F(92.5), F(95.0), F(100.0), F(103.6), F(107.5), F(112.0), END - 5]
    for f in frames:
        scene.frame_set(f); scene.camera = cam_for(f)
        still_output(scene, os.path.join(out, f'ch3_{f:04d}.png')); bpy.ops.render.render(write_still=True)
    result['review'] = [f'ch3_{f:04d}.png' for f in frames]
else:
    video_output(scene, os.path.join(out, 'ch3_plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'ch3_plate.mp4'
