# 01b - Style mix for "How BrahMos works" (~6 min, Hindi + English)

Goal: Branch Education's base (clean 3D, zoom to each part as it is named, synced callouts), plus techniques from 3 other channels so the video never sits still. **Every narration line gets its own visual.** We borrow techniques only: no music, characters, logos, fonts or recognizable looks are copied.

> **How sure are we?** Published interviews only say a little about how these channels work. They cover process (research, script first, voice then animation, music and SFX last) but give almost no shot-level detail. Items marked **[src]** come from a source listed at the bottom. Items marked **[obs]** are common, widely recognized conventions of the channel that a timed rewatch has not checked. Treat **[obs]** numbers, such as cut rates, as targets, not measurements.

---

## 1. Shortlist and why

| Channel | Fit for a missile explainer | Verdict |
|---|---|---|
| **Real Engineering** | Aerospace/defence topics, physics-first, airflow and pressure graphics, maps, chart overlays. Its creator holds an aeronautical engineering master's [src]. | **PICK** (physics + "why this design" layer) |
| **Mark Rober** | Hook formula, "but" structure, slow-mo reveals, music drops, comparisons with everyday things [src] | **PICK** (story, retention, punch) |
| **Animagraffs** | Clean 3D cutaways in the cross-section-book tradition (Stephen Biesty) [src], colour-coded systems, ghosted shells, minimal labels | **PICK** (cutaway clarity, x-ray language) |
| Jared Owen | Blender "what's inside" tours, slow orbit + peel [src]. Its look is too close to Branch's | Skip (already covered by Branch base) |
| Kurzgesagt | Visual metaphors chosen in a sketch phase, vibrant flat palette, custom score + SFX layer [src] | Borrow 1 idea only: scale comparisons. The flat 2D look clashes with our 3D |
| Smarter Every Day | High-speed slow-mo is the core [src]. The host is a former missile flight-test engineer [src]. Live-action only | Slow-mo idea folded into the Rober borrow |
| Wendover / Dhruv Rathee / Mohak Mangal | Map-driven geopolitics, quick B-roll, on-screen text. Rathee is described as "kinetic editing" with map animations and glitch transitions [src, weak] | Borrow the **map grammar** only (range rings from India) |
| Defence Squad / Indian defence explainers | Mostly talk or news formats. No strong 3D grammar found [src] | Skip. Use them only to check which facts Indian viewers expect |
| Ridddle | Stock-footage storytelling, dramatic VO | Skip |

**Final 3: Real Engineering + Mark Rober + Animagraffs**, on top of Branch Education. A small map borrow comes from Wendover and Rathee, and one scale-comparison borrow comes from Kurzgesagt.

---

## 2. Technique sheets

### 2a. Real Engineering: "the physics behind the design"
- **Shot types [obs]:** clean 3D hero model on a dark gradient. Sections cut the model in half lengthwise and show flow inside. A 2D chart or equation card sits beside the model, never on it. Real-world reference footage (launch clips) leads into the 3D.
- **Camera [obs]:** slow, steady dolly or truck along the airframe as the narration moves from nose to tail. Few whip moves. The camera holds still while a graph builds.
- **Physics display [obs]:** streamlines or particles through intakes, colour-ramped by pressure, temperature or speed (blue to red). Shock waves are drawn as thin bright lines. A line graph (altitude or speed over time) draws itself in sync with the narration.
- **Text [obs]:** sparse labels in thin sans-serif, one number at a time, units always shown.
- **Pacing [obs]:** visual change roughly every 4-8 s, slower than Rober. The "why" is explained before the "what".
- **Retention [obs]:** sets up a design constraint ("to go Mach 3 you can't use a turbine...") then reveals the engineering answer. History aside as a short cutaway.
- **Take for BrahMos:** the ramjet section, the shock-cone intake, pressure and temperature colour ramps, the trajectory graph, and the "why not a turbojet?" constraint framing.

