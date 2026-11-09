# Shared BrahMos scene module (runs after skilllib.py in the same job file).
# brahmos_import(path) -> dict name -> object, materials from 02_parts.md + the reference photos.
import bpy, math, os
from mathutils import Vector

NIGHT = (0.0056, 0.0129, 0.0185)        # night-blaze dark #111E26 (linear)
BLAZE = (0.93, 0.056, 0.0012)           # #F74304
LIME = (0.70, 1.0, 0.0003)              # #DAFF01
MISSILE_PARTS = ['nose_cowl', 'intake_cone', 'intake_strut_1', 'intake_strut_2', 'intake_strut_3', 'seeker',
                 'skin_fwd', 'skin_aft', 'red_band', 'dark_ring', 'air_duct', 'guidance_unit', 'warhead', 'fuel_tank',
                 'combustor', 'nozzle', 'booster', 'booster_band', 'cable_fairing'] + \
                [f'wing_{i}' for i in range(1, 5)] + [f'fin_{i}' for i in range(1, 5)]
CANISTER_PARTS = ['canister_tube', 'canister_cap_front', 'canister_cap_rear']


def _paint(name, color, rough=0.45, coat=0.3):
    m = simple_material(name, color, roughness=rough, metallic=0.0, coat=coat)
    return m


def _emit(name, color, strength):
    m = simple_material(name, color, roughness=0.4)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    return m


