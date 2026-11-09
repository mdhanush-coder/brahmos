"""Mixamo FBX workflow: import, scale fix, retarget by bone-name map, NLA clip combining, root motion, blending.
See references/character-mixamo.md for when to use each function."""
import bpy, re

MIXAMO_PREFIX = re.compile(r'^mixamorig\d*:')


def import_mixamo(path, name=None):
    """FBX import settings for Mixamo: no auto bone orientation (keeps the rest pose Mixamo exported),
    primary/secondary axes default (Y/X), animation kept, leaf bones ignored."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, use_anim=True, ignore_leaf_bones=True, automatic_bone_orientation=False,
                             force_connect_children=False, use_custom_normals=True, anim_offset=1.0)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next((o for o in new if o.type == 'ARMATURE'), None)
    if arm and name:
        arm.name = name
        if arm.animation_data and arm.animation_data.action:
            arm.animation_data.action.name = name
    fix_scale(arm, new)
    return arm, new


def fix_scale(arm, objs):
    """Mixamo FBX arrive as cm (armature scale 0.01, or 100x too big). Normalise to 1.0 and apply, keeping
    the animation correct: apply scale on the armature and its meshes together, then scale location curves."""
    if not arm:
        return
    s = arm.scale.x
    if abs(s - 1.0) < 1e-3:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        if o.type in ('ARMATURE', 'MESH'):
            o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    act = arm.animation_data.action if arm.animation_data else None
    if act:
        from_easing = globals().get('fcurves_of')
        fcs = from_easing(arm) if from_easing else list(getattr(act, 'fcurves', []))
        for fc in fcs:
            if fc.data_path.endswith('.location'):
                for k in fc.keyframe_points:
                    k.co.y *= s
                    k.handle_left.y *= s
                    k.handle_right.y *= s


def strip_prefix(arm):
    """'mixamorig:Hips' -> 'Hips' so clips from different downloads (mixamorig1:, mixamorig2:) share names."""
    for b in arm.data.bones:
        b.name = MIXAMO_PREFIX.sub('', b.name)


def retarget(src_arm, dst_arm, bone_map=None, use_location_for=('Hips',)):
    """Constraint retarget: each target bone copies the source bone's rotation (world space); the hips also
    copy location for root motion. Then bake to keyframes with retarget_bake(). bone_map: {dst: src}."""
    bone_map = bone_map or {b.name: MIXAMO_PREFIX.sub('', b.name) for b in dst_arm.pose.bones}
    src_names = {MIXAMO_PREFIX.sub('', b.name): b.name for b in src_arm.pose.bones}
    for pb in dst_arm.pose.bones:
        s = src_names.get(bone_map.get(pb.name, pb.name))
        if not s:
            continue
        c = pb.constraints.new('COPY_ROTATION')
        c.target, c.subtarget, c.name = src_arm, s, 'RT_rot'
        if pb.name in use_location_for:
            c2 = pb.constraints.new('COPY_LOCATION')
            c2.target, c2.subtarget, c2.name = src_arm, s, 'RT_loc'


def retarget_bake(dst_arm, start, end, action_name):
    bpy.ops.object.select_all(action='DESELECT')
    dst_arm.select_set(True)
    bpy.context.view_layer.objects.active = dst_arm
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=start, frame_end=end, only_selected=True, visual_keying=True,
                     clear_constraints=True, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    dst_arm.animation_data.action.name = action_name
    return dst_arm.animation_data.action


def push_to_nla(arm, action, start, track_name=None, blend_in=8, blend_out=8, repeat=1.0, extrapolation='NOTHING'):
    """NLA: one strip per clip; consecutive strips on alternating tracks overlap by blend frames and
    cross-fade with blend_in/blend_out (or use_auto_blend)."""
    ad = arm.animation_data or arm.animation_data_create()
    tr = ad.nla_tracks.get(track_name) if track_name else None
    tr = tr or ad.nla_tracks.new()
    if track_name:
        tr.name = track_name
    st = tr.strips.new(action.name, int(start), action)
    st.blend_in, st.blend_out, st.repeat = blend_in, blend_out, repeat
    st.extrapolation, st.blend_type = extrapolation, 'REPLACE'
    if hasattr(st, 'use_auto_blend'):
        st.use_auto_blend = False
    ad.action = None
    return st


def sequence_clips(arm, actions, start=1, overlap=8):
    """walk -> run -> stop: strips on alternating tracks A/B, each overlapping the previous by `overlap`."""
    f = start
    strips = []
    for i, act in enumerate(actions):
        st = push_to_nla(arm, act, f, track_name='A' if i % 2 == 0 else 'B', blend_in=overlap if i else 0,
                         blend_out=overlap)
        strips.append(st)
        f = st.frame_end - overlap
    return strips


def in_place(action, root='Hips', axes=(0, 1)):
    """Remove root motion on X/Y (keep Z bob) for in-place loops; move the character with an object path
    instead. Use Mixamo's 'In Place' checkbox when available - this is the fallback."""
    for fc in getattr(action, 'fcurves', []):
        if fc.data_path == f'pose.bones["{root}"].location' and fc.array_index in axes:
            first = fc.keyframe_points[0].co.y if fc.keyframe_points else 0
            for k in fc.keyframe_points:
                k.co.y = first
                k.handle_left.y = first
                k.handle_right.y = first
