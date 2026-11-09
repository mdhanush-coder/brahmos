def finish_plate(scene, step=2):
    """Make the plate compositable and measure where the device is: the floor becomes a shadow catcher, the film transparent
    (the designed background sits behind it in the Motion Graphic page), and keepout.json records the screen box of everything
    visible on every `step`-th frame (normalised, top-left origin), so overlay text can be checked never to cover the device."""
    import json, os
    from bpy_extras.object_utils import world_to_camera_view
    bd = bpy.data.objects.get('Backdrop')
    if bd:
        bd.is_shadow_catcher = True
    scene.render.film_transparent = True
    skip = ('Backdrop', 'skin_layer', 'return_glow_', 'foam_cut', 'antenna_cut', 'transistor_')
    objs = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render and not o.name.startswith(skip)]
    boxes = {}
    for f in range(scene.frame_start, scene.frame_end + 1, step):
        scene.frame_set(f)
        xs, ys = [], []
        for o in objs:
            for c in o.bound_box:
                p = world_to_camera_view(scene, scene.camera, o.matrix_world @ Vector(c))
                if p.z > 0:
                    xs.append(p.x)
                    ys.append(1 - p.y)
        if xs:
            boxes[f] = [round(max(0, min(xs)), 4), round(max(0, min(ys)), 4), round(min(1, max(xs)), 4), round(min(1, max(ys)), 4)]
    json.dump({'fps': scene.render.fps, 'step': step, 'frames': scene.frame_end, 'boxes': boxes}, open(os.path.join(out, 'keepout.json'), 'w'))
    scene.frame_set(scene.frame_start)
    result.update(keepout_frames=len(boxes), transparent=True, shadow_catcher=bool(bd))