### 2b. Mark Rober: "story, punch and retention"
- **Hook [src]:** open with a question the viewer wants answered, answer it early to earn trust, then immediately raise a bigger question. The first minute works as a pitch for the rest of the video.
- **Structure [src]:** "but" chaining, where each solution has a flaw that motivates the next. Upcoming reveals are teased to hold the middle. Ranked or countdown lists hide the last item.
- **Pacing [src]:** cuts land on a steady beat, then a slow-mo moment deliberately breaks the rhythm for the reveal. Each section is timed to a musical phrase.
- **Camera [src]:** speed-ramped orbit into slow-mo on a reveal. Successive shots keep moving in the same direction, which pulls the viewer forward. A slow push-in builds tension, then a wide shot pays it off.
- **Music/SFX [src]:** music drops out just before the key line. Layers are added as a point builds. SFX punctuate every reveal and every pacing change.
- **Comparisons [obs]:** everyday objects as yardsticks (football fields, cars, bullets), shown side by side to scale.
- **Take for BrahMos:** hook formula, "but" chain between systems, speed-ramp slow-mo on booster separation and impact, music-drop before the big numbers, race comparisons.

### 2c. Animagraffs: "x-ray clarity"
- **Influence [src]:** the founder's style comes from cross-section books (Stephen Biesty), and he aims for content "elevated to an art form". Jet-engine videos walk through variants step by step [src].
- **Shot types [obs]:** isometric 3/4 hero angle. The outer skin goes semi-transparent (ghosted) or a quarter-section is cut away, and inner parts keep solid, flat, saturated colours.
- **Colour code [obs]:** one colour per system, used the same way all the way through (fuel = one hue, air = another, structure = neutral grey).
- **Labels [obs]:** a thin leader line runs to a small label with no box or a light pill. The label appears only when its part is named.
- **Motion [obs]:** parts slide out along their own axis (exploded view), then slide back. Moving fluids are animated with simple dashes or particles, not realistic sim.
- **Take for BrahMos:** ghost-skin x-ray, the system colour code, exploded-view choreography, and minimal labels.

### 2d. Small borrows
- **Maps (Wendover / Rathee) [obs]:** flat dark map, India highlighted, range rings that grow out with a counter, a dotted arc from launch to target, with a camera push to the region. Rathee is described as fast "kinetic" editing with map animations [src, weak].
- **Scale (Kurzgesagt) [src]:** visual metaphors are picked in a sketch phase before animation. Use the same step: write one visual metaphor per line in the shot list before any Blender work.

---

## 3. Mixed style guide for BrahMos

### 3.1 What we take from whom
| Layer | Source | Rule |
|---|---|---|
| Base 3D, zoom-to-part, synced callouts | Branch | unchanged house pipeline (`tech-explainer-video` skill) |
| Story spine | Rober | hook = question, then early answer, then bigger question. Chapters are linked with "but..." |
| Physics layer | Real Engineering | every "how" line gets a flow, heat or pressure visual or a graph |
| Inside view | Animagraffs | ghost skin + colour-coded systems + exploded slide-outs |
| Context | Wendover/Rathee maps | at most 2 map moments (range, launch platforms) |
| Scale | Kurzgesagt-style metaphor | 1 metaphor per number |

### 3.2 Colour and label code (use the same codes in Blender materials and in GSAP overlays)
| Meaning | Colour | Hex | Used for |
|---|---|---|---|
| Airframe / structure | gunmetal grey | `#5B6670` | skin, fins (ghosted at 15-25% alpha in x-ray) |
| Solid booster / hot exhaust | ember orange | `#FF7A1A` | booster grain, flame, separation |
| Ramjet air (cold intake) | ice cyan | `#3FD0FF` | intake streamlines, low pressure |
| Compressed / hot air | magenta-red ramp | `#FF3B6B` | combustion chamber, high pressure |
| Liquid fuel | amber | `#FFC233` | fuel tank, injectors |
| Guidance / electronics / radar | electric green | `#38E08C` | seeker, INS/GPS, radar beams |
| Enemy / threat / target | warning red | `#E5383B` | ships, enemy radar, intercept zones |
| India / friendly / range rings | saffron to white | `#FF9933` / `#FFFFFF` | maps, flags, range rings |
| Background | deep navy gradient | `#0A1020` to `#16233D` | all overlays and the 3D world backdrop |

