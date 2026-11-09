# head_anim_job.py - the animated anatomy plate (user reference 2026-11-07: x-ray head, signal going through the vessels, the
# brain pumping, coloured light). Runs after skilllib + temple_model + head_scene. args: duration_s, beats [seconds], colors,
# orbit_deg, name. Each BEAT: the device's light cone flashes in the beat's colour, the yellow temporal artery carries a lit
# segment up from the device, then the brain's arteries light in the same colour and the brain swells and tints (pumps).
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30
END = int(round(A.get('duration_s', 6.2) * FPS))
scene.frame_start, scene.frame_end = 1, END
parts, info, P = build_head_scene()
for o in bpy.data.objects:                       # chapter 4's light-in-skin visuals are not part of this scene
    if o.name == 'skin_layer' or o.name.startswith(('glow_', 'return_glow_')):
        o.hide_render = True
cer, cbl, stem, arteries, sta = parts['cerebrum'], parts['cerebellum'], parts['brainstem'], parts['arteries'], parts['sta']
stem.hide_render = True       # a bare stump looked like a stray block; the neck's own vessels carry the story
c = Vector(info['brain_c'])

# ---- stage ----
scene.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items} else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
scene.render.fps = FPS
hdri_world(color=(0.55, 0.62, 0.80), strength=0.6, background_strength=0.0)
scene.view_settings.view_transform = 'Standard'
for name, loc, energy in (('key', (0.55, -0.7, 0.5), 25), ('rim', (-0.6, 0.6, 0.4), 45)):
    L = bpy.data.lights.new(name, 'AREA'); L.energy, L.size = energy, 0.5
    o = bpy.data.objects.new(name, L); scene.collection.objects.link(o); o.location = Vector(loc)
    bpy.context.view_layer.update(); look_at(o, c)

# ---- the brain, its arteries and its swell: one rig at the brain centre ----
rig = bpy.data.objects.new('brain_rig', None); scene.collection.objects.link(rig); rig.location = c
bpy.context.view_layer.update()


def pulse_copy(src, name, color, strength=7.0, thick=1.9):
    cu = src.data.copy()
    cu.bevel_depth = src.data.bevel_depth * thick
    cu.bevel_factor_mapping_start = cu.bevel_factor_mapping_end = 'SPLINE'
    cu.bevel_factor_start, cu.bevel_factor_end = 0.0, 0.0
    ob = bpy.data.objects.new(name, cu); scene.collection.objects.link(ob)
    ob.matrix_world = src.matrix_world.copy()
    m = bpy.data.materials.new(name + ' Mat'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    cu.materials.append(m)
    return ob, b


art_pulse, art_b = pulse_copy(arteries, 'ArteryPulse', (1, 0.1, 0.05), strength=9.0, thick=2.4)
sta_pulse, sta_b = pulse_copy(sta, 'STAPulse', (1.0, 0.8, 0.1), strength=9.0, thick=2.2)
for br in [o for o in bpy.data.objects if o.name.startswith('TemporalBranch')]:   # the branches carry it too
    br.data.bevel_factor_mapping_start = br.data.bevel_factor_mapping_end = 'SPLINE'
bpy.context.view_layer.update()
for o in (cer, cbl, stem, arteries, art_pulse):
    o.parent = rig
    o.matrix_parent_inverse = rig.matrix_world.inverted()
brain_b = cer.data.materials[0].node_tree.nodes['Principled BSDF']
cone_em = bpy.data.materials['Light Cone'].node_tree.nodes['Emission']

COLORS = A.get('colors', [[1.0, 0.16, 0.10], [0.17, 0.83, 0.35], [0.23, 0.48, 1.0]])     # red, green, infrared (blue)
BEATS = A.get('beats', [0.9, 2.4, 3.9, 5.4])


def kf(sock_owner, path, frame, value, interp='BEZIER'):
    setattr(sock_owner, path, value) if isinstance(path, str) else None


def key_socket(sock, frame, value, interp=None):
    sock.default_value = value
    sock.keyframe_insert('default_value', frame=frame)
    if interp:
        for fc in sock.id_data.animation_data.action.fcurves if hasattr(sock.id_data.animation_data.action, 'fcurves') else []:
            pass


def key_prop(obj, path, frame, value):
    setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame)


def set_interp(owner, interp, prefixes=None):
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


