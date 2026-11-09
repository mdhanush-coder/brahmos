"""Temple wearable, stylised 3D illustration. Shape from the reference picture: a plump kidney-bean pebble, smooth gold,
a dent along one long edge. Layers follow the user's exploded-view reference: hollow gold shell, flat silver foil battery
pouch, black fibreglass main PCB with dense gold traces and chips (+ copper antenna loop), a thin sensor board with a row of
green micro-LEDs, a foam ring, and a frosted translucent adhesive pad with a geometric grip grid. The three optical emitters
and the photodiode sit on the UNDERSIDE of the pad (skin side). No public dimensions exist: label it a 3D illustration.
Modelled at 10:1. Local frame: +Z outer face, skin side z = 0, +Y convex edge, -Y dented edge.
temple_device() -> {part_name: object}, skin side first (assembly order for the exploded view)."""
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


def _ramp(nodes, pairs, interp='LINEAR'):
    r = nodes.new('ShaderNodeValToRGB')
    r.color_ramp.interpolation = interp
    el = r.color_ramp.elements
    el[0].position, el[0].color = pairs[0][0], (pairs[0][1],) * 3 + (1,)
    el[1].position, el[1].color = pairs[1][0], (pairs[1][1],) * 3 + (1,)
    return r


def _gold_material():
    """True Gold, metallic 1, roughness 0.12 average with micro-scratch variation (fine noise -> ColorRamp -> Roughness)."""
    m = _pbr('Shell Gold', GOLD, metallic=1.0, rough=0.12)
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    tc, noise = N.new('ShaderNodeTexCoord'), N.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value, noise.inputs['Detail'].default_value = 600.0, 6.0
    r = _ramp(N, [(0.35, 0.07), (0.8, 0.2)])
    L.new(tc.outputs['Object'], noise.inputs['Vector'])
    L.new(noise.outputs['Fac'], r.inputs['Fac'])
    L.new(r.outputs['Color'], p.inputs['Roughness'])
    return m


def _pcb_material():
    """Matte black fibreglass (roughness 0.4) with dense gold circuit traces: Voronoi edge distance -> crisp ColorRamp drives the
    base colour (black -> #FFD700), Metallic and a Bump on the Normal. Object coordinates, so no UVs are needed."""
    m = bpy.data.materials.new('PCB Traces')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.4
    tc, vor = N.new('ShaderNodeTexCoord'), N.new('ShaderNodeTexVoronoi')
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 160.0
    ramp = _ramp(N, [(0.0, 1.0), (0.011, 0.0)], interp='CONSTANT')     # thin gold lines on black (0.022 read as gold mesh)
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    ins = [i for i in mix.inputs if i.type == 'RGBA']
    ins[0].default_value = (0.012, 0.012, 0.014, 1)      # black fibreglass
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