def _camo(name):
    """olive / maroon / dark green blobs, like the parade canisters (procedural, object space)"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 0.55; nz.inputs['Detail'].default_value = 1.5
    nz.inputs['Roughness'].default_value = 0.4
    ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp; cr.interpolation = 'CONSTANT'
    cr.elements[0].position, cr.elements[0].color = 0.0, (0.05, 0.075, 0.018, 1)     # olive
    cr.elements[1].position, cr.elements[1].color = 0.56, (0.05, 0.011, 0.008, 1)    # deep maroon (v1 read pink)
    e = cr.elements.new(0.42); e.color = (0.028, 0.045, 0.012, 1)                    # dark green
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.62
    return m


def brahmos_materials():
    alu = metal('alu_brushed', (0.86, 0.87, 0.88), roughness=0.24, anisotropic=0.45)
    return {
        'alu': alu,
        'titanium': metal('titanium', (0.55, 0.53, 0.50), roughness=0.3),
        'red': _paint('red_band', (0.55, 0.02, 0.02), 0.4),
        'dark': _paint('dark_ring', (0.012, 0.012, 0.014), 0.5, 0.1),
        'seeker': _emit('seeker_lime', LIME, 1.5),
        'electronics': _paint('electronics', (0.02, 0.025, 0.03), 0.55, 0.0),
        'warhead': metal('warhead_steel', (0.18, 0.18, 0.19), roughness=0.4),
        'duct': metal('duct_steel', (0.5, 0.52, 0.55), roughness=0.35),
        'fuel': _paint('fuel_amber', (0.85, 0.42, 0.03), 0.35),
        'combustor': metal('heat_steel', (0.42, 0.3, 0.22), roughness=0.38),
        'nozzle': metal('blued_steel', (0.12, 0.12, 0.16), roughness=0.3),
        'booster': _paint('booster_white', (0.72, 0.72, 0.70), 0.42),
        'blaze': _paint('booster_band', BLAZE, 0.4),
        'camo': _camo('canister_camo'),
        'cap': metal('canister_cap', (0.8, 0.8, 0.82), roughness=0.3),
    }

MAT_OF = {'nose_cowl': 'alu', 'intake_cone': 'titanium', 'seeker': 'seeker', 'skin_fwd': 'alu', 'skin_aft': 'alu',
          'red_band': 'red', 'dark_ring': 'dark', 'air_duct': 'duct', 'guidance_unit': 'electronics',
          'warhead': 'warhead', 'fuel_tank': 'fuel', 'combustor': 'combustor', 'nozzle': 'nozzle',
          'booster': 'booster', 'booster_band': 'blaze', 'cable_fairing': 'alu',
          'canister_tube': 'camo', 'canister_cap_front': 'cap', 'canister_cap_rear': 'camo'}


def _smooth(o, angle=32):
    for p in o.data.polygons:
        p.use_smooth = True
    try:
        mod = o.modifiers.new('smooth_by_angle', 'NODES')
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True); bpy.context.view_layer.objects.active = o
        o.modifiers.remove(mod)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception:
        try:
            o.data.set_sharp_from_angle(angle=math.radians(angle))
        except Exception:
            pass
    wn = o.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True


def brahmos_import(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:                                   # flatten: keep world transforms, drop importer empties
        if o.parent:
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    P = {}
    for o in new:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True); continue
        base = o.name.split('.')[0]
        o.name = base; P[base] = o
    # measure: the missile must be 8.4 m along +X with the tail at x = 0 (FreeCAD mm may arrive as metres)
    bpy.context.view_layer.update()
    lo, hi = bounds_world([o for n, o in P.items() if not n.startswith('canister')])
    result['import_bounds_raw'] = [[round(v, 3) for v in lo], [round(v, 3) for v in hi]]
    size = hi - lo
    from mathutils import Matrix
    T = Matrix.Identity(4)
    if max(size) > 100:                             # millimetres read as metres
        T = Matrix.Scale(0.001, 4) @ T
        size = size * 0.001; lo = lo * 0.001
    ax = max(range(3), key=lambda i: size[i])       # the long axis must be X
    if ax == 1:
        T = Matrix.Rotation(math.radians(-90), 4, 'Z') @ T
    elif ax == 2:
        T = Matrix.Rotation(math.radians(90), 4, 'Y') @ T
    for o in P.values():
        o.matrix_world = T @ o.matrix_world
    bpy.context.view_layer.update()
    lo, hi = bounds_world([o for n, o in P.items() if not n.startswith('canister')])
    shift = Vector((-lo.x, -(lo.y + hi.y) / 2, -(lo.z + hi.z) / 2))
    for o in P.values():
        o.location += shift
    bpy.context.view_layer.update()
    if bounds_world([P['seeker']])[0].x < 4.2:          # nose must point +X
        R = Matrix.Translation((4.2, 0, 0)) @ Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Translation((-4.2, 0, 0))
        for o in P.values():
            o.matrix_world = R @ o.matrix_world
        bpy.context.view_layer.update()
    lo, hi = bounds_world([o for n, o in P.items() if not n.startswith('canister')])
    result['import_bounds_m'] = [[round(v, 3) for v in lo], [round(v, 3) for v in hi]]
    assert 8.2 < hi.x - lo.x < 8.6, f'missile length {hi.x - lo.x:.3f} m, expected 8.4'
    M = brahmos_materials()
    for n, o in P.items():
        key = MAT_OF.get(n) or ('alu' if n.startswith(('wing_', 'fin_', 'intake_strut')) else 'alu')
        assign_material(o, M[key])
        _smooth(o)
    for k in (1, 2, 3):                             # struts poked ~2 mm through the cowl: clamp to its inner wall
        s = P.get(f'intake_strut_{k}')
        if not s:
            continue
        mw, mi = s.matrix_world, s.matrix_world.inverted()
        for v in s.data.vertices:
            w = mw @ v.co
            r = math.hypot(w.y, w.z)
            if r > 0.300:
                k_ = 0.300 / r; w.y *= k_; w.z *= k_
                v.co = mi @ w
    # roots: missile pivot at its centre of length, canister pivot likewise
    mroot = bpy.data.objects.new('missile_root', None); bpy.context.scene.collection.objects.link(mroot)
    croot = bpy.data.objects.new('canister_root', None); bpy.context.scene.collection.objects.link(croot)
    mroot.location = (4.2, 0, 0); croot.location = (4.2, 0, 0)
    bpy.context.view_layer.update()
    for n, o in P.items():
        r = croot if n.startswith('canister') else mroot
        o.parent = r; o.matrix_parent_inverse = r.matrix_world.inverted()
    P['missile_root'], P['canister_root'] = mroot, croot
    result['imported_parts'] = sorted(k for k in P if not k.endswith('_root'))
    result['missing_parts'] = [n for n in MISSILE_PARTS + CANISTER_PARTS if n not in P]
    return P


def night_world(strength=0.6):
    hdri_world('/library/hdri/environments-skies/Assets/Skies/Studio/photo_studio_01_4k.hdr',
               strength=strength, rotation_deg=40, color=NIGHT, background_strength=1.0)


def cam_at(name, loc, target, focal=50, fstop=8.0):
    cam = make_camera(name, focal=focal, fstop=fstop, clip=(0.05, 20000.0))   # default 200 m cuts the sea, ship, moon
    cam.location = Vector(loc)
    bpy.context.view_layer.update()                 # look_at reads matrix_world: stale = aims from the origin
    look_at(cam, Vector(target))
    bpy.context.view_layer.update()
    from bpy_extras.object_utils import world_to_camera_view
    p = world_to_camera_view(bpy.context.scene, cam, Vector(target))
    assert p.z > 0 and 0.3 < p.x < 0.7 and 0.3 < p.y < 0.7, f'{name} does not look at its target: {tuple(p)}'
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = fstop
    cam.data.dof.focus_distance = (Vector(loc) - Vector(target)).length
    return cam
