# Smooth animation (easing, Graph Editor, camera moves)

Sources: `learning/smooth-animation-a/notes.md` (ArtSyndrom3, Blender 5.1), `learning/smooth-animation-b/notes.md`
(Blender To Browser, Blender 5.0). Scripts: `easing_presets.py`, `camera_orbit.py`, `turntable.py`.

## The idea
Easing is velocity control. Handle length relative to the gap between two keys decides speed near the key: long flat
handle = slow near that key; short/zero handle = leaves/arrives at full speed. Default auto-clamped handles give
uniform "robotic" motion. Every professional move shapes the handles.

## The Big 3 (video A) and the equivalent values
Graph Editor: select keys, `S` then `X` scales the handles' time extent ("Scale: 2.0453 along X" is typical).
| Look | Do by hand | `easing_presets.PRESETS` (out_frac, in_frac) |
|---|---|---|
| Ease out (smooth ending) | S X on the LAST key | `ease_out` (0.15, 0.70) |
| Ease in (slow start, quick end) | S X on the FIRST key | `ease_in` (0.70, 0.15) |
| Ease in-out (quick whip) | S X on both | `ease_in_out` (0.50, 0.50) |
| Hero move default | EaseIt "Smooth" | `smooth` (0.40, 0.40) |
| Luxurious | EaseIt "Super Smooth" | `super_smooth` (0.60, 0.60) |
| Leave slowly, hit the cut at speed | first handle ~full, last ~0 | `transition_out` (0.90, 0.00) |
| Arrive from the cut at speed, settle | first ~0, last ~full | `transition_in` (0.00, 0.90) |
| UI pop that settles | - | `snappy` (0.20, 0.80) |
Duration changes the feel: longer gap + big handles = slow and silky; short gap + same handles = smooth but fast.
Fractions are of the key gap; handle type must be FREE (`handle_right_type = 'FREE'`), interpolation BEZIER.

## Graph Editor mechanics (by hand -> bpy)
- `Ctrl+Tab` toggles Dope Sheet <-> Graph Editor. Select in the Dope Sheet first; selection carries over.
- **Normalize** (header toggle) puts every channel in -1..1 so shapes are comparable; `Home` frames all.
- Lock channels you do not want to edit (padlock): `fcurve.lock = True`.
- Active Keyframe panel (N > F-Curve tab): Interpolation Bezier, Left/Right Handle Type Free, Key Frame, Value.
  F-curve option "Handle Smoothing: Continuous Acceleration" smooths velocity across keys.
- `G X` slides keys in time, `S X` stretches timing (video 4 stretched 60 -> 120 frames this way).
- `T` menu: Dynamic Effects (Back, Bounce, Elastic) exist; staying on Bezier "looks pretty good".
- **EaseIt** extension (Blender Extensions, Blender 4.2+, GPL): N panel > EaseIt tab, `A` select all, click preset.
  Presets: Symmetric (Default, Just Fine, Cubic, Exponential, Extreme, Linear, Max); Asymmetric (Smooth, Easy, Super
  Smooth, Smooth Out, Easy Out, Super Smooth Out); One-sided (Ease In Only, Ease Out Only); Advanced (Explosive,
  Springy, Overshoot 1/2/x3, Anticipation 1/2/3, Easy Going, Antic + Over, Agitated, Very Late Stop, Spring Back,
  Bouncy, Weird). Overshoot/spring presets ADD keyframes. Headless: use `easing_presets.ease(fc, name)`; for
  overshoot/bounce/elastic use `DYNAMIC` presets (`BACK/BOUNCE/ELASTIC` with `EASE_OUT`).
- **Relative Ease** add-on copies easing from one shot to another: `copy_easing(src_fc, dst_fc)`.

## Camera rig and shot recipe (video B, values exactly)
- Camera parented to a **plain-axes empty** ("shotN movement") in collection `shotN`; rotate the EMPTY, not the camera.
- Focal length 90 mm (typed over 50 mm) for a chair at 1080x1920; fps 25 in that file; cycles GPU.
- Rules card kept in the file: change rotation 40 deg, change duration 20 frames, change start after 40 frames,
  shot duration 50 frames, default drift after a change 10 deg. `camera_orbit.RULES`.
- Shot 1: entry key at frame 40-50 (end pose), then frame 1 pulled back (push-in reveal). Exit: Z rotation key at 40,
  +30 deg at 55 (later 20 frames / 40 deg).
- Shot 2+: duplicate empty + camera, move the empty, new collection, delete copied keys. Entry mirrors the exit:
  -40 deg at frame 40, 0 at 60. Bind the camera with `Ctrl+B` in the timeline at the **middle of the transition
  (peak velocity, ~frame 50)** and bind the previous camera at frame 1. Keep drifting (+10 deg at frame 90), then the
  exit +40 more (total 50). Copy easing from shot 1.
- **Remove the bump**: after pasting easing, a velocity jump appears at the middle key. Select the middle key and rotate
  its handles (R) until the slope is continuous: `remove_bump(fc, key_index)`.
- `shot_sequence(scene, [(pivot, camera), ...])` builds all of the above with markers and bump removal.
- Lights: two area lights (right, left); the left one **light-linked to the model only** (`two_area_lights`).
- Multi-angle sequences: new scene with Full Copy per angle (rotate the model in the copy, reuse empties).

## Hero transition recipe (5 s, 30 fps, 150 frames) - `scripts/example_hero_transition.py`, passed review
Library product, dark cyclorama, HDRI 0.5 + three-point (`330*r^2` W), 85 mm, motion-blur shutter 0.75.
- Shot A camera (f/5.6, 66 % of frame height at the end): pivot orbit -28 deg at f1 -> +4 at f52 (`ease_segment 0.30/0.70`,
  settles), +4 at f58 (near-hold 0.5/0.5), +46 at f80 (`0.90/0.00` = leaves at full speed). Dolly 1.30 -> 1.0 over f1-58
  (`ease_out`).
- Shot B camera (f/4, 80 % of frame height): pivot orbit -46 at f72 -> 0 at f98 (`0.00/0.90` = arrives at full speed,
  long settle), +12 at f150 (`0.45/0.60`, `remove_bump`). Dolly 1.04 -> 0.90 (`ease_in_out`).
- **Cut at f76** via `bind_camera` markers = the midpoint of the overlap, where both curves are at peak velocity, so
  motion blur hides the join. Nothing is ever linear, nothing stops dead.
- Size the cameras from the body height (not the bounding sphere), gate on `fill_fraction`, then render.
- Overlay (title, lower third, price tag...) belongs in Motion Graphic, not in the 3D scene.

## My additions that proved necessary (Phase 5)
- **Breathing dolly**: open close on the assembled/hero object (`dolly(cam, [(1,.3),(70,1),(250,1),(300,.3)])`, scales
  the camera's y AND z so it keeps aiming), with the pivot sliding between centres. Pull out as the action widens.
- Orbit the pivot slowly the whole shot (44 deg over 10 s, `ease_in_out`): a static camera reads as a still.
- Hold 2.5 s+ on any state the viewer must read.
- A 5 s product hero: 0-0.6 s settle-in from a slight scale/position offset (`hero_reveal`, `super_smooth`), orbit 25-40
  deg throughout, DOF f/4-f/8, end on a held hero angle.
- Audit: `audit_fcurves()` flags LINEAR segments and velocity bumps; run it every time.