def _pcb_image_material(path):
    """The user's PCB artwork on the UVs: image -> Base Color; its bright gold (ColorRamp on the image) -> Metallic and a small
    Bump, so the traces shine and stand proud of the black board. The image is packed into the .blend for later renders."""
    img = bpy.data.images.load(path)
    img.pack()
    m = bpy.data.materials.new('PCB Artwork')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.35
    tex = N.new('ShaderNodeTexImage')
    tex.image, tex.interpolation = img, 'Cubic'
    uvn = N.new('ShaderNodeUVMap')
    uvn.uv_map = 'UVMap'
    mask = _ramp(N, [(0.12, 0.0), (0.3, 1.0)])
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value, bump.inputs['Distance'].default_value = 0.35, 0.001
    L.new(uvn.outputs['UV'], tex.inputs['Vector'])
    L.new(tex.outputs['Color'], p.inputs['Base Color'])
    L.new(tex.outputs['Color'], mask.inputs['Fac'])
    L.new(mask.outputs['Color'], p.inputs['Metallic'])
    L.new(mask.outputs['Color'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def _foil_material():
    """Silver lithium-polymer pouch: metallic 0.8, roughness 0.35, crinkled-foil bump from a fine noise on the Normal."""
    m = _pbr('Battery Foil', (0.66, 0.68, 0.7), metallic=0.8, rough=0.35)
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    tc, noise, bump = N.new('ShaderNodeTexCoord'), N.new('ShaderNodeTexNoise'), N.new('ShaderNodeBump')
    noise.inputs['Scale'].default_value, noise.inputs['Detail'].default_value = 260.0, 8.0
    bump.inputs['Strength'].default_value, bump.inputs['Distance'].default_value = 0.45, 0.0015
    L.new(tc.outputs['Object'], noise.inputs['Vector'])
    L.new(noise.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def _pad_material(spacing=0.04, line=0.1):
    """Medical-grade adhesive pad from the user's reference: frosted, semi-translucent (transmission 0.85, roughness 0.3),
    raised ridges on three line sets 60 deg apart (a triangle grid, one triangle ~4 cm at 10:1) and a fine dot texture inside
    the triangles. Ridges: |fract(p.d / spacing) - 0.5| > 0.5 - line/2 for d at 0, 60, 120 deg; max of the three. The ridges and
    the dots drive the Bump; the ridges are also a little whiter. Object coordinates, no UVs."""
    m = _pbr('Adhesive Pad', (0.72, 0.75, 0.79), rough=0.3, trans=0.85)
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord')

    def math(op, a=None, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    ridges = None
    for deg in (0.0, 60.0, 120.0):
        dot = N.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = (math_cos(deg), math_sin(deg), 0.0)
        L.new(tc.outputs['Object'], dot.inputs[0])
        v = math('FRACT', math('MULTIPLY', dot.outputs['Value'], 1.0 / spacing))
        r = math('GREATER_THAN', math('ABSOLUTE', math('SUBTRACT', v, 0.5)), 0.5 - line / 2)
        ridges = r if ridges is None else math('MAXIMUM', ridges, r)
    vor = N.new('ShaderNodeTexVoronoi')                     # fine dots inside the triangles
    vor.inputs['Scale'].default_value = 700.0
    L.new(tc.outputs['Object'], vor.inputs['Vector'])
    dots = math('LESS_THAN', vor.outputs['Distance'], 0.32)
    height = math('ADD', ridges, math('MULTIPLY', dots, 0.3))
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value, bump.inputs['Distance'].default_value = 0.7, 0.0015
    L.new(height, bump.inputs['Height'])
    L.new(bump.outputs['Normal'], p.inputs['Normal'])
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    ins = [i for i in mix.inputs if i.type == 'RGBA']
    ins[0].default_value = (0.72, 0.75, 0.79, 1)            # frosted body
    ins[1].default_value = (0.95, 0.96, 0.98, 1)            # brighter ridges
    L.new(ridges, mix.inputs['Factor'])
    L.new([o for o in mix.outputs if o.type == 'RGBA'][0], p.inputs['Base Color'])
    return m


def math_cos(deg):
    return math.cos(math.radians(deg))


def math_sin(deg):
    return math.sin(math.radians(deg))


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


def _outline(k, n):
    a, b, bend = A0 * k[0], B0 * k[1], BEND * k[2]
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / PW), c)
        y = b * math.copysign(abs(s) ** (2 / PW), s) + bend * (1 - (x / a) ** 2)
        pts.append((x, y))
    return pts


def _bean(name, k, depth, z0, mat, bevel=0.0, seg=3, n=160, curl=0.0, uv=False):
    """Bean slab: outline = bowed superellipse (half sizes A0*k[0], B0*k[1]) extruded `depth` from z0; curl bends the ends down.
    uv=True: planar top-down UVs with the bow UNDONE (y - bend*(1-(x/a)^2)), so a straight oval artwork follows the bean."""
    a, b, bend = A0 * k[0], B0 * k[1], BEND * k[2]
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, -curl * (x / a) ** 2)) for (x, y) in _outline(k, n)]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, depth))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if uv:
        lay = bm.loops.layers.uv.new('UVMap')
        for face in bm.faces:
            for lp in face.loops:
                x, y = lp.vert.co.x, lp.vert.co.y
                yy = y - bend * (1 - (x / a) ** 2)
                lp[lay].uv = ((x + a) / (2 * a), (yy + b) / (2 * b))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location.z = z0
    return _finish(o, mat, bevel, seg)


def _pillow(name, z0, mat, h_side=0.010, h_dome=0.034, n=200, rings=22):
    """The shell: the bean outline lofted as rings (near-vertical sides, a smooth dome), capped on top, OPEN underneath and
    thickened inward (Solidify 3 mm at 10:1), so lifted off it is a hollow cover like the reference."""
    base = _outline((1, 1, 1), n)
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
    bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location.z = z0
    _finish(o, mat, 0.0)
    so = o.modifiers.new('Wall', 'SOLIDIFY')
    so.thickness, so.offset = 0.003, -1.0
    o.modifiers.move(len(o.modifiers) - 1, 0)
    return o


