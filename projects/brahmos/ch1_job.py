# Chapter 1 (Hook) plate, 45.88 s @ 30 fps. Runs after skilllib.py + brahmos_scene.py in one file.
# Cuts on the Hinglish word timings (cues_hinglish.json): blip 13.97, Brahmos 28.11, Mach 33.82, no turbine 42.27.
# A wide night sea + warship radar | B chase cam over the waves | C missile rips past | C2 side profile | D x-ray in the void.
# args: mode 'preview' (gate stills) or 'final' (the animation); pct, samples.
import os, math, bmesh
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30
def F(t): return int(round(t * FPS)) + 1
END = F(45.88) - 1
scene.frame_start, scene.frame_end = 1, END
fB, fC, fC2, fD = F(13.97), F(27.0), F(29.0), F(35.5)
fX0, fX1 = F(42.0), F(42.9)                              # x-ray ramp, on "no turbine" (42.27)

P = brahmos_import(inputs['brahmos.glb'])
root = P['missile_root']
for n, o in P.items():                                   # the canister is not in this chapter
    if n.startswith('canister'):
        o.hide_render = True; o.hide_viewport = True
MZ = 10.0                                                # flight height above the sea, m

# ---------- world: night gradient + faint stars (camera); weak studio HDRI light for the metal
w = bpy.data.worlds.new('night'); scene.world = w; w.use_nodes = True
nt = w.node_tree; nt.nodes.clear()
outw = nt.nodes.new('ShaderNodeOutputWorld')
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 0.0, (0.020, 0.040, 0.058, 1)    # horizon, a lighter night blue
cr.elements[1].position, cr.elements[1].color = 0.35, (*NIGHT, 1)                  # zenith = palette dark
vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 900
star = nt.nodes.new('ShaderNodeMath'); star.operation = 'LESS_THAN'; star.inputs[1].default_value = 0.012
starc = nt.nodes.new('ShaderNodeMath'); starc.operation = 'MULTIPLY'; starc.inputs[1].default_value = 0.35
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'ADD'
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 1.0
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
nt.links.new(vor.outputs['Distance'], star.inputs[0]); nt.links.new(star.outputs[0], starc.inputs[0])
nt.links.new(ramp.outputs['Color'], mix.inputs[6]); nt.links.new(starc.outputs[0], mix.inputs['Factor'])
mix.inputs[7].default_value = (0.8, 0.85, 1.0, 1)
nt.links.new(mix.outputs[2], bg.inputs['Color']); nt.links.new(bg.outputs[0], outw.inputs['Surface'])

# ---------- moon (visible disc) + moonlight
moon_dir = Vector((0.36, 0.93, 0.11)).normalized()   # behind the ship from camA
bpy.ops.mesh.primitive_uv_sphere_add(radius=32, location=moon_dir * 2600)
moon = bpy.context.active_object; moon.name = 'moon'
assign_material(moon, simple_material('moon_mat', (0.9, 0.92, 1.0)))
mm = moon.active_material.node_tree.nodes['Principled BSDF']
mm.inputs['Emission Color'].default_value = (0.85, 0.9, 1.0, 1); mm.inputs['Emission Strength'].default_value = 8.0
sun = bpy.data.objects.new('moonlight', bpy.data.lights.new('moonlight', 'SUN'))
scene.collection.objects.link(sun); sun.data.energy = 0.35; sun.data.color = (0.72, 0.8, 1.0); sun.data.angle = 0.01
sun.rotation_euler = (-moon_dir).to_track_quat('-Z', 'Y').to_euler()

# ---------- sea: displaced grid near the action + a flat far sea; both read waves through one moving empty
waves = bpy.data.objects.new('wave_origin', None); scene.collection.objects.link(waves)
waves['allow_linear'] = True
water = bpy.data.materials.new('sea'); water.use_nodes = True
wn = water.node_tree; wb = wn.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.004, 0.009, 0.014, 1); wb.inputs['Roughness'].default_value = 0.07
wtc = wn.nodes.new('ShaderNodeTexCoord'); wtc.object = waves
wnz = wn.nodes.new('ShaderNodeTexNoise'); wnz.inputs['Scale'].default_value = 0.35; wnz.inputs['Detail'].default_value = 6
bump = wn.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35
wn.links.new(wtc.outputs['Object'], wnz.inputs['Vector']); wn.links.new(wnz.outputs['Fac'], bump.inputs['Height'])
wn.links.new(bump.outputs['Normal'], wb.inputs['Normal'])
bpy.ops.mesh.primitive_grid_add(x_subdivisions=760, y_subdivisions=760, size=1500, location=(100, 500, 0))
sea = bpy.context.active_object; sea.name = 'sea_near'
tex = bpy.data.textures.new('swell', 'CLOUDS'); tex.noise_scale = 7.0; tex.noise_depth = 2
dm = sea.modifiers.new('swell', 'DISPLACE'); dm.texture = tex; dm.strength = 1.1; dm.mid_level = 0.5
dm.texture_coords = 'OBJECT'; dm.texture_coords_object = waves
for p in sea.data.polygons: p.use_smooth = True
assign_material(sea, water)
bpy.ops.mesh.primitive_plane_add(size=12000, location=(0, 0, -0.6))
far = bpy.context.active_object; far.name = 'sea_far'; assign_material(far, water)

