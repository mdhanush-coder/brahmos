# Notes - Smooth animation (B): "How to Make Smooth Camera Animations in Blender"

Source: https://www.youtube.com/watch?v=dFK3C83k4Wo (Blender To Browser, 11:53). Blender **5.0.0**. Evidence: `transcript.md`, `contact-sheets/`, `frames/` (frame-NNNN is at about (NNNN-1)×3 s).

## Scene settings read on screen
- Render engine **Cycles**, Device **GPU Compute** (0:27).
- Output: **Resolution 1080 × 1920 px (vertical 9:16), 100 %**, **Frame Rate 25 fps**, **Frame Start 1, End 250** (frame-0062/0065).
- Camera: Type Perspective, Lens Unit Millimetres, **Focal Length 90 mm** (typed over the default 50 mm, frame-0021), Shift 0/0, Clip 0.1 m - 1000 m.
- Office-chair model from BlenderKit: Scale 0.352 uniform, Z ≈ 0.528 m.

## Workflow
1. **Import the model (0:09).** BlenderKit (any model works).
2. **Infinite backdrop / cyclorama (0:29).** **Shift+A > Mesh > Plane**. In Edit Mode, select the back edge and **E** extrude up (the Z axis), then **Ctrl+B** bevel the corner edge (header showed many bevel segments). Scale the plane large so camera moves never leave it.
3. **Split the window (0:48)** so the Timeline is visible. Hold **Shift** for precise moves.
4. **Camera (0:50).** Add a camera, **Numpad 1** front view, place it in front of the chair with the chair centred. **Focal Length 90 mm** for the whole animation.
5. **Organise (1:08).** Rename the camera `shot1`, press **M > New Collection** "shot1".
6. **Pivot empty (1:30).** **Shift+A > Empty > Plain Axes** named "shot1 movement", in collection shot1. **Parent the camera to the empty** (Ctrl+P > Object). Rotating the empty orbits the camera in a circle. Do not animate the camera directly.
7. **Shot 1 entry (2:00).** At frame **~40-50**, hover Location and press **I** (or **K**) to key the end position. At frame **1**, pull the camera slightly back and key again. The result is a slow push-in reveal.
8. **Shot 1 exit (2:45).** Start at frame **40** with a rotation key. Go to frame **55** (15 frames later), set the empty's **Z rotation +30°** and key it. Later revised to **20 frames** (key at **60**) and **40°**.
9. **Graph Editor pass (3:03).**
   - **Lock X and Y Euler Rotation channels** (padlock in the channel list) so only Z is edited.
   - **Normalize** on, then the **Home** key to frame all.
   - Active Keyframe: **Interpolation Bézier**, **Left Handle Type Free**, Key Frame 56, Value 30°. F-curve "Handle Smoothing: Continuous Acceleration" (frame-0065).
   - Select both handles and **S X**, scaling along X ("Scale 0.7532 along X" visible). Play back and adjust by eye. Too much scale makes the middle too fast.
10. **The rules card.** Kept as an internal text block (frame-0159/0218):
    ```
    1. shot change rotation      = 40d
    2. shot change duration      = 20frames
    3. shot change start         = after 40 frames
    4. SHOT DURATION             = 50 frames
    5. after shot change default rotation = 10d
    ```
11. **Shot 2 (3:54).** **Shift+D** duplicate the empty and camera, move the empty to the next focus area, rename to shot2, **M** to a new collection "shot2", and delete the copied keys.
    - **Camera cut at max velocity**, i.e. the middle of the transition (frame ~**50**): select the shot2 camera, **Ctrl+B** (Bind Camera to Markers). Then at frame 1 bind the shot1 camera.
    - **Entry = mirror of exit**: rotation **-40°** at frame 40, back to **0°** at frame **60** (20 frames).
    - Copy the easing from shot 1 with the free **Relative Ease** add-on (sidebar tab "Relative Ease"): copy and paste the easing.
    - **Keep moving after the transition**: at frame **90** key **+10°**, so the camera never stops dead.
    - **Exit**: 20 frames later key **+50°** (10 already + 40).
12. **Remove the bump (7:54).** After pasting the easing there is a visible velocity "bump" just after the transition. Select the middle key's handles and **R** rotate them ("Rotation: 4.17") until the curve's slope flows continuously into the next segment (frame-0159).
13. **Shots 3-5 (8:25-11:00).** Same recipe: duplicate, rename, collection, new camera bound **50 frames after the last cut**, entry -40°, copy easing, +10° drift, exit +40°, smooth.
    - For the back view, **New Scene > Full Copy** (Scene selector "+"), then rotate the model in the copy. The cameras and empties are reused, so only the empties are moved.
14. **Lights (10:45).** "Nothing fancy". An **Area light** on the right side with intensity increased, then **Shift+D** duplicated to the left side. The left light uses **Light Linking to the model only**, so it adds no extra shadows on the backdrop. Lights are copy-pasted into the other scenes.

## Why
The empty pivot gives clean arcs. Fixed numbers (40°, 20 f, 50 f per shot, 10° drift) keep every shot's rhythm identical. Cutting at peak velocity hides the cut. Continuous slope across keys (no bump) is what reads as "smooth".

## bpy equivalents
`scripts/camera_orbit.py` (`make_orbit_rig`, `shot_sequence` implements the rules card + marker binding + bump removal), `scripts/easing_presets.py` (`copy_easing`, `remove_bump`), `scripts/studio_lighting.py` (`two_area_lights` with light linking).

## Unclear
- The exact entry-shot location offset (pulled back "slightly", value not read).
- Area-light power and size values (only "increase the intensity").
- Bevel segment count on the backdrop corner (header text too small).
- Cycles sample count and denoiser are not shown.
