# Chapter 2 (Open it) plate, 34.02 s @ 30 fps, TRANSPARENT (the designed background lives in the overlay page).
# Runs after skilllib.py + brahmos_scene.py. Word cues (absolute s, cues_hinglish.json): 8 m 57.2, bus 62.1,
# seeker 66.82, guidance 69.02, warhead 72.08, ramjet 73.91, booster 77.29. Chapter starts at 45.877 s.
# S1 hero turn (map overlay on the left) | S2 bus beside it at true scale, skin to glass | S3 parts come out on their words.
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30; T0 = 45.877
def F(t): return int(round((t - T0) * FPS)) + 1
END = int(round(34.023 * FPS))
scene.frame_start, scene.frame_end = 1, END
f2, f3 = F(56.537), F(63.527)

P = brahmos_import(inputs['brahmos.glb'])
root = P['missile_root']
for n, o in P.items():
    if n.startswith('canister'):
        o.hide_render = True; o.hide_viewport = True
night_world(0.55)
scene.render.film_transparent = True

# ---------- a city bus, 10.5 m, pale ghost blue-grey (a scale reference, not a product)
busm = simple_material('bus_ghost', (0.42, 0.5, 0.6), roughness=0.55)
glassm = simple_material('bus_glass', (0.02, 0.03, 0.05), roughness=0.15)
wheelm = simple_material('bus_wheel', (0.02, 0.02, 0.022), roughness=0.7)
def cube(name, size, loc, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object
    o.name = name; o.scale = size; assign_material(o, mat)
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        m = o.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = 4
    return o
BUS_L, BUS_Y, BUS_Z0 = 10.5, 2.6, -1.55
bus = [cube('bus_body', (BUS_L, 2.5, 2.9), (4.2, BUS_Y, BUS_Z0 + 0.35 + 1.45), busm, 0.18),
       cube('bus_windows', (BUS_L - 1.6, 2.54, 0.95), (4.0, BUS_Y, BUS_Z0 + 2.2), glassm),
       cube('bus_windscreen', (0.06, 2.3, 1.3), (4.2 + BUS_L / 2 + 0.01, BUS_Y, BUS_Z0 + 2.05), glassm)]
for i, x in enumerate((4.2 - BUS_L / 2 + 2.2, 4.2 + BUS_L / 2 - 2.0)):
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.3, location=(x, BUS_Y + side * 1.15, BUS_Z0 + 0.5),
                                            rotation=(math.pi / 2, 0, 0))
        w = bpy.context.active_object; w.name = f'bus_wheel_{i}{side}'; assign_material(w, wheelm); bus.append(w)
fBus = F(57.0)                                            # the bus fades up as "8 metres" is said
for o in bus:
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    o.hide_render = False; o.keyframe_insert('hide_render', frame=fBus)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=f3)

# ---------- x-ray: aluminium skin mixes to glass at the end of S2, internals stay solid and get named
alu = bpy.data.materials['alu_brushed']; an = alu.node_tree
pb = an.nodes['Principled BSDF']; outm = an.nodes['Material Output']
glass = an.nodes.new('ShaderNodeBsdfPrincipled'); glass.inputs['Base Color'].default_value = (0.55, 0.75, 1.0, 1)
glass.inputs['Alpha'].default_value = 0.10; glass.inputs['Roughness'].default_value = 0.15
mixx = an.nodes.new('ShaderNodeMixShader')
an.links.new(pb.outputs[0], mixx.inputs[1]); an.links.new(glass.outputs[0], mixx.inputs[2])
an.links.new(mixx.outputs[0], outm.inputs['Surface'])
fG0, fG1 = F(62.6), F(63.4)
for f, v in [(1, 0.0), (fG0, 0.0), (fG1, 0.9)]:
    mixx.inputs[0].default_value = v; mixx.inputs[0].keyframe_insert('default_value', frame=f)

def glow(matname, color, f_on, strength=2.0):
    nb_ = bpy.data.materials[matname].node_tree.nodes['Principled BSDF']
    nb_.inputs['Emission Color'].default_value = (*color, 1)
    for f, v in [(1, 0.0), (f_on - 4, 0.0), (f_on + 6, strength)]:
        nb_.inputs['Emission Strength'].default_value = v
        nb_.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

def move(objs, f_word, offset, lead=0.6, dur=0.8):
    """parts travel before the word (Branch: settle 0.6 s before it is said) and hold"""
    f0 = max(1, int(round(f_word - (lead + dur) * FPS))); f1 = int(round(f_word - lead * FPS))
    for o in objs:
        base = o.location.copy()
        o.location = base; o.keyframe_insert('location', frame=f0)
        o.location = base + Vector(offset); o.keyframe_insert('location', frame=f1)
        for fc in fcurves_of(o):
            ease(fc, 'smooth')

CY = (0.0, 0.75, 1.0)
cues = {'seeker': F(66.82), 'guidance': F(69.02), 'warhead': F(72.08), 'ramjet': F(73.91), 'booster': F(77.29)}
move([P['intake_cone'], P['seeker']] + [P[f'intake_strut_{k}'] for k in (1, 2, 3)], cues['seeker'], (0.6, 0, 1.5))
glow('seeker_lime', LIME, cues['seeker'], 4.0); glow('titanium', LIME, cues['seeker'], 0.6)
move([P['guidance_unit']], cues['guidance'], (0, 0, 1.5)); glow('electronics', LIME, cues['guidance'], 1.6)
move([P['warhead']], cues['warhead'], (0, 0, 1.5)); glow('warhead_steel', BLAZE, cues['warhead'], 1.6)
move([P['air_duct'], P['fuel_tank'], P['combustor'], P['nozzle']], cues['ramjet'], (0, 0, -1.6))
for m_ in ('duct_steel', 'heat_steel', 'blued_steel'):
    glow(m_, CY, cues['ramjet'], 1.8)