# ---------- warship: the user's model (battleshipwarship.glb, "battleship/warship" by Lin, Sketchfab, CC-BY-4.0: credit it)
SHIP_LEN = float(A.get('ship_len', 150.0))
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=inputs['warship.glb'])
new = [o for o in bpy.data.objects if o not in before]
ship_meshes = [o for o in new if o.type == 'MESH']
ship_norm = bpy.data.objects.new('ship_norm', None); scene.collection.objects.link(ship_norm)
for o in new:
    if o.parent is None:
        o.parent = ship_norm
bpy.context.view_layer.update()
lo, hi = bounds_world(ship_meshes); size = hi - lo
if size.y > size.x:                                           # long axis onto X
    ship_norm.rotation_euler.z = math.radians(90)
    bpy.context.view_layer.update(); lo, hi = bounds_world(ship_meshes); size = hi - lo
if A.get('ship_flip'):                                        # bow toward +X
    ship_norm.rotation_euler.z += math.pi
s_ = SHIP_LEN / size.x
ship_norm.scale = (s_, s_, s_)
bpy.context.view_layer.update(); lo, hi = bounds_world(ship_meshes)
draft = float(A.get('ship_draft', 0.06)) * (hi.z - lo.z)       # keel this far below the waterline
ship_norm.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z + draft))
bpy.context.view_layer.update(); lo, hi = bounds_world(ship_meshes)
result['ship'] = dict(parts=len(ship_meshes), length=round(hi.x - lo.x, 1), beam=round(hi.y - lo.y, 1),
                      height=round(hi.z - lo.z, 1), keel=round(lo.z, 1), top=round(hi.z, 1))
navm = bpy.data.materials.new('navlight'); navm.use_nodes = True
nb = navm.node_tree.nodes['Principled BSDF']; nb.inputs['Emission Color'].default_value = (1.0, 0.2, 0.1, 1)
nb.inputs['Emission Strength'].default_value = 40
top_obj = max(ship_meshes, key=lambda o: bounds_world([o])[1].z)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, hi.z + 0.8)); nav = bpy.context.active_object
nav.name = 'ship_navlight'; assign_material(nav, navm)
ship_root = bpy.data.objects.new('ship_root', None); scene.collection.objects.link(ship_root)
for o in (ship_norm, nav):
    o.parent = ship_root
ship_root.location = (-40, 340, 0); ship_root.rotation_euler.z = math.radians(12)
parts_ship = ship_meshes; radar = ship_norm                  # names kept for the hide keys below
for o in ship_meshes:                                         # the sea must not show through: no shadow catching, solid
    o.visible_shadow = True

# ---------- missile placement and motion (root at the missile's mid-length)
root['allow_linear'] = True
def place(f, loc, interp='CONSTANT'):
    root.location = loc; key(root, 'location', f)
place(1, (4.2, 0, MZ))                                     # static in A/B (the sea slides past it in B)
place(fC - 1, (4.2, 0, MZ))
place(fC, (-4.0, 0, MZ - 1.5))                            # C: the pass, left -> right past a still camera
place(fC2 - 1, (62.0, 0, MZ - 1.5))
place(fC2, (4.2, 0, MZ))                                   # C2 and D: static again
for fc in fcurves_of(root):
    for i, kp in enumerate(fc.keyframe_points):
        kp.interpolation = 'LINEAR' if abs(kp.co.x - fC) < 0.5 else 'CONSTANT'
# hide the missile in A (only the blip on the HUD exists then)
for o in [o for n, o in P.items() if not n.endswith('_root') and not n.startswith('canister')]:
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    o.hide_render = False; o.keyframe_insert('hide_render', frame=fB)
# the sea slides backwards under the missile in B and C2 (120 m/s on screen), still in A and C; D hides it
def wave_x(f, x):
    waves.location.x = x; key(waves, 'location', f, index=0)