- Pressure and temperature ramp: cyan `#3FD0FF`, then white, then `#FF3B6B`, then `#FFC233` (hottest). Always show a small legend bar in the corner the first time it appears.
- **Typography:** one geometric sans for English labels and one matching Devanagari face for Hindi (choose with the EngineX typography skill). Numbers are tabular, bold and large, with units in a lighter weight. No serif.
- **Labels:** thin 1.5 px leader line, a dot on the part, the label outside the model silhouette (memory rule: **text never covers the 3D model**). Show at most 2 labels at once. Each label fades out after the line that named it.
- **Text density:** at most 6 words per label. One "number slam" per scene at most. No paragraphs on screen.

### 3.3 Pacing rules
1. **A visual change every 3-5 s** (camera move, new label, cut, graph step or colour change). There should never be more than 6 s of static frame.
2. **Hard cut or major transition every 8-12 s.** That gives about 6-8 cuts per minute, above Branch's typical rate and below Rober's.
3. **One "pattern break" per chapter:** slow-mo, music drop, sudden silence plus a number slam, or a speed ramp. Never two in a row.
4. **Every chapter ends on a "but" or a question** that opens the next chapter (open loop). Close every loop by the end of the video.
5. **Camera always moves**, even slowly (2-5% dolly or orbit per shot). Consecutive shots keep the same screen direction, nose to tail, left to right, as the missile flies left to right.
6. **Music:** library tracks only (`find_sound`). Change the bed at chapter boundaries. Duck under the voice. Drop to silence 0.5 s before the 3 biggest numbers. Every reveal gets an SFX hit (whoosh, thump, sonic crack, mechanical clunk).
7. **The hook (first 15 s)** must contain: a question, a striking visual and a number.

### 3.4 Hook formula (first 15 s, Rober + Real Engineering)
- 0-3 s: black, then the canister lid blows off, smoke and booster flame (sound first, image a beat later).
- 3-8 s: *"A ship has about 20 seconds to react... and it still can't stop this."* Sea-skimming chase cam, a speed counter slams to **Mach 2.8**.
- 8-12 s: answer early: *"This is BrahMos, the fastest cruise missile of its kind in service."* Hero orbit, ghost skin flickers to x-ray for 1 s (a tease).
- 12-15 s: bigger question: *"But how does something with no turbine fly at three times the speed of sound?"* Cut to the black ramjet tube, with a "?" over the empty interior.
- *(Check all numbers against the fact ledger before locking the script.)*

### 3.5 Dynamic visual ideas mapped to script chapters

