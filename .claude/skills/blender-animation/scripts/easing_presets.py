"""Easing presets and F-curve utilities (bpy, Blender 4.4-5.x layered actions and legacy actions).

From the reference notes:
  - A-video: easing = handle length; S X on the handles; "transition" = one handle ~full, the other ~0;
    whip camera switch cuts at peak velocity.
  - B-video: Bezier + FREE handles; copy easing between shots; remove the velocity "bump" at middle keys.

Handle fractions are a share of the gap between two keys. Flat handles (same value as the key) mean
zero velocity at that key (an ease). A 0 fraction means the key is hit at full speed (cut point).
"""
import bpy

# (out_frac at the segment's first key, in_frac at its last key)
PRESETS = {
    'smooth':          (0.40, 0.40),   # default product move
    'super_smooth':    (0.60, 0.60),   # EaseIt "Super Smooth" look - long, luxurious
    'ease_in':         (0.70, 0.15),   # slow start, quicker arrival (A-video "Ease In")
    'ease_out':        (0.15, 0.70),   # quick start, long settle (A-video "Ease Out")
    'ease_in_out':     (0.50, 0.50),
    'transition_out':  (0.90, 0.00),   # leave slowly, hit the cut at full speed
    'transition_in':   (0.00, 0.90),   # arrive from the cut at full speed, settle long
    'snappy':          (0.20, 0.80),   # UI-like pop that settles
}
DYNAMIC = {  # Blender's built-in dynamic easing (Graph Editor T menu) for character
    'overshoot': ('BACK', 'EASE_OUT'),
    'bounce':    ('BOUNCE', 'EASE_OUT'),
    'elastic':   ('ELASTIC', 'EASE_OUT'),
}


def fcurves_of(idblock):
    """All F-curves animating an ID (object, shape-key datablock, ...), layered or legacy actions."""
    ad = getattr(idblock, 'animation_data', None)
    if not ad or not ad.action:
        return []
    act = ad.action
    out = []
    layers = getattr(act, 'layers', None)
    if layers:
        slot = getattr(ad, 'action_slot', None)
        for layer in layers:
            for strip in layer.strips:
                try:
                    cb = strip.channelbag(slot) if slot else None
                except Exception:
                    cb = None
                if cb:
                    out.extend(cb.fcurves)
    if not out and hasattr(act, 'fcurves'):
        try:
            out = list(act.fcurves)
        except Exception:
            pass
    return out


def ease_segment(fc, i, out_frac, in_frac):
    """Shape the segment between keyframe i and i+1 with flat FREE handles."""
    pts = fc.keyframe_points
    a, b = pts[i], pts[i + 1]
    gap = b.co.x - a.co.x
    a.interpolation = 'BEZIER'
    a.handle_right_type = 'FREE'
    b.handle_left_type = 'FREE'
    a.handle_right = (a.co.x + out_frac * gap, a.co.y)
    b.handle_left = (b.co.x - in_frac * gap, b.co.y)


def ease(fc, preset='smooth', segments=None):
    """Apply a preset to every segment (or the given segment indices) of an F-curve."""
    pts = fc.keyframe_points
    if len(pts) < 2:
        return
    idx = range(len(pts) - 1) if segments is None else segments
    if preset == 'linear':
        for i in idx:
            pts[i].interpolation = 'LINEAR'
    elif preset in DYNAMIC:
        interp, mode = DYNAMIC[preset]
        for i in idx:
            pts[i].interpolation = interp
            pts[i].easing = mode
    else:
        o, n = PRESETS[preset]
        for i in idx:
            ease_segment(fc, i, o, n)
    fc.update()


def ease_object(idblock, preset='smooth', data_path=None):
    for fc in fcurves_of(idblock):
        if data_path is None or fc.data_path == data_path:
            ease(fc, preset)


def remove_bump(fc, key_index):
    """B-video fix: give a pass-through key one continuous slope (neighbour average), so velocity flows."""
    pts = fc.keyframe_points
    if not 0 < key_index < len(pts) - 1:
        return
    p, k, n = pts[key_index - 1], pts[key_index], pts[key_index + 1]
    slope = (n.co.y - p.co.y) / max(n.co.x - p.co.x, 1e-6)
    k.handle_left_type = k.handle_right_type = 'ALIGNED'
    dl, dr = (k.co.x - p.co.x) / 3, (n.co.x - k.co.x) / 3
    k.handle_left = (k.co.x - dl, k.co.y - slope * dl)
    k.handle_right = (k.co.x + dr, k.co.y + slope * dr)
    fc.update()


def copy_easing(src_fc, dst_fc):
    """Relative-Ease equivalent: copy handle fractions segment by segment (same key count)."""
    s, d = src_fc.keyframe_points, dst_fc.keyframe_points
    for i in range(min(len(s), len(d)) - 1):
        gap = max(s[i + 1].co.x - s[i].co.x, 1e-6)
        o = (s[i].handle_right.x - s[i].co.x) / gap
        n = (s[i + 1].co.x - s[i + 1].handle_left.x) / gap
        ease_segment(dst_fc, i, o, n)
    dst_fc.update()


def key(obj, path, frame, value=None, index=-1):
    """Set (optionally) and keyframe a property; returns nothing. Example: key(o, 'location', 30, (0,0,1))."""
    if value is not None:
        setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame, index=index)


def whip_transition(cam_a_owner, cam_b_owner, cut_frame, data_path='rotation_euler'):
    """A-video camera switch: owner A leaves on 'transition_out', owner B arrives on 'transition_in'.
    Owners are the animated objects (cameras or their pivot empties). Bind cameras at the cut with markers."""
    for fc in fcurves_of(cam_a_owner):
        if fc.data_path == data_path:
            ease(fc, 'transition_out', segments=[len(fc.keyframe_points) - 2])
    for fc in fcurves_of(cam_b_owner):
        if fc.data_path == data_path:
            ease(fc, 'transition_in', segments=[0])


def bind_camera(scene, cam, frame):
    """Ctrl+B in the timeline: a marker that switches the active camera at frame."""
    m = scene.timeline_markers.new(f'cam_{cam.name}', frame=int(frame))
    m.camera = cam
    return m
