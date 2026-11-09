# Notes - Branch Education, "How do Digital and Analog Clocks Work?"

Source: https://www.youtube.com/watch?v=oEC5fIw0bL0 (15:35, 30 fps, 1080p). Credits: animation Eikonic Design, built in
**Blender 4.0.1**; clock internal model / iPhone model by Prakash Kakadiya; script Teddy Tablante; VO Phil Lee; sound
drilu.mx. Evidence: `transcript.md`, `contact-sheets/sheet-000..007.jpg` (122 frames, one per cut plus every ~8 s inside
long takes, sponsor 9:04-10:40 skipped). EngineX calls used for this study: 7.

## Measured numbers
| What | Value | How |
|---|---|---|
| Narration speed | **146 wpm** (2,266 words, 15:32) | word timestamps |
| Shots (excluding sponsor) | 73, median **6.0 s**, mean 11.5 s; 36 shots < 6 s, 5 > 20 s | scene detection |
| Longest continuous takes | 51 s (4:02 lattice), 67 s (6:48 inverter loop), **192 s** (10:53-14:05 PLL diagram) | scene detection |
| Cut vs. spoken part name (3D sections) | cut lands a median **0.62 s BEFORE** the word (14 terms within +-4 s) | term onset vs nearest cut |
| Pauses > 0.5 s | 97 (about one per sentence), median 0.6 s | word gaps |
Diagram sections do not cut at all: labels, numbers and highlights animate in place on the word.

## Structure of the film (sequence of the explanation)
1. **0:00-1:07 Hook in a real, photoreal room**: daylight through window blinds, a wall clock, a phone on a dresser,
   shallow DOF. The phone screen shows the subject (2.4 GHz, a signal generator UI). 0:22 the phone opens into an
   x-ray layer view. 1:02 abstract "data flowing on a PCB" (light streaks), 1:07 logo sting.
2. **1:10 "Let's open it"**: the clock movement floats on black; the casing peels away, revealing parts.
3. **System by system** (each named system gets a title chip): **GEAR TRAIN** (1:20) -> **ELECTROMAGNET** (1:27) ->
   magnetic field (1:45) -> driver gear -> compound gears -> second/minute/hour hand paths -> time setting gear
   -> **crystal oscillator** canister (3:45) -> **tuning fork** inside (3:47, the can goes transparent).
4. **Zoom from macro to micro**: 4:02 fade to black, 4:12 a hexagonal SiO2 cell, 4:20 the lattice, 4:27-5:02 charge
   applied (NEGATIVE / POSITIVE CHARGE chips), lattice stretches and shrinks.
