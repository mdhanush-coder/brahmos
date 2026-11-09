# Notes - Smooth animation (A): "The SECRET to Smooth Blender Animations - Easing & Graph Editor"

Source: https://youtu.be/4Mf2hgb1tP0 (ArtSyndrom3, 3:42). Blender **5.1.0** (title bar). Evidence: `transcript.md`, `contact-sheets/sheet-000..003.jpg`, `frames/frame-*.jpg` (frame-NNNN is at about (NNNN-1) s).

## Scene shown on screen
- Pocket-watch model on a vertical 9:16 card with a blue gradient backdrop. Outliner: `Area`, `Area.001` (two area lights), `Camera`, `Plane`, `pocket_watch`.
- Output properties: **Frame Rate 30 fps**, **Frame Start 1 / End 84 / Step 1**, Media Type Video, Container MPEG-4, Video Codec H.264, Color Depth 8 (frame-0042).
- Playback in the timeline uses "TAV" sync.

## Workflow
1. **The baseline (0:17).** The watch rises (Z location) and rotates between two keyframes. With default Bézier/auto-clamped handles the motion "looks like trash": it starts and stops abruptly, with uniform speed.
2. **Open the Graph Editor (0:24-0:28).** In the Dope Sheet press **Ctrl+Tab** to toggle to the Graph Editor (on-screen caption "CTRL + TAB - SWITCH VIEWS"). The editor-type menu (Shift+F6/F12 list) is also shown.
   - Vocabulary: the first key is called **In**, the last key **Out**.
3. **Select the keys cleanly (0:41-0:47).** Select the keyframe in the Dope Sheet first, then Ctrl+Tab back. Everything selected there stays selected in the Graph Editor. Enable **Normalize** (header toggle) so all channels sit in the -1..1 range (frame-0100, frame-0154).
4. **The Big 3 of easing (0:53-1:24), made by scaling handles with `S` then `X`:**
   - **Ease Out (smooth ending):** select the *last* key, press **S X** to stretch its handles horizontally. The header reads **"Scale: 2.0453 along X"** (frame-0055). The curve now flattens long into the end value. Caption "EASE OUT".
   - **Ease In-Out:** also select the *first* key and **S X** it. The result is described as a "quick whip". Caption "EASE IN-OUT".
   - **Ease In (slow start, quick end):** Ctrl+Z, then scale only the first key's handles up. Caption "EASE IN".
5. **Duration changes the feel (1:33-1:57).** **G** (caption "G KEY - MOVEMENT") moves a keyframe in time. Keys further apart plus big handles give slow, smooth motion. The same handles with keys close together give smooth but fast motion.
6. **Asymmetric "transition" easing (1:51-2:00).** Scale the first key's handle to almost full length (≈ the whole interval) and the last key's handle to almost 0. The result is a very slow start and a snap at the end (frame-0100: exponential-looking curve reaching 1.0).
7. **Camera-switch transition (2:16-2:53).** There are two cameras, `Camera.001` and `Camera.002`, in a second scene `Scene.001` (left-to-right move).
   - Camera 1: first key handle ≈ full (slow start, accelerating), last key handle ≈ 0 (leaves at full speed).
   - Camera 2: first key handle ≈ 0 (arrives at full speed), last key handle ≈ full (long deceleration).
   - The cut sits at the joint, where both curves are at maximum velocity (frame-0154: the two Normalized curves meet at the camera-marker line, values 1.0 and 0.0). The fast motion hides the cut, which is the "whip" transition.
   - Camera binding happens through timeline markers ("Camera.002" marker at the cut).
8. **EaseIt add-on (2:56-3:32).** From Blender Extensions: "EaseIt - Quickly apply easing presets to animation keyframes", by AndyCuccaro, v1.0.1, Blender 4.2 LTS and newer, GPL-3.0. Use: Graph Editor, **N** sidebar, **EaseIt** tab, **A** to select all keys, click a preset. Status bar: "Applied Super Smooth easing to 9 curve(s), 18 keyframes processed" (frame-0200).
   - Preset list (frame-0200). Symmetric: Default, Just Fine, Cubic, Exponential, Extreme, Linear, Max. Asymmetric: Smooth, Easy, Super Smooth, Smooth Out, Easy Out, Super Smooth Out. One-sided: Ease In Only, Ease Out Only. Advanced: Explosive, Springy, Overshoot 1/2, Anticipation 1/2/3, Easy Going, Antic + Over, Agitated, Very Late Stop, Overshoot x3, Spring Back, Bouncy, Weird.
   - The demo uses **Super Smooth**, then **Overshoot 2** ("27 keyframes created") and **Spring Back** ("63 keyframes created"). Overshoot and spring presets **add keyframes**.

## Why it works
Easing equals velocity control. A long handle means the value stays near the key for longer (slow), and a short handle means it leaves fast. Smoothness is the handle length relative to the gap between keys.

## bpy equivalents
`.claude/skills/blender-animation/scripts/easing_presets.py`: `ease(fcurve, preset)` sets handle types to FREE and handle lengths as a fraction of the key gap (In/Out/InOut/transition presets), `whip_transition(cam_a, cam_b, cut_frame)`, and `set_interp(obj, 'BEZIER', easing=...)`.

## Unclear
- The exact frame numbers of the watch's two keys (they look like ~frame 1-16 and ~47-50; the timeline is too small to read).
- The exact handle lengths used for "almost full / almost zero". They were dragged by eye, and no numbers were shown.
- Light settings for `Area` / `Area.001` are not shown.
