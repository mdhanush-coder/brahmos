# Look pass: the BrahMos model with materials, 4 lit stills (960x540, Cycles 48 spp) on the night background.
import os
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
P = brahmos_import(inputs['brahmos.glb'])
night_world(0.7)
scene.render.engine = 'CYCLES'
try: gpu(scene)
except NameError: scene.cycles.device = 'GPU'
scene.cycles.samples = 48; scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 50
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = -0.2
c = Vector((4.2, 0, 0))
key_l, fill, rim = three_point(c, 4.2, camera=None, key_power=60.0 * 4.2 * 4.2)
scene.frame_set(1)
shots = [('hero', (13.0, -8.0, 2.2), (4.6, 0, 0), 35, 8.0, []),
         ('side', (4.2, -13.0, 0.4), (4.2, 0, 0), 50, 11.0, []),
         ('nose', (9.7, -1.7, 0.8), (7.9, 0, 0.05), 50, 4.0, []),
         ('canister', (12.5, -9.5, 3.0), (4.2, 0, 0), 35, 8.0, CANISTER_PARTS)]
hide_missile_for = {'canister'}
paths = []
for name, loc, tgt, f, fs, show_only in shots:
    for o in scene.objects:
        if o.type == 'MESH':
            is_can = o.name.startswith('canister')
            o.hide_render = (not is_can) if name in hide_missile_for else is_can
    cam = cam_at('cam_' + name, loc, tgt, f, fs)
    scene.camera = cam
    p = os.path.join(out, f'look_{name}.png')
    still_output(scene, p)
    bpy.ops.render.render(write_still=True)
    paths.append(p)
result['stills'] = [os.path.basename(p) for p in paths]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'brahmos_look.blend'), copy=True)
