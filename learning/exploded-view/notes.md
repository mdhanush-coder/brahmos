# Notes - Exploded view: "Import a CAD model and create an Exploded View animation in Blender 3.0"

Source: https://www.youtube.com/watch?v=KFb4r8UVO0A (Derek Elliott, 25:31). Blender **3.0.0 Beta** (status bar). Key section from **7:50** on (inspection, origins, keyframes, shape keys, Graph Editor). Frame-NNNN is at about (NNNN-1)×4 s.

## Settings read on screen
- Output: **1920 × 1080**, **30 fps**, Frame Start 1, **End 60**, later **End 120**. PNG RGBA 8-bit, compression 15 % (frame-0286).
- Viewport shading: **Solid > Color: Random** (pastel per object) plus **Cavity ✔**, to tell parts apart (4:28).

## Workflow
1. **Import (1:35-3:19).** **File > Import > Wavefront (.obj)**. OBJ is the most reliable CAD-to-Blender format. STEP needs the **STEPper** add-on. STL, DAE and FBX also work.
   - CAD imports come in too big: **S 0.1** (sometimes another 0.1), then **Ctrl+A > Scale** to apply. Units are in Scene Properties.
2. **Split into parts (3:19-7:01).** **Tab**, **A**, **P > By Loose Parts**, **Tab** out. If the OBJ has materials you can also select by material.
   - Caption: "if your model gets WAY too split up (fillets, lofts etc all separate) then remove doubles before separation". Warning: Merge by Distance can fuse bearings that touch their housings, so prefer separating first and merging per part.
3. **Origins (5:32).** Right-click > **Set Origin > Origin to Geometry**. Caption: "origin to geometry is usually the best method for quickly placing origins logically". Then circle-select (**C**) works per part.
4. **Clean up.** Delete non-product parts (the phone and GoPro placeholders). **Ctrl+J** joins pieces that belong together (caption "CTRL+J = join parts"; logos to their mould, pins to overmoulds). **L** selects mesh islands (caption "L = select mesh islands").
5. **Inspect (7:01-12:17, key section).** Pull parts apart while holding **Ctrl** (grid snap), so they can be snapped back exactly ("like a super easy Lego kit"). Understand the stack order, which tells you the explode direction per part.
6. **Pivot origins for rotating parts (9:12-10:20).**
   - In Edit Mode, select vertices on the rotation axis (two opposing corners, or top and bottom of a circle), **Shift+S > Cursor to Selected**, Tab out, then right-click > **Set Origin > Origin to 3D Cursor**.
   - Caption: "snap origin to geometry doesn't work as well when there are very dense portions of the mesh (very common when threading is present)".
7. **Parenting (8:56-11:08).** **Ctrl+P > Object (Keep Transform)** sub-parts to the part they move with (weights to the arm, ball to the joint). It is not needed for purely linear explodes.
8. **Assembled keys (12:17-14:01).**
   - Re-assemble with Ctrl-snap. Frame **1**, **A** select all.
   - Timeline **Keying > Active Keying Set = Location**, then **I** inserts Location keys on every selected part.
   - Keys double as "save states" that snap parts back.
9. **Exploded keys (14:01-16:21).**
   - Go to frame **30** (1 s at 30 fps). Turn on **Auto Keying** (record button) with **"Only Active Keying Set"** so only Location is keyed.
   - Move each part **along its assembly axis**, by eye, no snapping: the base slides down, the cap goes up, the side cover goes out sideways, the knob goes out.
   - Think about the camera angle while placing.
10. **Return (16:21).** Circle-select all keys, **Shift+D**, and place ~**20 frames** later so it re-assembles. End = **60**, which leaves a hold.
11. **Rotation interest (17:15-19:28).**
    - Keying set to **Rotation**. Key rotation at the start and end on all parts.
    - In the middle, **F3 > Randomize Transform** with only **Randomize Rotation** ✔ (Location 0, Scale 1; Random Seed 0; small angles), then **I**.
    - Only the selected few parts, with no clipping. Pressing I over a field keys that property for the active object only.
12. **Shape-key deformation (19:28-21:23).** The clip flexes.
    - Object Data > Shape Keys **+** twice (Basis, Key 1). Edit Key 1: **Alt+Z** X-ray, select two hinge vertices, **Shift+S Cursor to Selected**, select the tab and **Ctrl+Numpad+** to grow.
    - **Proportional editing (Connected Only)**, **R** with **pivot = 3D Cursor** (`.` key).
    - Keyframe the **Value 0 to 1 to 0** (depress at f25, pop back as the clip clears, a second click later). Range 0-1.
13. **Graph Editor timing (21:23-23:50).**
    - **Normalize**. **A**, then **G X** to slide all keys, then **S X** to stretch the timing ("Dx: 22.000"). End becomes **120**, making the animation slower and leaving room for the shape-key keys.
    - Curves are Bézier with auto-clamped S-shapes (frame-0328): parts leave and return with ease-in-out, staggered on the shared timing.
14. **Dynamic effects (23:50).** Graph Editor **T** gives the interpolation menu (Dynamic Effects: Back, Bounce, Elastic). Bounce was tried ("bonkers") and he recommends staying on **Bézier**. Advice for moving the whole product: add an **Empty** and parent all top-level parts to it.

## Why
Separating, setting origins and keying "assembled" first guarantees the exact re-assembly. The Location-only keying set prevents stray rotation and scale keys. Sliding along assembly axes keeps it technically readable. Ease-in-out plus a hold gives the "breathing" exploded beat.

## bpy equivalents
`scripts/exploded_view.py`: `separate_loose(obj)`, `origins_to_geometry(objs)`, `set_origin_to_points(obj, verts)`, `explode(parts, axis_map, start, explode_len, hold, stagger, distance)` (keys assembled, then exploded, then assembled with Bézier ease and per-part stagger), `wobble_rotation()` (seeded randomize-rotation mid keys), `shape_key_click()`, `add_callouts()` (labels and leader lines that follow parts). `scripts/easing_presets.py` for handle shaping.

## Unclear
- Per-part explode distances (eyeballed).
- Randomize Transform rotation amount (the panel shows 0° at the moment captured; the value set afterwards is not visible).
- Lighting and render settings (he says rendering is model-dependent and skips it).
