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