def _glow_mat(name, color, strength):
    """Light you can see: Emission mixed with Transparent, fading from the source (Generated Z = 1) to the far end (Z = 0)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        N.remove(n)
    out, tr, em, mix = N.new('ShaderNodeOutputMaterial'), N.new('ShaderNodeBsdfTransparent'), N.new('ShaderNodeEmission'), N.new('ShaderNodeMixShader')
    em.inputs['Color'].default_value = (*color, 1.0)
    em.inputs['Strength'].default_value = strength
    tc, sep, pw = N.new('ShaderNodeTexCoord'), N.new('ShaderNodeSeparateXYZ'), N.new('ShaderNodeMath')
    pw.operation, pw.inputs[1].default_value = 'POWER', 1.6
    L.new(tc.outputs['Generated'], sep.inputs[0])
    L.new(sep.outputs['Z'], pw.inputs[0])
    L.new(pw.outputs[0], mix.inputs['Fac'])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m


def _haze_mat(name, color, strength, falloff=2.2, gain=60.0):
    """Light diffusing in tissue: a VOLUME emission (no surface at all, so no hard edge) whose colour falls off smoothly from the
    centre of the object to its rim: Spherical gradient on Object coords (unit sphere) ^ falloff, times the colour. The Emission
    node keeps the name 'Emission' so a job can key its Strength (the pulse)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        N.remove(n)
    out, em = N.new('ShaderNodeOutputMaterial'), N.new('ShaderNodeEmission')
    em.name = 'Emission'
    em.inputs['Strength'].default_value = strength
    tc, grad, pw = N.new('ShaderNodeTexCoord'), N.new('ShaderNodeTexGradient'), N.new('ShaderNodeMath')
    grad.gradient_type = 'SPHERICAL'
    pw.operation, pw.inputs[1].default_value = 'POWER', falloff
    mul = N.new('ShaderNodeMix')
    mul.data_type, mul.blend_type = 'RGBA', 'MULTIPLY'
    mul.inputs['Factor'].default_value = 1.0
    ins = [i for i in mul.inputs if i.type == 'RGBA']
    ins[0].default_value = (*color, 1.0)
    g = N.new('ShaderNodeMath')            # volume emission integrates over a few cm only: it needs a large gain to show
    g.operation, g.inputs[1].default_value = 'MULTIPLY', gain
    L.new(tc.outputs['Object'], grad.inputs['Vector'])
    L.new(grad.outputs['Fac'], pw.inputs[0])
    L.new(pw.outputs[0], g.inputs[0])
    L.new(g.outputs[0], ins[1])
    L.new([o for o in mul.outputs if o.type == 'RGBA'][0], em.inputs['Color'])
    L.new(em.outputs[0], out.inputs['Volume'])
    return m


def _haze(name, mat, loc, size, parent):
    """A soft glow cloud: a unit sphere scaled to `size`, volume only (see _haze_mat)."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.data.materials.append(mat)
    o.parent = parent
    o.visible_shadow = False
    return o


def _light_in_skin(pad, leds, diode_x, skin_z=-0.0056):
    """PPG light as it really travels: each emitter's light enters the skin and spreads (a soft haze under it, deeper than wide);
    some of it curves back up to the photodiode (a chain of small hazes along a 'banana' arc, scale 0 until a job grows them in).
    A faint translucent skin layer shows where it happens. Everything rides the pad (origin = world origin at build time)."""
    for led, color, name in leds:
        _haze(f'glow_{name}', _haze_mat(f'Beam {name.title()}', color, 4.0), (led.location.x, 0.0, skin_z - 0.012),
              (0.016, 0.016, 0.02), pad)
    rmat = _haze_mat('Return Light', (1.0, 0.55, 0.65), 3.0, gain=120.0)
    x0, x1, depth, n = leds[1][0].location.x, diode_x, 0.03, 30      # 14 read as separate pearls: 30 overlapping clouds merge into one arc
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        z = skin_z - 0.002 - depth * 4 * t * (1 - t)
        h = _haze(f'return_glow_{i:02d}', rmat, (x, 0.0, z), (0.009, 0.009, 0.009), pad)
        h.scale = (0.0, 0.0, 0.0)
    skin = _bean('skin_layer', (0.95, 0.9, 1.0), 0.03, skin_z - 0.03, _skin_mat())
    skin.parent = pad
    skin.visible_shadow = False
    return skin


def _skin_mat():
    """A barely-there tissue tint: 80 % transparent, 20 % soft pink, so the glows inside read as 'under the skin'."""
    m = bpy.data.materials.new('Skin Layer')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    p = N['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.8, 0.5, 0.45, 1.0)
    p.inputs['Roughness'].default_value = 0.6
    tr, mix = N.new('ShaderNodeBsdfTransparent'), N.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = 0.2
    out = N['Material Output']
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(p.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m


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


PCB_TOP, PCB_A, PCB_CURL = 0.027, A0 * 0.85, 0.006


def _top(x):
    """Height of the PCB's top face at x (the board curls down toward its ends)."""
    return PCB_TOP - PCB_CURL * (x / PCB_A) ** 2


