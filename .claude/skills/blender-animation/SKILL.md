---
name: blender-animation
description: Use for ANY Blender, 3D modeling, product visualization, exploded view, 3D transition, or animation task through EngineX. Defines the required modeling, animation, lighting, asset, and render-review workflow.
---

# Blender animation through EngineX (professional bar)

Every Blender/3D task here runs through EngineX tools (`blender/script`, `blender/render`, `motion-graphic/render`,
`media-fetch`, `video`, `image/montage`). Local file tools only write files. Default output of a bare script is a grey
box under default light: **that is a failure, not a draft.** This skill exists to prevent it.

## 0. Setup for every job (copy this)
1. `python .claude/skills/blender-animation/scripts/bundle.py` -> `scripts/skilllib.py` (all helper modules in one file).
2. `create_upload_url` for `skilllib.py` (and your job file), `curl -T` it, pass keys as `files={"skilllib.py": key}`.
3. Job code starts: `exec(open(inputs['skilllib.py']).read(), globals())`. Helpers: `fcurves_of ease key whip_transition
   bind_camera make_orbit_rig make_camera look_at frame_distance frame_width_distance orbit dolly push_in shot_sequence
   cyclorama hdri_world three_point two_area_lights render_preset video_output still_output turntable hero_reveal
   gather_asset rotate_assembly explode auto_axes bounds_world add_callout wobble_rotation shape_key_click
   library_material anodized metal assign_material drone_motor image_plane silhouette_from_alpha relief_regions
   review_frames render_review audit_fcurves check_framing fill_fraction sample_pixel`.
4. Long renders: `waitMs` max is 120000 and a longer wait **times out the client and loses the job id**. Always send
   `idempotencyKey` (so the job can be found again) and `waitMs: 0` for anything that renders an animation, then poll
   `get_job` (`show: true` shows the newest frame).