5. **Back up to the part**: 5:12 the tuning fork with the effect shown on it ("Movement exaggerated for this
   visualization"), coloured +/- electrodes (red/blue), legs bending.
6. **3D -> 2D schematic**: 6:30 **INTEGRATED CIRCUIT** chip lit on the PCB -> 6:35 a schematic drawn OVER the blurred 3D
   (inverter, tuning-fork symbol, two capacitors) -> 6:50 a full 2D HUD diagram (inverter, 1/0 boxes, timer readouts,
   15-bit binary counter, 32,768 -> 1.00 s).
7. **Back to the real thing**: 7:57 the coil and PCB, 8:00 the magnet flips (red/blue), 8:07 the hands tick,
   8:17 big numbers over a glowing clock face (32,768; +-20 ppm; +-1.73 s per day), 8:40 back to the room.
8. **Second subject reuses the first**: 10:45 the phone exploded in 3D (5 GHz, "30k-150k x FASTER"), then a single
   192 s schematic take that grows piece by piece: ring oscillator -> PHASE LOCKED LOOP title -> VCO -> crystal
   oscillator -> comparator -> integrator -> frequency divider -> 2.4 GHz result.
9. **Close**: 14:35 back to the photoreal phone (exploded, 1 GHz), 14:42 the room, credits, end card on a glowing chip.
Pattern: **real world -> open it -> one system at a time -> zoom to the physics -> abstract to a diagram -> return to the
real object -> return to the room.** Every abstraction is bracketed by the real object.

## Visual grammar (repeatable rules)
- **Two lighting worlds**: (a) context = photoreal warm daylight interior, window-blind shadow stripes, long lens, very
  shallow DOF; (b) internals = black void, one soft key from above, a rim, subtle haze/volumetric light shafts, floor
  invisible. Internals never show a room.
- **Focus by subtraction**: the part being named is solid and lit; the rest of the assembly drops to a faint
  **blue-grey ghost / wireframe** (2:12, 2:25, 3:47) or goes out of focus. Housings turn to glass to reveal what is
  inside (crystal canister).
- **Highlight on the word**: the named part gets an **orange glow ring / outline** (2:10, 2:50) or an orange tint
  (2:12 gear, 3:17 hand); energy and signals are orange.
- **Consistent colour code**: orange = active / signal / current; red vs blue = the two magnet poles and +/- charge
  (05:17-06:25 swap colours as polarity flips); oxygen red vs silicon white in the lattice; white matte plastic for
  gears; metal stays metal.
- **Physics shown, not told**: magnetic field = glowing particle arcs; charge = +/- badges on the electrodes;
  piezo motion = legs bending (exaggerated, with a disclaimer); timing = a squiggle running along the wire (6:40).
- **Callout chips**: section titles in bold italic caps, yellow-orange, lower-right ("GEAR TRAIN", "ELECTROMAGNET",
  "INTEGRATED CIRCUIT"); gear ratios as compact chips "12 < 48", "40 < 10" with the arrow pointing at the driven
  gear; numbers huge and kinetic (counters roll: 00000 -> 32,768; 0.00 -> 1.00 s); units small ("GHz", "MHz").
- **Honesty labels**: small italic top-left disclaimers: "Movement exaggerated for this visualization",
  "*Diagrams do not necessarily reflect commonly used symbology".
- **Schematics**: dark grid "HUD" background, white 2 px line art, orange accents, small Title Case labels, one block
  added at a time, signal flow as moving chevrons/dashes, oscilloscope boxes for waveforms, readouts in boxed mono.
  Schematic icons match the 3D parts (the tuning-fork symbol is the fork's silhouette).
- **Branding**: small "Branch Education" bug bottom-right on every shot.

## Camera language
- **Lead with the camera**: the camera starts moving to the next part ~0.5-0.6 s before the narrator says it, and is
  settled on it as the word lands.
- **Follow the causal chain** in one move: coil -> iron strip -> driver gear -> each gear pair -> the shaft -> the hand
  (1:27-3:32 is a sequence of short shots that read as one journey).
- Mostly slow dollies/arcs with parallax and rack focus; macro lenses (long focal, shallow DOF) for parts;
  **scale transitions** (dive into the crystal, fade to the atomic scale, come back out).
- A long locked-off diagram take is used for logic that needs to be built step by step; the "camera" there is the
  diagram growing.

## Naming
Functional, plain-English names in Title Case on screen, defined once by the narrator and reused exactly:
Driver Gear, Electromagnet (Coil of Wire + Strip of Iron), Compound Gear, Idler, Second/Minute/Hour Hand, Time Setting
Gear, Crystal Oscillator, Quartz Crystal Tuning Fork, Integrated Circuit, Inverter, Capacitor, Feedback Loop, Binary
Counter (15-bit, D flip-flops x15), Ring Oscillator, Voltage-Controlled Oscillator (VCO), Phase Comparator, Integrator,
Frequency Divider, Phase Locked Loop. Acronyms are spoken in full first ("voltage-controlled oscillator, or VCO").
Section titles (chips) = system names in CAPS; values always with units.

## Script technique (heard)
- Analogy before mechanism ("like pushing a kid on a swing set ... but in both directions").
- "This is a complicated circuit, but here's one way of thinking about it" -> simplified model, flagged as such.
- Numbers are concrete and checkable (12->48 then 8->60 gives 1 rev / 60 s; 32,768 Hz; 20 ppm = 1.7 s/day).
- Ties the second topic back to the first ("just like the one in the wall clock that took 32,768 cycles...").

## Unclear (not readable at this frame density)
- Exact lens values, render engine (Cycles vs EEVEE) and samples: not stated anywhere.
- How the ghost/x-ray material is built (could be a holdout/wireframe overlay or a compositor pass).
- Whether the HUD schematics are Blender (grease pencil/curves) or compositing software; they look 2D composited.