PCB_B = B0 * 0.7


def _fit(x, y, m):
    """Clamp a part centre so a footprint of half-size m stays inside the PCB's real outline (bowed superellipse) and inside
    the antenna ring. The bean bows +Y in the middle, so its lower edge there is ~2.6 cm (10:1) higher than at the ends:
    fixed coordinates put parts over the edge (seen: SMD, transistor, resistor hanging off)."""
    a = PCB_A
    x = max(-a + m + 0.008, min(a - m - 0.008, x))
    yu = PCB_B * (1 - abs(x / a) ** PW) ** (1 / PW)
    mid = BEND * (1 - (x / a) ** 2)
    return x, max(mid - yu + m, min(mid + yu - m, y))


def _stick(o, host):
    bpy.context.view_layer.update()
    o.parent = host
    o.matrix_parent_inverse = host.matrix_world.inverted()


def _ic(name, w, l, h, x, y, per_side, four, body_m, pin_m):
    """A packaged chip: black epoxy body (w along x, l along y) standing on gull-wing tin pins on two (+-x) or four sides."""
    x, y = _fit(x, y, max(w, l) / 2 + 0.005 + 0.006)
    z = _top(x)
    body = _box(name, (w, l, h), (x, y, z + 0.0008 + h / 2), body_m, bevel=0.0005)
    sides = [('x', 1), ('x', -1)] + ([('y', 1), ('y', -1)] if four else [])
    k = 0
    for ax, sgn in sides:
        span = l if ax == 'x' else w
        step = span / (per_side + 0.6)
        for i in range(per_side):
            t = (i - (per_side - 1) / 2) * step
            if ax == 'x':
                loc, size = (x + sgn * (w / 2 + 0.0016), y + t, z + 0.0005), (0.0034, 0.0011, 0.0009)
            else:
                loc, size = (x + t, y + sgn * (l / 2 + 0.0016), z + 0.0005), (0.0011, 0.0034, 0.0009)
            pin = _box(f'{name}_pin_{k:02d}', size, loc, pin_m)
            _stick(pin, body)
            k += 1
    return body


def _smd(name, x, y, vertical, host, body_m, cap_m):
    """An 0603 resistor/capacitor: black body with two tin end caps (10:1 -> 16 x 8 mm)."""
    x, y = _fit(x, y, 0.008 + 0.006)
    z = _top(x)
    L, W, H = 0.016, 0.008, 0.005
    sz = (W, L, H) if vertical else (L, W, H)
    body = _box(name, sz, (x, y, z + H / 2), body_m, bevel=0.0004)
    for s in (1, -1):
        off = (0, s * (L / 2 - 0.0015), 0) if vertical else (s * (L / 2 - 0.0015), 0, 0)
        csz = (W + 0.0004, 0.003, H + 0.0003) if vertical else (0.003, W + 0.0004, H + 0.0003)
        cap = _box(f'{name}_cap_{"a" if s > 0 else "b"}', csz, (x + off[0], y + off[1], z + H / 2), cap_m, bevel=0.0003)
        _stick(cap, body)
    _stick(body, host)
    return body


def _transistor(name, x, y, host, body_m, leg_m):
    """A TO-92 transistor: a black half-cylinder (flat face toward -Y) on three legs."""
    x, y = _fit(x, y, 0.0045 + 0.007)
    z = _top(x)
    body = _cyl(name, 0.0045, 0.009, (x, y, z + 0.0055 + 0.0045), body_m, verts=32)
    cut = _box(f'{name}_cut', (0.012, 0.006, 0.012), (x, y - 0.0045 - 0.0012, z + 0.01), body_m)
    _hole(body, cut)
    cut.parent, cut.matrix_parent_inverse = body, body.matrix_world.inverted()
    for i, dx in enumerate((-0.0025, 0.0, 0.0025)):
        leg = _cyl(f'{name}_leg_{i}', 0.0004, 0.0055, (x + dx, y - 0.001, z + 0.00275), leg_m, verts=8)
        _stick(leg, body)
    _stick(body, host)
    return body


