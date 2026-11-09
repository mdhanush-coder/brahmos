"""Render presets for EngineX Blender 5.x jobs. preview = fast review frames; final = delivery."""
import bpy

PRESETS = {
    # name: (engine, percent, samples, motion_blur)
    'preview':       ('CYCLES', 40, 32, True),
    'preview_eevee': ('EEVEE', 40, 32, True),
    'final':         ('CYCLES', 100, 256, True),
    'final_eevee':   ('EEVEE', 100, 128, True),
}


def _eevee_id():
    ids = {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    return 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ids else 'BLENDER_EEVEE_NEXT'


def apply(scene, name='preview', res=(1920, 1080), fps=30, shutter=0.5, look='AgX - Medium High Contrast'):
    engine, pct, samples, blur = PRESETS[name]
    r = scene.render
    r.engine = 'CYCLES' if engine == 'CYCLES' else _eevee_id()
    r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], pct
    r.fps = fps
    r.use_motion_blur = blur
    r.motion_blur_shutter = shutter
    r.film_transparent = False
    if engine == 'CYCLES':
        c = scene.cycles
        c.samples = samples
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.02 if 'preview' in name else 0.01
        c.use_denoising = True
        try:
            c.denoiser = 'OPENIMAGEDENOISE'
        except Exception:
            pass
        c.max_bounces, c.glossy_bounces, c.transmission_bounces = 8, 6, 8
        try:
            gpu(scene)  # EngineX helper: Cycles on the card
        except NameError:
            c.device = 'GPU'
    else:
        e = scene.eevee
        e.taa_render_samples = samples
        if hasattr(e, 'use_raytracing'):
            e.use_raytracing = True
        if hasattr(e, 'use_shadows'):
            e.use_shadows = True
    vs = scene.view_settings
    vs.view_transform = 'AgX'
    try:
        vs.look = look
    except TypeError:
        vs.look = 'None'
    return scene


def video_output(scene, path, crf='HIGH'):
    """MP4 H.264. Blender 5.x needs image_settings.media_type = 'VIDEO' before FFMPEG."""
    im = scene.render.image_settings
    if hasattr(im, 'media_type'):
        im.media_type = 'VIDEO'
    im.file_format = 'FFMPEG'
    ff = scene.render.ffmpeg
    ff.format, ff.codec = 'MPEG4', 'H264'
    ff.constant_rate_factor = crf
    ff.ffmpeg_preset = 'GOOD'
    scene.render.filepath = path


def still_output(scene, path, fmt='PNG'):
    im = scene.render.image_settings
    if hasattr(im, 'media_type'):
        im.media_type = 'IMAGE'
    im.file_format = fmt
    scene.render.filepath = path