| # | Chapter / likely line | Visual (Blender = B, GSAP overlay = G) | Borrowed from |
|---|---|---|---|
| 1 | Hook: launch | B: vertical canister cold-launch, lid pops, smoke particle burst, booster ignites. Speed ramp to slow-mo at ignition | Rober |
| 2 | Hook: reaction time | B: sea-skimming chase cam 5 m above procedural ocean waves, low sun. G: countdown "20 s" in red in the corner | Rober |
| 3 | Hook: "how?" | B: hero orbit, then a 1 s x-ray flicker. G: big "?" outside the silhouette | Rober open loop |
| 4 | Open it: overview | B: exploded view along the long axis: nose/seeker, guidance bay, fuel tank, ramjet, booster. Each slides out with a clunk SFX. G: colour-coded labels | Animagraffs + Branch |
| 5 | Open it: two stages | B: ghost skin. Booster glows orange and ramjet section glows cyan/red. G: "Stage 1: solid booster / Stage 2: liquid ramjet" two-column card beside the model | Animagraffs |
| 6 | System 1, booster: burn | B: section of the booster grain, with a flame front moving through the grain as an emission shader. G: thrust counter climbing | Real Eng |
| 7 | System 1: separation | B: **slow-mo booster separation**: clamp release, booster tumbles away, smoke trail bends. Music drop then thump | Rober / SmarterEveryDay slow-mo |
| 8 | System 1: "but a rocket can't..." | G: split screen: rocket fuel burn time vs ramjet. Fuel-tank bars draining, rocket empties first | Rober "but" chain |
| 9 | System 2, ramjet: intake | B: lengthwise section of the nose intake, **shock cone** with 2-3 oblique shock lines (thin white planes), cyan streamlines slowing and compressing | Real Eng |
| 10 | System 2: pressure | B/G: streamline colour ramp from cyan to white to red as pressure rises. Legend bar in the corner. G: "air squeezed with no compressor" | Real Eng + colour code |
| 11 | System 2: combustion | B: amber fuel spray from injectors into the red zone, flame holders light, exhaust exits nozzle. Particle speed increases at the exit | Animagraffs + Real Eng |
| 12 | System 2: why no turbine | G: side-by-side turbojet (spinning blades, labelled) vs ramjet (empty tube). The blades fade out with a "not needed above ~Mach 2" tag | Real Eng constraint framing |
| 13 | System 2: needs speed to start | G: line graph thrust vs speed. Ramjet thrust is zero until high speed, and the booster fills the gap (orange area under the curve) | Real Eng graph |
| 14 | System 3, guidance: INS/GPS midcourse | B: missile on a flight path over a stylised terrain map. G: green dotted planned path, satellite icons pinging | Wendover map grammar |
| 15 | System 3: radar horizon | G: Earth-curve diagram: ship radar beam (red) grazes the horizon, missile flying under it at sea-skim height is invisible. Radar range shrinks as the missile drops | Real Eng diagram |
| 16 | System 3: seeker turns on | B: nose x-ray, green radar cone sweeps out ahead, locks on a ship silhouette. G: "LOCK" pill outside the model | Animagraffs + Rober SFX |
| 17 | System 3: terminal manoeuvre | B: top-down chase of an S-weave / pop-up dive. G: trail line drawn behind | Rober chase |
| 18 | System 4, warhead/energy: speed race | G: horizontal race lane, all to scale: airliner (~Mach 0.85), rifle bullet (~Mach 2.5-3), BrahMos (~Mach 2.8), subsonic cruise missile (~Mach 0.7). Running time to 100 km for each | Rober comparison |
| 19 | System 4: kinetic energy | G: KE = 1/2 m v^2 builds itself. v^2 is highlighted. Blocks of equivalent energy stack up (e.g. "x times a subsonic missile of the same mass") | Real Eng + Kurzgesagt scale |
| 20 | System 4: reaction time | G: timeline bar of defender reaction time: subsonic vs supersonic from the horizon. The supersonic bar is about a third as long | Rober "but" / Real Eng |
| 21 | Dive: inside flight | B: continuous fly-through camera inside the ghosted missile from intake to nozzle, following one cyan air particle that turns red. One long take (about 10 s) as the pattern break | Animagraffs + Branch dive |
| 22 | Connect: platforms | G: map of India: icons pop in for ship, land launcher, Su-30MKI, submarine. Each launch variant gets a 1-2 s B-cut | Wendover map |
| 23 | Connect: range | G: range rings grow from Indian bases with a number counter (290 km base, then extended variants). Dotted arcs to sea areas. **No political targeting graphics** | Rathee/Wendover map |
| 24 | Close: impact/payoff | B: final slow-mo sea-skim to a target hull silhouette, cut to white flash just before contact (no gore). Then silence | Rober payoff |
| 25 | Close: recap | B: missile reassembles from the exploded view. G: the 4 system colours light up in sequence as each is named. End on hero orbit + title | Animagraffs + Branch |

