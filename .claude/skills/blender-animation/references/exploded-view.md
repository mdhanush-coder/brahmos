# Exploded view of a technical product

Source: `learning/exploded-view/notes.md` (Derek Elliott, CAD -> exploded view, key section from 7:50), then proven and
extended in Phase 5 (`tests/exploded-motor/`). Scripts: `exploded_view.py`, `product_models.py`, `callouts_page.py`,
`example_exploded_motor.py` (a complete working job; start from it).

## Pipeline
`blender/script` job -> clean plate (`plate.mp4`) + `tracks.json` -> `callouts_page.py` -> `motion-graphic/render`
(plate as `<video>` in `media`) -> `sign_output`. Never put labels in the 3D scene.

## Getting parts (video steps, with bpy)
1. Import: OBJ is the most reliable from CAD (STEP needs the STEPper add-on). CAD arrives too large: scale 0.1, apply.
2. Split: Edit Mode `P > By Loose Parts` -> `separate_loose(obj)`. If a model is split too far (fillets, lofts), Merge by
   Distance first - but not on assemblies where bearings touch housings (it welds them); then separate.
3. Origins: `Set Origin > Origin to Geometry` -> `origins_to_geometry(parts, 'BOUNDS')` (BOUNDS beats MEDIAN on
   threaded/dense parts). Rotating parts: put the origin on the axis (`set_origin_to_point`).
4. Clean: delete non-product bits, `Ctrl+J` join pieces that move together, `L` selects islands, parent sub-parts
   (Ctrl+P keep transform) only if they must rotate with something.
5. **Library assets**: `gather_asset(id, size, min_parts, max_parts)` collects unparented meshes, splits by loose parts
   if < min_parts, merges the smallest into one 'hardware' part if > max_parts. Few library assemblies have real parts
   (the SimReady gearbox is body + 2 gears). For a convincing exploded view build parts procedurally:
   `product_models.drone_motor()` returns 11 real parts (2207 outrunner: base mount, 685ZZ bearings, 12-tooth stator,
   copper windings, bell with cooling slots, 14 N52 magnets, 5 mm shaft, circlip, M5 hex nut, 4 M3 screws).

## Keying (video steps -> `explode()`)
- Key ASSEMBLED first (Active Keying Set = **Location**, `I`). Keys double as save states.
- EXPLODED: move each part along its assembly axis (**axial moves only**, never diagonals), by eye, no snapping. Auto
  Key with "Only Active Keying Set" keeps scale/rotation clean.
- Return: duplicate the keys ~20-30 frames later. Hold.
- Rotation interest: keying set Rotation, key start/end, `F3 > Randomize Transform` (rotation only) in the middle on a
  FEW parts, without clipping -> `wobble_rotation(parts, frame, degrees, seed)`.
- Shape-key detail (flexing clip): `+` twice (Basis, Key 1), edit Key 1 with proportional editing (connected only), `R`
  about the 3D cursor; key Value 0 -> 1 -> 0 -> `shape_key_click`.
- Graph Editor: Normalize, `A`, `G X` slide, `S X` stretch (60 -> 120 frames in the video). Stay on Bezier.
- Moving the whole product: parent all parts to one Empty.

## Timing recipe that passed review (10 s, 30 fps, 11 parts)
`stag=6` frames between parts, `elen=36` (1.2 s move), `rlen=30`, `start_hold=18`, hold = 300-18-(18+2*(n-1)*6+36+30)
= 78 frames. Order: top of the stack leaves first, returns last. Distances are an explicit plan per part
(`distances={name: metres}`), outer parts furthest, so parts never pass through each other.
`explode(..., preset='smooth')`, `order=parts`, `distances=dist`.

## Composition (the part that failed first)
- Long axis horizontal for 16:9: `rotate_assembly(parts, 'Y', 90)`. A vertical stack uses ~10 % of the frame.
- Camera: pivot at the exploded centre, `frame_width_distance(width, 50, fill=0.60)`, height 0.26*d, 50 mm, f/11,
  orbit -22 -> +22 deg over the shot (`ease_in_out`), `dolly` factor 0.3 -> 1.0 -> 0.3, pivot sliding assembled <-> exploded
  centre. First and last frames are hero close-ups of the assembled motor.
- Floor: dark cyclorama (size 150, roughness 0.8, colour ~0.02), parts float 0.45 m above it, three-point lights at
  `key_power=320`, HDRI 0.5 for reflections only (`background_strength=1`).
- Materials: anodised parts from the library ORM set via `library_material`, metals via `metal()`; ALWAYS
  `assign_material`.

## Callouts via Motion Graphic
- `tracks.json`: for every part, per frame `[x, y(top), visible]` of its bounds centre via `world_to_camera_view`, plus
  `out`/`back` frames and a `row` (x-rank % 4: neighbours never share a row).
- `callouts_page.py tracks.json overlay.html --title ... --subtitle ...` builds the page: pills with index chip, label,
  spec line; leader line drawn from the part to the pill with a pulsing dot; counter "NN / N" with progress bar; title.
  It simulates the layout on every frame and exits non-zero on any overlap.
- Render: `motion-graphic/render` with `html` = the file's text, `media` = [plate key], `format: mp4`, `quality: high`.
  The plate is available as `assets/<basename>`; pass `--plate assets/plate.mp4`.
- Only label what you can state truthfully (dimensions from the model: 5 mm shaft, 685ZZ 5x11x5, 12N, 14 magnets...).

## Checklist before the long render
`check_framing` ok at 1/70/150/240/300 - `fill_fraction` >= 0.5 of frame width at peak - `audit_fcurves` ok - pixel
colour assertions pass - 6 review frames looked at - label overlap report empty.
