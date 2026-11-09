"""Second eye (user: "where is the second eye"), slimmer brainstem, softer world light so the gold is richer."""
import ast
s = open('head_scene.py', encoding='utf-8').read()

a = s.index("    # eye on the device's side (+X)")
b = s.index('    # device: ray-cast')
EYES = '''    # both eyes (x = +/-3.2 cm), each just under the front surface (found by a ray from the front)
    eyes = []
    for sx in (1, -1):
        ex = 0.032 * sx
        hit_e, _, _, _ = hb[0].ray_cast(Vector((ex, -0.5, zE)), Vector((0, 1, 0)))
        eye_c = Vector((ex, (hit_e.y if hit_e else yF) + 0.009, zE))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.0118, location=eye_c)
        e = bpy.context.active_object; e.name = 'Eye' if sx > 0 else 'Eye_L'; bpy.ops.object.shade_smooth()
        e.data.materials.append(_emit_mat('Sclera', (0.92, 0.94, 0.97), 0.15, rough=0.15))
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0056, depth=0.0012, location=eye_c + Vector((0, -0.0114, 0)),
                                            rotation=(math.pi / 2, 0, 0))
        iris = bpy.context.active_object; iris.name = 'Iris' if sx > 0 else 'Iris_L'
        iris.data.materials.append(_emit_mat('Iris', (0.18, 0.32, 0.45), 0.2))
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0026, depth=0.0014, location=eye_c + Vector((0, -0.0118, 0)),
                                            rotation=(math.pi / 2, 0, 0))
        pupil = bpy.context.active_object; pupil.name = 'Pupil' if sx > 0 else 'Pupil_L'
        pupil.data.materials.append(_emit_mat('Pupil', (0.01, 0.01, 0.012), 0.0, rough=0.05))
        eyes.append(e)
    eye = eyes[0]
'''
s = s[:a] + EYES + s[b:]
old = "radius1=0.011, radius2=0.015, depth=0.11"
assert old in s
s = s.replace(old, "radius1=0.0075, radius2=0.010, depth=0.11")
ast.parse(s)
open('head_scene.py', 'w', encoding='utf-8').write(s)

j = open('head_review_job.py', encoding='utf-8').read()
old = "hdri_world(color=(0.55, 0.62, 0.80), strength=1.0, background_strength=0.0)"
assert old in j
j = j.replace(old, "hdri_world(color=(0.55, 0.62, 0.80), strength=0.6, background_strength=0.0)")
open('head_review_job.py', 'w', encoding='utf-8').write(j)
parts = ['../../.claude/skills/blender-animation/scripts/skilllib.py', 'temple_model.py', 'head_scene.py', 'head_review_job.py']
b2 = '\n\n'.join(open(p, encoding='utf-8').read() for p in parts)
ast.parse(b2)
open('job_head_review2.py', 'w', encoding='utf-8').write(b2)
print('ok')
