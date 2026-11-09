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
