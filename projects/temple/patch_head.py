"""One-off patch: head_scene.py -> procedural head, x-ray rim from the surface angle, folds in metres, eye by raycast.
Also fixes the review job's camera aim (look_at needs a view_layer update first)."""
import ast

s = open('head_scene.py', encoding='utf-8').read()

# 1) x-ray material: rim from |dot(N, I)|, dithered transparency (no sorting problems)
a = s.index('def _xray_mat'); b = s.index('def _emit_mat')
XRAY = '''def _xray_mat(name, rim=(0.25, 0.55, 1.0), core_alpha=0.04, rim_strength=2.4, power=2.2):
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
    gain = N.new('ShaderNodeMath'); gain.operation = 'MULTIPLY_ADD'; gain.inputs[1].default_value = 1.5; gain.inputs[2].default_value = core_alpha
    L.new(pw.outputs[0], gain.inputs[0])
    fac = N.new('ShaderNodeMath'); fac.operation = 'MINIMUM'; fac.inputs[1].default_value = 1.0; L.new(gain.outputs[0], fac.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*rim, 1); em.inputs['Strength'].default_value = rim_strength
    tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader')
    L.new(fac.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    m.use_backface_culling = False
    return m


'''
s = s[:a] + XRAY + s[b:]
old = "    if hasattr(m, 'surface_render_method'):\n        m.surface_render_method = 'BLENDED'\n    m.use_backface_culling = False\n    return m\n\n\ndef _link"
assert old in s
s = s.replace(old, "    m.use_backface_culling = False\n    return m\n\n\ndef _link")

# 2) procedural head
a = s.index('def _mannequin_head'); b = s.index('def _slice')
HEAD = '''def _procedural_head():
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


'''
s = s[:a] + HEAD + s[b:]

# 3) folds in metres
old = 'def _fold(bm, center, freq=34.0, depth=0.0032, warp=0.55):'
assert old in s
s = s.replace(old, 'def _fold(bm, center, freq=120.0, depth=0.0032, warp=0.55):')

# 4) scene builder up to the device block
a = s.index('def build_head_scene'); b = s.index('    # device: ray-cast')
BUILD = '''def build_head_scene(face=None, seed=7):
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
    # eye on the device's side (+X): sits just under the front surface (found by a ray from the front)
    ex = 0.032
    hit_e, _, _, _ = hb[0].ray_cast(Vector((ex, -0.5, zE)), Vector((0, 1, 0)))
    eye_c = Vector((ex, (hit_e.y if hit_e else yF) + 0.009, zE))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.0118, location=eye_c)
    eye = bpy.context.active_object; eye.name = 'Eye'; bpy.ops.object.shade_smooth()
    eye.data.materials.append(_emit_mat('Sclera', (0.92, 0.94, 0.97), 0.15, rough=0.15))
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0056, depth=0.0012, location=eye_c + Vector((0, -0.0114, 0)),
                                        rotation=(math.pi / 2, 0, 0))
    iris = bpy.context.active_object; iris.name = 'Iris'
    iris.data.materials.append(_emit_mat('Iris', (0.18, 0.32, 0.45), 0.2))
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0026, depth=0.0014, location=eye_c + Vector((0, -0.0118, 0)),
                                        rotation=(math.pi / 2, 0, 0))
    pupil = bpy.context.active_object; pupil.name = 'Pupil'
    pupil.data.materials.append(_emit_mat('Pupil', (0.01, 0.01, 0.012), 0.0, rough=0.05))
'''
s = s[:a] + BUILD + s[b:]
s = s.replace("probe = Vector((0.3, yF + 0.055, zE + 0.012))", "probe = Vector((0.3, -0.012, zE + 0.022))")

# veins and temporal artery roots in head coordinates
a = s.index('    roots_v = []'); b = s.index('    veins = _tree_curve')
VEINS = '''    roots_v = []
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        roots_v.append((Vector((math.cos(ang) * 0.044, 0.028 + math.sin(ang) * 0.042, -0.20)), (0, 0, 1)))
    for i in range(10):
        ang = i / 10 * 2 * math.pi
        roots_v.append((Vector((math.cos(ang) * 0.075, 0.012 + math.sin(ang) * 0.09, zE - 0.03)),
                        (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 1)))
'''
s = s[:a] + VEINS + s[b:]
old = "sta_root = Vector((W * 0.98, yF + 0.085, zE - 0.055))"
assert old in s
s = s.replace(old, "sta_root = Vector((0.074, 0.030, zE - 0.052))")
ast.parse(s)
open('head_scene.py', 'w', encoding='utf-8').write(s)

# review job: camera aim needs a view_layer update, closer camera, better angles
j = open('head_review_job.py', encoding='utf-8').read()
old = "o = bpy.data.objects.new(name, L); scene.collection.objects.link(o); o.location = Vector(loc); look_at(o, c)"
assert old in j
j = j.replace(old, "o = bpy.data.objects.new(name, L); scene.collection.objects.link(o); o.location = Vector(loc)\n    bpy.context.view_layer.update(); look_at(o, c)")
old = "    cam.location = c + Vector((dx, dy, dz)) * A.get('dist', 1.0)\n    look_at(cam"
assert old in j
j = j.replace(old, "    cam.location = c + Vector((dx, dy, dz)) * A.get('dist', 0.7)\n    bpy.context.view_layer.update()   # look_at reads matrix_world: stale until updated (Phase-5 bug)\n    look_at(cam")
old = "views = {'three_quarter': (0.55, -0.55, 0.06), 'side': (0.80, 0.0, 0.05), 'front': (0.0, -0.85, 0.04)}"
assert old in j
j = j.replace(old, "views = {'three_quarter': (0.6, -0.6, 0.08), 'side': (1.0, 0.0, 0.05), 'front': (0.0, -1.0, 0.05)}")
open('head_review_job.py', 'w', encoding='utf-8').write(j)

parts = ['../../.claude/skills/blender-animation/scripts/skilllib.py', 'temple_model.py', 'head_scene.py', 'head_review_job.py']
b = '\n\n'.join(open(p, encoding='utf-8').read() for p in parts)
ast.parse(b)
open('job_head_review2.py', 'w', encoding='utf-8').write(b)
print('patched, bundle', len(b))