for k, t in enumerate(BEATS):
    col = COLORS[k % len(COLORS)]
    f0 = int(round(t * FPS)) + 1
    if f0 + 40 > END + 30:
        continue
    # 1) the device's light cone flashes in this beat's colour
    cone_em.inputs['Color'].default_value = (*col, 1); cone_em.inputs['Color'].keyframe_insert('default_value', frame=f0 - 1)
    for fr, v in ((f0 - 3, 1.5), (f0 + 3, 14.0), (f0 + 20, 1.5)):
        key_socket(cone_em.inputs['Strength'], fr, v)
    # 2) a lit segment runs up the temporal artery from the device (yellow stays yellow: it is the vessel's own colour)
    for sp in [sta_pulse] + [o for o in bpy.data.objects if o.name.startswith('TemporalBranch')]:
        cu = sp.data
        key_prop(cu, 'bevel_factor_start', f0 - 1, 0.0); key_prop(cu, 'bevel_factor_end', f0 - 1, 0.0)
        key_prop(cu, 'bevel_factor_end', f0 + 14, 1.0); key_prop(cu, 'bevel_factor_start', f0 + 6, 0.0); key_prop(cu, 'bevel_factor_start', f0 + 20, 1.0)
    # 3) the brain's arteries light in the beat's colour, root to tip
    art_b.inputs['Emission Color'].default_value = (*col, 1); art_b.inputs['Emission Color'].keyframe_insert('default_value', frame=f0 + 9)
    art_b.inputs['Base Color'].default_value = (*col, 1); art_b.inputs['Base Color'].keyframe_insert('default_value', frame=f0 + 9)
    cu = art_pulse.data
    key_prop(cu, 'bevel_factor_start', f0 + 9, 0.0); key_prop(cu, 'bevel_factor_end', f0 + 9, 0.0)
    key_prop(cu, 'bevel_factor_end', f0 + 24, 1.0); key_prop(cu, 'bevel_factor_start', f0 + 16, 0.0); key_prop(cu, 'bevel_factor_start', f0 + 34, 1.0)
    # 4) the brain pumps: swell and tint as the pulse lands
    brain_b.inputs['Emission Color'].default_value = (*col, 1); brain_b.inputs['Emission Color'].keyframe_insert('default_value', frame=f0 + 12)
    for fr, v in ((f0 + 12, 0.0), (f0 + 20, 0.45), (f0 + 38, 0.0)):
        key_socket(brain_b.inputs['Emission Strength'], fr, v)
    for fr, v in ((f0 + 10, 1.0), (f0 + 19, 1.045), (f0 + 34, 1.0)):
        rig.scale = (v, v, v); rig.keyframe_insert('scale', frame=fr)
# colours step (constant), bevel runs are linear (a lit segment travels at a steady speed), the swell eases
color_socks = {cone_em.id_data: [cone_em.inputs['Color']], art_b.id_data: [art_b.inputs['Emission Color'], art_b.inputs['Base Color']],
               brain_b.id_data: [brain_b.inputs['Emission Color']]}
for tree, socks in color_socks.items():
    set_interp(tree, 'CONSTANT', [s.path_from_id() for s in socks])
for sp in [sta_pulse, art_pulse] + [o for o in bpy.data.objects if o.name.startswith('TemporalBranch')]:
    set_interp(sp.data, 'LINEAR')

# ---- camera: one slow orbit with the head's centre as the DOF target ----
tgt = Vector((0, 0.02, 0.02))
piv = bpy.data.objects.new('cam_piv', None); scene.collection.objects.link(piv); piv.location = tgt
cam = make_camera('Cam', focal=A.get('focal', 50), fstop=5.6, focus=piv)
cam.parent = piv
cam.location = Vector(A.get('cam_offset', (0.14, -0.66, 0.05)))
bpy.context.view_layer.update()
look_at_local(cam, piv)
scene.camera = cam
deg = A.get('orbit_deg', -12)
for f, d in ((1, 0), (END, deg)):
    piv.rotation_euler.z = math.radians(d)
    key(piv, 'rotation_euler', f, tuple(piv.rotation_euler), index=2)
for fc in fcurves_of(piv):
    for i in range(len(fc.keyframe_points) - 1):
        ease_segment(fc, i, 0.4, 0.4)
bind_camera(scene, cam, 1)

render_preset(scene, 'preview', res=(1920, 1080), fps=FPS)
scene.render.engine = scene.render.engine
fills = {}
os.makedirs(out, exist_ok=True)
review = sorted({1, int(BEATS[0] * FPS) + 10, int(BEATS[0] * FPS) + 20, int(BEATS[1] * FPS) + 18, END})
render_review(scene, out, review)
finish_plate(scene)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, A.get('name', 'head_anim') + '.blend'), copy=True)
result.update(frames=END, beats=BEATS, review=review)