5. Reference job to copy from: `scripts/example_exploded_motor.py` (+ `callouts_page.py`).
6. **EngineX call budget: at most 500 calls per video (user's manager rule), aim far lower.** Plan the calls before
   starting; batch (one montage for all review frames, one `sign_output` for every file, up to 50 keys); predict
   output keys (`frame-NNNN.jpg`, `sheet-NNN.jpg`) instead of polling `get_job` (its echo is huge); wait with a
   background `sleep` instead of polling; download H.264 (`bv*[vcodec^=avc1]`) so scene detection needs no proxy;
   one Blender job per sequence; **never re-run a job that succeeded** - `idempotencyKey` on every run. Count and
   report the calls used. (Studying the Branch video cost 7 calls.)

## 1. MANDATORY WORKFLOW (every task, in order)
1. **Plan the shot list.** Write duration, fps (30 default), resolution, every camera move, and the beats with frame
   numbers *before* touching Blender. Hold at least 1 s on the hero state; open on a close-up or wide, never mid-air.
2. **Find real assets first.** `python scripts/find_asset.py <words>` (see `references/asset-library.md`). Model from
   primitives only if the catalog has nothing usable; then follow step 3 in full (`scripts/product_models.py` shows the
   standard: separate real parts, real proportions, bevels, weighted normals). Say which you did.
3. **Model with detail.** Bevel every hard edge (width ~ 1/60 of the part, 2-3 segments, `limit_method=ANGLE`),
   Weighted Normal, smooth shading, real-world proportions and scale (metres), **separate objects for anything that
   moves**, origins at the pivot (hinge/axis centre), no overlapping z-fighting faces.
4. **PBR materials from the library**, applied with `assign_material()` only. Check `material['missing_maps']`.
   Metals: metallic 1, roughness never 0 (0.12-0.4). Never leave a default grey material.
5. **Lighting.** HDRI for reflections + key/fill/rim (`three_point`) or a studio cyclorama. Floor/backdrop bigger than
   anything the camera can see. Never default light.
6. **Camera.** Deliberate focal length (products 50-90 mm; see `lighting-camera-render.md`), DOF on the subject,
   a camera move on every shot (orbit, dolly, push-in), rig on a pivot empty, never rotate the camera directly.
7. **Animate with easing** per `references/smooth-animation.md`: Bezier + FREE handles, in/out handle fractions,
   remove velocity bumps, camera cuts at peak velocity. No linear unless the object is tagged `allow_linear`.
8. **Render preview frames** (>= 5 spread over the timeline, plus the first and last frame) at low res.
9. **Review them** with the self-review loop below. Look at the images; do not trust numbers alone.
10. **Fix, then repeat 8-9** until every check passes.
11. **Final render** at delivery settings (`render_preset(scene, 'final')` or the plate settings), then report.

## 2. QUALITY BAR (hard rules)
- No default primitive as a final object. No default grey material. No default lighting.
- No LINEAR/CONSTANT interpolation unless intended and tagged. Every move has ease in AND out (or a deliberate one-sided
  ease with a reason). `audit_fcurves()` must return `ok: true`.
- Camera deliberately placed and moving; subject fills 40-85 % of the frame at the hero beat (`fill_fraction`), is never
  clipped (`check_framing` ok), and the first/last frames are composed stills, not empties.
- Motion blur ON for fast motion (shutter 0.5, `render_preset` does it). DOF on for hero shots (f/8-f/11 for product
  assemblies so the whole stack stays sharp, f/2.8-f/4 for single-object macro).
- Labels/callouts/titles are 2D type from Motion Graphic over a clean 3D plate (`callouts_page.py`), never 3D text
  floating in the scene (collides, aliases, clips).
- Colour must be what was asked: assert it with `sample_pixel` (a red part renders red) before long renders.
- Credit any library asset that carries an `attribution` where the result is published.

## 3. SELF-REVIEW LOOP (do not skip, do not shorten)
Render at least **6 frames** spread across the timeline at low resolution (`review_frames(scene, 6)`; include frame 1
and the last frame). **Look at every frame** (put them on one `image/montage` sheet, `sign_output`, download, `Read`).
Check each one for:
1. **Silhouette** - does the subject read at thumbnail size? Parts separated, nothing merged into a blob?
2. **Materials** - correct colours and metals, no grey/white default, no stretched textures, reflections plausible.
3. **Lighting** - shape-defining key, readable shadows, no blown highlights or dead black, background separates the subject.
4. **Framing** - subject large enough, inside the safe area, composed on first and last frames, no stray edges of the
   backdrop, no dead empty areas.
5. **Motion smoothness** - `audit_fcurves()` (no linear segments, no velocity bumps), plus sampled frames either side of
   each key look continuous; camera cuts happen at peak velocity.
Numeric gates run *before* looking: `check_framing(scene, parts, frames)`, `fill_fraction`, `audit_fcurves`,
`sample_pixel` colour assertions. Gate the expensive render on them (see the example job).
Then **fix and repeat** until all pass. The final answer lists what was checked and what was fixed on each pass.

## 4. Reference files - when to load
| Request | Read | Scripts |
|---|---|---|
| any animation, camera move, transition, "smooth" | `references/smooth-animation.md` | `easing_presets.py`, `camera_orbit.py`, `turntable.py` |
| product hero / whip transition between two angles | `references/smooth-animation.md` (Hero transition) | `example_hero_transition.py` |
| narrated "how it works" video, visuals synced to voice, Branch Education style | `references/narrated-explainer.md`; for a FULL video from a topic use the `tech-explainer-video` skill | `beat_sheet.py --snap`, `focus_rig.py` (untested), `callouts_page.py --beats` |
| exploded view, product breakdown, labels/callouts | `references/exploded-view.md` | `exploded_view.py`, `product_models.py`, `callouts_page.py`, `example_exploded_motor.py` |
| 2D image/photo/logo -> 3D relief or object | `references/image-to-3d.md` | `image_to_3d.py` |
| characters, walk/run/idle, Mixamo FBX, NLA | `references/character-mixamo.md` | `mixamo_import.py` |
| lights, camera lens, DOF, render engine/samples, HDRI | `references/lighting-camera-render.md` | `studio_lighting.py`, `render_presets.py`, `review.py` |
| finding models/materials/HDRIs/rigs | `references/asset-library.md` | `find_asset.py`, `assets/catalog.json`, `materials.py` |
| a product from reference pictures, layered explode, light/optics, overlays that avoid the model | section 7 (Temple) | `projects/temple/*` |
Always also read `references/lighting-camera-render.md` for any task that renders.

## 5. Delivering
- Final render through EngineX (`blender/script` animation or `blender/render`), 2D overlays through
  `motion-graphic/render` (plate as `<video>` in `media`, page from `callouts_page.py`), return `sign_output` links.
- Report: shot list, assets used (with attribution), what the review passes found and fixed, render settings, links.
- If a review pass shows a problem class this skill does not prevent, add it to the Failure log below in the same task.

## 6. FAILURE LOG (each line was a real defect found by the review loop; the guard is in the scripts)
1. **Camera aimed at nothing** (empty grey frames): a stale `matrix_world` copied back over `rotation_euler`.
   Guard: `look_at_local` asserts the aim; `check_framing` fails when the subject is off-frame.
2. **Subject only 10 % of frame**: vertical explode in a 16:9 frame. Guard: `rotate_assembly` puts the axis on X;
   `fill_fraction`; `frame_width_distance`.
3. **Parts rendered default grey** whatever material was set: an applied Boolean leaves an empty material slot 0.
   Guard: `assign_material()` clears slots; `_boolean` clears after apply; `sample_pixel` asserts colour.
4. **Boolean ate whole parts** (base mount lost its arms): overlapping primitives need `use_self=True` on EXACT.
5. **USD import resets the frame range** (review frames came out as -1 and 0): set `frame_start/end` after importing.
6. **SimReady USD meshes come back unparented**: collect them by set difference, not `holder.children`.
   `separate_loose` returns by set difference too (headless has no `selected_objects` after operators).
7. **Mix-node tint never connected** (`inputs['A']` is the float socket): pick sockets by `.type == 'RGBA'`.
8. **Dolly scaled y only**, so the subject slid out of frame: scale the whole local offset; slide the pivot between the
   assembled and exploded centres.
9. **World-space leader curve** collapsed to the world origin when scaled: build it in local space at the anchor.
10. **Labels collided / sat under the floor / clipped**: labels moved to Motion Graphic, rows staggered by x rank,
    `overlap_report` checks every frame.
11. **Long render lost its job id** on a client timeout: always `idempotencyKey` + `waitMs: 0` + `get_job`.
12. **Last parts' labels only visible ~1 s**: explode needs a hold of >= 2.5 s after the last part arrives
    (stagger 6 frames, start hold 18).
13. **A gate rule can be wrong too** (blue nut sampled on a specular highlight failed `b > 1.5 r`): gate on dominance
    (`b > r and b > g`), then look at the frame.
14. **Hero opened at 20 % of the frame and cropped the body at the bottom** (`check_framing` only tests "inside the
    frame"): size cameras from the BODY height (`bbox.z`), not the bounding sphere (chains/cables inflate it), and gate on
    size: `fill_fraction` h >= 0.35 at the opening, >= 0.6 at the hero, <= 1.05 everywhere (see `example_hero_transition.py`).
15. **Bright pool on the floor from a close key light**: floor colour ~0.015, roughness 0.85, key power ~330*r^2, lights
    >= 4r away; check the first frame for hotspots.
16. **Exploded view: subject small next to the labels**: camera `fill` 0.74 on the exploded width, labels 24 px / pill
    320x82, vignette in the overlay; gate `0.55 <= fill_width <= 0.92` at the peak.
17. **A client timeout loses the job id**: a call that does not return cannot be recovered (there is no job list).
    Long renders: `idempotencyKey` + `waitMs: 0`, then `get_job`. Measured: 1280x720 / 64 spp Cycles, 300 frames of this
    scene = 5.8 min (~1.2 s/frame); budget 1080p / 96 spp at ~2.5x that.
18. **A wrong gate wasted nothing, a missing gate wasted 20 minutes** (twice a full render was started on a scene that
    had never been looked at): preview 3-6 frames, assert, look, THEN launch the animation.
19. **Gold rendered pale cream** (Temple hero, `AgX - Medium High Contrast` + a flat white studio reflection on a flat face):
    brand/gold colours need `view_transform='Standard'`, `look='None'`, exposure -0.2, a deeper base (1.0, 0.68, 0.2), the
    HDRI at ~0.55 and the key at ~190*r^2; judge on the lit review sheet, never on the Workbench snapshot.
20. **A flat metal face reads as a button/coin**: give it a raised plate in a rougher gold plus a thin dark groove ring
    (the groove must stand ABOVE the shell top, or it is hidden), so the face has a panel line and a second reflection.
21. **The EngineX `kit.py` is not served by `get_skill`** (only the .md references): use the local `bundle.py` ->
    `skilllib.py`, concatenate `skilllib.py + model + job` into ONE file, upload it once per iteration
    (`create_upload_url` + `curl -T`), run with `code="exec(open(inputs['job.py']).read(), globals())"`. First real
    EngineX run of this pipeline: build + 6 lit review frames in 6.7 s, no fix needed for camera/rig/audit.
22. **Invented shape instead of the real one**: Temple was first modelled as an oval with a groove ring; the reference picture
    is a plump kidney-bean pebble with no panel lines. Ask for / look at the product's real reference image BEFORE modelling;
    loft a smooth shell from rings of the outline (rounded bottom, vertical side, dome) instead of bevelling a flat slab, so
    the whole face has a soft gradient. Space emitters >= 3x their radius or their glows merge.
23. **Exploded layers seen only edge-on / from below** (Temple ch4: PCB traces never faced the camera): crane the rig by keying
    the orbit pivot's rotation X (negative = camera rises; ~-38 deg gives ~50 deg looking down) on the exploded holds, and
    pull the dolly back at the same keys or the lifted top part crosses the frame edge. Key the pivot's Z too, so the aim
    tracks the assembled device (low) vs the exploded stack (mid). Never add a pass-through dolly key inside a monotonic move
    (audit flags a velocity bump). Judge fine texture (traces, grids) on a 1080p border crop, not on the 640 px sheet.
24. **Light beams looked like lightsabers** (emissive cone meshes: hard surface edge, fade only along the length, clipped
    colour, both walls stacked). Visible light = a VOLUME emission (no surface) with a Spherical gradient ^2 falloff on
    Object coords; small clouds need a gain of 60-120 (volume emission integrates over only a few cm). A path of light =
    >= 30 overlapping clouds (14 read as beads). For tissue optics (PPG) show diffusion in a faint (<= 7 % opaque) skin layer.
25. **Parts hung off the board edge** (SMD, transistor, resistor placed by fixed x,y on a BOWED bean PCB: its lower edge is
    2.6 cm higher mid-board than at the ends). Clamp every placed part with its footprint against the real outline
    (`_fit(x, y, half_size + clearance)` in projects/temple/temple_model.py), verify locally in plain Python before a job,
    and check pairwise overlaps after moving (one clamp pushed an SMD into the CPU's pins).
26. **Overlay text covered the 3D device** (user rule: text must never obstruct the model). The device filled the centre
    (16-84 % of the width), and labels sat on both sides of it. Fix: export the device's screen box per frame from Blender
    (`finish_plate()` -> keepout.json), place the transparent plate right of centre in the page (scale 0.78, +300 px), keep
    ALL words in one left column, and run `keepout_check.py` (every element vs every frame it is up, +24 px) before any
    render. A hidden flex child still takes space: elements shown at different times get their own absolute position.
27. **Designed background, not a flat stage** (user rule): render plates with `film_transparent` + the floor as a shadow
    catcher, WebM with alpha, and put the background (palette radial gradient, a glow that follows the device, a faint
    dot grid, seeded dust, vignette) in the Motion Graphic page behind the plate.
28. **An emitter stuck out of its window** (green LED edge 2 mm past the window end) and **LED colours clipped to white**
    (emission 8-12 under Standard view). Check every small part's footprint against its housing with clearance, and keep
    emitter peaks <= 5 so green stays green.
29. **Boolean cutter parented without an offset cut nothing** (foam-ring hole, antenna loop): `cutter.parent = target` keeps
    the cutter's location as LOCAL, so its z must be relative to the target's origin (z0 of target subtracted), or set
    `matrix_parent_inverse`. Hidden inside a closed shell it went unnoticed until the explode showed solid slabs.
30. **An assembly that must tip toward the camera mid-explode**: parent every top-level part to one pivot empty with
    `matrix_parent_inverse = pivot.matrix_world.inverted()` BEFORE `explode()` (its offsets are converted through the
    parent, so they stay along the stack axis), parts that ride a layer (chips on the PCB, emitters on the pad) parented to
    that layer the same way, then key the pivot's rotation. A hollow shell = loft open at the bottom + Solidify inward.
31. **User artwork on a bowed part**: planar top-down UVs with the bow undone (`y - bend*(1-(x/a)^2)`) so an oval artwork
    follows the bean; pack the image into the .blend (`img.pack()`) so later `render` jobs on the saved scene still have it;
    gold in the artwork -> ColorRamp -> Metallic + Bump, so traces shine and stand proud.
32. **Detail is judged on a border crop, not the 640 px sheet**: `render` on the saved scene with `set` =
    resolution_percentage 100 + use_border/use_crop_to_border + border_min/max -> a 1080p crop in ~2.5 s. Every fine-detail
    defect in Temple (traces, pad grid, LED outside its window, parts off the board) was only visible this way.
33. **Render cost, measured (Temple, Cycles + OptiX, denoise)**: 1080p / 64 spp ~1.8 s/frame; 960x540 / 32 spp ~1.1 s/frame
    (739 frames ~14 min). One Blender job per person runs at a time: queue order matters; `cancel_job` frees the slot at once
    (cancel a superseded render before launching its replacement). The user wants a LOW-RES video pass before any full final.
34. **The reference IS the spec**: the user corrected the device four times with pictures (shape, layer stack, PCB artwork,
    pad texture). Keep ONE shared model file for every chapter (`temple_model.py`), rebuild every chapter that uses it after a
    change, and never claim a feature in labels that the fact sheet does not support (pasted notes about voice AI were left out).
35. **Lit review sheets are the cheapest look**: `image/montage` of the review PNGs (one call, < 1 s) -> `sign_output` -> curl ->
    Read. Typical pass = upload URL + job + montage + sign = 4 calls; a crop adds 2. Temple ch1+ch4 to approval: ~170 calls.

36. **Motion Director review of a narrated 3D chapter** (`get_skill enginex-motion-director`, camera.md): one lead move at
    a time and the CAMERA STILL while words are read (<= 2-3 % over a hold). Temple ch4 broke both (crane + dolly + tip
    together; a 32 % push under words in ch1). Fix pattern: object moves (explode, tip, re-assembly) are the lead while the
    camera holds; the camera gets 1-2 composed moves (rise+pull back as one) placed in the gaps between on-screen words; a
    slow orbit drift <= ~15 deg per chapter. If a held camera then clips the subject (the upright exploded stack crossed the
    frame top), change the OBJECT's pose (keep it tipped, re-assemble tipped) rather than add a camera move under words.

## 7. Worked project to copy from
`projects/temple/`: `temple_model.py` (multi-layer device from references: lofted shell, UV artwork, chips with pins,
`_fit` clamping, volume light), `ch1_job.py` (360 hero turntable), `ch4_job.py` (explode + crane + tip + emitter pulses +
light in skin), `finish_plate.py` (transparent plate + keepout.json), `bg_layer.html` + `build_pages.py` (designed
background, plate placement), `overlay_ch1/ch4.html` (word-timed overlays), `keepout_check.py` (text never over the model).
