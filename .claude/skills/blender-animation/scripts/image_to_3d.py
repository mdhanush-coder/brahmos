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
