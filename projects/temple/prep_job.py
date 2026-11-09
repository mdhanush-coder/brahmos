# Opens a chapter .blend (input), makes the plate compositable and measures where the device is on screen.
# 1) Backdrop -> shadow catcher, film transparent: the plate keeps only the device and its floor shadow, so a designed
#    background can sit behind it in the Motion Graphic page.
# 2) For every STEP-th frame, the screen box of everything visible (normalised, top-left origin), written to keepout.json:
#    the overlay's text must stay outside these boxes.
import bpy, os, json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

S = bpy.context.scene
STEP = args.get('step', 2)
bd = bpy.data.objects.get('Backdrop')
if bd:
    bd.is_shadow_catcher = True
S.render.film_transparent = True
skip = ('Backdrop', 'skin_layer', 'return_glow_', 'foam_cut', 'antenna_cut', 'transistor_')
objs = [o for o in S.objects if o.type == 'MESH' and not o.hide_render and not o.name.startswith(skip)]
boxes = {}
for f in range(S.frame_start, S.frame_end + 1, STEP):
    S.frame_set(f)
    cam = S.camera
    xs, ys = [], []
    for o in objs:
        for c in o.bound_box:
            p = world_to_camera_view(S, cam, o.matrix_world @ Vector(c))
            if p.z > 0:
                xs.append(p.x)
                ys.append(1 - p.y)
    if xs:
        boxes[f] = [round(max(0, min(xs)), 4), round(max(0, min(ys)), 4), round(min(1, max(xs)), 4), round(min(1, max(ys)), 4)]
json.dump({'fps': S.render.fps, 'step': STEP, 'frames': S.frame_end, 'boxes': boxes}, open(os.path.join(out, 'keepout.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, args.get('name', 'scene') + '.blend'), copy=True)
result.update(objects=len(objs), frames=len(boxes), transparent=S.render.film_transparent, shadow_catcher=bool(bd))
