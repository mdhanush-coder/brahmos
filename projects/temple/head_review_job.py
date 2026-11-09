# head_review_job.py - first look at the anatomy scene (user reference: x-ray head, pink brain with red arteries, blue veins,
# eye, gold device sending a coloured light cone, glowing yellow temporal artery). Runs after skilllib + temple_model + head_scene.
import os, math
A = args
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
parts, info, P = build_head_scene(face=A.get('face'))
result['info'] = info
# stage: transparent film (a designed page sits behind), Eevee, dark world so emissive parts read
scene.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items} else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 50
scene.render.film_transparent = bool(A.get('transparent', False))   # review over a dark world; plates are transparent
hdri_world(color=(0.55, 0.62, 0.80), strength=0.6, background_strength=0.0)   # reflections for the gold; the camera sees black
scene.view_settings.view_transform = 'Standard'
c = Vector(info['brain_c'])
for name, loc, energy in (('key', (0.55, -0.7, 0.5), A.get('key', 25)), ('rim', (-0.6, 0.6, 0.4), A.get('rim', 45))):
    L = bpy.data.lights.new(name, 'AREA'); L.energy, L.size = energy, 0.5
    o = bpy.data.objects.new(name, L); scene.collection.objects.link(o); o.location = Vector(loc)
    bpy.context.view_layer.update(); look_at(o, c)
cam = make_camera('Cam', focal=A.get('focal', 85), fstop=2.8, focus=None)
scene.camera = cam
os.makedirs(out, exist_ok=True)
# three review angles: 3/4 from the device side (the reference), front, back-left
views = {'three_quarter': (0.6, -0.6, 0.08), 'side': (1.0, 0.0, 0.05), 'front': (0.12, -1.0, 0.05)}
for nm, (dx, dy, dz) in views.items():
    cam.location = c + Vector((dx, dy, dz)) * A.get('dist', 0.7)
    bpy.context.view_layer.update()   # look_at reads matrix_world: stale until updated (Phase-5 bug)
    look_at(cam, c + Vector((0, 0, -0.01)))
    scene.render.filepath = os.path.join(out, f'head_{nm}.png')
    im = scene.render.image_settings
    if hasattr(im, 'media_type'):
        im.media_type = 'IMAGE'
    im.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'head.blend'), copy=True)
result['done'] = True
