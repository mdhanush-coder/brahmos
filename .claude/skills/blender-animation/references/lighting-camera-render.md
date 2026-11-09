# Lighting, camera, render

Values below are either read from the reference videos (marked V) or settled in the Phase-5 tests (marked T).
Scripts: `studio_lighting.py`, `camera_orbit.py`, `render_presets.py`, `review.py`.

## Camera
- Products: 50-90 mm. V: 90 mm for a chair at 1080x1920 (tight, flattering, little perspective). T: 50 mm for a wide
  exploded product at 16:9, close-up start via a 0.3x dolly.
- Sensor 36 mm; `frame_width_distance(width, focal, fill)` (horizontal layouts) and `frame_distance(radius, focal, fill)`
  (vertical) place the camera so the subject fills `fill` of the frame (0.6-0.8).
- DOF: `fstop` 11 for assemblies (everything sharp), 4-8 for hero objects, 2.8 macro; focus object = the pivot empty.
- Camera always on a pivot empty at the subject centre; aim with `look_at_local` (it asserts the aim). Clip start 0.01.
- Moves: orbit +-20-25 deg, dolly breathing (0.3 -> 1.0), push-in reveal; never a static camera.
- Vertical (reels): 1080x1920; horizontal: 1920x1080; fps 30 (V video A used 30, video B 25, video 4 30).

## Lighting
- Studio = HDRI (reflections, `strength` 0.5-0.7, rotation ~40 deg) + three-point:
  key 45 deg camera-left and high, warm (1.0, .95, .88), power `~600*r^2` W (T: `key_power=320` was right for r=1);
  fill opposite at 25 % power, cool (0.9, .95, 1.0), softer (size 4r); rim behind and above at 120 % for the edge.
- Camera sees a dark flat background while the object still gets HDRI light: `hdri_world(..., background_strength=1.0)`
  (Light Path "Is Camera Ray" mix).
- Backdrop: `cyclorama(size, height, bevel)` = plane, back edge extruded, corner beveled (V), **much larger than the
  camera can see** (T: size 150) so no edge ever appears; colour ~0.02, roughness 0.8 for a dark studio.
- Two-light variant (V): area lights left/right; the second **light-linked to the model only** to avoid extra shadows.
- Metals need something to reflect: a plain dark room makes them look dead. Keep the HDRI on.
- Avoid pure white parts: a white default material in a lit scene reads as a defect (and was one: see Failure log 3).

## Render engines and settings
| Use | Engine | Samples | Notes |
|---|---|---|---|
| preview frames | Cycles | 32 | 40 % of target res, adaptive threshold 0.02, OIDN denoise |
| delivery plate (T) | Cycles OptiX | 64 at 1280x720 (upscale) / 128 at 1080p | adaptive 0.01, denoise, bounces 8/6/8 |
| fast / background assets (V) | EEVEE | render 64, viewport 16 | Raytracing on, Shadows on, Film filter 1.50 px |
| stills, hero | Cycles | 256 | |
- Colour: **AgX**, look "Medium High Contrast"; filmic is gone in 4+.
- Motion blur on, shutter 0.5. Output: `video_output` = FFMPEG MP4 H.264 CRF HIGH (`media_type='VIDEO'` first on 5.x).
- GPU: Cycles always on the card in EngineX (`device: auto` = OptiX).
- Timing seen (T): 6 review frames at 768x432/32 spp ~5 s total; plate cost grows with samples x pixels - budget
  before launching and watch `get_job` progress.

## Review numbers to hit
Subject >= 50 % of frame width at the hero beat, <= 85 % anywhere (no edge crowding); label pills >= 22 px at 1080p;
background luminance clearly different from the subject's edges; no clipped highlights on the key side;
`audit_fcurves().ok`; `check_framing().ok`; colour assertions pass.
