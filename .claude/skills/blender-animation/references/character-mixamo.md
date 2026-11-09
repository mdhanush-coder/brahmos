# Character animation with Mixamo FBX

Mixamo needs the user's Adobe login: **never download from it.** The user places files in `./assets/mixamo/`
(see `assets/mixamo/README.md` for the folder convention). Script: `scripts/mixamo_import.py`.
**Status: written from the standard workflow, NOT yet run in an EngineX job - test on the first real FBX and log
the result in SKILL.md's Failure log.**

## When a clip is missing, tell the user exactly this
Say: which animation to search (Mixamo > Animations > search box), whether it needs "In Place", and the export panel:
- **Format: FBX Binary (.fbx)**
- **Skin: With Skin** for the FIRST file of a character (the mesh + armature); **Without Skin** for every later clip
  of the same character (smaller, armature only).
- **Frames per second: 30**
- **Keyframe Reduction: none** (off)
- Pose: T-pose (character upload), "In Place" ticked for loops (walk, run, idle) unless the clip travels (jump, roll).
Filename convention requested: `<character>__<action>__<inplace|root>.fbx`, e.g. `knight__walk__inplace.fbx`.
Typical searches: Idle ("Breathing Idle"), Walk ("Walking"), Run ("Running"), Jump ("Jump"), Turn ("Left Turn 90"),
Wave ("Waving"), Sit ("Sitting Idle"), Fall ("Falling Idle"), Death ("Standing React Death Forward"), Dance ("Hip Hop
Dancing"), Punch ("Punching Bag"), Kick ("Mma Kick").

## Import settings (File > Import > FBX, or `import_mixamo`)
Apply Transform off (keep rest pose); Armature: **Automatic Bone Orientation off**, **Ignore Leaf Bones on**,
Force Connect Children off; Animation on; Custom Normals on. Primary/Secondary axis default (Y forward / Z up works
with Blender's import). Naming: bones are `mixamorig:Hips` / `mixamorig1:Hips`...; run `strip_prefix(arm)` so clips
from different downloads share bone names.

## Armature scale fix
Mixamo FBX come in at 100x or 0.01 scale (cm). `fix_scale(arm, objs)`: select the armature + meshes, apply Scale
(Ctrl+A), then multiply the **location** F-curves of the root/hips by the same factor so the animation matches.
Verify: character ~1.7-1.9 m tall, feet on Z=0.

## Retargeting onto our rigs
1. `strip_prefix` on the source; target bones named like Mixamo (or provide `bone_map={dst: src}`).
2. `retarget(src_arm, dst_arm, bone_map)` adds Copy Rotation per bone (hips also Copy Location).
3. `retarget_bake(dst_arm, start, end, action_name)` bakes (Visual Keying, Clear Constraints) into an action.
4. Check foot sliding and arm-through-body in review frames; fix by lowering hips copy influence or editing the action.
Library rigs: `python find_asset.py --type rig` (33 entries, mostly vehicles/props; characters with skeletons are rare).

## Combining clips in the NLA
`push_to_nla(arm, action, start)` puts each action on a strip; `sequence_clips(arm, [idle, walk, run], overlap=8)`
alternates tracks A/B with overlapping strips and `blend_in/blend_out = 8` frames for cross-fades. Set
`extrapolation='HOLD'` on the last strip, `repeat` on loops. Blend types: REPLACE for the base, ADD for layered
gestures. Transition length 6-12 frames at 30 fps (walk -> run 8-10; idle -> walk 12).

## Root motion
- **In Place clips** + move the character with an object path / location keys (easing from `smooth-animation.md`).
  Match speed to stride (walk ~1.4 m/s, run ~3-4 m/s) to avoid foot sliding.
- **Root-motion clips**: keep Hips X/Y translation, make sure the character object stays at the origin; if you need the
  clip in place use `in_place(action, 'Hips')` (locks X/Y to the first key, keeps the vertical bob).
- Looping: first and last keys must match; add a Cycles F-curve modifier or NLA repeat.

## Blending between actions (checklist)
Overlap strips by the blend length - match foot phase (left foot forward to left foot forward) - blend over the
passing pose - never blend two root-motion clips without in-placing one - review frames at the join.
