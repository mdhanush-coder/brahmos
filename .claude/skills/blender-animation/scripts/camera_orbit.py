"""Camera rigs: pivot-empty orbit (B-video), DOF, multi-shot sequence with the B-video rules card.
Needs easing_presets.py loaded first (key, ease, fcurves_of, remove_bump, bind_camera)."""
import bpy, math
from mathutils import Vector


def look_at(obj, target):
    d = Vector(target) - obj.matrix_world.translation
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def make_camera(name='Cam', focal=85.0, sensor=36.0, fstop=2.8, focus=None, clip=(0.01, 200.0)):
    cd = bpy.data.cameras.new(name)
    cd.lens, cd.sensor_width = focal, sensor
    cd.clip_start, cd.clip_end = clip
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    if focus is not None:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if isinstance(focus, bpy.types.Object):
            cd.dof.focus_object = focus
        else:
            cd.dof.focus_distance = float(focus)
    return cam


def make_orbit_rig(target=(0, 0, 0), distance=4.0, height=0.6, focal=85.0, name='shot1', fstop=4.0):
    """Empty at the target; camera parented to it and pointed at it. Rotate the EMPTY (Z) to orbit.
    Returns (empty, camera). Focal 85-100 mm for products (B-video: 90 mm), DOF focused on the pivot."""
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    piv = bpy.data.objects.new(f'{name} movement', None)
    piv.empty_display_type = 'PLAIN_AXES'
    piv.location = Vector(target)
    col.objects.link(piv)
    cam = make_camera(f'{name}_cam', focal=focal, fstop=fstop, focus=piv)
    bpy.context.scene.collection.objects.unlink(cam)
    col.objects.link(cam)
    cam.parent = piv
    cam.location = Vector((0, -distance, height))
    look_at_local(cam, piv)
    return piv, cam


def look_at_local(cam, piv):
    """Aim a parented camera at its pivot. Phase-5 bug: re-assigning a stale cam.matrix_world after setting
    rotation_euler silently erased the aim (camera looked straight down, render = empty backdrop).
    Set the rotation only, then update and ASSERT the direction."""
    bpy.context.view_layer.update()
    look_at(cam, piv.matrix_world.translation)
    bpy.context.view_layer.update()
    fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    to_t = (piv.matrix_world.translation - cam.matrix_world.translation).normalized()
    assert fwd.dot(to_t) > 0.99, f'camera not aimed at its pivot (dot={fwd.dot(to_t):.2f})'


def frame_distance(radius, focal, sensor=36.0, fill=0.7, aspect=16 / 9):
    """Distance at which an object of bounding radius fills `fill` of the frame height."""
    fov_v = 2 * math.atan((sensor / aspect) / (2 * focal))
    return radius / (fill * math.tan(fov_v / 2))


def frame_width_distance(width, focal, sensor=36.0, fill=0.85):
    """Camera distance at which a subject `width` m wide (horizontal explode) fills `fill` of the frame width."""
    return (width / 2) / (fill * sensor / (2 * focal))


def dolly(cam, keys, preset='smooth'):
    """Breathing push-in/pull-out. keys: [(frame, factor)] multiplying the camera's current local Y distance.
    Open close (0.5) so the assembled product reads, pull out to 1.0 as it explodes, return before re-assembly."""
    # Scale the whole local offset (y AND z): the camera must slide along its aim line to keep looking at the
    # pivot. Scaling y alone (Phase-5 v3) pushed the subject out of frame at the close-up ends.
    by, bz = cam.location.y, cam.location.z
    for f, k in keys:
        cam.location.y, cam.location.z = by * k, bz * k
        cam.keyframe_insert('location', frame=f)
    cam.location.y, cam.location.z = by, bz
    for fc in fcurves_of(cam):
        if fc.data_path == 'location':
            ease(fc, preset)


def orbit(piv, start, end, degrees, preset='smooth', axis=2):
    rot = list(piv.rotation_euler)
    key(piv, 'rotation_euler', start, tuple(rot), index=axis)
    rot[axis] += math.radians(degrees)
    key(piv, 'rotation_euler', end, tuple(rot), index=axis)
    for fc in fcurves_of(piv):
        if fc.data_path == 'rotation_euler' and fc.array_index == axis:
            ease(fc, preset)


def push_in(cam, start, end, dolly=0.5, preset='super_smooth'):
    """Entry reveal (B-video shot 1): camera starts pulled back by `dolly` m along its local Y offset."""
    end_loc = cam.location.copy()
    key(cam, 'location', end, tuple(end_loc))
    start_loc = end_loc.copy()
    start_loc.y -= dolly
    key(cam, 'location', start, tuple(start_loc))
    for fc in fcurves_of(cam):
        if fc.data_path == 'location':
            ease(fc, preset)


# B-video rules card (25 fps there; scale with fps)
RULES = dict(change_rotation=40.0, change_duration=20, change_start=40, shot_duration=50, drift=10.0)


def shot_sequence(scene, shots, rules=RULES):
    """shots: list of (pivot, camera). Builds: entry(-rot -> 0) / drift (+drift) / exit (+rot),
    transitions eased transition_in / transition_out, cameras bound at transition midpoints, bumps removed.
    Returns the last frame."""
    r = rules
    f = scene.frame_start
    for n, (piv, cam) in enumerate(shots):
        base = piv.rotation_euler.z
        keys = []
        if n > 0:  # entry from previous cut
            keys += [(f, base - math.radians(r['change_rotation'])), (f + r['change_duration'] // 2, base)]
        hold_start = keys[-1][0] if keys else f
        exit_start = hold_start + r['change_start']
        keys += [(exit_start, base + math.radians(r['drift']))]
        if n < len(shots) - 1:
            keys += [(exit_start + r['change_duration'] // 2, base + math.radians(r['drift'] + r['change_rotation']))]
        elif not any(k[0] == hold_start for k in keys):
            keys.insert(0, (hold_start, base))
        for fr, val in keys:
            piv.rotation_euler.z = val
            piv.keyframe_insert('rotation_euler', frame=fr, index=2)
        for fc in fcurves_of(piv):
            if fc.data_path == 'rotation_euler' and fc.array_index == 2:
                pts = fc.keyframe_points
                for i in range(len(pts) - 1):
                    ease_segment(fc, i, 0.45, 0.45)
                if n > 0:
                    ease_segment(fc, 0, 0.0, 0.9)               # arrive from the cut at speed
                if n < len(shots) - 1:
                    ease_segment(fc, len(pts) - 2, 0.9, 0.0)    # leave into the cut at speed
                for i in range(1, len(pts) - 1):
                    remove_bump(fc, i)
        bind_camera(scene, cam, f)
        f = (exit_start + r['change_duration'] // 2) if n < len(shots) - 1 else exit_start
    scene.frame_end = max(scene.frame_end, f)
    return f