### 3.6 Blender / GSAP implementation notes
- **Ghost skin:** Mix Shader (Transparent + Principled) driven by a single `xray` float on the material. Keyframe it 0 to 0.8 instead of separate models.
- **Section:** Boolean with a half-space cube, or alpha-clip by object-space Y < 0. Cap faces in a flat colour (Animagraffs look).
- **Shock cones:** thin cone meshes with emission + alpha fresnel, scaled on the shot. These are illustrative, not CFD. Say "simplified" in the VO only if asked.
- **Streamlines:** curve objects with an animated dash texture (offset driver), material ramp keyed to the pressure colour code. Particles are optional and cost render time.
- **Ocean chase:** Ocean modifier, camera parented to an empty following the missile with a 2-3% lag. Add motion blur on this shot only.
- **Slow-mo:** render at a 3x frame step on separation, impact and launch, and retime in the edit rather than re-simulating.
- **GSAP overlays:** the counter uses `gsap.to(obj,{val, snap})`. Range rings and graph lines use stroke-dashoffset draws. Use `back.out(1.6)` easing for number slams and `power2.inOut` for everything else. Keep all overlays in the side safe-area (left or right 35%) so the model stays clear.
- **Hindi:** the same overlay file with a lang switch. Numbers stay in Western digits for readability. Units are spoken in Hindi, written as `km`, `Mach`.

### 3.7 Do / don't
- DO: a visual for every line, the same colour code throughout, open loops at chapter ends, music drops before big numbers, and every claim backed by the fact ledger.
- DON'T: copy any channel's music, character, logo or font. No gore or real-casualty footage, and no "target country" maps. No text over the model. Don't stack more than 2 labels, and don't slam numbers back to back.

---

## Sources
- Real Engineering interview (process, writing, animation quality): https://portershed.com/?p=2086
- Real Engineering / Throttle Media: https://www.irishtimes.com/advertising-feature/2025/12/19/full-throttle
- Real Engineering creator background (aeronautical MSc): https://ioplus.nl/archive/en/five-cool-youtube-channels-for-innovation-fans/
- Animagraffs about (Biesty cross-section influence, "art form"): https://animagraffs.com/about/
- Animagraffs coverage: https://gigazine.net/gsc_news/en/20140703-animagraffs , https://boingboing.net/?p=1096786 , https://awsprod.merlot.org/merlot/viewCompositeReview.htm?id=1381399
- Mark Rober techniques breakdown (hook, "but", slow-mo, music drops, speed ramps): https://rosetta.to/u/digspaghetti/deconstructing-the-mark-rober-effect-ft-hayden-hillier-smith
- Mark Rober growth/hook analysis: https://rosetta.to/u/vidiq/the-expected-and-totally-predictable-rise-of-mark-rober , https://www.opus.pro/blog/mark-robers-growth-playbook-how-he-engineered-one-of-youtubes-most-trusted-brands
- Kurzgesagt process: https://kurzgesagt.org/youtube/ , https://rosetta.to/u/kurzgesagt/how-to-make-a-kurzgesagt-video-in-1200-hours
- Kurzgesagt style commentary: https://artsatmichigan.umich.edu/ink/2019/09/27/simple-bright-beautiful-the-work-of-kurzgesagt
- Jared Owen process: https://www.blendernation.com/2018/11/19/meet-the-artist-jared-owen/ , https://www.blendernation.com/2020/04/02/video-whats-inside-the-space-needle/
- Smarter Every Day (slow-mo core, missile test engineer): https://www.quantumcomposers.com/photonics-news-blog/post/2019/10/15/quantum-composers-helping-you-get-smarter-every-day , https://www.sciencefriday.com/segments/youtuber-wants-to-make-you-smarter-every-day/
- Dhruv Rathee editing style (weak, tutorial/gig sources): https://recapio.com/digest/how-to-edit-like-dhruvrathee-on-phone-by-tube-sensei , https://videohighlight.com/v/KvH3Hd0qR6c
- Indian defence explainer landscape: https://recapio.com/digest/bhaart-kii-nii-misaail-se-hddknp-defence-knowledge-show-by-defence-knowledge-show
- Branch Education tools (Blender Eevee/Cycles, Premiere, Reaper; third-party mirror of the channel page): https://yt2009-a6hh.onrender.com/channel/UCdp4_l1vPmpN-gDbUwhaRUQ