def _resistor(name, x, y, host, body_m, lead_m, bands):
    """A through-hole resistor lying on the board: beige body along X with four colour bands and leads bent down into the board."""
    x, y = _fit(x, y, 0.011 + 0.006)               # half-length incl. leads 0.011, plus clearance
    z = _top(x) + 0.0045
    body = _cyl(name, 0.0028, 0.013, (x, y, z), body_m, verts=24)
    body.rotation_euler.y = math.radians(90)
    for i, (bx, col) in enumerate(zip((-0.0042, -0.0022, -0.0002, 0.0034), bands)):
        band = _cyl(f'{name}_band_{i}', 0.00295, 0.0011, (x + bx, y, z), col, verts=24)
        band.rotation_euler.y = math.radians(90)
        _stick(band, body)
    for s in (1, -1):
        h = _cyl(f'{name}_lead_h{"a" if s > 0 else "b"}', 0.0004, 0.004, (x + s * 0.0085, y, z), lead_m, verts=8)
        h.rotation_euler.y = math.radians(90)
        v = _cyl(f'{name}_lead_v{"a" if s > 0 else "b"}', 0.0004, z - _top(x), (x + s * 0.0105, y, (z + _top(x)) / 2), lead_m, verts=8)
        _stick(h, body)
        _stick(v, body)
    _stick(body, host)
    return body


def _hole(target, cutter):
    cutter.display_type, cutter.hide_render = 'WIRE', True
    cutter.parent = target
    bo = target.modifiers.new('Hole', 'BOOLEAN')
    bo.object, bo.operation, bo.solver = cutter, 'DIFFERENCE', 'EXACT'
    target.modifiers.move(len(target.modifiers) - 1, 0)


