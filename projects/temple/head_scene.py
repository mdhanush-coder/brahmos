# head_scene.py - the Temple anatomy scene (user reference 2026-11-07): a translucent blue x-ray head, a pink folded brain covered
# in red arteries, blue veins under the skin, the eye, the gold Temple device on the temple sending a coloured light cone into the
# head, and a glowing yellow vessel path (the superficial temporal artery). Built for Eevee. Needs skilllib + temple_model loaded
# and place_asset (EngineX runtime). Everything random is seeded, so every build is identical.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

HEAD_ASSET = 'dxm-v11-015-mannequin-male'


def _nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt, nt.nodes, nt.links


def _xray_mat(name, rim=(0.25, 0.55, 1.0), core_alpha=0.025, rim_strength=1.5, power=3.2):
    """Hologram glass: nearly clear in the middle, glowing blue where the surface turns away from the camera."""
    m = bpy.data.materials.new(name)
    nt, N, L = _nodes(m)
    out = N.new('ShaderNodeOutputMaterial')
    geo = N.new('ShaderNodeNewGeometry')
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    L.new(geo.outputs['Normal'], dot.inputs[0]); L.new(geo.outputs['Incoming'], dot.inputs[1])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(dot.outputs['Value'], ab.inputs[0])
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(ab.outputs[0], inv.inputs[1])
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power; L.new(inv.outputs[0], pw.inputs[0])
    gain = N.new('ShaderNodeMath'); gain.operation = 'MULTIPLY_ADD'; gain.inputs[1].default_value = 1.0; gain.inputs[2].default_value = core_alpha
    L.new(pw.outputs[0], gain.inputs[0])
    fac = N.new('ShaderNodeMath'); fac.operation = 'MINIMUM'; fac.inputs[1].default_value = 1.0; L.new(gain.outputs[0], fac.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*rim, 1); em.inputs['Strength'].default_value = rim_strength
    tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader')
    L.new(fac.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    m.use_backface_culling = False
    return m


def _emit_mat(name, color, strength, base=None, rough=0.35):
    m = bpy.data.materials.new(name)
    nt, N, L = _nodes(m)
    out = N.new('ShaderNodeOutputMaterial')
    b = N.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*(base or color), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    L.new(b.outputs[0], out.inputs['Surface'])
    return m


def _brain_mat():
    """Pink tissue, darker red-brown in the folds (the 'groove' colour attribute written by _fold())."""
    m = bpy.data.materials.new('Brain')
    nt, N, L = _nodes(m)
    out = N.new('ShaderNodeOutputMaterial')
    b = N.new('ShaderNodeBsdfPrincipled')
    attr = N.new('ShaderNodeAttribute'); attr.attribute_name = 'groove'
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.86, 0.50, 0.52, 1)     # gyri: pink
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.42, 0.12, 0.14, 1)     # sulci: deep red
    L.new(attr.outputs['Fac'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.55
    if 'Subsurface Weight' in b.inputs:
        b.inputs['Subsurface Weight'].default_value = 0.35
        b.inputs['Subsurface Radius'].default_value = (0.012, 0.004, 0.003)
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 0.08          # a wet sheen
    L.new(b.outputs[0], out.inputs['Surface'])
    return m


def _light_cone_mat(name='Light Cone'):
    """Coloured light from the device: bright at the device, fading into the head (alpha along the cone)."""
    m = bpy.data.materials.new(name)
    nt, N, L = _nodes(m)
    out = N.new('ShaderNodeOutputMaterial')
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1)
    ramp.color_ramp.elements[1].color = (0.06, 0.06, 0.06, 1)
    L.new(sep.outputs['Z'], ramp.inputs['Fac'])
    em = N.new('ShaderNodeEmission'); em.name = 'Emission'
    em.inputs['Color'].default_value = (0.17, 0.83, 0.35, 1); em.inputs['Strength'].default_value = 6.0
    tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader')
    L.new(ramp.outputs['Color'], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    m.use_backface_culling = False
    return m


def _link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


# ---------------------------------------------------------------- head
def _procedural_head():
    """A stylised hologram head (no real face): cranium, jaw, chin, nose, ears and neck as overlapping blobs merged by a
    voxel remesh. Face toward -Y, +Z up, origin at the middle of the head (eye level z=0, crown z=+0.115, neck to -0.23)."""
    bm = bmesh.new()
    blobs = [((0, 0.012, 0.012), (0.078, 0.095, 0.103)), ((0, -0.020, -0.050), (0.062, 0.070, 0.062)),
             ((0, -0.050, -0.095), (0.030, 0.030, 0.025)), ((0, -0.088, -0.022), (0.011, 0.020, 0.028)),
             ((0.079, 0.018, -0.012), (0.008, 0.017, 0.025)), ((-0.079, 0.018, -0.012), (0.008, 0.017, 0.025))]
    for c, r in blobs:
        g = bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
        for v in g['verts']:
            v.co = Vector((v.co.x * r[0] + c[0], v.co.y * r[1] + c[1], v.co.z * r[2] + c[2]))
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.047, radius2=0.043, depth=0.19)
    for v in g['verts']:
        v.co = Vector((v.co.x, v.co.y + 0.028, v.co.z - 0.135))
    me = bpy.data.meshes.new('HeadBlobs'); bm.to_mesh(me); bm.free()
    ob = _link(bpy.data.objects.new('Head', me))
    rm = ob.modifiers.new('merge', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.0022
    dg = bpy.context.evaluated_depsgraph_get()
    merged = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.remove(rm)
    ob.data = merged
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def _slice(ob, z, band=0.006):
    pts = [v.co for v in ob.data.vertices if abs(v.co.z - z) < band]
    return (max(abs(p.x) for p in pts), min(p.y for p in pts), max(p.y for p in pts))


# ---------------------------------------------------------------- brain
def _fold(bm, center, freq=120.0, depth=0.0032, warp=0.55):
    """Gyri: grooves along Voronoi cell edges (F2 - F1 small), warped by turbulence so they curl like real folds.
    Writes the groove strength (0 gyrus .. 1 sulcus) into the 'groove' colour attribute for the shader."""
    col = bm.loops.layers.float_color.new('groove')
    val = {}
    bm.normal_update()
    for v in bm.verts:
        p = (v.co - center) * freq
        p = p + noise.turbulence_vector(p * 0.35, 2, False) * warp * 3.0
        d, _ = noise.voronoi(p, distance_metric='DISTANCE')
        g = math.exp(-((d[1] - d[0]) / 0.22) ** 2)
        val[v] = g
        v.co -= v.normal * depth * g
    for f in bm.faces:
        for lp in f.loops:
            g = val[lp.vert]
            lp[col] = (g, g, g, 1)


def _ellipsoid(name, center, axes, segs=(256, 160), shape=None, half=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        if shape:
            x, y, z = shape(x, y, z)
        v.co = Vector((x * axes[0], y * axes[1], z * axes[2]))
    if half:   # keep x >= 0 (one hemisphere; a Mirror modifier makes the other with a gap = the longitudinal fissure)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(-1, 0, 0), clear_inner=True)
        edges = [e for e in bm.edges if e.is_boundary]
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(half, 0, 0))
    return bm


def _brain(c, ax):
    """Cerebrum (two hemispheres, folded), cerebellum (banded), brainstem."""
    def shape(x, y, z):   # flatter underneath (temporal lobes), narrower at the front, fuller at the back
        z = z if z > 0 else z * 0.78
        x = x * (1.0 - 0.14 * max(0.0, -y))
        return x, y, z
    bm = _ellipsoid('Cerebrum', c, ax, shape=shape, half=0.0026)
    _fold(bm, Vector((0, 0, 0)))
    me = bpy.data.meshes.new('Cerebrum'); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    cer = _link(bpy.data.objects.new('Cerebrum', me))
    cer.location = c
    mir = cer.modifiers.new('fissure', 'MIRROR'); mir.use_axis[0] = True
    mat = _brain_mat()
    cer.data.materials.append(mat)
    # cerebellum: under the back of the cerebrum, horizontal folia
    cc = c + Vector((0, ax[1] * 0.62, -ax[2] * 0.62))
    bm = _ellipsoid('Cerebellum', cc, (ax[0] * 0.62, ax[1] * 0.30, ax[2] * 0.36), segs=(160, 100))
    col = bm.loops.layers.float_color.new('groove')
    bm.normal_update()
    vv = {}
    for v in bm.verts:
        g = max(0.0, math.sin(v.co.z * 520.0 + v.co.y * 60.0)) ** 6
        vv[v] = g
        v.co -= v.normal * 0.0012 * g
    for f in bm.faces:
        for lp in f.loops:
            lp[col] = (vv[lp.vert],) * 3 + (1,)
    me = bpy.data.meshes.new('Cerebellum'); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    cbl = _link(bpy.data.objects.new('Cerebellum', me)); cbl.location = cc
    cbl.data.materials.append(mat)
    # brainstem: a tapered tube down into the neck
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.0075, radius2=0.010, depth=0.06,
                                    location=c + Vector((0, ax[1] * 0.25, -ax[2] - 0.035)))
    stem = bpy.context.active_object; stem.name = 'Brainstem'
    bpy.ops.object.shade_smooth()
    stem.data.materials.append(mat)
    return cer, cbl, stem


# ---------------------------------------------------------------- vessels
def _tree_curve(name, mat, roots, surface, rng, offset, steps=(22, 12, 6), step=0.0042, r0=0.0011, branch_p=0.16,
                turn=0.55, up=None, bounds=None):
    """Branching vessels grown over a surface: each segment steps along the surface, turns a little, sometimes forks;
    radius tapers by generation. surface = (BVHTree, object matrix). Returns one curve object."""
    bvh, mw = surface
    inv = mw.inverted()
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 1.0; cu.bevel_resolution = 2; cu.use_fill_caps = True

    def snap(p):
        loc, nrm, _, _ = bvh.find_nearest(inv @ p)
        if loc is None:
            return p, Vector((0, 0, 1))
        n = (mw.to_3x3() @ nrm).normalized()
        return mw @ loc + n * offset, n

    def grow(p, d, gen, rad):
        pts = []
        p, n = snap(p)
        for i in range(steps[min(gen, len(steps) - 1)]):
            pts.append((p.copy(), rad * (1 - 0.6 * i / steps[min(gen, len(steps) - 1)])))
            d = (d - n * d.dot(n)).normalized()
            side = n.cross(d)
            d = (d + side * rng.uniform(-turn, turn) + (up * 0.25 if up is not None else Vector())).normalized()
            p, n = snap(p + d * step)
            if bounds and not bounds(p):
                break
            if gen < len(steps) - 1 and i > 2 and rng.random() < branch_p:
                nd = (d + side * rng.choice((-1, 1)) * rng.uniform(0.6, 1.2)).normalized()
                grow(p, nd, gen + 1, rad * 0.62)
        if len(pts) > 1:
            sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
            for k, (q, r) in enumerate(pts):
                sp.points[k].co = (q.x, q.y, q.z, 1); sp.points[k].radius = r
    for p, d in roots:
        grow(Vector(p), Vector(d).normalized(), 0, r0)
    ob = _link(bpy.data.objects.new(name, cu))
    ob.data.materials.append(mat)
    return ob


def _bvh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(ob, dg), ob.matrix_world.copy()


# ---------------------------------------------------------------- the whole scene
def build_head_scene(face=None, seed=7):
    rng = random.Random(seed)
    head = _procedural_head()
    head.data.materials.append(_xray_mat('Head XRay'))
    front, size = '-Y', tuple(head.dimensions)
    top = 0.115
    zE = 0.0
    hb = _bvh(head)
    W, yF, yB = _slice(head, zE + 0.03)
    # brain: fills the cranium above the eye line, leaves the skull's thickness
    cz = 0.045
    ax = (W * 0.80, (yB - yF) * 0.40, max(0.04, top - 0.022 - cz))
    c = Vector((0, (yF + yB) / 2 + 0.012, cz))
    cer, cbl, stem = _brain(c, ax)
    # both eyes (x = +/-3.2 cm), each just under the front surface (found by a ray from the front)
    eyes = []
    for sx in (1, -1):
        ex = 0.032 * sx
        hit_e, _, _, _ = hb[0].ray_cast(Vector((ex, -0.5, zE)), Vector((0, 1, 0)))
        eye_c = Vector((ex, (hit_e.y if hit_e else yF) + 0.009, zE))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.0098, location=eye_c)
        e = bpy.context.active_object; e.name = 'Eye' if sx > 0 else 'Eye_L'; bpy.ops.object.shade_smooth()
        e.data.materials.append(_emit_mat('Sclera', (0.92, 0.94, 0.97), 0.15, rough=0.15))
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0056, depth=0.0012, location=eye_c + Vector((0, -0.0114, 0)),
                                            rotation=(math.pi / 2, 0, 0))
        iris = bpy.context.active_object; iris.name = 'Iris' if sx > 0 else 'Iris_L'
        iris.data.materials.append(_emit_mat('Iris', (0.18, 0.32, 0.45), 0.2))
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0026, depth=0.0014, location=eye_c + Vector((0, -0.0118, 0)),
                                            rotation=(math.pi / 2, 0, 0))
        pupil = bpy.context.active_object; pupil.name = 'Pupil' if sx > 0 else 'Pupil_L'
        pupil.data.materials.append(_emit_mat('Pupil', (0.01, 0.01, 0.012), 0.0, rough=0.05))
        eyes.append(e)
    eye = eyes[0]
    # device: ray-cast onto the temple (behind and above the eye), pad against the skin, longest side 5.5 cm
    hb = _bvh(head)
    probe = Vector((0.3, -0.012, zE + 0.022))
    hit, nrm, _, _ = hb[0].ray_cast(probe, Vector((-1, 0, 0)))
    nrm = nrm.normalized() if nrm.x > 0 else Vector((1, 0, 0))
    P = temple_device()
    roots = [o for o in P.values() if o.parent is None]
    rig = _link(bpy.data.objects.new('DeviceRig', None))
    bpy.context.view_layer.update()
    for o in roots:
        o.parent = rig
    lo, hi = bounds_world(list(P.values()))
    k = 0.055 / max(hi - lo)
    rig.scale = (k, k, k)
    rig.location = hit + nrm * 0.002 - Vector((0, 0, lo.z * k))
    rig.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    # light cone from the device into the head (toward the brain), along -normal
    depth = 0.055
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.004, radius2=0.022, depth=depth, end_fill_type='NOTHING')
    cone = bpy.context.active_object; cone.name = 'LightCone'
    cone.rotation_euler = (-nrm).to_track_quat('Z', 'Y').to_euler()
    cone.location = hit - nrm * (depth / 2 - 0.002)
    cone.data.materials.append(_light_cone_mat())
    # arteries over the brain surface (red), seeded along the lateral fissure on both sides and over the top
    art = _emit_mat('Artery', (0.95, 0.04, 0.03), 1.3, rough=0.3)
    cb = _bvh(cer)
    roots_a = []
    for sx in (1, -1):
        for i in range(7):
            a = -0.9 + i * 0.3
            p = c + Vector((sx * ax[0] * 0.95, ax[1] * 0.55 * a, -ax[2] * 0.25 + 0.01 * math.sin(i)))
            roots_a.append((p, (0, 0.2 * rng.uniform(-1, 1), 1)))
        for i in range(4):
            p = c + Vector((sx * ax[0] * 0.3, ax[1] * (-0.6 + 0.4 * i), ax[2] * 0.98))
            roots_a.append((p, (sx, rng.uniform(-0.5, 0.5), -0.2)))
    arteries = _tree_curve('Arteries', art, roots_a, cb, rng, offset=0.0009, steps=(18, 10, 6), step=0.004, r0=0.0014)
    # veins under the skin of the face, scalp and neck (blue)
    vein = _emit_mat('Vein', (0.04, 0.22, 1.0), 0.9, base=(0.02, 0.08, 0.5), rough=0.3)
    roots_v = []
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        roots_v.append((Vector((math.cos(ang) * 0.044, 0.028 + math.sin(ang) * 0.042, -0.20)), (0, 0, 1)))
    for i in range(10):
        ang = i / 10 * 2 * math.pi
        roots_v.append((Vector((math.cos(ang) * 0.075, 0.012 + math.sin(ang) * 0.09, zE - 0.03)),
                        (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 1)))
    veins = _tree_curve('Veins', vein, roots_v, hb, rng, offset=-0.0025, steps=(30, 14, 7), step=0.006, r0=0.0008,
                        up=Vector((0, 0, 1)), bounds=lambda p: p.z < top - 0.004)
    # superficial temporal artery: from in front of the ear, up under the device, then two branches over the scalp
    sta_m = _emit_mat('STA Glow', (1.0, 0.78, 0.05), 3.2, rough=0.2)
    sta_root = Vector((0.074, 0.030, zE - 0.052))
    sta = _tree_curve('TemporalArtery', sta_m, [(sta_root, (0, -0.25, 1))], hb, random.Random(seed + 3), offset=-0.0015,
                      steps=(26, 16, 0), step=0.0045, r0=0.0016, branch_p=0.0, turn=0.18, up=Vector((0, 0, 1)),
                      bounds=lambda p: p.z < top - 0.01)
    for d in ((0, -1, 0.6), (0, 1, 0.5)):
        br = _tree_curve('TemporalBranch', sta_m, [(sta_root + Vector((0, -0.006, 0.075)), d)], hb, random.Random(seed + 5),
                         offset=-0.0015, steps=(22,), step=0.0045, r0=0.0011, branch_p=0.0, turn=0.25, bounds=lambda p: p.z < top - 0.006)
    parts = {'head': head, 'cerebrum': cer, 'cerebellum': cbl, 'brainstem': stem, 'eye': eye, 'device': rig, 'cone': cone,
             'arteries': arteries, 'veins': veins, 'sta': sta}
    info = {'front': front, 'size': list(size), 'top': top, 'eye_z': zE, 'W': W, 'yF': yF, 'yB': yB, 'brain_c': list(c),
            'brain_axes': list(ax), 'device_at': list(hit), 'device_normal': list(nrm)}
    return parts, info, P
