# BrahMos — creative plan (all 9 EngineX skills)

## A. The idea (Motion Director: "idea first")
**The radar screen is the frame of the whole video.** We open on a warship's radar at night: a blip at the edge, 30 s on
the clock. Every chapter starts with a radar-sweep wipe and a range ring that tells you where the story is
(290 km, 15 km up, 30 km, 10 m...), the blip creeping closer each time. The last chapter lands back on the same radar with
the clock at 0:00, closing the hook's loop ("what would you do in that half minute?").
Test: it can't be swapped onto another video. The HUD is the BrahMos story itself: speed vs warning time.

Candidates rejected: "follow one breath of air through the engine" (kept as the ramjet chapter's device, not the whole
video); "India vs the world speed race" (it's a map/graph idea, used once in ch6).

## B. Style (Motion Director styles.md)
- **Main: science-space**: precise diagrams, labels with leader lines drawing to the part, zooms through scales, calm
  authority (pace 1.3, `camera` / `enter-soft` eases, no cartoon bounce).
- **Accent: hud**, only in the radar/guidance moments (ch1, ch5, ch9): mono readouts typing on, rotating rings, lock
  brackets. Never moving while being read.
- **Payoff moments in trailer grammar**: launch (ch3) and the 9x slam (ch6) get a held beat, a hit, then slow motion.
- Rules kept: one lead move at a time; camera still while words are read; one entrance per role; Hindi animated by word
  or line, never letter; ≤ 3 flashes a second (the launch flash and muzzle smoke count).

## C. What each EngineX skill does in this video
| Skill | Its job here | Where it shows |
|---|---|---|
| **FreeCAD** | Build the airframe as a *measured, parametric* part: ogive nose + intake cone, 8.4 m x 0.67 m body, 4 mid wings + 4 tail fins, the booster section, the sealed canister. Export GLB, `inspect` the sizes. Every chapter uses this ONE model (no shape drift between shots). | Every 3D shot; the "size next to a bus" beat is true to scale |
| **Blender** | All 3D: night ocean + warship silhouette, low chase cam over waves, canister launch with smoke, slow-mo booster separation, x-ray glass skin (Animagraffs), ramjet cutaway with volumetric air coloured cold→hot (Real Engineering), seeker radar rings, Su-30 release, the final nose-to-nozzle fly-through. Transparent plates + `finish_plate` keep-out. | ch1-5, ch7, ch9 |
| **Motion Director** | Plans every move against the voice's word timings; `motion-check` on each chapter page before any render; one lead move per scene. | Whole video |
| **Color Palette** | One palette, dark lead (night). The accent marks the ONE thing per frame (the blip, the flame, the 9x). Data colours that label real physics (cyan cold air, amber fuel, green radar) are the one documented exception, as on Temple. | Every frame |
| **Typography** | Display for hooks and big numbers, a Devanagari-capable text face for Hindi lines, a mono for HUD readouts. 72 / 48 / 30 px minimums. | Every overlay |
| **Design Polish** | `check_design` on every chapter page (Hindi vowel marks, contrast on the real pixels, reading time 17 chars/s), then `polish-media` on the final render. | Every chapter, final |
| **Emotive Speech** | Category 4 "Science and tech explainer", ENGLISH narration (user, 2026-11-09: English only), the approved brief. Voice to pick by ear: raghav was never tested in English; the skill lists arnav / nandini / yash as Indian-accent English that was heard right. | Voice |
| **Image Director** | 2D inserts that don't deserve a 3D build: the bike-rider wind inset (no face, from behind), cricket ball slow-vs-fast, factory floor, Philippines coast. One look for all (cinematic photo, graded into the palette). Plus the thumbnail's background. | ch4, ch6, ch8 inserts; thumbnail |
| **Poster Director** | The YouTube thumbnail (category thumb-explainer): missile breaking the frame over a giant "MACH 3", English hook "30 SECONDS TO STOP IT?", in the video's palette. Plus 3 title options. | Thumbnail |

Also: sound effects from the library (radar ping, whoosh, sonic boom, booster roar), music generated with `text-to-music`
(Temple lesson: no library music, Content ID). India map only from the official map assets (hf-assets/maps): never a
hand-drawn border.

## D. Scene by scene (one visual for every line; details in 03_script_hi.md after `||`)
| Ch | Lead visual | Pattern break | HUD frame |
|---|---|---|---|
| 1 Hook | Radar blip → low chase cam over night waves → missile rips past in slow-mo | Slow-mo pass + title stamp | 0:30 clock starts |
| 2 Name & parts | Two rivers draw and merge into the wordmark → missile beside a bus (true scale) → glass skin, 5 parts slide out | X-ray reveal | Range ring "1998 → 2001" |
| 3 Launch | Truck raises 3 canisters → cap blows, fire column → pitch-over → booster separates | Speed ramp to slow motion at separation | Ring "MACH 1" |
| 4 Ramjet | Split screen jet engine vs empty pipe → bike wind inset → shock lines on the intake cone, air cyan→magenta → fuel, flame, thrust | Graph that draws itself (thrust vs speed) | Ring "MACH 2.8" |
| 5 Guidance | Flight profile 15 km → INS drift corrected by satellite pings → drop to 10 m → radar horizon diagram → seeker lock → S-weave | Curved-Earth diagram | Blip appears at 30 km |
| 6 Speed | Push into warhead, fade to navy → ½mv² writes itself → bars 1→4→9 → cricket ball → race bars 2 min vs 30 s | Number slam "9x" | Clock 0:10 |
| 7 Everywhere | Four panels land/sea/air/underwater → Su-30 release → range rings grow 290 → 500 → 800 | Map zoom | Rings widen |
| 8 Made in India | Night launch silhouette + headline card → factory → 80% bar fills → globe: Philippines, Vietnam, Indonesia | Globe spin | — |
| 9 Close | ONE continuous fly-through nose → nozzle, air → shock → flame → recap colours → back to the radar | The single long shot | Clock 0:00, freeze |

## E. Pacing rules (from 01b_style_mix.md)
A visual change every 3-5 s, never more than 6 s of still frame; a cut every 8-12 s; camera always drifting, same screen
direction (missile flies left → right in every shot); each chapter ends on an open question or a beat.

## F. Assumptions (say if any is wrong)
- 16:9, 1920x1080, 30 fps; ENGLISH ONLY: narration (03_script.md) and every on-screen word. Hindi draft kept as backup only.
- Fonts: Unbounded (display), Rajdhani (text and labels), JetBrains Mono (HUD). Palette night-blaze/dark.
- Cutaways of the inside are labelled "illustrative" (no public cutaway exists); [EST] numbers get a small tag.
- No target maps, no casualties, no named bases; Operation Sindoor appears only as the PM's public confirmation.
- Call budget: ~74 planned by plan_video.py + FreeCAD (~6) + Image Director (~8) + thumbnail (~6) + polish passes; target ≤ 250.