glow('fuel_amber', (0.9, 0.5, 0.05), cues['ramjet'], 0.6)
move([P['booster'], P['booster_band']], cues['booster'], (-2.6, 0, 0))
glow('booster_white', BLAZE, cues['booster'], 0.9)

# ---------- lights, cameras (missile right of centre; words live in the left column)
c = Vector((4.2, 0, 0))
three_point(c, 4.2, camera=None, key_power=55.0 * 4.2 * 4.2)
for o in scene.objects:
    if o.type == 'LIGHT':
        o.visible_camera = False
cam1 = cam_at('cam_hero', (11.5, -10.5, 2.4), (4.6, 0, 0.0), focal=40, fstop=8)
cam1.data.shift_x = -0.14
piv = bpy.data.objects.new('hero_pivot', None); scene.collection.objects.link(piv); piv.location = c
bpy.context.view_layer.update()
cam1.parent = piv; cam1.matrix_parent_inverse = piv.matrix_world.inverted()
for f, d in [(1, 0.0), (f2 - 1, 12.0)]:                      # a slow 12 deg drift, no words move with it
    piv.rotation_euler.z = math.radians(d); key(piv, 'rotation_euler', f, index=2)
for fc in fcurves_of(piv): ease(fc, 'smooth')
cam2 = cam_at('cam_scale', (3.2, -19.5, 1.2), (3.6, 1.2, 0.1), focal=40, fstop=11)
cam2.data.shift_x = -0.12
cam3 = cam_at('cam_explode', (5.2, -15.0, 3.6), (3.9, 0, -0.05), focal=42, fstop=11)
cam3.data.shift_x = -0.15
for f, y in [(f3, -15.0), (END, -14.6)]:                       # <= 3 % drift over the whole explode
    cam3.location.y = y; key(cam3, 'location', f, index=1)
for cam, f in [(cam1, 1), (cam2, f2), (cam3, f3)]:
    bind_camera(scene, cam, f)
scene.camera = cam1
def cam_for(f):
    cam = cam1
    for m in sorted(scene.timeline_markers, key=lambda m: m.frame):
        if m.frame <= f and m.camera: cam = m.camera
    return cam

# ---------- render
scene.render.engine = 'CYCLES'
try: gpu(scene)
except NameError: scene.cycles.device = 'GPU'
scene.cycles.samples = int(A.get('samples', 24)); scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = int(A.get('pct', 50))
scene.render.fps = FPS; scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.5
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'

# gates: every named part inside the frame, and right of the 40 % text column, when it is named
from bpy_extras.object_utils import world_to_camera_view
gate = {}
for name, objs in [('seeker', [P['intake_cone']]), ('guidance', [P['guidance_unit']]), ('warhead', [P['warhead']]),
                   ('ramjet', [P['combustor'], P['air_duct']]), ('booster', [P['booster']])]:
    f = cues[name] + 15; scene.frame_set(f); cam = cam_for(f)
    xs, ys = [], []
    for o in objs + [P['nose_cowl'], P['skin_aft']]:
        for v in o.bound_box:
            p = world_to_camera_view(scene, cam, o.matrix_world @ Vector(v)); xs.append(p.x); ys.append(p.y)
    gate[name] = dict(frame=f, xmin=round(min(xs), 3), xmax=round(max(xs), 3), ymin=round(min(ys), 3), ymax=round(max(ys), 3),
                      ok=bool(min(xs) > 0.4 and max(xs) < 0.97 and min(ys) > 0.03 and max(ys) < 0.97))
scene.frame_set(F(60.0)); p_bus = [world_to_camera_view(scene, cam2, o.matrix_world @ Vector(v)).x for o in bus for v in o.bound_box]
gate['bus'] = dict(xmin=round(min(p_bus), 3), xmax=round(max(p_bus), 3))
result['gate'] = gate
result['cues'] = cues; result['frames'] = dict(S2=f2, S3=f3, end=END)

if A.get('mode', 'preview') == 'preview':
    frames = A.get('frames') or [20, f2 - 20, F(60.0), F(63.6), cues['seeker'] + 10, cues['guidance'] + 10,
                                  cues['warhead'] + 10, cues['ramjet'] + 10, cues['booster'] + 10, END - 5]
    for f in frames:
        scene.frame_set(f); scene.camera = cam_for(f)
        still_output(scene, os.path.join(out, f'ch2_{f:04d}.png'))
        scene.render.image_settings.color_mode = 'RGBA'
        bpy.ops.render.render(write_still=True)
    result['review'] = [f'ch2_{f:04d}.png' for f in frames]
else:
    im = scene.render.image_settings
    if hasattr(im, 'media_type'): im.media_type = 'VIDEO'
    im.file_format = 'FFMPEG'; im.color_mode = 'RGBA'
    ff = scene.render.ffmpeg; ff.format = 'WEBM'; ff.codec = 'WEBM'; ff.constant_rate_factor = 'HIGH'
    scene.render.filepath = os.path.join(out, 'ch2_plate.webm')
    bpy.ops.render.render(animation=True)
    result['plate'] = 'ch2_plate.webm'