wave_x(1, 0); wave_x(fB, 0); wave_x(fC - 1, -120 * (fC - fB) / FPS); wave_x(fC2, -120 * (fC - fB) / FPS)
wave_x(fD, -120 * (fD - fB + fC - fC2) / FPS)
for fc in fcurves_of(waves):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
for o in [sea, far, moon]:
    o.hide_render = False; o.keyframe_insert('hide_render', frame=1)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=fD)
for o in parts_ship + [nav]:
    o.hide_render = False; o.keyframe_insert('hide_render', frame=1)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=fC2)

# exhaust glow: an orange point light behind the tail (lights the spray and the water in B/C/C2)
glow = bpy.data.objects.new('exhaust_glow', bpy.data.lights.new('exhaust_glow', 'POINT'))
scene.collection.objects.link(glow); glow.data.color = (1.0, 0.45, 0.12); glow.data.shadow_soft_size = 0.4
glow.parent = root; glow.location = (-6.5, 0, 0); glow.data.shadow_soft_size = 1.5
for f, e in [(1, 0), (fB, 260), (fD - 1, 260), (fD, 0)]:
    glow.data.energy = e; glow.data.keyframe_insert('energy', frame=f)

# ---------- studio lights for D (off before), a cool rim for the night shots
c = Vector((4.2, 0, MZ))
key_l, fill, rim = three_point(c, 4.2, camera=None, key_power=55.0 * 4.2 * 4.2)
for L_, e in ((key_l, key_l.data.energy), (fill, fill.data.energy), (rim, rim.data.energy)):
    for f, v in [(1, 0), (fD - 1, 0), (fD, e)]:
        L_.data.energy = v; L_.data.keyframe_insert('energy', frame=f)
nrim = area_light('night_rim', (4.2, 9, MZ + 7), c, 1600, 6.0, (0.6, 0.72, 1.0))
for f, v in [(1, 0), (fB, 1600), (fD - 1, 1600), (fD, 0)]:
    nrim.data.energy = v; nrim.data.keyframe_insert('energy', frame=f)

# ---------- x-ray: every aluminium surface mixes to a glassy ghost on "no turbine"
alu = bpy.data.materials['alu_brushed']; an = alu.node_tree
pb = an.nodes['Principled BSDF']; outm = an.nodes['Material Output']
glass = an.nodes.new('ShaderNodeBsdfPrincipled'); glass.inputs['Base Color'].default_value = (0.55, 0.75, 1.0, 1)
glass.inputs['Alpha'].default_value = 0.12; glass.inputs['Roughness'].default_value = 0.15
mixx = an.nodes.new('ShaderNodeMixShader'); mixx.name = 'xray'
an.links.new(pb.outputs[0], mixx.inputs[1]); an.links.new(glass.outputs[0], mixx.inputs[2])
an.links.new(mixx.outputs[0], outm.inputs['Surface'])
for f, v in [(1, 0.0), (fX0, 0.0), (fX1, 0.92)]:
    mixx.inputs[0].default_value = v; mixx.inputs[0].keyframe_insert('default_value', frame=f)
try:
    alu.surface_render_method = 'BLENDED'
except Exception:
    pass
def ghost(matname, alpha=0.08):
    m = bpy.data.materials[matname]; t = m.node_tree
    b0 = t.nodes['Principled BSDF']; o0 = t.nodes['Material Output']
    g = t.nodes.new('ShaderNodeBsdfTransparent'); mx = t.nodes.new('ShaderNodeMixShader')
    t.links.new(b0.outputs[0], mx.inputs[1]); t.links.new(g.outputs[0], mx.inputs[2])
    t.links.new(mx.outputs[0], o0.inputs['Surface'])
    for f, v in [(1, 0.0), (fX0, 0.0), (fX1, 1 - alpha)]:
        mx.inputs[0].default_value = v; mx.inputs[0].keyframe_insert('default_value', frame=f)
for mname in ('fuel_amber', 'electronics', 'warhead_steel', 'booster_white', 'booster_band', 'seeker_lime', 'titanium'):
    ghost(mname)
for mname in ('duct_steel', 'heat_steel', 'blued_steel'):   # the empty pipe, intake to nozzle, glows cyan
    nb_ = bpy.data.materials[mname].node_tree.nodes['Principled BSDF']
    nb_.inputs['Emission Color'].default_value = (0.0, 0.75, 1.0, 1)
    for f, v in [(1, 0.0), (fX0, 0.0), (fX1 + 6, 2.2)]:
        nb_.inputs['Emission Strength'].default_value = v
        nb_.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

