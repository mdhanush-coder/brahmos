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