def temple_device(pcb_image=None):
    gold = _gold_material()
    pad_m = _pad_material()
    glass = _pbr('Optical Glass', (0.012, 0.008, 0.012), rough=0.06, coat=1.0)
    foam = _pbr('Foam Black', (0.01, 0.01, 0.011), rough=0.9)
    pcb_m = _pcb_material()
    board = _pbr('Sensor Board', (0.012, 0.012, 0.014), metallic=0.1, rough=0.4, coat=0.2)
    chip = _pbr('Chip Black', (0.015, 0.015, 0.018), metallic=0.3, rough=0.3)
    copper = _pbr('Antenna Copper', (0.95, 0.52, 0.38), metallic=1.0, rough=0.3)
    foil = _foil_material()
    led_g = _pbr('LED Green', (0.0, 0.2, 0.02), emit=(0.1, 1.0, 0.15), estr=4.0)
    led_r = _pbr('LED Red', (0.2, 0.0, 0.0), emit=(1.0, 0.05, 0.03), estr=4.0)
    led_i = _pbr('LED Infrared', (0.12, 0.0, 0.08), emit=(0.75, 0.0, 0.35), estr=4.0)   # IR is invisible: shown deep magenta by convention
    micro = _pbr('Micro LED', (0.0, 0.2, 0.02), emit=(0.1, 1.0, 0.15), estr=4.0)      # 10 flooded the PCB underside with green
    diode = _pbr('Photodiode', (0.03, 0.03, 0.05), metallic=0.5, rough=0.2)

    P = {}
    # skin side: optical window, three emitters and photodiode under the pad
    P['optical_window'] = _box('optical_window', (0.135, 0.05, 0.006), (0.0, 0.0, -0.0005), glass, bevel=0.004)
    # emitters INSIDE the window (half length 0.0675): green at -0.062 stuck out by 2 mm (user, 2026-11-07); keep >= 4 mm clear
    P['led_green'] = _cyl('led_green', 0.0075, 0.003, (-0.055, 0.0, -0.0036), led_g)
    P['led_red'] = _cyl('led_red', 0.0075, 0.003, (-0.032, 0.0, -0.0036), led_r)
    P['led_infrared'] = _cyl('led_infrared', 0.0075, 0.003, (-0.009, 0.0, -0.0036), led_i)
    P['photodiode'] = _box('photodiode', (0.02, 0.02, 0.003), (0.045, 0.0, -0.0036), diode, bevel=0.0008)
    P['adhesive_pad'] = _bean('adhesive_pad', (0.93, 0.88, 1.0), 0.0045, 0.0, pad_m, bevel=0.001)
    # light leaving each emitter, and the light that returns to the photodiode (pad origin is the world origin at build time)
    _light_in_skin(P['adhesive_pad'], [(P['led_green'], (0.1, 1.0, 0.15), 'green'), (P['led_red'], (1.0, 0.05, 0.03), 'red'),
                                       (P['led_infrared'], (0.75, 0.0, 0.35), 'infrared')], diode_x=0.045)
    P['foam_ring'] = _bean('foam_ring', (0.88, 0.76, 1.0), 0.006, 0.0125, foam, bevel=0.0006)
    _hole(P['foam_ring'], _bean('foam_cut', (0.68, 0.46, 1.0), 0.02, -0.002, foam))      # z0 is RELATIVE to the parent (foam_ring z0 0.0125)
    # sensor board with a row of green micro-LEDs on top (decorative status lights, as in the reference picture)
    P['sensor_board'] = _bean('sensor_board', (0.82, 0.52, 1.0), 0.0022, 0.0185, board, bevel=0.0005)
    a_b = A0 * 0.82
    for i, x in enumerate([-0.105 + 0.03 * j for j in range(8)]):
        for row, yy in enumerate((0.012, -0.010)):
            y = yy + BEND * 0.52 * (1 - (x / a_b) ** 2)
            led = _cyl(f'micro_led_{i}_{row}', 0.0028, 0.002, (x, y, 0.0022 + 0.001), micro, verts=16)
            led.parent = P['sensor_board']
    if pcb_image:
        pcb_m = _pcb_image_material(pcb_image)                       # the user's artwork, UV-mapped top-down
    P['pcb'] = _bean('pcb', (0.85, 0.7, 1.0), 0.0035, 0.0235, pcb_m, bevel=0.0006, curl=0.006, uv=True)
    P['antenna'] = _bean('antenna', (0.83, 0.68, 1.0), 0.0009, 0.027, copper)
    _hole(P['antenna'], _bean('antenna_cut', (0.8, 0.64, 1.0), 0.01, -0.001, copper))    # relative to antenna z0 0.027
    tin = _pbr('Tin Pins', (0.8, 0.8, 0.82), metallic=0.95, rough=0.28)
    P['heart_rate_sensor'] = _ic('heart_rate_sensor', 0.026, 0.02, 0.0045, -0.075, 0.016, 4, False, chip, tin)
    P['motion_sensor'] = _ic('motion_sensor', 0.02, 0.02, 0.004, 0.035, 0.036, 3, True, chip, tin)
    P['thermometer'] = _ic('thermometer', 0.014, 0.012, 0.0035, 0.09, 0.012, 2, False, chip, tin)
    P['processor'] = _ic('processor', 0.036, 0.036, 0.005, -0.02, -0.004, 6, True, chip, tin)
    # small parts on the board (reference: SMD, transistor, resistor): they ride the PCB in the explode
    for i, (x, y, v) in enumerate([(-0.105, -0.01, True), (-0.045, 0.03, False), (0.012, 0.012, True), (0.06, -0.022, False),
                                   (0.065, 0.035, True), (-0.06, -0.035, False), (0.016, -0.04, False), (0.11, -0.005, True),
                                   (-0.12, 0.02, True), (0.04, 0.0, False)]):
        _smd(f'smd_{i:02d}', x, y, v, P['pcb'], chip, tin)
    for i, (x, y) in enumerate([(-0.002, 0.04), (0.085, -0.03)]):
        _transistor(f'transistor_{i}', x, y, P['pcb'], chip, tin)
    bands = [_pbr(f'Band {n}', c, rough=0.4) for n, c in (('Brown', (0.18, 0.07, 0.02)), ('Black', (0.01, 0.01, 0.01)),
                                                          ('Red', (0.7, 0.02, 0.02)), ('Gold', (1.0, 0.7, 0.25)))]
    _resistor('resistor_0', -0.09, -0.03, P['pcb'], _pbr('Resistor Beige', (0.75, 0.55, 0.32), rough=0.5), tin, bands)
    # flat silver foil pouch battery
    P['battery'] = _box('battery', (0.17, 0.075, 0.011), (0.0, 0.012, 0.0405), foil, bevel=0.0035, seg=3)
    P['shell'] = _pillow('shell', 0.0125, gold)
    return P