# ---------- cameras (one per shot), missile right of centre where words sit on the left
camA = cam_at('camA', (-190, -60, 7.5), (-40, 340, 14), focal=50, fstop=16)
camA.data.shift_x = -0.12
dolly_keys = [(1, camA.location.copy()), (fB - 1, camA.location.copy() + (Vector((-40, 340, 14)) - camA.location) * 0.06)]
for f, l in dolly_keys:
    camA.location = l; key(camA, 'location', f)
camB = cam_at('camB', (-7.5, -5.0, MZ + 1.6), (6.0, 0, MZ + 0.2), focal=30, fstop=5.6)
for f, d in [(fB, 0.0), (fC - 1, 1.2)]:                     # a slow drift in, the sea is the motion
    camB.location.y = -5.0 + d * 0.6; key(camB, 'location', f, index=1)
camC = cam_at('camC', (26, -9.5, MZ - 2.6), (27, 0, MZ - 0.8), focal=22, fstop=8)
camC2 = cam_at('camC2', (5.6, -15.5, MZ + 1.0), (4.6, 0, MZ), focal=45, fstop=8)
camC2.data.shift_x = -0.16
camD = cam_at('camD', (4.4, -17.0, MZ + 0.6), (4.4, 0, MZ), focal=45, fstop=11)
camD.data.shift_x = -0.1
for f, y in [(fD, -17.0), (END, -16.3)]:
    camD.location.y = y; key(camD, 'location', f, index=1)
for cam, f in [(camA, 1), (camB, fB), (camC, fC), (camC2, fC2), (camD, fD)]:
    bind_camera(scene, cam, f)
scene.camera = camA
for cam in (camA, camB, camD):
    for fc in fcurves_of(cam):
        ease_segment(fc, 0, 0.3, 0.3) if len(fc.keyframe_points) > 1 else None

for o in scene.objects:                                    # lights never show up as shapes in frame
    if o.type == 'LIGHT':
        o.visible_camera = False
# ---------- render settings
scene.render.engine = 'CYCLES'
try: gpu(scene)
except NameError: scene.cycles.device = 'GPU'
scene.cycles.samples = int(A.get('samples', 24)); scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = int(A.get('pct', 50))
scene.render.fps = FPS; scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.5
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = 0.0

# ---------- gates: missile on screen (and right of centre) where it must be
from bpy_extras.object_utils import world_to_camera_view
def cam_for(f):
    cam = camA
    for m in sorted(scene.timeline_markers, key=lambda m: m.frame):
        if m.frame <= f and m.camera: cam = m.camera
    return cam
gate = {}
for name, f in [('B', fB + 60), ('C_pass', fC + 30), ('C2', fC2 + 60), ('D', fD + 60), ('D_xray', fX1 + 10)]:
    scene.frame_set(f); cam = cam_for(f)
    p = world_to_camera_view(scene, cam, root.matrix_world.translation)
    gate[name] = dict(frame=f, cam=cam.name, x=round(p.x, 3), y=round(p.y, 3), in_frame=bool(0 < p.x < 1 and 0 < p.y < 1 and p.z > 0))
result['gate'] = gate
result['frames'] = dict(B=fB, C=fC, C2=fC2, D=fD, xray=[fX0, fX1], end=END)

if A.get('mode', 'preview') == 'preview':
    frames = A.get('frames') or [40, fB - 30, fB + 90, fC - 30, fC + 22, fC + 34, fC2 + 90, fD + 40, fX0 - 10, END - 10]
    for f in frames:
        scene.frame_set(f); scene.camera = cam_for(f)
        still_output(scene, os.path.join(out, f'ch1_{f:04d}.png'))
        bpy.ops.render.render(write_still=True)
    scene.frame_set(40)
    chk = cam_at('cam_shipcheck', (-40 + 30, 340 - 230, 12), (-40, 340, 12), focal=50, fstop=16)
    scene.camera = chk; ev = scene.view_settings.exposure; scene.view_settings.exposure = 2.5
    still_output(scene, os.path.join(out, 'ship_check.png')); bpy.ops.render.render(write_still=True)
    scene.view_settings.exposure = ev
    result['review'] = [f'ch1_{f:04d}.png' for f in frames]
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'ch1.blend'), copy=True)
else:
    video_output(scene, os.path.join(out, 'ch1_plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'ch1_plate.mp4'
