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
