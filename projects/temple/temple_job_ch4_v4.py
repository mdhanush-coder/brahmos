# ===== easing_presets.py =====
"""Easing presets and F-curve utilities (bpy, Blender 4.4-5.x layered actions and legacy actions).

From the reference notes:
  - A-video: easing = handle length; S X on the handles; "transition" = one handle ~full, the other ~0;
    whip camera switch cuts at peak velocity.
  - B-video: Bezier + FREE handles; copy easing between shots; remove the velocity "bump" at middle keys.

Handle fractions are a share of the gap between two keys. Flat handles (same value as the key) mean
zero velocity at that key (an ease). A 0 fraction means the key is hit at full speed (cut point).
"""
import bpy

# (out_frac at the segment's first key, in_frac at its last key)
PRESETS = {
    'smooth':          (0.40, 0.40),   # default product move
    'super_smooth':    (0.60, 0.60),   # EaseIt "Super Smooth" look - long, luxurious
    'ease_in':         (0.70, 0.15),   # slow start, quicker arrival (A-video "Ease In")
    'ease_out':        (0.15, 0.70),   # quick start, long settle (A-video "Ease Out")
    'ease_in_out':     (0.50, 0.50),
    'transition_out':  (0.90, 0.00),   # leave slowly, hit the cut at full speed
    'transition_in':   (0.00, 0.90),   # arrive from the cut at full speed, settle long
    'snappy':          (0.20, 0.80),   # UI-like pop that settles
}
DYNAMIC = {  # Blender's built-in dynamic easing (Graph Editor T menu) for character
    'overshoot': ('BACK', 'EASE_OUT'),
    'bounce':    ('BOUNCE', 'EASE_OUT'),
    'elastic':   ('ELASTIC', 'EASE_OUT'),
}


def fcurves_of(idblock):
    """All F-curves animating an ID (object, shape-key datablock, ...), layered or legacy actions."""
    ad = getattr(idblock, 'animation_data', None)
    if not ad or not ad.action:
        return []
    act = ad.action
    out = []
    layers = getattr(act, 'layers', None)
    if layers:
        slot = getattr(ad, 'action_slot', None)
        for layer in layers:
            for strip in layer.strips:
                try:
                    cb = strip.channelbag(slot) if slot else None
                except Exception:
                    cb = None
                if cb:
                    out.extend(cb.fcurves)
    if not out and hasattr(act, 'fcurves'):
        try:
            out = list(act.fcurves)
        except Exception:
            pass
    return out


def ease_segment(fc, i, out_frac, in_frac):
    """Shape the segment between keyframe i and i+1 with flat FREE handles."""
    pts = fc.keyframe_points
    a, b = pts[i], pts[i + 1]
    gap = b.co.x - a.co.x
    a.interpolation = 'BEZIER'
    a.handle_right_type = 'FREE'
    b.handle_left_type = 'FREE'
    a.handle_right = (a.co.x + out_frac * gap, a.co.y)
    b.handle_left = (b.co.x - in_frac * gap, b.co.y)


def ease(fc, preset='smooth', segments=None):
    """Apply a preset to every segment (or the given segment indices) of an F-curve."""
    pts = fc.keyframe_points
    if len(pts) < 2:
        return
    idx = range(len(pts) - 1) if segments is None else segments
    if preset == 'linear':
        for i in idx:
            pts[i].interpolation = 'LINEAR'
    elif preset in DYNAMIC:
        interp, mode = DYNAMIC[preset]
        for i in idx:
            pts[i].interpolation = interp
            pts[i].easing = mode
    else:
        o, n = PRESETS[preset]
        for i in idx:
            ease_segment(fc, i, o, n)
    fc.update()


def ease_object(idblock, preset='smooth', data_path=None):
    for fc in fcurves_of(idblock):
        if data_path is None or fc.data_path == data_path:
            ease(fc, preset)


def remove_bump(fc, key_index):
    """B-video fix: give a pass-through key one continuous slope (neighbour average), so velocity flows."""
    pts = fc.keyframe_points
    if not 0 < key_index < len(pts) - 1:
        return
    p, k, n = pts[key_index - 1], pts[key_index], pts[key_index + 1]
    slope = (n.co.y - p.co.y) / max(n.co.x - p.co.x, 1e-6)
    k.handle_left_type = k.handle_right_type = 'ALIGNED'
    dl, dr = (k.co.x - p.co.x) / 3, (n.co.x - k.co.x) / 3
    k.handle_left = (k.co.x - dl, k.co.y - slope * dl)
    k.handle_right = (k.co.x + dr, k.co.y + slope * dr)
    fc.update()


def copy_easing(src_fc, dst_fc):
    """Relative-Ease equivalent: copy handle fractions segment by segment (same key count)."""
    s, d = src_fc.keyframe_points, dst_fc.keyframe_points
    for i in range(min(len(s), len(d)) - 1):
        gap = max(s[i + 1].co.x - s[i].co.x, 1e-6)
        o = (s[i].handle_right.x - s[i].co.x) / gap
        n = (s[i + 1].co.x - s[i + 1].handle_left.x) / gap
        ease_segment(dst_fc, i, o, n)
    dst_fc.update()


def key(obj, path, frame, value=None, index=-1):
    """Set (optionally) and keyframe a property; returns nothing. Example: key(o, 'location', 30, (0,0,1))."""
    if value is not None:
        setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame, index=index)


def whip_transition(cam_a_owner, cam_b_owner, cut_frame, data_path='rotation_euler'):
    """A-video camera switch: owner A leaves on 'transition_out', owner B arrives on 'transition_in'.
    Owners are the animated objects (cameras or their pivot empties). Bind cameras at the cut with markers."""
    for fc in fcurves_of(cam_a_owner):
        if fc.data_path == data_path:
            ease(fc, 'transition_out', segments=[len(fc.keyframe_points) - 2])
    for fc in fcurves_of(cam_b_owner):
        if fc.data_path == data_path:
            ease(fc, 'transition_in', segments=[0])


def bind_camera(scene, cam, frame):
    """Ctrl+B in the timeline: a marker that switches the active camera at frame."""
    m = scene.timeline_markers.new(f'cam_{cam.name}', frame=int(frame))
    m.camera = cam
    return m


# ===== camera_orbit.py =====
"""Camera rigs: pivot-empty orbit (B-video), DOF, multi-shot sequence with the B-video rules card.
Needs easing_presets.py loaded first (key, ease, fcurves_of, remove_bump, bind_camera)."""
import bpy, math
from mathutils import Vector


def look_at(obj, target):
    d = Vector(target) - obj.matrix_world.translation
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def make_camera(name='Cam', focal=85.0, sensor=36.0, fstop=2.8, focus=None, clip=(0.01, 200.0)):
    cd = bpy.data.cameras.new(name)
    cd.lens, cd.sensor_width = focal, sensor
    cd.clip_start, cd.clip_end = clip
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    if focus is not None:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if isinstance(focus, bpy.types.Object):
            cd.dof.focus_object = focus
        else:
            cd.dof.focus_distance = float(focus)
    return cam


def make_orbit_rig(target=(0, 0, 0), distance=4.0, height=0.6, focal=85.0, name='shot1', fstop=4.0):
    """Empty at the target; camera parented to it and pointed at it. Rotate the EMPTY (Z) to orbit.
    Returns (empty, camera). Focal 85-100 mm for products (B-video: 90 mm), DOF focused on the pivot."""
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    piv = bpy.data.objects.new(f'{name} movement', None)
    piv.empty_display_type = 'PLAIN_AXES'
    piv.location = Vector(target)
    col.objects.link(piv)
    cam = make_camera(f'{name}_cam', focal=focal, fstop=fstop, focus=piv)
    bpy.context.scene.collection.objects.unlink(cam)
    col.objects.link(cam)
    cam.parent = piv
    cam.location = Vector((0, -distance, height))
    look_at_local(cam, piv)
    return piv, cam


def look_at_local(cam, piv):
    """Aim a parented camera at its pivot. Phase-5 bug: re-assigning a stale cam.matrix_world after setting
    rotation_euler silently erased the aim (camera looked straight down, render = empty backdrop).
    Set the rotation only, then update and ASSERT the direction."""
    bpy.context.view_layer.update()
    look_at(cam, piv.matrix_world.translation)
    bpy.context.view_layer.update()
    fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    to_t = (piv.matrix_world.translation - cam.matrix_world.translation).normalized()
    assert fwd.dot(to_t) > 0.99, f'camera not aimed at its pivot (dot={fwd.dot(to_t):.2f})'


def frame_distance(radius, focal, sensor=36.0, fill=0.7, aspect=16 / 9):
    """Distance at which an object of bounding radius fills `fill` of the frame height."""
    fov_v = 2 * math.atan((sensor / aspect) / (2 * focal))
    return radius / (fill * math.tan(fov_v / 2))


def frame_width_distance(width, focal, sensor=36.0, fill=0.85):
    """Camera distance at which a subject `width` m wide (horizontal explode) fills `fill` of the frame width."""
    return (width / 2) / (fill * sensor / (2 * focal))


def dolly(cam, keys, preset='smooth'):
    """Breathing push-in/pull-out. keys: [(frame, factor)] multiplying the camera's current local Y distance.
    Open close (0.5) so the assembled product reads, pull out to 1.0 as it explodes, return before re-assembly."""
    # Scale the whole local offset (y AND z): the camera must slide along its aim line to keep looking at the
    # pivot. Scaling y alone (Phase-5 v3) pushed the subject out of frame at the close-up ends.
    by, bz = cam.location.y, cam.location.z
    for f, k in keys:
        cam.location.y, cam.location.z = by * k, bz * k
        cam.keyframe_insert('location', frame=f)
    cam.location.y, cam.location.z = by, bz
    for fc in fcurves_of(cam):
        if fc.data_path == 'location':
            ease(fc, preset)


def orbit(piv, start, end, degrees, preset='smooth', axis=2):
    rot = list(piv.rotation_euler)
    key(piv, 'rotation_euler', start, tuple(rot), index=axis)
    rot[axis] += math.radians(degrees)
    key(piv, 'rotation_euler', end, tuple(rot), index=axis)
    for fc in fcurves_of(piv):
        if fc.data_path == 'rotation_euler' and fc.array_index == axis:
            ease(fc, preset)


def push_in(cam, start, end, dolly=0.5, preset='super_smooth'):
    """Entry reveal (B-video shot 1): camera starts pulled back by `dolly` m along its local Y offset."""
    end_loc = cam.location.copy()
    key(cam, 'location', end, tuple(end_loc))
    start_loc = end_loc.copy()
    start_loc.y -= dolly
    key(cam, 'location', start, tuple(start_loc))
    for fc in fcurves_of(cam):
        if fc.data_path == 'location':
            ease(fc, preset)


# B-video rules card (25 fps there; scale with fps)
RULES = dict(change_rotation=40.0, change_duration=20, change_start=40, shot_duration=50, drift=10.0)


