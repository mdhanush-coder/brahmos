"""Self-review helpers: render N preview frames spread over the timeline and audit every F-curve.
Needs easing_presets.py loaded first (fcurves_of)."""
import bpy, json, os


def review_frames(scene, n=6, start=None, end=None):
    s, e = start or scene.frame_start, end or scene.frame_end
    if n == 1:
        return [s]
    return sorted({int(round(s + (e - s) * i / (n - 1))) for i in range(n)})


def render_review(scene, folder, frames, prefix='review'):
    os.makedirs(folder, exist_ok=True)
    paths = []
    for f in frames:
        scene.frame_set(f)
        p = os.path.join(folder, f'{prefix}_{f:04d}.png')
        im = scene.render.image_settings
        if hasattr(im, 'media_type'):
            im.media_type = 'IMAGE'
        im.file_format = 'PNG'
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    return paths


def audit_fcurves(objects=None):
    """Flags: LINEAR/CONSTANT segments (unless the object is tagged allow_linear), single-key curves,
    velocity jumps at pass-through keys (the 'bump'), and segments faster than 1/3 of the shot length allows.
    Returns a dict suitable for result['fcurve_audit']."""
    rep = {'curves': 0, 'linear_segments': [], 'bumps': [], 'single_key': []}
    owners = objects or [o for o in bpy.data.objects]
    owners = list(owners) + [k for k in bpy.data.shape_keys]
    for o in owners:
        for fc in fcurves_of(o):
            rep['curves'] += 1
            pts = fc.keyframe_points
            tag = f'{getattr(o, "name", "?")}:{fc.data_path}[{fc.array_index}]'
            if len(pts) == 1:
                rep['single_key'].append(tag)
            allow = isinstance(o, bpy.types.Object) and o.get('allow_linear')
            for i in range(len(pts) - 1):
                if pts[i].interpolation in ('LINEAR', 'CONSTANT') and not allow and pts[i].co.y != pts[i + 1].co.y:
                    rep['linear_segments'].append(f'{tag} @ {pts[i].co.x:.0f}')
            for i in range(1, len(pts) - 1):
                p, k, n = pts[i - 1], pts[i], pts[i + 1]
                if (k.co.y - p.co.y) * (n.co.y - k.co.y) <= 0:
                    continue  # extreme or hold: a flat key is correct there
                eps = 0.5
                v_in = (fc.evaluate(k.co.x) - fc.evaluate(k.co.x - eps)) / eps
                v_out = (fc.evaluate(k.co.x + eps) - fc.evaluate(k.co.x)) / eps
                avg = abs(n.co.y - p.co.y) / max(n.co.x - p.co.x, 1e-6)
                if avg > 1e-6 and (abs(v_in) < 0.25 * avg or abs(v_out) < 0.25 * avg):
                    rep['bumps'].append(f'{tag} @ {k.co.x:.0f}')
    rep['ok'] = not rep['linear_segments'] and not rep['bumps']
    return rep


def check_framing(scene, objects, frames, margin=0.02):
    """Project every object's bound-box corners through the scene camera at each frame. Fails fast (before any
    render) if the camera points away, the subject is clipped, or parts leave the frame.
    Returns {'ok': bool, 'problems': [...]}. Run it after building the rig, on the review frames."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    cam, problems = scene.camera, []
    if cam is None:
        return {'ok': False, 'problems': ['no scene camera']}
    for f in frames:
        scene.frame_set(f)
        for o in objects:
            pts = [world_to_camera_view(scene, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
            if all(p.z <= 0 for p in pts):
                problems.append(f'f{f} {o.name}: behind camera')
                continue
            lo_x, hi_x = min(p.x for p in pts), max(p.x for p in pts)
            lo_y, hi_y = min(p.y for p in pts), max(p.y for p in pts)
            if hi_x < 0 or lo_x > 1 or hi_y < 0 or lo_y > 1:
                problems.append(f'f{f} {o.name}: fully outside frame')
            elif lo_x < margin or hi_x > 1 - margin or lo_y < margin or hi_y > 1 - margin:
                problems.append(f'f{f} {o.name}: touches/crosses frame edge')
    return {'ok': not problems, 'problems': problems[:30]}


def fill_fraction(scene, objects, frame):
    """Share of the frame width/height the union of `objects` covers at `frame`. A frame passes framing only if
    the subject is inside AND big enough: Phase-5 v2 'passed' check_framing with the subject at ~10 % of the frame."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    scene.frame_set(frame)
    xs, ys = [], []
    for o in objects:
        for c in o.bound_box:
            p = world_to_camera_view(scene, scene.camera, o.matrix_world @ Vector(c))
            xs.append(p.x)
            ys.append(p.y)
    return {'w': round(max(xs) - min(xs), 2), 'h': round(max(ys) - min(ys), 2)}


def sample_pixel(path, x, y_top, r=3):
    """Average sRGB (0-1) around normalised image point (x from left, y_top from top). Use to assert that a part
    renders the colour it was given (a red part must be red), before spending minutes on the final render."""
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    cx, cy = int(min(max(x, 0), 0.999) * w), int(min(max(1 - y_top, 0), 0.999) * h)
    win = a[max(cy - r, 0):cy + r + 1, max(cx - r, 0):cx + r + 1, :3].reshape(-1, 3).mean(axis=0)
    bpy.data.images.remove(img)
    return [round(float(v), 3) for v in win]


def write_report(folder, data):
    with open(os.path.join(folder, 'review.json'), 'w') as fh:
        json.dump(data, fh, indent=1)
