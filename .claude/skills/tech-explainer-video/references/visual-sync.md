# Visual sync: shot types, dwell, and how each is built

All values measured on Branch Education (`learning/branch-clocks/notes.md`). Frames are at 30 fps.

## Timing contract (applied by beat_sheet.py --snap)
1. The camera **starts moving 0.8 s before** and is **settled 0.6 s before** the part's name is spoken.
2. If a sentence start (gap > 0.5 s) is within 1.5 s, the settle snaps to it (Branch also cuts on sentences).
3. **Dwell**: no move off a part before the end of the sentence that explains it + 0.4 s, and never < 2.5 s.
4. Numbers and chips appear ON the spoken word (no lead), hold >= 2 s, leave with the beat.
5. A beat with nothing new for > 8 s gets a slow drift (orbit 6 deg / dolly 5 %) so the frame never freezes.

## Shot types (shot= in the script)
| shot | Look | Built with |
|---|---|---|
| room | photoreal daylight interior, blind-stripe shadows, 85-135 mm, f/2-2.8, slow push | library scene/props (`find_asset.py --type scene`), `studio_lighting.hdri_world`, `camera_orbit.push_in` |
| explode | housing opens, parts separate in assembly order | `exploded_view.explode`, `rotate_assembly`, timings from `exploded-view.md` |
| focus | dark void; camera flies to each named part; others ghost; named part glows orange | `focus_rig.camera_to_beats`, `ghost_material`, `glow_rig`, `glow_beats` |
| macro | very close detail, 135-200 mm, rack focus | `make_camera(focal=150, fstop=4)`, focus object keyed per beat |
| dive | push into a part, fade to black, the physics at a new scale (atoms, field lines, charges) | Blender: instanced spheres + emissive curves; or a Motion Graphic canvas page for 2D physics |
| schematic | 2D HUD diagram over a blurred still of the part, block by block on the word | Motion Graphic page (SVG + GSAP), white 2 px lines, orange accents, Title Case labels |
| numbers | big kinetic number with units over the part | Motion Graphic chip from `number=` |
| return | back to the real device doing the thing, then the room | same rig as room/focus |

## Colour and label code (whole video, never change)
Orange = active / signal / current - red and blue = poles, +/- charge - ghost = blue-grey 12 % - chips: bold italic CAPS
yellow-orange, lower right - numbers: huge, units small - labels: Title Case - disclaimers: small italic top-left when
motion or scale is exaggerated - brand bug bottom-right.

## Sync review (step 10)
For each chapter: sample one frame at every beat's settle frame (from beats.json) on one sprite/montage and confirm the
named part is centred, sharp and glowing; the chip/number shows on its word; no beat moves before its dwell ends.
Any miss -> fix that chapter's beats or rig and re-render only that chapter.