def shot_sequence(scene, shots, rules=RULES):
    """shots: list of (pivot, camera). Builds: entry(-rot -> 0) / drift (+drift) / exit (+rot),
    transitions eased transition_in / transition_out, cameras bound at transition midpoints, bumps removed.
    Returns the last frame."""
    r = rules
    f = scene.frame_start
    for n, (piv, cam) in enumerate(shots):
        base = piv.rotation_euler.z
        keys = []
        if n > 0:  # entry from previous cut
            keys += [(f, base - math.radians(r['change_rotation'])), (f + r['change_duration'] // 2, base)]
        hold_start = keys[-1][0] if keys else f
        exit_start = hold_start + r['change_start']
        keys += [(exit_start, base + math.radians(r['drift']))]
        if n < len(shots) - 1:
            keys += [(exit_start + r['change_duration'] // 2, base + math.radians(r['drift'] + r['change_rotation']))]
        elif not any(k[0] == hold_start for k in keys):
            keys.insert(0, (hold_start, base))
        for fr, val in keys:
            piv.rotation_euler.z = val
            piv.keyframe_insert('rotation_euler', frame=fr, index=2)
        for fc in fcurves_of(piv):
            if fc.data_path == 'rotation_euler' and fc.array_index == 2:
                pts = fc.keyframe_points
                for i in range(len(pts) - 1):
                    ease_segment(fc, i, 0.45, 0.45)
                if n > 0:
                    ease_segment(fc, 0, 0.0, 0.9)               # arrive from the cut at speed
                if n < len(shots) - 1:
                    ease_segment(fc, len(pts) - 2, 0.9, 0.0)    # leave into the cut at speed
                for i in range(1, len(pts) - 1):
                    remove_bump(fc, i)
        bind_camera(scene, cam, f)
        f = (exit_start + r['change_duration'] // 2) if n < len(shots) - 1 else exit_start
    scene.frame_end = max(scene.frame_end, f)
    return f


# ===== studio_lighting.py =====
"""Studio lighting: cyclorama backdrop (B-video), HDRI world, key/fill/rim area lights, light linking."""
import bpy, math, bmesh
from mathutils import Vector


def cyclorama(size=12.0, height=6.0, bevel=2.0, segments=16, color=(0.8, 0.8, 0.8), roughness=0.45, name='Backdrop'):
    """B-video infinite backdrop: plane, back edge extruded up, corner beveled. Big enough for camera moves."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    s = size / 2
    v = [bm.verts.new(p) for p in ((-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0), (-s, s, height), (s, s, height))]
    bm.faces.new((v[0], v[1], v[2], v[3]))
    bm.faces.new((v[3], v[2], v[5], v[4]))
    corner = [e for e in bm.edges if set(e.verts) == {v[2], v[3]}]
    bmesh.ops.bevel(bm, geom=corner, offset=bevel, segments=segments, affect='EDGES', profile=0.5)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(simple_material(f'{name}_mat', color, roughness))
    return ob


def simple_material(name, color=(0.8, 0.8, 0.8), roughness=0.5, metallic=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    if coat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = coat
    return m


def hdri_world(path=None, strength=1.0, rotation_deg=0.0, color=(0.05, 0.05, 0.055), background_strength=None):
    """HDRI lighting. If background_strength is given, the camera sees a flat colour but objects still get
    the HDRI lighting and reflections (Light Path 'Is Camera Ray' mix) - the usual product-studio trick."""
    w = bpy.context.scene.world or bpy.data.worlds.new('World')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    if path:
        env = nt.nodes.new('ShaderNodeTexEnvironment')
        env.image = bpy.data.images.load(path, check_existing=True)
        mapn, coord = nt.nodes.new('ShaderNodeMapping'), nt.nodes.new('ShaderNodeTexCoord')
        mapn.inputs['Rotation'].default_value[2] = math.radians(rotation_deg)
        nt.links.new(coord.outputs['Generated'], mapn.inputs['Vector'])
        nt.links.new(mapn.outputs['Vector'], env.inputs['Vector'])
        nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    else:
        bg.inputs['Color'].default_value = (*color, 1)
    if background_strength is None:
        nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
        return w
    flat = nt.nodes.new('ShaderNodeBackground')
    flat.inputs['Color'].default_value = (*color, 1)
    flat.inputs['Strength'].default_value = background_strength
    lp, mix = nt.nodes.new('ShaderNodeLightPath'), nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    nt.links.new(bg.outputs['Background'], mix.inputs[1])
    nt.links.new(flat.outputs['Background'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return w


def area_light(name, location, target, power=500.0, size=2.0, color=(1, 1, 1), spread_deg=180.0):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.size, ld.color = power, size, color
    if hasattr(ld, 'spread'):
        ld.spread = math.radians(spread_deg)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(location)
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    return ob


def three_point(target=(0, 0, 0), radius=1.0, camera=None, key_power=None, warm_key=True):
    """Key 45 deg camera-left and high, fill opposite at ~1/4 the power, rim behind and above for the silhouette.
    Powers scale with radius squared, so the same call works for a watch or a car."""
    t = Vector(target)
    s = max(radius, 0.05)
    base = key_power or 600.0 * s * s
    fwd = Vector((0, -1, 0))
    if camera is not None:
        fwd = (camera.matrix_world.translation - t)
        fwd.z = 0
        fwd = fwd.normalized() if fwd.length else Vector((0, -1, 0))
    side = fwd.cross(Vector((0, 0, 1)))
    d = 4.0 * s
    key_l = area_light('Key', t + (fwd * 0.7 - side * 0.7) * d + Vector((0, 0, 0.8 * d)), t, base, 2.5 * s,
                       (1.0, 0.95, 0.88) if warm_key else (1, 1, 1))
    fill = area_light('Fill', t + (fwd * 0.8 + side * 0.9) * d + Vector((0, 0, 0.2 * d)), t, base * 0.25, 4.0 * s,
                      (0.9, 0.95, 1.0))
    rim = area_light('Rim', t - fwd * 1.1 * d + side * 0.3 * d + Vector((0, 0, 0.9 * d)), t, base * 1.2, 1.5 * s)
    return key_l, fill, rim


def two_area_lights(model, power=400.0, distance=3.0):
    """B-video: one area light right, a duplicate left that is light-linked to the model only (no extra
    shadow on the backdrop)."""
    c = model.matrix_world.translation
    r = area_light('Area_R', c + Vector((distance, -distance * 0.5, distance * 0.6)), c, power)
    l = area_light('Area_L', c + Vector((-distance, -distance * 0.5, distance * 0.6)), c, power * 0.6)
    link_light_to(l, [model])
    return r, l


def link_light_to(light_obj, receivers):
    col = bpy.data.collections.new(f'{light_obj.name}_receivers')
    for o in receivers:
        col.objects.link(o)
    light_obj.light_linking.receiver_collection = col
    return col


# ===== render_presets.py =====
"""Render presets for EngineX Blender 5.x jobs. preview = fast review frames; final = delivery."""
import bpy

RENDER_PRESETS = {
    # name: (engine, percent, samples, motion_blur)
    'preview':       ('CYCLES', 40, 32, True),
    'preview_eevee': ('EEVEE', 40, 32, True),
    'final':         ('CYCLES', 100, 256, True),
    'final_eevee':   ('EEVEE', 100, 128, True),
}


def _eevee_id():
    ids = {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    return 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ids else 'BLENDER_EEVEE_NEXT'


def render_preset(scene, name='preview', res=(1920, 1080), fps=30, shutter=0.5, look='AgX - Medium High Contrast'):
    engine, pct, samples, blur = RENDER_PRESETS[name]
    r = scene.render
    r.engine = 'CYCLES' if engine == 'CYCLES' else _eevee_id()
    r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], pct
    r.fps = fps
    r.use_motion_blur = blur
    r.motion_blur_shutter = shutter
    r.film_transparent = False
    if engine == 'CYCLES':
        c = scene.cycles
        c.samples = samples
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.02 if 'preview' in name else 0.01
        c.use_denoising = True
        try:
            c.denoiser = 'OPENIMAGEDENOISE'
        except Exception:
            pass
        c.max_bounces, c.glossy_bounces, c.transmission_bounces = 8, 6, 8
        try:
            gpu(scene)  # EngineX helper: Cycles on the card
        except NameError:
            c.device = 'GPU'
    else:
        e = scene.eevee
        e.taa_render_samples = samples
        if hasattr(e, 'use_raytracing'):
            e.use_raytracing = True
        if hasattr(e, 'use_shadows'):
            e.use_shadows = True
    vs = scene.view_settings
    vs.view_transform = 'AgX'
    try:
        vs.look = look
    except TypeError:
        vs.look = 'None'
    return scene


def video_output(scene, path, crf='HIGH'):
    """MP4 H.264. Blender 5.x needs image_settings.media_type = 'VIDEO' before FFMPEG."""
    im = scene.render.image_settings
    if hasattr(im, 'media_type'):
        im.media_type = 'VIDEO'
    im.file_format = 'FFMPEG'
    ff = scene.render.ffmpeg
    ff.format, ff.codec = 'MPEG4', 'H264'
    ff.constant_rate_factor = crf
    ff.ffmpeg_preset = 'GOOD'
    scene.render.filepath = path


def still_output(scene, path, fmt='PNG'):
    im = scene.render.image_settings
    if hasattr(im, 'media_type'):
        im.media_type = 'IMAGE'
    im.file_format = fmt
    scene.render.filepath = path


# ===== turntable.py =====
"""Turntable and hero-move rigs. Needs easing_presets.py loaded first."""
import bpy, math


def turntable(target_obj, start, end, turns=1.0, preset='linear'):
    """Rotate the product (via a parent empty) around Z. 'linear' only for seamless loops; use
    'smooth' / 'super_smooth' for a hero move that starts and settles."""
    piv = bpy.data.objects.new(f'{target_obj.name}_turntable', None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = target_obj.matrix_world.translation.copy()
    mw = target_obj.matrix_world.copy()
    target_obj.parent = piv
    target_obj.matrix_world = mw
    key(piv, 'rotation_euler', start, (0, 0, 0), index=2)
    key(piv, 'rotation_euler', end, (0, 0, math.tau * turns), index=2)
    for fc in fcurves_of(piv):
        ease(fc, preset)
        if preset == 'linear':
            fc.modifiers.new('CYCLES')
    return piv


def hero_reveal(obj, start, end, rise=0.3, spin_deg=200.0, scale_from=0.85):
    """5 s product hero: rises, spins and settles (super_smooth), with a small overshoot-free scale-in."""
    loc, rot, sc = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()
    key(obj, 'location', end, tuple(loc))
    key(obj, 'rotation_euler', end, tuple(rot))
    key(obj, 'scale', end, tuple(sc))
    key(obj, 'location', start, (loc.x, loc.y, loc.z - rise))
    key(obj, 'rotation_euler', start, (rot.x, rot.y, rot.z - math.radians(spin_deg)))
    key(obj, 'scale', start, tuple(v * scale_from for v in sc))
    ease_object(obj, 'super_smooth')


# ===== exploded_view.py =====
"""Exploded-view rig (from learning/exploded-view/notes.md, Derek Elliott workflow), fully scripted.
Needs easing_presets.py loaded first.

Steps it automates: separate by loose parts, origin to geometry (or a custom pivot), key ASSEMBLED,
key EXPLODED along each part's assembly axis (staggered in sequence), hold, re-assemble, ease all
(Bezier, no linear), optional seeded rotation wobble, shape-key click, callout labels with leader lines.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix


def gather_asset(asset_id, size=0.6, min_parts=6, max_parts=9):
    """place_asset + make the result explode-ready. Lessons from the Phase-5 test:
    - SimReady USD meshes come back UNPARENTED (holder.children_recursive has no meshes): collect new meshes
      by set difference, never from the holder.
    - Few meshes (gearbox = body + 2 gears): split by loose parts until >= min_parts.
    - Dozens of slivers: join the smallest into one 'hardware' part so the explode stays readable (<= max_parts).
    Result: world-space, unparented, scale-applied parts with origins at their bounds centre, sitting on Z=0,
    longest side = size metres."""
    before = set(bpy.data.objects)
    place_asset(asset_id, size=size)
    bpy.context.view_layer.update()
    new = [o for o in bpy.data.objects if o not in before]
    parts = [o for o in new if o.type == 'MESH' and not o.hide_render]
    for o in parts:  # world transform baked, no parents
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    for o in [o for o in new if o.type != 'MESH']:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    lo, hi = bounds_world(parts)
    k = size / max(max(hi - lo), 1e-6)
    if abs(k - 1) > 1e-3:  # place_asset could not scale unparented meshes: normalise here
        for o in parts:
            o.matrix_world = __import__('mathutils').Matrix.Scale(k, 4) @ o.matrix_world
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if len(parts) < min_parts:
        split = []
        for o in parts:
            split += separate_loose(o)
        parts = [o for o in split if o.type == 'MESH']
    parts.sort(key=lambda o: (lambda d: d.x * d.y * d.z)(o.dimensions), reverse=True)
    if len(parts) > max_parts:
        small = parts[max_parts - 1:]
        bpy.ops.object.select_all(action='DESELECT')
        for o in small:
            o.select_set(True)
        bpy.context.view_layer.objects.active = small[0]
        bpy.ops.object.join()
        small[0].name = 'hardware'
        parts = parts[:max_parts - 1] + [small[0]]
    origins_to_geometry(parts, center='BOUNDS')
    lo, hi = bounds_world(parts)
    shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in parts:
        o.location -= shift
    bpy.context.view_layer.update()
    return parts


def rotate_assembly(parts, axis='Y', degrees=90.0, pivot=None):
    """Turn the whole assembly (baked into the meshes) so its long/explode axis lies along X. An explode along Z
    fills only a thin vertical strip of a 16:9 frame (Phase-5 review: subject ~10 % of the frame)."""
    lo, hi = bounds_world(parts)
    c = Vector(pivot) if pivot else (lo + hi) / 2
    R = Matrix.Translation(c) @ Matrix.Rotation(math.radians(degrees), 4, axis) @ Matrix.Translation(-c)
    for o in parts:
        o.matrix_world = R @ o.matrix_world
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    origins_to_geometry(parts, center='BOUNDS')


def separate_loose(obj):
    """Edit > P > By Loose Parts. Returns the resulting objects (by set difference: headless jobs have no
    reliable context.selected_objects after an operator)."""
    before = set(bpy.data.objects)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    return [obj] + [o for o in bpy.data.objects if o not in before]


def origins_to_geometry(objs, center='BOUNDS'):
    """Right-click > Set Origin > Origin to Geometry. 'BOUNDS' is better than 'MEDIAN' on dense/threaded
    meshes (video caption: median gets pulled toward thread detail)."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center=center)


def set_origin_to_point(obj, world_point):
    """Shift+S Cursor to Selected + Origin to 3D Cursor, without the cursor: move the mesh, not the object."""
    p_local = obj.matrix_world.inverted() @ Vector(world_point)
    obj.data.transform(__import__('mathutils').Matrix.Translation(-p_local))
    obj.matrix_world.translation = Vector(world_point)


def bounds_world(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def auto_axes(parts, center=None, prefer='Z'):
    """Assembly axis per part: from the assembly centre to the part centre, snapped to the dominant axis
    (technical explodes move along X/Y/Z, never diagonals). The part nearest the centre stays put."""
    lo, hi = bounds_world(parts)
    c = Vector(center) if center else (lo + hi) / 2
    out = {}
    for o in parts:
        plo, phi = bounds_world([o])
        d = (plo + phi) / 2 - c
        if d.length < 1e-4:
            out[o.name] = Vector((0, 0, 0))
            continue
        ax = max(range(3), key=lambda i: abs(d[i]) * (1.15 if 'XYZ'[i] == prefer else 1.0))
        v = Vector((0, 0, 0))
        v[ax] = 1.0 if d[ax] >= 0 else -1.0
        out[o.name] = v
    return out


def explode(parts, axes=None, start=1, assembled_hold=20, explode_len=30, stagger=6, hold=60,
            spread=1.0, return_len=None, preset='smooth', order=None, distances=None):
    """Key assembled -> exploded (staggered, in `order`) -> hold -> re-assembled.
    spread: explode distance as a multiple of the assembly's size, scaled per part by its distance from the
    centre rank so outer parts travel further (no collisions). Returns the last frame."""
    axes = axes or auto_axes(parts)
    order = order or sorted(parts, key=lambda o: -(sum(bounds_world([o]), Vector()) / 2 -
                                                   sum(bounds_world(parts), Vector()) / 2).length)
    lo, hi = bounds_world(parts)
    size = max(hi - lo)
    return_len = return_len or explode_len
    t0 = start + assembled_hold
    last = start
    n = len(order)
    for i, o in enumerate(order):
        a = axes[o.name]
        home = o.location.copy()
        rank = 1.0 - i / max(n, 1) * 0.5           # outer parts first and furthest
        dist = (distances or {}).get(o.name, spread * size * 0.6 * rank)  # explicit plan wins
        t_out = t0 + i * stagger
        t_back = t0 + (n - 1) * stagger + explode_len + hold + (n - 1 - i) * stagger
        key(o, 'location', start, tuple(home))
        key(o, 'location', t_out, tuple(home))
        if a.length:
            disp = a * dist  # world space; convert into the parent's space (place_asset parents to a scaled empty)
            if o.parent:
                disp = (o.parent.matrix_world.inverted().to_3x3() @ disp)
            key(o, 'location', t_out + explode_len, tuple(home + disp))
            key(o, 'location', t_back, tuple(home + disp))
        key(o, 'location', t_back + return_len, tuple(home))
        for fc in fcurves_of(o):
            if fc.data_path == 'location':
                ease(fc, preset)
        o['explode_out_frame'] = t_out + explode_len
        o['explode_back_frame'] = t_back
        last = max(last, t_back + return_len)
    return last


def wobble_rotation(parts, frame, degrees=8.0, seed=0, around=None):
    """F3 > Randomize Transform (rotation only) as keys: zero at the part's first/last key, random at `frame`."""
    rnd = random.Random(seed)
    for o in parts:
        fr = [k.co.x for fc in fcurves_of(o) if fc.data_path == 'location' for k in fc.keyframe_points]
        if not fr:
            continue
        r0 = o.rotation_euler.copy()
        key(o, 'rotation_euler', min(fr), tuple(r0))
        key(o, 'rotation_euler', max(fr), tuple(r0))
        r = tuple(v + math.radians(rnd.uniform(-degrees, degrees)) for v in r0)
        key(o, 'rotation_euler', around(o) if around else frame, r)
        for fc in fcurves_of(o):
            if fc.data_path == 'rotation_euler':
                ease(fc, 'smooth')


def shape_key_click(obj, frames_values):
    """Shape-key deformation (clip depress): frames_values = [(frame, 0..1), ...] on 'Key 1'."""
    if not obj.data.shape_keys:
        obj.shape_key_add(name='Basis')
    k = obj.data.shape_keys.key_blocks.get('Key 1') or obj.shape_key_add(name='Key 1')
    for f, v in frames_values:
        k.value = v
        k.keyframe_insert('value', frame=f)
    for fc in fcurves_of(obj.data.shape_keys):
        ease(fc, 'snappy')
    return k


def emission_material(name, color=(1, 1, 1), strength=2.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em, out = nt.nodes.new('ShaderNodeEmission'), nt.nodes.new('ShaderNodeOutputMaterial')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def add_callout(part, text, camera, offset=(0.0, 0.0, 0.0), size=0.06, appear=None, color=(1, 1, 1),
                accent=(1.0, 0.55, 0.1), font=None):
    """Label + leader line + dot, parented to the part so they travel with it; the label always faces the
    camera (Copy Rotation of the camera). Scales in (snappy ease) at `appear` and out before re-assembly."""
    lo, hi = bounds_world([part])
    anchor = (lo + hi) / 2
    tip = anchor + Vector(offset)
    # text
    cu = bpy.data.curves.new(f'{part.name}_label', 'FONT')
    vertical = abs(offset[2]) > abs(offset[0])   # label above/below the part, else to its left/right
    left = offset[0] < 0                          # left labels are right-aligned so text never runs into the part
    cu.body, cu.size = text, size
    cu.align_x = 'CENTER' if vertical else ('RIGHT' if left else 'LEFT')
    cu.align_y = 'CENTER'
    if font:
        cu.font = bpy.data.fonts.load(font)
    lab = bpy.data.objects.new(cu.name, cu)
    bpy.context.scene.collection.objects.link(lab)
    lab.data.materials.append(emission_material(f'{part.name}_label_mat', color, 3.0))
    if vertical:
        lab.location = tip + Vector((0, 0, size * 0.9 * (1 if offset[2] > 0 else -1)))
    else:
        lab.location = tip + Vector((-size * 0.4 if left else size * 0.4, 0, 0))
    c = lab.constraints.new('COPY_ROTATION')
    c.target = camera
    # leader line (poly curve) + dot
    ln = bpy.data.curves.new(f'{part.name}_leader', 'CURVE')
    ln.dimensions, ln.bevel_depth = '3D', size * 0.04
    sp = ln.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (0, 0, 0, 1)                 # LOCAL points; the object sits at the anchor, so scaling it
    sp.points[1].co = (*(tip - anchor), 1)         # collapses onto the part (world-space points collapsed to the origin)
    line = bpy.data.objects.new(ln.name, ln)
    line.location = anchor
    bpy.context.scene.collection.objects.link(line)
    line.data.materials.append(emission_material(f'{part.name}_leader_mat', accent, 4.0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size * 0.12, location=anchor)
    dot = bpy.context.active_object
    dot.name = f'{part.name}_dot'
    dot.data.materials.append(line.data.materials[0])
    bpy.context.view_layer.update()
    grp = []
    for o in (lab, line, dot):
        mw = o.matrix_world.copy()
        o.parent = part
        o.matrix_world = mw
        grp.append(o)
    if appear is not None:
        t_in, t_out = appear
        for o in grp:
            s = o.scale.copy()
            key(o, 'scale', t_in - 1, (0, 0, 0))
            key(o, 'scale', t_in + 8, tuple(s))
            key(o, 'scale', t_out, tuple(s))
            key(o, 'scale', t_out + 6, (0, 0, 0))
            for fc in fcurves_of(o):
                ease(fc, 'snappy')
    return lab, line, dot


# ===== materials.py =====
"""PBR materials from the EngineX library catalog (assets/catalog.json texture_maps) as Principled BSDF.
Library materials are mostly MDL (not readable by Blender): build them from their texture maps instead.
Lessons: colour variants (Anodized Red/Black/Blue) share ONE base-colour texture - the tint lived in the MDL,
so pass `tint`. ORM = R ambient occlusion, G roughness, B metallic. No UVs on procedural parts -> box mapping."""
import bpy, os


def assign_material(obj, mat):
    """The ONLY way to put a material on a mesh. Clears every slot first and points all faces at slot 0.
    Phase-5 bug: an applied Boolean modifier leaves an EMPTY slot 0, so `data.materials.append(mat)` made the
    material slot 1 while every face used slot 0 -> the part rendered default grey/white, whatever the material."""
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0


def anodized(name, color, roughness=0.35, metallic=0.9):
    """Flat but physically plausible coloured metal (anodised aluminium, painted metal). The fallback when a library
    material's texture files are missing, and good enough for smooth anodised parts: ORM/normal add almost nothing."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = roughness
    return m


def library_material(name, maps, tint=(1, 1, 1), metallic=None, roughness=None, scale=4.0, normal_strength=0.6,
                     coat=0.0, box_blend=0.25):
    """ALWAYS check the result: material['missing_maps'] lists texture files that do not exist on disk. Library MDL
    texture paths are resolved from the .mdl text and can point at files that are not shipped (Phase-5: the base
    'Aluminum_Anodized' maps loaded as magenta = metallic 1 / roughness 0 / garbage normals -> parts rendered white).
    If it is non-empty, swap to anodized()/metal() instead of rendering."""
    missing = [k for k, v in maps.items() if not os.path.exists(v)]
    maps = {k: v for k, v in maps.items() if k not in missing}
    """maps: {'albedo': path, 'normal': path, 'orm'|'roughness'|'metallic': path} from find_asset.py --json.
    metallic/roughness override (or multiply when maps exist) for exact looks."""
    m = bpy.data.materials.new(name)
    m['missing_maps'] = ','.join(missing)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    coord, mapn = nt.nodes.new('ShaderNodeTexCoord'), nt.nodes.new('ShaderNodeMapping')
    mapn.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(coord.outputs['Object'], mapn.inputs['Vector'])

    def tex(path, non_color=False):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(path, check_existing=True)
        if non_color:
            t.image.colorspace_settings.name = 'Non-Color'
        t.projection, t.projection_blend = 'BOX', box_blend
        nt.links.new(mapn.outputs['Vector'], t.inputs['Vector'])
        return t

    tinted = tuple(tint) != (1, 1, 1)
    if maps.get('albedo') and tinted:
        # Colour variants (Anodized Red/Black/Blue) share one near-white albedo texture: the colour is the tint.
        # Phase-5: multiplying through a Mix node rendered WHITE, so use the tint as the flat base colour and keep
        # only the ORM + normal maps for surface response.
        b.inputs['Base Color'].default_value = (*tint, 1)
    elif maps.get('albedo'):
        a = tex(maps['albedo'])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type, mix.blend_type = 'RGBA', 'MULTIPLY'
        # GOTCHA (Phase-5): ShaderNodeMix has float/vector/colour variants that share the names 'A'/'B'/'Result';
        # inputs['A'] returns the FLOAT socket, so the tint silently never connected and parts rendered white.
        # Pick sockets by type.
        mix.inputs[0].default_value = 1.0
        col_in = [s for s in mix.inputs if s.type == 'RGBA']
        nt.links.new(a.outputs['Color'], col_in[0])
        col_in[1].default_value = (*tint, 1)
        nt.links.new([s for s in mix.outputs if s.type == 'RGBA'][0], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*tint, 1)
    rough_src = metal_src = None
    if maps.get('orm'):
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        nt.links.new(tex(maps['orm'], True).outputs['Color'], sep.inputs['Color'])
        rough_src, metal_src = sep.outputs['Green'], sep.outputs['Blue']
    if maps.get('roughness'):
        rough_src = tex(maps['roughness'], True).outputs['Color']
    if maps.get('metallic'):
        metal_src = tex(maps['metallic'], True).outputs['Color']
    for src, sock, override in ((rough_src, 'Roughness', roughness), (metal_src, 'Metallic', metallic)):
        if src is not None and override is None:
            nt.links.new(src, b.inputs[sock])
        elif src is not None:
            mul = nt.nodes.new('ShaderNodeMath')
            mul.operation = 'MULTIPLY'
            nt.links.new(src, mul.inputs[0])
            mul.inputs[1].default_value = override
            nt.links.new(mul.outputs['Value'], b.inputs[sock])
        elif override is not None:
            b.inputs[sock].default_value = override
    if maps.get('normal'):
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = normal_strength
        nt.links.new(tex(maps['normal'], True).outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if coat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = coat
    return m


def metal(name, color, roughness=0.25, anisotropic=0.0):
    """Measured-ish metal fallback when no texture fits (copper 0.955,0.638,0.538; steel 0.56,0.57,0.58;
    aluminium 0.91,0.92,0.92; gold 1.0,0.766,0.336). Still PBR: metallic 1, roughness never 0."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = max(roughness, 0.05)
    if anisotropic and 'Anisotropic' in b.inputs:
        b.inputs['Anisotropic'].default_value = anisotropic
    return m


# ===== product_models.py =====
"""Detailed procedural products for when the library has no suitable multi-part asset (exploded views need
separate, real parts). Real proportions, chamfers via Bevel modifiers, smooth shading + Weighted Normal.
drone_motor(): 2207-class brushless outrunner, modelled at 10:1 (stator 22 mm -> 0.22 m) for comfortable
camera/DOF numbers. Returns {part_name: object} in assembly order, bottom to top."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


def _obj(name, bm, smooth=True, bevel=0.004, segments=3, angle=35):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = smooth
    if bevel:
        bv = ob.modifiers.new('Bevel', 'BEVEL')
        bv.width, bv.segments, bv.limit_method, bv.angle_limit = bevel, segments, 'ANGLE', math.radians(angle)
        bv.harden_normals = True
    ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL').keep_sharp = True
    return ob


def _ring(bm, r_out, r_in, h, z=0.0, seg=64):
    """Closed tube (annulus) from z to z+h; only its own verts are moved."""
    before = set(bm.verts)
    outer = bmesh.ops.create_circle(bm, cap_ends=False, radius=r_out, segments=seg)['verts']
    inner = bmesh.ops.create_circle(bm, cap_ends=False, radius=r_in, segments=seg)['verts']
    edges = list({e for v in outer + inner for e in v.link_edges})
    bmesh.ops.bridge_loops(bm, edges=edges)
    faces = list({f for v in outer for f in v.link_faces})
    ext = bmesh.ops.extrude_face_region(bm, geom=faces)
    bmesh.ops.translate(bm, verts=[g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, h))
    mine = [v for v in bm.verts if v not in before]
    if z:
        bmesh.ops.translate(bm, verts=mine, vec=(0, 0, z))
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in mine for f in v.link_faces}))


def _cyl(bm, r, h, z=0.0, seg=64, matrix=None):
    m = Matrix.Translation((0, 0, z + h / 2))
    if matrix:
        m = matrix @ m
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h, matrix=m)


def _box(bm, size, loc, rot_z=0.0):
    m = Matrix.Translation(loc) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((*size, 1))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)


def _boolean(ob, cutter_bm, op='DIFFERENCE'):
    me = bpy.data.meshes.new(ob.name + '_cut')
    cutter_bm.to_mesh(me)
    cutter_bm.free()
    cut = bpy.data.objects.new(ob.name + '_cut', me)
    bpy.context.scene.collection.objects.link(cut)
    md = ob.modifiers.new('Bool', 'BOOLEAN')
    md.object, md.operation, md.solver = cut, op, 'EXACT'
    md.use_self = True  # parts are built from overlapping primitives; without this the exact solver drops them
    bpy.context.view_layer.objects.active = ob
    ob.modifiers.move(len(ob.modifiers) - 1, 0)
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cut, do_unlink=True)
    ob.data.materials.clear()  # the exact solver leaves an empty slot 0 behind (see materials.assign_material)


def drone_motor():
    P = {}
    # base mount: disc + 4 arms + centre boss, 4 M3 holes
    bm = bmesh.new()
    _cyl(bm, 0.135, 0.025, 0.0)
    for k in range(2):  # two crossing bars = 4 arms at 45/135/225/315 deg
        _box(bm, (0.30, 0.055, 0.025), (0, 0, 0.0125), rot_z=math.radians(45 + 90 * k))
    _cyl(bm, 0.06, 0.05, 0.0)
    P['base_mount'] = _obj('base_mount', bm, bevel=0.005)
    cut = bmesh.new()
    for k in range(4):
        a = math.radians(45 + 90 * k)
        _cyl(cut, 0.016, 0.1, -0.02, seg=32, matrix=Matrix.Translation((0.12 * math.cos(a), 0.12 * math.sin(a), 0)))
    _cyl(cut, 0.03, 0.2, -0.05, seg=48)
    _boolean(P['base_mount'], cut)
    # bottom bearing (685ZZ: 5x11x5 mm -> 0.025/0.055/0.05)
    bm = bmesh.new(); _ring(bm, 0.055, 0.025, 0.05, z=0.0)
    P['bearing_bottom'] = _obj('bearing_bottom', bm, bevel=0.003)
    P['bearing_bottom'].location.z = 0.0
    # stator: core ring + 12 T-teeth, 0.07 tall
    bm = bmesh.new(); _ring(bm, 0.06, 0.03, 0.07, z=0.06)
    for k in range(12):
        a = math.tau * k / 12
        _box(bm, (0.05, 0.022, 0.07), (0.08 * math.cos(a), 0.08 * math.sin(a), 0.095), rot_z=a)
        _box(bm, (0.012, 0.05, 0.07), (0.106 * math.cos(a), 0.106 * math.sin(a), 0.095), rot_z=a)
    P['stator'] = _obj('stator', bm, smooth=False, bevel=0.0015, segments=2)
    # copper windings around each tooth
    bm = bmesh.new()
    for k in range(12):
        a = math.tau * k / 12
        _box(bm, (0.036, 0.034, 0.085), (0.082 * math.cos(a), 0.082 * math.sin(a), 0.095), rot_z=a)
    P['windings'] = _obj('windings', bm, bevel=0.012, segments=4, angle=20)
    # rotor bell: shell + top cap with 6 cooling slots
    bm = bmesh.new(); _ring(bm, 0.14, 0.128, 0.095, z=0.045)
    _ring(bm, 0.14, 0.03, 0.014, z=0.14)
    P['rotor_bell'] = _obj('rotor_bell', bm, bevel=0.004)
    cut = bmesh.new()
    for k in range(6):
        a = math.tau * k / 6
        _box(cut, (0.06, 0.022, 0.06), (0.085 * math.cos(a), 0.085 * math.sin(a), 0.147), rot_z=a)
    _boolean(P['rotor_bell'], cut)
    # 14 N52 magnets glued inside the bell
    bm = bmesh.new()
    for k in range(14):
        a = math.tau * k / 14
        _box(bm, (0.008, 0.042, 0.08), (0.123 * math.cos(a), 0.123 * math.sin(a), 0.095), rot_z=a)
    P['magnets'] = _obj('magnets', bm, bevel=0.0015, segments=2)
    # shaft (5 mm) with top thread region
    bm = bmesh.new(); _cyl(bm, 0.025, 0.32, -0.04, seg=48)
    P['shaft'] = _obj('shaft', bm, bevel=0.004)
    # top bearing
    bm = bmesh.new(); _ring(bm, 0.055, 0.025, 0.04, z=0.155)
    P['bearing_top'] = _obj('bearing_top', bm, bevel=0.003)
    # circlip (C ring) under the base
    bm = bmesh.new(); _ring(bm, 0.04, 0.026, 0.01, z=-0.03, seg=48)
    P['circlip'] = _obj('circlip', bm, bevel=0.002)
    cut = bmesh.new(); _box(cut, (0.03, 0.02, 0.05), (0.035, 0, -0.025))
    _boolean(P['circlip'], cut)
    # M5 prop nut (hex) on top
    bm = bmesh.new(); _cyl(bm, 0.055, 0.06, 0.2, seg=6)
    _cyl(bm, 0.042, 0.02, 0.26, seg=48)
    P['prop_nut'] = _obj('prop_nut', bm, smooth=False, bevel=0.006)
    cut = bmesh.new(); _cyl(cut, 0.026, 0.2, 0.15, seg=32)
    _boolean(P['prop_nut'], cut)
    # 4 M3 cap screws from below
    bm = bmesh.new()
    for k in range(4):
        a = math.radians(45 + 90 * k)
        x, y = 0.12 * math.cos(a), 0.12 * math.sin(a)
        _cyl(bm, 0.027, 0.03, -0.03, seg=32, matrix=Matrix.Translation((x, y, 0)))
        _cyl(bm, 0.015, 0.07, 0.0, seg=24, matrix=Matrix.Translation((x, y, 0)))
    P['screws'] = _obj('screws', bm, bevel=0.004)
    # sit on the floor
    lo = min((o.matrix_world @ Vector(c)).z for o in P.values() for c in o.bound_box)
    for o in P.values():
        o.location.z -= lo
    return P


def _pbr(name, color, roughness=0.4, metallic=0.0, transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    b.inputs['IOR'].default_value = ior
    for k in ('Transmission Weight', 'Transmission'):
        if k in b.inputs:
            b.inputs[k].default_value = transmission
            break
    return m


def ballpoint_pen(lift=0.12):
    """Stick ballpoint (BIC Cristal type) at 10:1 (1 mm -> 0.01 m): clear hex barrel with the side air hole, blue cap
    with clip, end plug, ink tube with the ink column, brass tip with a ball socket, 1.0 mm tungsten-carbide ball.
    Built along +Z (tip at z=0) then laid along X (tip at -X, clip up). Returns {part: object} tip -> end.
    Sources: ball 0.7-1.0 mm in a socket, ink fed by gravity + capillarity, barrel hole equalises pressure
    (BIS IS 3705, engineersgarage, Design Museum)."""
    P = {}
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.0052,
                              matrix=Matrix.Translation((0, 0, -0.0015)))
    P['ball'] = _obj('ball', bm, bevel=0)
    # tip: cone that wraps the ball (lip r 0.007 > ball r 0.0052 holds it), collar, neck pushed into the tube
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.007, radius2=0.0165, depth=0.10,
                          matrix=Matrix.Translation((0, 0, 0.05)))
    _cyl(bm, 0.0165, 0.03, 0.10, seg=48)
    _cyl(bm, 0.0124, 0.07, 0.12, seg=48)
    P['tip'] = _obj('tip', bm, bevel=0.0015)
    cut = bmesh.new()
    bmesh.ops.create_uvsphere(cut, u_segments=32, v_segments=16, radius=0.0054,
                              matrix=Matrix.Translation((0, 0, -0.0015)))
    _cyl(cut, 0.0028, 0.20, -0.01, seg=24)                  # ink channel behind the ball
    _boolean(P['tip'], cut)
    bm = bmesh.new()
    _ring(bm, 0.0155, 0.0125, 1.42, z=0.13, seg=48)
    P['ink_tube'] = _obj('ink_tube', bm, bevel=0.001)
    bm = bmesh.new()
    _cyl(bm, 0.0121, 0.95, 0.19, seg=48)
    P['ink'] = _obj('ink', bm, bevel=0.002)
    # barrel: round nose + hex body (corner up after laying down), bore, one air hole facing the camera (-Y)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.022, radius2=0.040, depth=0.20,
                          matrix=Matrix.Translation((0, 0, 0.18)))
    _cyl(bm, 0.044, 1.30, 0.28, seg=6)
    P['barrel'] = _obj('barrel', bm, smooth=False, bevel=0.006, angle=50)
    cut = bmesh.new()
    _cyl(cut, 0.019, 1.80, -0.05, seg=48)
    _cyl(cut, 0.006, 0.05, -0.025, seg=24, matrix=Matrix.Translation((0, -0.035, 0.80)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    _boolean(P['barrel'], cut)
    bm = bmesh.new()                                         # rim around the hole: a separate part the camera can name
    _ring(bm, 0.0105, 0.0062, 0.002, seg=32)
    bmesh.ops.transform(bm, verts=bm.verts, matrix=Matrix.Translation((0, -0.0372, 0.80)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    P['air_hole'] = _obj('air_hole', bm, bevel=0)
    bm = bmesh.new()
    _cyl(bm, 0.0185, 0.08, 1.50, seg=48)
    _cyl(bm, 0.030, 0.03, 1.58, seg=48)
    P['end_plug'] = _obj('end_plug', bm, bevel=0.003)
    # cap: closed tube over the nose + clip on -X (up after laying down)
    bm = bmesh.new()
    _ring(bm, 0.050, 0.046, 0.50, z=-0.04, seg=48)
    _cyl(bm, 0.050, 0.04, -0.08, seg=48)
    _box(bm, (0.012, 0.03, 0.40), (-0.061, 0, 0.22))
    _box(bm, (0.022, 0.03, 0.04), (-0.052, 0, 0.42))
    P['cap'] = _obj('cap', bm, bevel=0.003)
    mats = {'ball': _pbr('tungsten_carbide', (0.46, 0.47, 0.49), 0.12, 1.0),
            'tip': _pbr('brass', (0.91, 0.76, 0.40), 0.22, 1.0),
            'ink_tube': _pbr('polypropylene', (0.92, 0.93, 0.95), 0.25, 0.0, 0.85, 1.49),
            'ink': _pbr('ink_blue', (0.01, 0.03, 0.30), 0.3),
            'barrel': _pbr('clear_polystyrene', (0.95, 0.97, 1.0), 0.04, 0.0, 1.0, 1.59),
            'end_plug': _pbr('blue_plastic', (0.02, 0.10, 0.55), 0.35)}
    mats['air_hole'], mats['cap'] = mats['barrel'], mats['end_plug']
    for n, o in P.items():
        assign_material(o, mats[n])
    parts = list(P.values())
    rotate_assembly(parts, axis='Y', degrees=90.0, pivot=(0, 0, 0))    # +Z -> +X, tip at -X, clip (-X) -> +Z
    lo = min((o.matrix_world @ Vector(c)).z for o in parts for c in o.bound_box)
    for o in parts:
        o.location.z += lift - lo
    return P


# ===== focus_rig.py =====
"""Branch-style focus rig: camera visits each named part on its beat, every OTHER part turns into an x-ray ghost, the named
part glows. Needs easing_presets.py (key, ease, fcurves_of) loaded first; beats come from beat_sheet.py.

Ghost design (material assignment cannot be animated, shader values can):
  every material of every part ->  Mix Shader( real surface , ghost )   factor = Attribute(OBJECT, "ghost")
  ghost = Mix Shader( Transparent BSDF , faint blue-grey Emission )      factor = Layer Weight (Fresnel)
Each object carries a custom property "ghost" (0 = real, 1 = x-ray); ghost_beats() keyframes it per beat:
ghosted from (spoken word - 0.8 s) until the end of the sentence that names the part + 0.4 s (beat 'dwell_f').
Shared materials are fine: the Attribute node reads the value of the object being shaded."""
import bpy, math
from mathutils import Vector

GHOST_PROP = 'ghost'


def _center(o):
    return o.matrix_world @ (sum((Vector(c) for c in o.bound_box), Vector()) / 8)


def _radius(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return max((p - _center(o)).length for p in pts)


GLOW_PROP = 'glow'


def install_ghost(parts, color=(0.42, 0.62, 0.9), strength=0.55, fresnel_blend=0.35,
                  glow_color=(1.0, 0.45, 0.05), glow_strength=3.0, glow_blend=0.5):   # blend .93 = facing^~7: a thin rim (.8 washed the whole part)
    """Insert the ghost mix into every material used by `parts` (once per material) and add the 'ghost' property."""
    done = set()
    for o in parts:
        o[GHOST_PROP] = 0.0
        o[GLOW_PROP] = 0.0
        for slot in o.material_slots:
            m = slot.material
            if m is None or m.name in done or m.get('_ghosted'):
                continue
            done.add(m.name)
            m.use_nodes = True
            nt = m.node_tree
            out = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial' and n.is_active_output),
                       None) or next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
            surf = out.inputs['Surface']
            if not surf.links:
                continue
            real = surf.links[0].from_socket
            # rim glow added ON TOP of the real shader (no extra mesh: a copied shell rendered as a solid orange fill,
            # pen test #4): strength = Attribute(OBJECT,'glow') x Layer Weight Facing (rim only)
            ga = nt.nodes.new('ShaderNodeAttribute')
            ga.attribute_type, ga.attribute_name = 'OBJECT', GLOW_PROP
            gl = nt.nodes.new('ShaderNodeLayerWeight')
            gl.inputs['Blend'].default_value = glow_blend
            gm = nt.nodes.new('ShaderNodeMath')
            gm.operation = 'MULTIPLY'
            gm.inputs[1].default_value = glow_strength
            gm2 = nt.nodes.new('ShaderNodeMath')
            gm2.operation = 'MULTIPLY'
            ge = nt.nodes.new('ShaderNodeEmission')
            ge.inputs['Color'].default_value = (*glow_color, 1)
            gadd = nt.nodes.new('ShaderNodeAddShader')
            gp = nt.nodes.new('ShaderNodeMath')           # rim = facing ** 6 (the raw Facing output washed the whole part, tests #4-#5)
            gp.operation = 'POWER'
            gp.inputs[1].default_value = 6.0
            nt.links.new(gl.outputs['Facing'], gp.inputs[0])
            nt.links.new(ga.outputs['Fac'], gm2.inputs[0])
            nt.links.new(gp.outputs['Value'], gm2.inputs[1])
            nt.links.new(gm2.outputs['Value'], gm.inputs[0])
            nt.links.new(gm.outputs['Value'], ge.inputs['Strength'])
            nt.links.new(real, gadd.inputs[0])
            nt.links.new(ge.outputs['Emission'], gadd.inputs[1])
            real = gadd.outputs['Shader']
            attr = nt.nodes.new('ShaderNodeAttribute')
            attr.attribute_type, attr.attribute_name = 'OBJECT', GHOST_PROP
            lw = nt.nodes.new('ShaderNodeLayerWeight')
            lw.inputs['Blend'].default_value = fresnel_blend
            tr = nt.nodes.new('ShaderNodeBsdfTransparent')
            em = nt.nodes.new('ShaderNodeEmission')
            em.inputs['Color'].default_value = (*color, 1)
            em.inputs['Strength'].default_value = strength
            mix_g = nt.nodes.new('ShaderNodeMixShader')
            nt.links.new(lw.outputs['Fresnel'], mix_g.inputs['Fac'])
            nt.links.new(tr.outputs['BSDF'], mix_g.inputs[1])
            nt.links.new(em.outputs['Emission'], mix_g.inputs[2])
            mix = nt.nodes.new('ShaderNodeMixShader')
            nt.links.new(attr.outputs['Fac'], mix.inputs['Fac'])
            nt.links.new(real, mix.inputs[1])
            nt.links.new(mix_g.outputs['Shader'], mix.inputs[2])
            nt.links.new(mix.outputs['Shader'], surf)
            if hasattr(m, 'surface_render_method'):
                m.surface_render_method = 'BLENDED'       # EEVEE: sorted transparency (dithered shows noise)
            if hasattr(m, 'use_transparency_overlap'):
                m.use_transparency_overlap = True
            m.use_backface_culling = False
            m['_ghosted'] = True


def ghost_render_settings(scene):
    """Transparency that holds in both preview and final: enough transparent bounces for nested ghosts in Cycles,
    blended materials + ray-traced transparency in EEVEE."""
    if hasattr(scene, 'cycles'):
        scene.cycles.transparent_max_bounces = 32
        scene.cycles.max_bounces = max(scene.cycles.max_bounces, 12)
    e = getattr(scene, 'eevee', None)
    if e is not None and hasattr(e, 'use_raytracing'):
        e.use_raytracing = True


def ghost_windows(beats, fps=30, lead_s=0.8):
    """[(start_f, end_f, part)] per beat that names a part: from word - lead to dwell end; clipped so they never overlap."""
    w = []
    for b in beats:
        if not b.get('part'):
            continue
        s = int(round((b.get('word_t', (b['settle_f'] - 1) / fps) - lead_s) * fps)) + 1
        s = min(s, b.get('move_f', s))     # sentence snapping can land the camera earlier than word-0.8 s: ghost with the move
        e = b.get('dwell_f', b['end_f'])
        w.append([max(1, s), max(e, s + 1), b['part']])
    w.sort()
    for i in range(len(w) - 1):
        if w[i][1] > w[i + 1][0]:
            w[i][1] = w[i + 1][0]
    return [tuple(x) for x in w if x[1] > x[0]]


def ghost_values(windows, part_name, frames):
    """0/1 state of one part at given frames: ghosted while another part is the focus."""
    def v(f):
        for s, e, p in windows:
            if s <= f < e:
                return 0.0 if p == part_name else 1.0
        return 0.0
    return [v(f) for f in frames]


def ghost_beats(parts, beats, fps=30, lead_s=0.8, ramp_f=10, exempt=()):
    """Keyframe the 'ghost' property of every part (smooth ramps of ramp_f frames at every change)."""
    wins = ghost_windows(beats, fps, lead_s)
    edges = sorted({f for s, e, _ in wins for f in (s, e)})
    for o in parts:
        if o.name in exempt:
            continue
        o[GHOST_PROP] = 0.0
        o.keyframe_insert(f'["{GHOST_PROP}"]', frame=1)
        prev = 0.0
        for f in edges:
            new = ghost_values(wins, o.name, [f])[0]
            if new != prev:
                o[GHOST_PROP] = prev
                o.keyframe_insert(f'["{GHOST_PROP}"]', frame=f)
                o[GHOST_PROP] = new
                o.keyframe_insert(f'["{GHOST_PROP}"]', frame=f + ramp_f)
                prev = new
        for fc in fcurves_of(o):
            if fc.data_path == f'["{GHOST_PROP}"]':
                ease(fc, 'smooth')
    return wins


def glow_rig(part, color=(1.0, 0.45, 0.05), strength=2.5):
    """Orange rim highlight: a slightly larger shell with an emissive Fresnel material, keyed visible per beat."""
    shell = part.copy()
    shell.data = part.data.copy()
    shell.name = f'{part.name}_glow'
    for k in list(shell.keys()):
        del shell[k]
    part.users_collection[0].objects.link(shell)
    shell.animation_data_clear()
    shell.parent = part
    shell.matrix_parent_inverse = part.matrix_world.inverted()
    sol = shell.modifiers.new('grow', 'SOLIDIFY')
    sol.thickness, sol.offset, sol.use_flip_normals = _radius(part) * 0.01, 1.0, False   # flipped normals made the outside 'backfacing' and the inside the glow: a solid fill (pen test #4)
    m = bpy.data.materials.new(f'{part.name}_glow_mat')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    fres, em, tr, mix, out, geo, bmix = (nt.nodes.new(t) for t in ('ShaderNodeLayerWeight', 'ShaderNodeEmission',
                                                                   'ShaderNodeBsdfTransparent', 'ShaderNodeMixShader',
                                                                   'ShaderNodeOutputMaterial', 'ShaderNodeNewGeometry',
                                                                   'ShaderNodeMixShader'))
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    fres.inputs['Blend'].default_value = 0.8    # narrow rim only: a wide one drowned the part (pen test #3)
    nt.links.new(fres.outputs['Facing'], mix.inputs['Fac'])
    nt.links.new(tr.outputs['BSDF'], mix.inputs[1])
    nt.links.new(em.outputs['Emission'], mix.inputs[2])
    # back faces of the shell see 'total internal reflection' (Fresnel = 1) = a solid orange fill: make them transparent
    nt.links.new(geo.outputs['Backfacing'], bmix.inputs['Fac'])
    nt.links.new(mix.outputs['Shader'], bmix.inputs[1])
    nt.links.new(tr.outputs['BSDF'], bmix.inputs[2])
    nt.links.new(bmix.outputs['Shader'], out.inputs['Surface'])
    shell.data.materials.clear()
    shell.data.materials.append(m)
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'BLENDED'
    shell.hide_render = True
    shell.keyframe_insert('hide_render', frame=1)
    return shell


def camera_to_beats(cam_pivot, cam, parts_by_name, beats, focal=135.0, fill=0.45, sensor=36.0, drift_deg=6.0, width_fill=0.7, establish=True):
    """Per beat: hold the current framing until move_f, travel to the part by settle_f (smooth), dwell with a slow
    drift until the next move. Distance puts the part at `fill` of frame height. The first move starts from wherever
    the rig already is (set an opening wide shot before calling)."""
    cam.data.lens = focal
    fov_v = 2 * math.atan((sensor / (16 / 9)) / (2 * focal))
    fov_h = 2 * math.atan(sensor / (2 * focal))
    scene = bpy.context.scene
    todo = []
    first = True
    cur = scene.frame_current
    for b in beats:                       # targets are measured AT the settle frame: parts have exploded away by then
        o = parts_by_name.get(b.get('part'))
        if o is None:
            continue
        scene.frame_set(b['settle_f'])
        bpy.context.view_layer.update()
        lo, hi = bounds_world(list(parts_by_name.values()) if (first and establish) else [o])   # first named part: show the whole exploded assembly
        first = False
        c, ext = (lo + hi) / 2, hi - lo
        # camera looks along +Y: the part's X extent is its width on screen, Z its height. A long thin part (barrel)
        # must be fitted by width, a round one by height (pen test #2: a radius-based distance put the barrel at 3 % height)
        d_h = max(ext.z, 1e-4) / (fill * 2 * math.tan(fov_v / 2))
        d_w = max(ext.x, 1e-4) / (width_fill * 2 * math.tan(fov_h / 2))
        todo.append((b, c.copy(), max(d_h, d_w)))
    scene.frame_set(cur)
    p0, c0 = cam_pivot.location.copy(), cam.location.copy()
    for b, c, dist in todo:
        for ob, path, v in ((cam_pivot, 'location', cam_pivot.location.copy()), (cam, 'location', cam.location.copy())):
            setattr(ob, path, v)                                # hold the framing we leave until move_f
            ob.keyframe_insert(path, frame=b['move_f'])
        key(cam_pivot, 'rotation_euler', b['move_f'], index=2)
        cam_pivot.location = c
        key(cam_pivot, 'location', b['settle_f'])
        cam.location = Vector((0, -dist, dist * 0.25))
        key(cam, 'location', b['settle_f'])
        key(cam_pivot, 'rotation_euler', b['settle_f'], index=2)
        cam_pivot.rotation_euler.z += math.radians(drift_deg)  # never a frozen frame during the dwell
        key(cam_pivot, 'rotation_euler', max(b['settle_f'] + 1, b['end_f'] - 1), index=2)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = cam_pivot
    for ob in (cam_pivot, cam):
        for fc in fcurves_of(ob):
            ease(fc, 'smooth')


def glow_property_beats(parts_by_name, beats, ramp_f=8):
    """Key the 'glow' property 0->1 on the named part from settle_f to dwell_f (rim emission lives in its material)."""
    for o in parts_by_name.values():
        o[GLOW_PROP] = 0.0
        o.keyframe_insert(f'["{GLOW_PROP}"]', frame=1)
    for b in beats:
        o = parts_by_name.get(b.get('part'))
        if not o:
            continue
        end = b.get('dwell_f', b['end_f'])
        for f, v in ((max(1, b['settle_f'] - ramp_f), 0.0), (b['settle_f'], 1.0), (end, 1.0), (end + ramp_f, 0.0)):
            o[GLOW_PROP] = v
            o.keyframe_insert(f'["{GLOW_PROP}"]', frame=f)
    for o in parts_by_name.values():
        for fc in fcurves_of(o):
            if fc.data_path == f'["{GLOW_PROP}"]':
                ease(fc, 'smooth')


def glow_beats(glows_by_name, beats):
    """Glow shell visible from settle_f to dwell_f (or end_f) of each beat that names its part."""
    for b in beats:
        g = glows_by_name.get(b.get('part'))
        if not g:
            continue
        end = b.get('dwell_f', b['end_f'])
        for f, v in ((b['settle_f'] - 1, True), (b['settle_f'], False), (end - 1, False), (end, True)):
            g.hide_render = v
            g.keyframe_insert('hide_render', frame=f)


def _selfcheck_windows():
    beats = [{'part': 'a', 'word_t': 2.0, 'settle_f': 43, 'end_f': 200, 'dwell_f': 120},
             {'part': 'b', 'word_t': 3.5, 'settle_f': 88, 'end_f': 300, 'dwell_f': 250}]
    w = ghost_windows(beats, 30, 0.8)
    assert w[0] == (37, 82, 'a') and w[1] == (82, 250, 'b'), w     # clipped, no overlap
    assert ghost_values(w, 'a', [10, 50, 100, 260]) == [0, 0, 1, 0]
    assert ghost_values(w, 'c', [50, 100, 260]) == [1, 1, 0]
    return True


# ===== image_to_3d.py =====
"""2D image -> 3D relief object (learning/image-to-3d/notes.md), headless.
Manual Knife steps become: alpha silhouette, or a polygon/rectangle list in normalised image UV (0..1)."""
import bpy, bmesh
from mathutils import Vector


def image_plane(path, height=1.0, name=None):
    """Shift+A > Image > Mesh Plane equivalent: Principled, alpha, Linear/Clip, Height (Absolute)."""
    img = bpy.data.images.load(path, check_existing=True)
    w, h = img.size
    width = height * w / max(h, 1)
    name = name or bpy.path.display_name_from_filepath(path)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((x * width, 0, z * height)) for x, z in ((-.5, 0), (.5, 0), (.5, 1), (-.5, 1))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new('UVMap')
    for loop, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = co
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(f'{name}_mat')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image, tex.interpolation, tex.extension = img, 'Linear', 'CLIP'
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.6
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'DITHERED'
    ob.data.materials.append(m)
    return ob, img


def silhouette_from_alpha(ob, img, cells=96, threshold=0.5):
    """Knife-around-the-silhouette + delete outside faces, done by alpha: grid-subdivide, drop transparent cells."""
    import numpy as np
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cells, use_grid_fill=True)
    uv = bm.loops.layers.uv.active
    kill = []
    for f in bm.faces:
        u = sum(l[uv].uv.x for l in f.loops) / len(f.loops)
        v = sum(l[uv].uv.y for l in f.loops) / len(f.loops)
        a = px[min(int(v * h), h - 1), min(int(u * w), w - 1), 3]
        if a < threshold:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bmesh.ops.dissolve_limit(bm, angle_limit=0.01, verts=bm.verts[:], edges=bm.edges[:])
    bm.to_mesh(ob.data)
    bm.free()


def keep_polygon(ob, poly_uv):
    """Knife outline given as UV polygon [(u,v),...]: delete faces whose centre is outside it."""
    def inside(p, poly):
        x, y, c = p[0], p[1], False
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
                c = not c
        return c
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    if len(bm.faces) < 50:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=64, use_grid_fill=True)
    uv = bm.loops.layers.uv.active
    kill = [f for f in bm.faces if not inside((sum(l[uv].uv.x for l in f.loops) / len(f.loops),
                                               sum(l[uv].uv.y for l in f.loops) / len(f.loops)), poly_uv)]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()


def extrude_depth(ob, depth=0.2):
    """A, E: extrude the whole front backwards (+Y) so the object has body; keeps the front UVs."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    verts = [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=verts, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()


def relief_regions(ob, regions):
    """Per feature: knife its rectangle, select, E in/out. regions = [((u0,v0,u1,v1), depth), ...];
    depth < 0 pushes out toward the viewer (-Y), > 0 recesses (windows/doors). Front faces only."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv = bm.loops.layers.uv.active
    for (u0, v0, u1, v1), d in regions:
        sel = []
        for f in bm.faces:
            if f.normal.y > -0.5:
                continue
            u = sum(l[uv].uv.x for l in f.loops) / len(f.loops)
            v = sum(l[uv].uv.y for l in f.loops) / len(f.loops)
            if u0 <= u <= u1 and v0 <= v <= v1:
                sel.append(f)
        if not sel:
            continue
        r = bmesh.ops.extrude_face_region(bm, geom=sel)
        verts = [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0, d, 0))
    bm.to_mesh(ob.data)
    bm.free()


def bevel_all(ob, width=0.004, segments=2):
    """Ctrl+B general bevel as a non-destructive modifier, so edges catch highlights."""
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width, m.segments, m.limit_method = width, segments, 'ANGLE'
    ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
    return m


# ===== mixamo_import.py =====
"""Mixamo FBX workflow: import, scale fix, retarget by bone-name map, NLA clip combining, root motion, blending.
See references/character-mixamo.md for when to use each function."""
import bpy, re

MIXAMO_PREFIX = re.compile(r'^mixamorig\d*:')


def import_mixamo(path, name=None):
    """FBX import settings for Mixamo: no auto bone orientation (keeps the rest pose Mixamo exported),
    primary/secondary axes default (Y/X), animation kept, leaf bones ignored."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, use_anim=True, ignore_leaf_bones=True, automatic_bone_orientation=False,
                             force_connect_children=False, use_custom_normals=True, anim_offset=1.0)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next((o for o in new if o.type == 'ARMATURE'), None)
    if arm and name:
        arm.name = name
        if arm.animation_data and arm.animation_data.action:
            arm.animation_data.action.name = name
    fix_scale(arm, new)
    return arm, new


def fix_scale(arm, objs):
    """Mixamo FBX arrive as cm (armature scale 0.01, or 100x too big). Normalise to 1.0 and apply, keeping
    the animation correct: apply scale on the armature and its meshes together, then scale location curves."""
    if not arm:
        return
    s = arm.scale.x
    if abs(s - 1.0) < 1e-3:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        if o.type in ('ARMATURE', 'MESH'):
            o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    act = arm.animation_data.action if arm.animation_data else None
    if act:
        from_easing = globals().get('fcurves_of')
        fcs = from_easing(arm) if from_easing else list(getattr(act, 'fcurves', []))
        for fc in fcs:
            if fc.data_path.endswith('.location'):
                for k in fc.keyframe_points:
                    k.co.y *= s
                    k.handle_left.y *= s
                    k.handle_right.y *= s


def strip_prefix(arm):
    """'mixamorig:Hips' -> 'Hips' so clips from different downloads (mixamorig1:, mixamorig2:) share names."""
    for b in arm.data.bones:
        b.name = MIXAMO_PREFIX.sub('', b.name)


def retarget(src_arm, dst_arm, bone_map=None, use_location_for=('Hips',)):
    """Constraint retarget: each target bone copies the source bone's rotation (world space); the hips also
    copy location for root motion. Then bake to keyframes with retarget_bake(). bone_map: {dst: src}."""
    bone_map = bone_map or {b.name: MIXAMO_PREFIX.sub('', b.name) for b in dst_arm.pose.bones}
    src_names = {MIXAMO_PREFIX.sub('', b.name): b.name for b in src_arm.pose.bones}
    for pb in dst_arm.pose.bones:
        s = src_names.get(bone_map.get(pb.name, pb.name))
        if not s:
            continue
        c = pb.constraints.new('COPY_ROTATION')
        c.target, c.subtarget, c.name = src_arm, s, 'RT_rot'
        if pb.name in use_location_for:
            c2 = pb.constraints.new('COPY_LOCATION')
            c2.target, c2.subtarget, c2.name = src_arm, s, 'RT_loc'


def retarget_bake(dst_arm, start, end, action_name):
    bpy.ops.object.select_all(action='DESELECT')
    dst_arm.select_set(True)
    bpy.context.view_layer.objects.active = dst_arm
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=start, frame_end=end, only_selected=True, visual_keying=True,
                     clear_constraints=True, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    dst_arm.animation_data.action.name = action_name
    return dst_arm.animation_data.action


def push_to_nla(arm, action, start, track_name=None, blend_in=8, blend_out=8, repeat=1.0, extrapolation='NOTHING'):
    """NLA: one strip per clip; consecutive strips on alternating tracks overlap by blend frames and
    cross-fade with blend_in/blend_out (or use_auto_blend)."""
    ad = arm.animation_data or arm.animation_data_create()
    tr = ad.nla_tracks.get(track_name) if track_name else None
    tr = tr or ad.nla_tracks.new()
    if track_name:
        tr.name = track_name
    st = tr.strips.new(action.name, int(start), action)
    st.blend_in, st.blend_out, st.repeat = blend_in, blend_out, repeat
    st.extrapolation, st.blend_type = extrapolation, 'REPLACE'
    if hasattr(st, 'use_auto_blend'):
        st.use_auto_blend = False
    ad.action = None
    return st


def sequence_clips(arm, actions, start=1, overlap=8):
    """walk -> run -> stop: strips on alternating tracks A/B, each overlapping the previous by `overlap`."""
    f = start
    strips = []
    for i, act in enumerate(actions):
        st = push_to_nla(arm, act, f, track_name='A' if i % 2 == 0 else 'B', blend_in=overlap if i else 0,
                         blend_out=overlap)
        strips.append(st)
        f = st.frame_end - overlap
    return strips


def in_place(action, root='Hips', axes=(0, 1)):
    """Remove root motion on X/Y (keep Z bob) for in-place loops; move the character with an object path
    instead. Use Mixamo's 'In Place' checkbox when available - this is the fallback."""
    for fc in getattr(action, 'fcurves', []):
        if fc.data_path == f'pose.bones["{root}"].location' and fc.array_index in axes:
            first = fc.keyframe_points[0].co.y if fc.keyframe_points else 0
            for k in fc.keyframe_points:
                k.co.y = first
                k.handle_left.y = first
                k.handle_right.y = first


# ===== review.py =====
"""Self-review helpers: render N preview frames spread over the timeline and audit every F-curve.
Needs easing_presets.py loaded first (fcurves_of)."""
import bpy, json, os


def review_frames(scene, n=6, start=None, end=None):
    s, e = start or scene.frame_start, end or scene.frame_end
    if n == 1:
        return [s]
    return sorted({int(round(s + (e - s) * i / (n - 1))) for i in range(n)})


def render_review(scene, folder, frames, prefix='review'):
    os.makedirs(folder, exist_ok=True)
    paths = []
    for f in frames:
        scene.frame_set(f)
        p = os.path.join(folder, f'{prefix}_{f:04d}.png')
        im = scene.render.image_settings
        if hasattr(im, 'media_type'):
            im.media_type = 'IMAGE'
        im.file_format = 'PNG'
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    return paths


def audit_fcurves(objects=None):
    """Flags: LINEAR/CONSTANT segments (unless the object is tagged allow_linear), single-key curves,
    velocity jumps at pass-through keys (the 'bump'), and segments faster than 1/3 of the shot length allows.
    Returns a dict suitable for result['fcurve_audit']."""
    rep = {'curves': 0, 'linear_segments': [], 'bumps': [], 'single_key': []}
    owners = objects or [o for o in bpy.data.objects]
    owners = list(owners) + [k for k in bpy.data.shape_keys]
    for o in owners:
        for fc in fcurves_of(o):
            rep['curves'] += 1
            pts = fc.keyframe_points
            tag = f'{getattr(o, "name", "?")}:{fc.data_path}[{fc.array_index}]'
            if len(pts) == 1:
                rep['single_key'].append(tag)
            allow = isinstance(o, bpy.types.Object) and o.get('allow_linear')
            for i in range(len(pts) - 1):
                if pts[i].interpolation in ('LINEAR', 'CONSTANT') and not allow and pts[i].co.y != pts[i + 1].co.y:
                    rep['linear_segments'].append(f'{tag} @ {pts[i].co.x:.0f}')
            for i in range(1, len(pts) - 1):
                p, k, n = pts[i - 1], pts[i], pts[i + 1]
                if (k.co.y - p.co.y) * (n.co.y - k.co.y) <= 0:
                    continue  # extreme or hold: a flat key is correct there
                eps = 0.5
                v_in = (fc.evaluate(k.co.x) - fc.evaluate(k.co.x - eps)) / eps
                v_out = (fc.evaluate(k.co.x + eps) - fc.evaluate(k.co.x)) / eps
                avg = abs(n.co.y - p.co.y) / max(n.co.x - p.co.x, 1e-6)
                if avg > 1e-6 and (abs(v_in) < 0.25 * avg or abs(v_out) < 0.25 * avg):
                    rep['bumps'].append(f'{tag} @ {k.co.x:.0f}')
    rep['ok'] = not rep['linear_segments'] and not rep['bumps']
    return rep


def check_framing(scene, objects, frames, margin=0.02):
    """Project every object's bound-box corners through the scene camera at each frame. Fails fast (before any
    render) if the camera points away, the subject is clipped, or parts leave the frame.
    Returns {'ok': bool, 'problems': [...]}. Run it after building the rig, on the review frames."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    cam, problems = scene.camera, []
    if cam is None:
        return {'ok': False, 'problems': ['no scene camera']}
    for f in frames:
        scene.frame_set(f)
        for o in objects:
            pts = [world_to_camera_view(scene, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
            if all(p.z <= 0 for p in pts):
                problems.append(f'f{f} {o.name}: behind camera')
                continue
            lo_x, hi_x = min(p.x for p in pts), max(p.x for p in pts)
            lo_y, hi_y = min(p.y for p in pts), max(p.y for p in pts)
            if hi_x < 0 or lo_x > 1 or hi_y < 0 or lo_y > 1:
                problems.append(f'f{f} {o.name}: fully outside frame')
            elif lo_x < margin or hi_x > 1 - margin or lo_y < margin or hi_y > 1 - margin:
                problems.append(f'f{f} {o.name}: touches/crosses frame edge')
    return {'ok': not problems, 'problems': problems[:30]}


def fill_fraction(scene, objects, frame):
    """Share of the frame width/height the union of `objects` covers at `frame`. A frame passes framing only if
    the subject is inside AND big enough: Phase-5 v2 'passed' check_framing with the subject at ~10 % of the frame."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    scene.frame_set(frame)
    xs, ys = [], []
    for o in objects:
        for c in o.bound_box:
            p = world_to_camera_view(scene, scene.camera, o.matrix_world @ Vector(c))
            xs.append(p.x)
            ys.append(p.y)
    return {'w': round(max(xs) - min(xs), 2), 'h': round(max(ys) - min(ys), 2)}


def sample_pixel(path, x, y_top, r=3):
    """Average sRGB (0-1) around normalised image point (x from left, y_top from top). Use to assert that a part
    renders the colour it was given (a red part must be red), before spending minutes on the final render."""
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    cx, cy = int(min(max(x, 0), 0.999) * w), int(min(max(1 - y_top, 0), 0.999) * h)
    win = a[max(cy - r, 0):cy + r + 1, max(cx - r, 0):cx + r + 1, :3].reshape(-1, 3).mean(axis=0)
    bpy.data.images.remove(img)
    return [round(float(v), 3) for v in win]


def write_report(folder, data):
    with open(os.path.join(folder, 'review.json'), 'w') as fh:
        json.dump(data, fh, indent=1)
"""Temple wearable, stylised 3D illustration. Shape from the reference picture: a plump kidney-bean pebble, smooth
champagne gold, a dent along one long edge, no panel lines. No public dimensions exist: label it a 3D illustration.
Modelled at 10:1 (shell 0.34 x ~0.19 x 0.043 m). Local frame: +Z outer face, skin side z = 0, +Y is the convex edge,
-Y the dented edge. temple_device() -> {part_name: object}, skin side first (assembly order for the exploded view).
Visual layers only (no feature claims): pad, optical module (3 emitters + photodiode), foam ring, flexible PCB, chips,
antenna loops, battery pouch, shell."""
import bpy, bmesh, math
from mathutils import Vector

GOLD = (1.0, 0.76, 0.32)          # #FFE29A in linear light (True Gold)
A0, B0, BEND, PW = 0.17, 0.085, 0.026, 2.4       # half length, half width, how far the middle bows, superellipse power


def _pbr(name, base, metallic=0.0, rough=0.4, emit=None, estr=0.0, coat=0.0, trans=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*base, 1.0)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = rough
    if coat:
        p.inputs['Coat Weight'].default_value = coat
    if trans:
        p.inputs['Transmission Weight'].default_value = trans
    if emit is not None:
        p.inputs['Emission Color'].default_value = (*emit, 1.0)
        p.inputs['Emission Strength'].default_value = estr
    return m


def _pcb_material():
    """Fibreglass green (#0F2C11-ish, roughness 0.4) with raised gold traces: Voronoi edge distance -> ColorRamp (crisp) drives
    the base colour (green -> #FFD700), Metallic and a Bump on the Normal. Object coordinates, so the PCB needs no UVs."""
    m = bpy.data.materials.new('PCB Traces')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.4
    tc = N.new('ShaderNodeTexCoord')
    vor = N.new('ShaderNodeTexVoronoi')
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 110.0
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (1, 1, 1, 1)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.012, (0, 0, 0, 1)   # thin traces: 0.07 was ~all gold
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    ins = [i for i in mix.inputs if i.type == 'RGBA']
    ins[0].default_value = (0.01, 0.06, 0.015, 1)        # forest green fibreglass
    ins[1].default_value = (1.0, 0.68, 0.0, 1)           # #FFD700 traces
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value, bump.inputs['Distance'].default_value = 0.5, 0.002
    L.new(tc.outputs['Object'], vor.inputs['Vector'])
    L.new(vor.outputs['Distance'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], mix.inputs['Factor'])
    L.new([o for o in mix.outputs if o.type == 'RGBA'][0], p.inputs['Base Color'])
    L.new(ramp.outputs['Color'], p.inputs['Metallic'])
    L.new(ramp.outputs['Color'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def _finish(o, mat, bevel, seg=3):
    for poly in o.data.polygons:
        poly.use_smooth = True
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL')
        bv.width, bv.segments, bv.limit_method, bv.angle_limit = bevel, seg, 'ANGLE', math.radians(35)
        bv.harden_normals = True
    o.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL').keep_sharp = True
    o.data.materials.clear()
    o.data.materials.append(mat)
    for poly in o.data.polygons:
        poly.material_index = 0
    return o


def _bean(name, k, depth, z0, mat, bevel=0.0, seg=3, n=160, curl=0.0, dy=0.0):
    """Bean slab: outline = superellipse (half sizes A0*k[0], B0*k[1]) bowed by BEND*k[2] (middle pushed to +Y, so the
    -Y edge is dented), extruded `depth` from z0. curl bends the ends down (a flexible part following the temple)."""
    a, b, bend = A0 * k[0], B0 * k[1], BEND * k[2]
    bm = bmesh.new()
    vs = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / PW), c)
        y = b * math.copysign(abs(s) ** (2 / PW), s)
        y += bend * (1 - (x / a) ** 2) + dy
        vs.append(bm.verts.new((x, y, -curl * (x / a) ** 2)))
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, depth))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location.z = z0
    return _finish(o, mat, bevel, seg)


def _pillow(name, z0, mat, h_side=0.010, h_dome=0.034, n=200, rings=22):
    """The shell: the bean outline lofted as rings (rounded flat bottom, near-vertical sides, a smooth dome), capped top and
    bottom. No bevel: the dome gives the whole face a soft gradient like the reference picture."""
    a, b, bend = A0, B0, BEND
    base = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / PW), c)
        y = b * math.copysign(abs(s) ** (2 / PW), s) + bend * (1 - (x / a) ** 2) * 1.0
        base.append((x, y))
    cy = sum(p[1] for p in base) / n
    prof = [(0.965, 0.0), (0.99, 0.0012), (1.0, 0.004), (1.0, h_side)]
    for j in range(1, rings + 1):
        ph = j * math.radians(80) / rings
        prof.append((math.cos(ph) ** 0.9, h_side + h_dome * math.sin(ph)))
    bm = bmesh.new()
    R = [[bm.verts.new((x * s, cy + (y - cy) * s, z)) for (x, y) in base] for (s, z) in prof]
    for j in range(len(R) - 1):
        for i in range(n):
            bm.faces.new([R[j][i], R[j][(i + 1) % n], R[j + 1][(i + 1) % n], R[j + 1][i]])
    bm.faces.new(R[0][::-1])
    bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location.z = z0
    return _finish(o, mat, 0.0)


def _cyl(name, r, d, loc, mat, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc)
    o = bpy.context.object
    o.name = name
    return _finish(o, mat, 0.0)


def _box(name, size, loc, mat, bevel=0.0, seg=2):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, bevel, seg)


def _hole(target, cutter):
    cutter.display_type, cutter.hide_render = 'WIRE', True
    cutter.parent = target
    bo = target.modifiers.new('Hole', 'BOOLEAN')
    bo.object, bo.operation, bo.solver = cutter, 'DIFFERENCE', 'EXACT'
    target.modifiers.move(len(target.modifiers) - 1, 0)


def temple_device():
    gold = _pbr('Shell Gold', GOLD, metallic=1.0, rough=0.15)      # True Gold #FFE29A, roughness in the 0.05-0.15 mirror range
    pad_m = _pbr('Adhesive Pad', (0.06, 0.06, 0.07), rough=0.45, trans=0.55)          # semi-translucent skin pad
    glass = _pbr('Optical Glass', (0.012, 0.008, 0.012), rough=0.06, coat=1.0)
    foam = _pbr('Foam Black', (0.01, 0.01, 0.011), rough=0.9)
    pcb_m = _pcb_material()
    chip = _pbr('Chip Black', (0.015, 0.015, 0.018), metallic=0.3, rough=0.35)
    copper = _pbr('Antenna Copper', (0.95, 0.52, 0.38), metallic=1.0, rough=0.3)
    batt = _pbr('Battery Silver', (0.62, 0.64, 0.66), metallic=1.0, rough=0.32)
    led_g = _pbr('LED Green', (0.0, 0.2, 0.02), emit=(0.1, 1.0, 0.15), estr=8.0)
    led_r = _pbr('LED Red', (0.2, 0.0, 0.0), emit=(1.0, 0.05, 0.03), estr=8.0)
    led_i = _pbr('LED Infrared', (0.12, 0.0, 0.08), emit=(0.75, 0.0, 0.35), estr=8.0)   # IR is invisible: shown deep magenta by convention
    diode = _pbr('Photodiode', (0.03, 0.03, 0.05), metallic=0.5, rough=0.2)

    P = {}
    P['optical_window'] = _box('optical_window', (0.135, 0.05, 0.006), (0.0, 0.0, -0.0005), glass, bevel=0.004)
    P['led_green'] = _cyl('led_green', 0.0075, 0.003, (-0.062, 0.0, -0.0036), led_g)
    P['led_red'] = _cyl('led_red', 0.0075, 0.003, (-0.038, 0.0, -0.0036), led_r)
    P['led_infrared'] = _cyl('led_infrared', 0.0075, 0.003, (-0.014, 0.0, -0.0036), led_i)
    P['photodiode'] = _box('photodiode', (0.02, 0.02, 0.003), (0.045, 0.0, -0.0036), diode, bevel=0.0008)
    P['adhesive_pad'] = _bean('adhesive_pad', (0.93, 0.88, 1.0), 0.0045, 0.0, pad_m, bevel=0.001)
    P['foam_ring'] = _bean('foam_ring', (0.88, 0.76, 1.0), 0.008, 0.0125, foam, bevel=0.0008)
    _hole(P['foam_ring'], _bean('foam_cut', (0.68, 0.46, 1.0), 0.02, -0.002, foam))      # z0 is RELATIVE to the parent (foam_ring z0 0.0125)
    P['pcb'] = _bean('pcb', (0.85, 0.7, 1.0), 0.0035, 0.021, pcb_m, bevel=0.0006, curl=0.006)
    P['antenna'] = _bean('antenna', (0.83, 0.68, 1.0), 0.0009, 0.0245, copper)
    _hole(P['antenna'], _bean('antenna_cut', (0.8, 0.64, 1.0), 0.01, -0.001, copper))    # relative to antenna z0 0.0245
    P['heart_rate_sensor'] = _box('heart_rate_sensor', (0.026, 0.026, 0.004), (-0.075, 0.016, 0.0275), chip, bevel=0.0008)
    P['motion_sensor'] = _box('motion_sensor', (0.02, 0.02, 0.004), (0.035, 0.036, 0.0275), chip, bevel=0.0008)
    P['thermometer'] = _box('thermometer', (0.016, 0.016, 0.004), (0.09, 0.012, 0.0275), chip, bevel=0.0008)
    P['processor'] = _box('processor', (0.032, 0.032, 0.005), (-0.02, -0.004, 0.028), chip, bevel=0.001)
    P['battery'] = _bean('battery', (0.5, 0.36, 0.7), 0.011, 0.031, batt, bevel=0.004, seg=3)
    P['shell'] = _pillow('shell', 0.0125, gold)
    return P
# Chapter 4 (How Temple works), 89.92 -> 129.37 s = 39.45 s = 1184 frames @ 30. Device lies flat, shell lifts first, the layers
# slide apart along Z (top-down order), the three emitters pulse like a heartbeat while the PPG explanation is spoken, then it
# re-assembles before the cut. Camera: elevated 3/4 orbit + slow push. Runs after skilllib.py + temple_model.py in one file.
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
FPS = 30
END = int(round(A.get('duration_s', 39.45) * FPS))
scene.frame_start, scene.frame_end = 1, END

P = temple_device()
parts = list(P.values())
LIFT = 0.06                                   # the optical module sinks 0.05 below the pad: keep everything above the floor
for o in parts:
    o.location.z += LIFT
bpy.context.view_layer.update()
# the whole stack hangs on one pivot so it can tip toward the camera (underside + emitters) while the light is explained
asm = bpy.data.objects.new('assembly', None)
scene.collection.objects.link(asm)
asm.location = (0.0, -0.02, 0.16)
bpy.context.view_layer.update()
for o in parts:
    o.parent = asm
    o.matrix_parent_inverse = asm.matrix_world.inverted()      # local location keeps its world value; explode keys stay in world axes while untilted

# explode plan (metres along Z, world space), top-down order so the shell opens first
order_names = ['shell', 'battery', 'processor', 'heart_rate_sensor', 'motion_sensor', 'thermometer', 'antenna', 'pcb',
               'foam_ring', 'adhesive_pad', 'optical_window', 'led_green', 'led_red', 'led_infrared', 'photodiode']
dist = {'shell': 0.26, 'battery': 0.17, 'processor': 0.115, 'heart_rate_sensor': 0.115, 'motion_sensor': 0.115,
        'thermometer': 0.115, 'antenna': 0.10, 'pcb': 0.085, 'foam_ring': 0.045, 'adhesive_pad': 0.0,
        'optical_window': 0.05, 'led_green': 0.05, 'led_red': 0.05, 'led_infrared': 0.05, 'photodiode': 0.05}
axes = {n: Vector((0, 0, 1)) for n in order_names}
axes['adhesive_pad'] = Vector((0, 0, 0))
for n in ('optical_window', 'led_green', 'led_red', 'led_infrared', 'photodiode'):
    axes[n] = Vector((0, 0, -1))
order = [P[n] for n in order_names]
n = len(order)
START, HOLD_IN, EXP, STAG, RET = 30, 40, 54, 10, 54
t0 = START + HOLD_IN
hold = END - 30 - (t0 + 2 * (n - 1) * STAG + EXP + RET)
last = explode(parts, axes=axes, start=START, assembled_hold=HOLD_IN, explode_len=EXP, stagger=STAG, hold=hold,
               return_len=RET, preset='smooth', order=order, distances=dist)

# emitters: a heartbeat pulse (strength 3 -> 10 -> 3) every 33 frames from the first PPG word (frame 296) to the end of the chapter
for mname, phase in (('LED Green', 0), ('LED Red', 4), ('LED Infrared', 8)):
    sock = bpy.data.materials[mname].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    sock.default_value = 0.0
    sock.keyframe_insert('default_value', frame=1)
    sock.keyframe_insert('default_value', frame=285 + phase)
    f = 296 + phase
    while f + 24 < END - 10:
        for ff, v in ((f, 3.0), (f + 8, 10.0), (f + 22, 3.0)):
            sock.default_value = v
            sock.keyframe_insert('default_value', frame=ff)
        f += 33
    sock.default_value = 0.0
    sock.keyframe_insert('default_value', frame=END)

# tip the stack toward the camera so the underside emitters face it: 0 -> -62 deg over f290-380 (the light explanation starts at f296),
# hold, then back to 0 over f900-1010 as the layers re-assemble
for f, deg in ((1, 0), (290, 0), (380, -62), (900, -62), (1010, 0), (END, 0)):
    asm.rotation_euler.x = math.radians(deg)
    key(asm, 'rotation_euler', f, tuple(asm.rotation_euler), index=0)
for fc in fcurves_of(asm):
    if fc.data_path == 'rotation_euler' and fc.array_index == 0:
        for i in range(len(fc.keyframe_points) - 1):
            ease_segment(fc, i, 0.4, 0.4)

c = Vector((0.0, -0.02, 0.10 + LIFT))
rh = 0.20
r = 0.30
cyclorama(size=r * 60, height=r * 24, bevel=r * 8, color=(0.0045, 0.0045, 0.0045), roughness=0.9)
hdri_world(A.get('hdri', '/library/hdri/environments-skies/Assets/Skies/Studio/photo_studio_01_4k.hdr'),
           strength=0.85, rotation_deg=30, color=(0.0116, 0.0116, 0.0116), background_strength=1.0)
d = frame_distance(rh, 70, fill=0.60)               # sized for the fully exploded stack at factor 1.0
piv, cam = make_orbit_rig(c, distance=d, height=d * 0.45, focal=70, name='explode', fstop=8.0)
orbit(piv, 1, END, 40, preset='ease_in_out')
dolly(cam, [(1, 0.5), (100, 0.5), (230, 1.0), (430, 0.62), (900, 0.62), (1010, 0.9), (1150, 0.5), (END, 0.5)],
      preset='ease_in_out')   # close on the assembled device, out for the explode, IN on the emitters while the light is explained, back out, close for the cut
bind_camera(scene, cam, 1)
scene.camera = cam
three_point(c, r, camera=cam, key_power=190.0 * r * r)

render_preset(scene, 'preview', res=tuple(A.get('res', [1920, 1080])), fps=FPS)
scene.cycles.samples = 32
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.2
gate = [1, 200, 330, 420, 600, 760, 900, END]
fills = {f: fill_fraction(scene, parts, f) for f in gate}
framing = check_framing(scene, parts, gate)
size_ok = fills[1]['h'] >= 0.25 and all(v['h'] <= 1.0 and v['w'] <= 0.97 for v in fills.values())
result.update(fills=fills, framing=framing, size_ok=size_ok, audit=audit_fcurves(), last_key=last, hold=hold,
              out_frames={o.name: o.get('explode_out_frame') for o in parts})
render_review(scene, out, gate)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'ch4.blend'), copy=True)
if A.get('mode') == 'final' and size_ok:
    scene.render.resolution_percentage = 100
    scene.cycles.samples = A.get('samples', 96)
    video_output(scene, os.path.join(out, 'plate.mp4'))
    bpy.ops.render.render(animation=True)
    result['plate'] = 'plate.mp4'
