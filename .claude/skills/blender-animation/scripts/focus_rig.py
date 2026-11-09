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
