"""Concatenate the bpy helper scripts into one skilllib.py for an EngineX blender/script job.
Usage: python bundle.py [out_path]. In the job: exec(open(inputs['skilllib.py']).read(), globals())"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['easing_presets.py', 'camera_orbit.py', 'studio_lighting.py', 'render_presets.py', 'turntable.py',
         'exploded_view.py', 'materials.py', 'product_models.py', 'focus_rig.py', 'image_to_3d.py', 'mixamo_import.py', 'review.py']
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'skilllib.py')
src = '\n\n'.join(f'# ===== {n} =====\n' + open(os.path.join(HERE, n), encoding='utf-8').read() for n in ORDER)
src = src.replace('PRESETS = {\n    # name: (engine', 'RENDER_PRESETS = {\n    # name: (engine').replace('engine, pct, samples, blur = PRESETS[name]', 'engine, pct, samples, blur = RENDER_PRESETS[name]')
src = src.replace('def apply(scene, name=', 'def render_preset(scene, name=')
compile(src, 'skilllib.py', 'exec')
open(out, 'w', encoding='utf-8').write(src)
print('wrote', out, len(src), 'bytes')
