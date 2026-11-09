"""Turntable and hero-move rigs. Needs easing_presets.py loaded first."""
import bpy, math


def turntable(target_obj, start, end, turns=1.0, preset='linear'):
    """Rotate the product (via a parent empty) around Z. 'linear' only for seamless loops; use
    'smooth' / 'super_smooth' for a hero move that starts and settles."""
    piv = bpy.data.objects.new(f'{target_obj.name}_turntable', None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = target_obj.matrix_world.translation.copy()
    mw = target_obj.matrix_world.copy()
    target_obj.parent = piv
    target_obj.matrix_world = mw
    key(piv, 'rotation_euler', start, (0, 0, 0), index=2)
    key(piv, 'rotation_euler', end, (0, 0, math.tau * turns), index=2)
    for fc in fcurves_of(piv):
        ease(fc, preset)
        if preset == 'linear':
            fc.modifiers.new('CYCLES')
    return piv


def hero_reveal(obj, start, end, rise=0.3, spin_deg=200.0, scale_from=0.85):
    """5 s product hero: rises, spins and settles (super_smooth), with a small overshoot-free scale-in."""
    loc, rot, sc = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()
    key(obj, 'location', end, tuple(loc))
    key(obj, 'rotation_euler', end, tuple(rot))
    key(obj, 'scale', end, tuple(sc))
    key(obj, 'location', start, (loc.x, loc.y, loc.z - rise))
    key(obj, 'rotation_euler', start, (rot.x, rot.y, rot.z - math.radians(spin_deg)))
    key(obj, 'scale', start, tuple(v * scale_from for v in sc))
    ease_object(obj, 'super_smooth')
